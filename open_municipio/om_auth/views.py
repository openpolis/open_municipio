from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages
from django.utils.translation import ugettext_lazy as _

from social_auth import __version__ as version
from social_auth.utils import setting

from open_municipio.users.forms import *


@login_required
def login_done(request):
    """Login complete view, displays user data"""
    return redirect(request.user.get_profile())


def login_error(request):
    """Error view"""
    messages = get_messages(request)
    return render_to_response('om_auth/error.html',
                              {'version': version,
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
    session_variable = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
    dsa_session = request.session[session_variable]
    backend =  dsa_session['kwargs']['backend']
    details = dsa_session['kwargs']['details']
    print dsa_session
    if backend.name == 'twitter':
        IntegrationForm = SocialTwitterIntegrationForm
    else:
        IntegrationForm = SocialIntegrationForm

    error = None
    if request.method == 'POST':
        social_form = IntegrationForm(request.POST)
        if social_form.is_valid():
            request.session['saved_username'] = social_form.cleaned_data['username']
            request.session['saved_location'] = social_form.cleaned_data['location']
            request.session['saved_says_is_politician'] = social_form.cleaned_data['says_is_politician']
            request.session['saved_uses_nickname'] = social_form.cleaned_data['uses_nickname']
            request.session['saved_wants_newsletter'] = social_form.cleaned_data['wants_newsletter']
            backend = dsa_session['backend']
            return redirect('socialauth_complete', backend=backend)
        else:
            error = _('Form is invalid')
    else:
        social_form = IntegrationForm()

    return render_to_response('om_auth/form.html', {
            'error': error,
            'social_form': social_form,
            'backend_name': backend.name,
            'details': details,
        }, RequestContext(request)
    )
