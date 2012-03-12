from django.conf.urls.defaults import *
from django.views.generic import DetailView

from open_municipio.people.models import Person


urlpatterns = patterns('',
    url(r'^citizen/(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=Person,
        context_object_name='person',
        template_name='people/citizen_detail.html',
    ), name='om_citizen_detail'),

    url(r'^person/(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=Person,
        context_object_name='person',
        template_name='people/person_detail.html',
    ), name='om_person_detail')
)
    