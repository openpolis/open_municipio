from django.conf.urls.defaults import *
from open_municipio.people.models import Person
from open_municipio.people.views import PoliticianDetailView, PoliticianListView


urlpatterns = patterns('',
    url(r'^$', PoliticianListView.as_view(), name='om_politician_list'),

    url(r'^(?P<slug>[-\w]+)/$', PoliticianDetailView.as_view(
        model=Person,
        context_object_name='person',
        template_name='people/politician_detail.html',
    ), name='om_politician_detail')
)
    