from django.conf.urls.defaults import *
from django.views.generic import DetailView

from open_municipio.people.models import Person


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
         model=Person,
         context_object_name='person',
         template_name='person_detail.html',
    ), name='om_person_detail')
)
    