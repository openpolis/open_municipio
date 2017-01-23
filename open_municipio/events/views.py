from django.views.generic import TemplateView, DetailView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime
from django.conf import settings
from haystack.query import SearchQuerySet
from django.utils.translation import ugettext_lazy as _

from .models import Event
from open_municipio.people.models import Institution
from open_municipio.acts.models import Act
from open_municipio.acts.models import Speech
from open_municipio.om_search.views import ExtendedFacetedSearchView
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from .forms import EventsSearchForm

class EventActSpeechesView(ListView):
    model = Speech
    template_name = "events/event_speech_list.html"
    event = None

    def get_queryset(self):
        # set the event object
        pk = self.kwargs["pk"]
        self.event = Event.objects.get(pk=pk)

        # set the act object
        act_pk = self.kwargs["act_pk"]
        self.act = Act.objects.get(pk=act_pk)

        # return the related speeches
        res = Speech.objects.filter(act__pk=act_pk)
    
#        print "found %s" % res
        return res


    def get_context_data(self, **kwargs):
        context = super(EventActSpeechesView, self).get_context_data(**kwargs)

        extra_context = {
            'event' : self.event,
            'act' : self.act,
        }

        context.update(extra_context)
 
        return context


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        # the event
        event = self.get_object()

        # call the base implementation first to get a context
        context = super(EventDetailView, self).get_context_data(**kwargs)

        # mix-in tab-related context
        self.tab = self.kwargs.get('tab', 'default')
        extra_context = getattr(self, 'get_related_%(tab)s' % {'tab': self.tab})()
        if extra_context:
            context.update(extra_context)

        context['n_acts'] = event.eventact_set.count()

        # first day of current month
        filter_since = datetime.today().replace(day=1)
        context['future_events'] = Event.objects.filter(date__gte=filter_since)

        return context

    def get_related_default(self):
        """
        Retrieve context needed for populating the default tab.
        """
        pass
    
    def get_related_acts(self):
        """
        Retrieve context needed for populating the *amendments* tab.
        """
        pass

    def get_template_names(self):

        if self.tab == 'default': # default tab selected
            return 'events/event_detail.html'
        else:
            return 'events/event_detail_%(tab)s.html' % {'tab': self.tab}


class EventSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """

    This view allows faceted search and navigation of the events.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized

    """
    __name__ = 'EventSearchView'

    FACETS_SORTED = ['date', 'institution']

    FACETS_LABELS = {
        'institution': _('Institution'),
        'date': _('Data'),
    }
    DATE_INTERVALS_RANGES = { }

    def __init__(self, *args, **kwargs):

        # dynamically compute date ranges for faceted search
        curr_year = datetime.today().year
        for curr_year in xrange(settings.OM_START_YEAR, curr_year + 1):
            date_range = self._build_date_range(curr_year)
            self.DATE_INTERVALS_RANGES[curr_year] = date_range
    
        sqs = SearchQuerySet().filter(django_ct='events.event').\
            facet('institution')

        for (year, range) in self.DATE_INTERVALS_RANGES.items():
            sqs = sqs.query_facet('date', range['qrange'])

        kwargs['searchqueryset'] = sqs.highlight()

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = EventsSearchForm

        super(EventSearchView, self).__init__(*args, **kwargs)

    def _build_date_range(self, curr_year):
        return { 'qrange': '[%s-01-01T00:00:00Z TO %s-12-31T00:00:00Z]' % \
                (curr_year, curr_year), 'r_label': curr_year }

    def build_page(self):
        self.results_per_page = int(self.request.GET.get('results_per_page', settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE))
        return super(EventSearchView, self).build_page()

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(EventSearchView, self).build_form(form_kwargs)

    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(EventSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets, 'date')

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(EventSearchView, self).extra_context()

        extra['base_url'] = reverse('om_event_search') + '?' + extra['params'].urlencode()

        # get data about custom date range facets
        extra['facet_queries_date'] = self._get_custom_facet_queries_date('date')

        extra['facets_sorted'] = self.FACETS_SORTED
        extra['facets_labels'] = self.FACETS_LABELS

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

        extra['related_search'] = [
            { 'label' : _('acts'), 'url' : reverse('om_act_search') + '?q=' + self.query },
            { 'label' : _('speeches'), 'url' : reverse('om_speech_search') + '?q=' + self.query },
            { 'label' : _('votations'), 'url' : reverse('om_votation_search') + '?q=' + self.query },
        ]

        return extra
