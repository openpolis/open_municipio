from django.conf.urls.defaults import *

from open_municipio.autocomplete.views import TagAutoCompleteView


urlpatterns = patterns('',
    url(r'^tags/', TagAutoCompleteView.as_view(),  name='om_autocomplete_tag'),
)
