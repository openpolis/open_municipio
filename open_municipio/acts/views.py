from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, ListView, FormView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import simplejson as json
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from haystack.query import SearchQuerySet

from voting.views import RecordVoteOnItemView

from open_municipio.acts.models import Act, Agenda, CGDeliberation, Deliberation, Interpellation, Interrogation, Motion, Amendment, Transition
from open_municipio.acts.forms import ActDescriptionForm, ActTransitionForm, ActFinalTransitionForm, ActTitleForm
from open_municipio.locations.models import Location

from open_municipio.monitoring.forms import MonitoringForm

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.om_search.views import ExtendedFacetedSearchView
from open_municipio.people.models import Person
from open_municipio.acts.models import Speech

from open_municipio.taxonomy.models import Tag, Category

from open_municipio.locations.forms import ActLocationsAddForm          

import re



class ActSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """

    This view allows faceted search and navigation of the acts.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized whenever

    """
    __name__ = 'ActSearchView'

    FACETS_SORTED = ['act_type', 'is_key', 'is_proposal', 'initiative', 'organ', 'pub_date', 'has_locations', 'month', 'status']
    FACETS_LABELS = {
        'act_type': _('Act type'),
        'is_key': _('Is key act'),
        'is_proposal': _('Is proposal'),
        'initiative': _('Initiative'),
        'organ': _('Organ'),
        'pub_date': _('Pubblication year'),
        'month': _('Pubblication month'),
        'status': _('Status')
    }
    DATE_INTERVALS_RANGES = { }

    def __init__(self, *args, **kwargs):

        # dynamically compute date ranges for faceted search
        curr_year = datetime.today().year
        for curr_year in xrange(settings.OM_START_YEAR, curr_year + 1):
            date_range = self._build_date_range(curr_year)
            self.DATE_INTERVALS_RANGES[curr_year] = date_range
    
        sqs = SearchQuerySet().filter(django_ct='acts.act').\
            facet('act_type').facet('is_key').facet('is_proposal').\
            facet('initiative').facet('organ').facet('month').facet('status')

        for (year, range) in self.DATE_INTERVALS_RANGES.items():
            sqs = sqs.query_facet('pub_date', range['qrange'])

        sqs = sqs.order_by('-pub_date').highlight()
        kwargs['searchqueryset'] = sqs

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ActSearchView, self).__init__(*args, **kwargs)

    def _build_date_range(self, curr_year):
        return { 'qrange': '[%s-01-01T00:00:00Z TO %s-12-31T00:00:00Z]' % \
                (curr_year, curr_year), 'r_label': curr_year }

    def build_page(self):
        self.results_per_page = int(self.request.GET.get('results_per_page', settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE))
        return super(ActSearchView, self).build_page()

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(ActSearchView, self).build_form(form_kwargs)

    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(ActSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets, 'pub_date')

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """

        extra = super(ActSearchView, self).extra_context()
        extra['base_url'] = reverse('om_act_search') + '?' + extra['params'].urlencode()

        person_slug = self.request.GET.get('person', None)
        if person_slug:
            try:
                extra['person'] = Person.objects.get(slug=person_slug)
            except ObjectDoesNotExist:
                pass

        category_slug = self.request.GET.get('category', None)
        if category_slug:
            try:
                extra['category'] = Category.objects.get(slug=category_slug)
            except ObjectDoesNotExist:
                pass

        tag_slug = self.request.GET.get('tag', None)
        if tag_slug:
            try:
                extra['tag'] = Tag.objects.get(slug=tag_slug)
            except ObjectDoesNotExist:
                pass

        location_slug = self.request.GET.get('location', None)
        if location_slug:
            try:
                extra['location'] = Location.objects.get(slug=location_slug)
            except ObjectDoesNotExist:
                pass

        recipient_slug = self.request.GET.get('recipient', None)
        if recipient_slug:
            try:
                extra['recipient'] = Person.objects.get(slug=recipient_slug)
            except ObjectDoesNotExist:
                pass

        # get data about custom date range facets
        extra['facet_queries_date'] = self._get_custom_facet_queries_date('pub_date')

        extra['facets_sorted'] = self.FACETS_SORTED
        extra['facets_labels'] = self.FACETS_LABELS

        # check if is_proposal facets must be shown
        if 'is_proposal' in extra['facets']['fields']:
            extra['show_is_proposal_facets'] = sum(map(lambda x: x[1], extra['facets']['fields']['is_proposal']['counts']))

        # check if initiative facets must be shown
        if 'initiative' in extra['facets']['fields']:
            extra['show_initiative_facets'] = sum(map(lambda x: x[1], extra['facets']['fields']['initiative']['counts']))

        paginator = Paginator(self.results, self.results_per_page)
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page_obj = paginator.page(paginator.num_pages)

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj


        return extra


from django.http import HttpResponse

class ActListView(ListView):
    template_name = 'acts/act_list.html'
    queryset = Act.objects.select_subclasses().order_by('-presentation_date')
    context_object_name = 'acts'
    
    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(ActListView, self).get_context_data(**kwargs)
        context['key_acts'] = Act.featured.all()
        
        return context


class ActLiveEditView(FormView):
    def dispatch(self, *args, **kwargs):
        return super(ActLiveEditView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response_data = {}

        try:
            if not self.request.user.is_authenticated() or not self.kwargs.get('pk') == request.POST.get('id'):
                raise Exception('NOT_ALLOWED1')

            target_act = Act.objects.get(pk=self.kwargs.get('pk'))
            target_act_field = self.request.POST.get('act_field')

            if target_act_field == 'adj_title':
                if not request.user.has_perm('acts.change_act'):
                    raise Exception('NOT_ALLOWED2')
                form = ActTitleForm(self.request.POST, instance=target_act)

            elif target_act_field == 'description':
                if not (self.request.user.get_profile().person and\
                   self.request.user.get_profile().person in [p.person for p in target_act.presenters]):
                    raise Exception('NOT_ALLOWED3')
                form = ActDescriptionForm(self.request.POST, instance=target_act)

            else:
                raise Exception('INVALID_FIELD')

            if not form.is_valid():
                raise Exception( form.errors )

            form.save()
            response_data['text'] = form.cleaned_data[ target_act_field ]

        except Act.DoesNotExist:
            response_data['error'] = 'ACT_NOT_FOUND'
        except Exception as e:
            response_data['error'] = e.args[0]

        return HttpResponse(json.dumps(response_data), mimetype="application/json")


class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'

    def get_context_data(self, **kwargs):
        # the monitored act
        # it's a deliberation, not an act, from the urls
        act = self.get_object()

        # call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # mix-in tab-related context
        self.tab = self.kwargs.get('tab', 'default')
        extra_context = getattr(self, 'get_related_%(tab)s' % {'tab': self.tab})()
        if extra_context:
            context.update(extra_context)

        if self.request.user.has_perm('acts.change_act'):
            # add a form for editing title of act
            context['title_form'] = ActTitleForm(initial = {
                'id': act.pk,
                'adj_title': act.adj_title or act.title,
                })
 
        if self.request.user.has_perm('locations.change_taggedactbylocation'):
            # add a form for classifying an act using locations
            context['location_form'] = ActLocationsAddForm(initial = {
                'act': act,
                'locations': act.locations,
                })
        
        # add a form for the description of the act
        signers = [p.person for p in act.presenters]
        try:
            if self.request.user.is_authenticated() and\
               self.request.user.get_profile().person and \
               self.request.user.get_profile().person in signers:
                context['description_form'] = ActDescriptionForm(initial = {
                    'id': act.pk,
                    'description': act.description,
                })
        except ObjectDoesNotExist:
            context['description_form'] = False
        
        # is the user monitoring the act?
        context['is_user_monitoring'] = False
        try:
            if self.request.user.is_authenticated():
                # add a monitoring form, to context,
                # to switch monitoring on and off
                context['monitoring_form'] = MonitoringForm(data = {
                    'content_type_id': act.content_type_id,
                    'object_pk': act.id,
                    'user_id': self.request.user.id
                })
                
                if act in self.request.user.get_profile().monitored_objects:
                    context['is_user_monitoring'] = True
        except ObjectDoesNotExist:
            context['is_user_monitoring'] = False

        # some user can edit categories and tags
        if self.request.user.has_perm('taxonomy.change_taggedact'):
            # all categories and tags
            context['topics'] = {
                'categories' : Category.objects.all(),
                'tags' : Tag.objects.all()
            }

        context['n_documents'] = act.attachment_set.count()
        context['n_votes'] = act.votation_set.count()
        context['n_amendments'] = act.amendment_set.count()
        context['n_speeches'] = len(act.speeches)

        # retrieve a dictionary with status and its transitions
        context['act_type'] = act._meta.verbose_name
        context['transition_groups'] = act.get_transitions_groups()

        # default public date and idnum
        # may be override for approved acts (see Deliberation and CGDeliberation)
        context['public_date'] = act.presentation_date
        context['public_idnum'] = act.idnum


        # some user can set transitions
        if self.request.user.has_perm('acts.change_transition') : #and context['status_list']
            context['transition_forms'] = {}
            if len(context['transition_groups']) == 5:
                context['transition_forms']['transition_to_council_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COUNCIL' },prefix="council")
                context['transition_forms']['transition_to_committee_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COMMITTEE' },prefix="committee")
            context['transition_forms']['transition_to_final_form'] = ActFinalTransitionForm(initial={'act': act },prefix="final")
            context['transition_forms']['transition_to_final_form'].fields['final_status'].widget.choices = act.FINAL_STATUSES

        return context
    
    def get_related_default(self):
        """
        Retrieve context needed for populating the default tab.
        """
        pass
    
    def get_related_amendments(self):
        """
        Retrieve context needed for populating the *amendments* tab.
        """
        pass

    def get_related_documents(self):
        """
        Retrieve context needed for populating the *documents* tab.
        """
        pass
    
    def get_template_names(self):
        model_name = self.model.__name__.lower()

        # deliberations and cgdeliberations use the same template
        if model_name == 'cgdeliberation':
            model_name = 'deliberation'
        if self.tab == 'default': # default tab selected
            return 'acts/%(model)s_detail.html' % {'model': model_name}
        else:
            return 'acts/%(model)s_detail_%(tab)s.html' % {'model': model_name, 'tab': self.tab}


class AgendaDetailView(ActDetailView):
    model = Agenda


class CGDeliberationDetailView(ActDetailView):
    model = CGDeliberation
    template_name = "acts/deliberation_detail.html"

    def get_context_data(self, **kwargs):
        """
        ``public_date`` and ``public_idnum`` override for approved deliberations
        """
        context = super(CGDeliberationDetailView, self).get_context_data(**kwargs)
        d = self.get_object()

        if d.status == 'APPROVED':
            if d.approval_date:
                context['public_date'] = d.approval_date

            if d.final_idnum:
                context['public_idnum'] = d.final_idnum

        return context


class DeliberationDetailView(ActDetailView):
    model = Deliberation

    def get_context_data(self, **kwargs):
        """
        ``public_date`` and ``public_idnum`` override for approved deliberations
        """
        context = super(DeliberationDetailView, self).get_context_data(**kwargs)
        d = self.get_object()

        if d.status == 'APPROVED':
            if d.approval_date:
                context['public_date'] = d.approval_date

            if d.final_idnum:
                context['public_idnum'] = d.final_idnum

        return context


class InterpellationDetailView(ActDetailView):
    model = Interpellation


class InterrogationDetailView(ActDetailView):
    model = Interrogation


class MotionDetailView(ActDetailView):
    model = Motion


class AmendmentDetailView(ActDetailView):
    model = Amendment
    

## tags/categories management
class ActTagEditorView(View):
    """
    Server-side component of the "Act-Tag-Editor" widget.
    """
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ActTagEditorView, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        """
        Returns the ``Act`` instance being tagged.
        """
        tagged_act = get_object_or_404(Act, pk=self.kwargs.get('pk'))
        return tagged_act
    
    def get_success_url(self):
        # on success, redirect to act's detail page
        return self.tagged_act.downcast().get_absolute_url()
    
    def post(self, request, *args, **kwargs):
        tagged_act = self.tagged_act = self.get_object()

        # remove old topics
        tagged_act.tag_set.clear()

        new_topics = {} # new set of topics (categories + tags) for the act
        r = re.compile(r'^categories\[(\d+)\]$')
        new_tags_ids = set()
        new_tags = set()
        for param in self.request.POST:
            if r.match(param):
                m = r.match(param)
                category = get_object_or_404(Category, pk=int(m.group(1)))
                new_topics[category] = []
                tag_ids = self.request.POST[param].split(',')
                if tag_ids != [u'']: # if this category has been associated to at least one tag
                    new_tags_ids |= set(tag_ids) 
                    for tag_id in tag_ids:
                        tag = get_object_or_404(Tag, id=int(tag_id))
                        new_topics[category].append(tag)
                        new_tags.add(tag)

        # adding new topics
        for cat in new_topics.keys():
            tagged_act.tag_set.add(*new_topics.get(cat), tagger=self.request.user, category=cat)

        
        return HttpResponseRedirect(self.get_success_url())   
 
    
class ActTransitionToggleBaseView(FormView):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ActTransitionToggleBaseView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form=None):
        msg = "Invalid transition for this act!"
        return HttpResponseBadRequest(msg)

    def get_success_url(self):
        return self.act.downcast().get_absolute_url()

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


class ActTransitionAddView(ActTransitionToggleBaseView):
    def post(self, request, *args, **kwargs):
        self.act = get_object_or_404(Act, pk=kwargs['pk'])
        nameprefix = request.POST.get('prefix', '')

        if 'final' == nameprefix:
            form = ActFinalTransitionForm(request.POST,prefix=nameprefix)
            form.fields['final_status'].widget.choices = self.act.downcast().FINAL_STATUSES
        else:
            form = ActTransitionForm(request.POST,prefix=nameprefix)

        if not form.is_valid():
            return self.form_invalid(form)

        form.save()

        return HttpResponseRedirect( self.get_success_url() )


class ActTransitionRemoveView(ActTransitionToggleBaseView):
    def post(self, request, *args, **kwargs):
        """
        TODO: clean transition from news, act's status and status_is_final
        """
        self.act = get_object_or_404(Act, pk=kwargs['pk'])

        transition = get_object_or_404(Transition, pk=request.POST['transition_id'])
        transition.delete()

        return HttpResponseRedirect(self.get_success_url())
    
    
class RecordVoteOnActView(RecordVoteOnItemView):
    model = Act   


class SpeechSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """
    """
    __name__ = 'SpeechSearchView'

    FACETS_SORTED = [ 'date', 'month' ]
    FACETS_LABELS = { 
        'date': _('Year'),
        'month': _('Month')
    }

    DATE_INTERVALS_RANGES = { } 

    def __init__(self, *args, **kwargs):

        # dynamically compute date ranges for faceted search
        curr_year = datetime.today().year
        for curr_year in xrange(settings.OM_START_YEAR, curr_year + 1):
            date_range = self._build_date_range(curr_year)
            self.DATE_INTERVALS_RANGES[curr_year] = date_range
    
        sqs = SearchQuerySet().filter(django_ct='acts.speech').facet('month')

        for (year, range) in self.DATE_INTERVALS_RANGES.items():
            sqs = sqs.query_facet('date', range['qrange'])

        kwargs['searchqueryset'] = sqs.order_by('-date').highlight()

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(SpeechSearchView, self).__init__(*args, **kwargs)

    def _build_date_range(self, curr_year):
        return { 'qrange': '[%s-01-01T00:00:00Z TO %s-12-31T00:00:00Z]' % \
                (curr_year, curr_year), 'r_label': curr_year }

    def build_page(self):
        self.results_per_page = int(self.request.GET.get('results_per_page', settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE))
        return super(SpeechSearchView, self).build_page()

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        form_kwargs['act_url'] = self.request.GET.get("act_url")

        return super(SpeechSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        extra = super(SpeechSearchView, self).extra_context()
        
        extra['base_url'] = reverse('om_speech_search') + '?' + extra['params'].urlencode()

        # get data about custom date range facets
        extra['facet_queries_date'] = self._get_custom_facet_queries_date('date')

        extra['facets_sorted'] = self.FACETS_SORTED
        extra['facets_labels'] = self.FACETS_LABELS

        person_slug = self.request.GET.get('person', None)
        if person_slug:
            try:
                extra['person'] = Person.objects.get(slug=person_slug)
            except ObjectDoesNotExist:
                pass

        paginator = Paginator(self.results, self.results_per_page)
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    
        extra['paginator'] = paginator
        extra['page_obj'] = page_obj
    
        return extra

class SpeechDetailView(DetailView):
    model = Speech
    context_object_name = 'speech'
    template_name = "acts/speech_detail.html"



