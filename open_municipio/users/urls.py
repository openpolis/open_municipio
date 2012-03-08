from django.conf.urls.defaults import *
from django.views.generic import DetailView
from django.contrib.auth.models import User

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(
         model=User,
         context_object_name='registered_user',
         template_name='users/user_detail.html',
    ), name='users_user_detail')
)

urlpatterns += patterns('profiles.views',
    url(r'^profile/edit/$',
       'edit_profile',
       name='profiles_edit_profile'),
    url(r'^profile/(?P<username>\w+)/$',
       'profile_detail',
       name='profiles_profile_detail'),
    url(r'^$',
       'profile_list',
       name='profiles_profile_list'),
)
