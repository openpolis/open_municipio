from django.conf.urls import *

from open_municipio.autocomplete.views import TagAutoCompleteView


urlpatterns = patterns('',
    url(r'^tags/', TagAutoCompleteView.as_view(),  name='om_autocomplete_tag'),
)
