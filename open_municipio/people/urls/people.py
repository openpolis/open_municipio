from django.conf.urls.defaults import *

from open_municipio.people.models import Person
from open_municipio.people.views import PersonDetailView


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', PersonDetailView.as_view(
         model=Person,
         context_object_name='person',
         template_name='person_detail.html',
    ), name='om_person_detail')
)
    