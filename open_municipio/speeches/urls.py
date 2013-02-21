from django.conf.urls.defaults import patterns, url

from open_municipio.speeches.views import generate_speech_report

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', generate_speech_report),

)
