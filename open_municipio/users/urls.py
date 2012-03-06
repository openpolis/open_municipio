from django.conf.urls.defaults import *
from django.views.generic import DetailView
from django.contrib.auth.models import User

urlpatterns = patterns('',
    url(r'^(?P<pk>\w+)/$', DetailView.as_view(
         model=User,
         context_object_name='registered_user',
         template_name='users/user_detail.html',
    ), name='users_user_detail')
)

urlpatterns += patterns('profiles.views',
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
