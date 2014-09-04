from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.people.models import Person, InstitutionCharge
from django.utils.translation import ugettext_lazy as _

from .models import Attendance, ChargeAttendance

from open_municipio.acts.models import Agenda, Deliberation, Interrogation, Interpellation, Motion, Act


class AttendanceDetailView(DetailView):
    """
    Renders an Attendance page
    """
    model = Attendance
    template_name = 'attendances/attendance_detail.html'
    context_object_name = 'attendance'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AttendanceDetailView, self).get_context_data(**kwargs)

        # get last two calendar events

        attendance = self.get_object()

        context['n_absents'] = attendance.n_absents

        return context

