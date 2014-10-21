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

        ca = ChargeAttendance.objects.filter(attendance=attendance).order_by('charge__person__last_name', 'charge__person__first_name')

        names_presents = self._get_names(ca, ["PRES",])
        names_absents = self._get_names(ca, ["ABSENT","MISSION",])

        context['n_presents'] = attendance.chargeattendance_set.filter(value=ChargeAttendance.VALUES.pres).count()
        context['n_absents'] = attendance.chargeattendance_set.exclude(value=ChargeAttendance.VALUES.pres).count()
        context['names_presents'] = names_presents
        context['names_absents'] = names_absents

        return context

    def _get_names(self, voters, value_list):
        
        matching = filter(lambda v: v.value in value_list, voters)

        return ", ".join(map(self._get_label, matching))
       

    def _get_label(self, ca):

        assert isinstance(ca, ChargeAttendance)

        name = ca.charge.person.first_name
        surname = ca.charge.person.last_name
        group = ""
        try:
            group = " (%s)" % (ca.charge.current_groupcharge.group.acronym,)
        except: 
            pass

        label = "%s. %s%s" % (name[0], surname, group)

        return label
