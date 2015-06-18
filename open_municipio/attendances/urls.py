from django.conf.urls.defaults import *

from .views import AttendanceDetailView #, AttendanceSearchView

urlpatterns = patterns('',
    # faceted navigation
#    url(r'^$', AttendanceSearchView(template='attendances/attendance_search.html'), name='om_attendance_search'),
    # attendance detail
    url(r'^(?P<pk>\d+)/$', AttendanceDetailView.as_view(), name='om_attendance_detail'),
)
