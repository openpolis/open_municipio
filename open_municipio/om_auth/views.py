from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages
from django.utils.translation import ugettext_lazy as _

from social_auth import __version__ as version
from social_auth.utils import setting

from open_municipio.users.forms import UserSocialRegistrationForm, ProfileSocialRegistrationForm


@login_required
def login_done(request):
    """Login complete view, displays user data"""
    return redirect(request.user.get_profile())


def login_error(request):
    """Error view"""
    messages = get_messages(request)
    return render_to_response('om_auth/error.html', {'version': version,
                                             'messages': messages},
                              RequestContext(request))


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


def login_form(request):
    """
    When a user registers through a social network we need some
    additional information.
    """
    error = None
    if request.method == 'POST':
        profile_form = ProfileSocialRegistrationForm(request.POST)
        user_form = UserSocialRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            session_variable = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
            request.session['saved_username'] = user_form.cleaned_data['username']
            request.session['saved_privacy_level'] = profile_form.cleaned_data['privacy_level']
            request.session['saved_wants_newsletter'] = profile_form.cleaned_data['wants_newsletter']
            request.session['saved_city'] = profile_form.cleaned_data['city']
            backend = request.session[session_variable]['backend']
            return redirect('socialauth_complete', backend=backend)
        else:
            error = _('Form is invalid')

    user_form = UserSocialRegistrationForm()
    profile_form = ProfileSocialRegistrationForm()
    return render_to_response('om_auth/form.html', {
            'error': error,
            'user_form': user_form,
            'profile_form': profile_form,
            }, RequestContext(request))
