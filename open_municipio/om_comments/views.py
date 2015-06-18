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

from django.contrib import comments
from django.contrib.auth.decorators import login_required

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.om_search.views import ExtendedFacetedSearchView

from voting.views import RecordVoteOnItemView

from open_municipio.om_comments.models import CommentWithMood

import datetime



class DeleteOwnCommentView(View):
    """
    Users can delete their own comments within a certain time lapse.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteOwnCommentView, self).dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):    
        now = datetime.datetime.now()
        control_date = now - datetime.timedelta(seconds=settings.OM_COMMENTS_REMOVAL_MAX_TIME)
        # retrieve the comment that has been asked for removal
        comment = get_object_or_404(comments.get_model(), pk=self.kwargs.get('pk', None))
        # check if the comment may be removed, i.e if all the following conditions hold true:
        # * it was posted by the same user who made the removal request
        # * it belongs to the current site
        # * the time thresold for removal has not expired, yet 
        if (comment.user == request.user) and (comment.site.pk == settings.SITE_ID) and (comment.submit_date >= control_date):    
            # flag the comment as removed!
            comment.is_removed = True
            comment.save()
  
        # Whatever happened, just get back to the detail page of the content object the comment is attached to
        return HttpResponseRedirect(comment.content_object.get_absolute_url())
    

class RecordVoteOnCommentView(RecordVoteOnItemView):
    model = CommentWithMood

    def get(self, *args, **kwargs):
        """ 
        In django-voting, the GET request is not allowed. Here we "trick" the 
        library to accept it, transforming it to a POST request.
        """
    
        return super(RecordVoteOnCommentView, self).post(*args, **kwargs)

class CommentSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """

    This view allows faceted search and navigation of the comments.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized

    """
    __name__ = 'CommentSearchView'

    FACETS_SORTED = [ 'date', 'month' ]

    FACETS_LABELS = {
        'date': _('Year'),
        'month': _('Sitting month')
    }
    DATE_INTERVALS_RANGES = { }

    def __init__(self, *args, **kwargs):

        # dynamically compute date ranges for faceted search
        curr_year = datetime.datetime.today().year
        for curr_year in xrange(settings.OM_START_YEAR, curr_year + 1):
            date_range = self._build_date_range(curr_year)
            self.DATE_INTERVALS_RANGES[curr_year] = date_range
    
        sqs = SearchQuerySet().filter(django_ct='om_comments.commentwithmood').\
            facet('month')

        for (year, range) in self.DATE_INTERVALS_RANGES.items():
            sqs = sqs.query_facet('date', range['qrange'])

        kwargs['searchqueryset'] = sqs.order_by('-date').highlight()

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(CommentSearchView, self).__init__(*args, **kwargs)

    def _build_date_range(self, curr_year):
        return { 'qrange': '[%s-01-01T00:00:00Z TO %s-12-31T00:00:00Z]' % \
                (curr_year, curr_year), 'r_label': curr_year }

    def build_page(self):
        self.results_per_page = int(self.request.GET.get('results_per_page', settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE))
        return super(CommentSearchView, self).build_page()

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        #form_kwargs['act_url'] = self.request.GET.get("act_url")

        return super(CommentSearchView, self).build_form(form_kwargs)

    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(CommentSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets, 'date')

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(CommentSearchView, self).extra_context()
        extra['base_url'] = reverse('om_comments_search') + '?' + extra['params'].urlencode()

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

        return extra
