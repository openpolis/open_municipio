from django.conf.urls.defaults import *

urlpatterns = patterns('profiles.views',
    url(r'^profile/create/$',
       'create_profile',
       name='profiles_create_profile'),
    url(r'^profile/edit/$',
       'edit_profile',
       name='profiles_edit_profile'),
    url(r'^profile/(?P<username>\w+)/$',
       'profile_detail', { 'public_profile_field': 'is_public' },
       name='profiles_profile_detail'),
    url(r'^$',
       'profile_list', { 'public_profile_field': 'is_public' },
       name='profiles_profile_list'),
)
