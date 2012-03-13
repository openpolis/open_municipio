from django.conf.urls.defaults import *
from django.views.generic import DetailView
from django.views.generic.list import ListView

from open_municipio.people.models import Person


urlpatterns = patterns('',

    url(r'^$', ListView.as_view(template_name='people/person_list.html', model=Person), name='om_politician_list'),

    url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=Person,
        context_object_name='person',
        template_name='people/person_detail.html',
    ), name='om_person_detail')
)
    