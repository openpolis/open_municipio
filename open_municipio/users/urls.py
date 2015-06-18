from django.conf.urls.defaults import *
from open_municipio.users.forms import UserProfileForm
from open_municipio.users.views import UserDetailView, UserProfileListView, UserProfileDetailView
from django.contrib.auth.models import User
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<username>[\w\.@]+)/$',
        UserDetailView.as_view(),
    name='users_user_detail'),
)

urlpatterns += patterns('profiles.views',
    url(r'^profile/edit/$',
       'edit_profile',
       { 'form_class': UserProfileForm},
       name='profiles_edit_profile'),
    url(r'^profile/(?P<username>[\w\.@]+)/$',
        UserProfileDetailView.as_view(),
       name='profiles_profile_detail'),
    url(r'^$',
        UserProfileListView.as_view(),
       name='profiles_profile_list'),
)
