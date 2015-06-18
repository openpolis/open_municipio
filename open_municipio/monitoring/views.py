from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic import FormView
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from open_municipio.monitoring.models import Monitoring
from open_municipio.monitoring.forms import MonitoringForm

class MonitoringToggleBaseView(FormView):
    form_class = MonitoringForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MonitoringToggleBaseView, self).dispatch(*args, **kwargs)
       
    def form_invalid(self, form=None):
        msg = "It appears that the monitoring form has been tampered with !"
        return HttpResponseBadRequest(msg)
    
    def get_success_url(self):
        # FIXME: redirects shouldn't rely on the ``Referer`` header,
        # since it might be missing from the HTTP request,
        # depending on client's configuration.  
        return self.request.META['HTTP_REFERER']
    

class MonitoringStartView(MonitoringToggleBaseView):
    """
    Start the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.
    """
    def post(self, request, *args, **kwargs):
        # chek if current user has a profile
        try:
            current_user_profile = request.user.get_profile()
        except ObjectDoesNotExist:
            current_user_profile = False

        # starts a monitoring, by creating an instance,
        # only if non-existing
        if current_user_profile:
            monitoring, created = Monitoring.objects.get_or_create(
                    content_type_id=request.POST['content_type_id'],
                    object_pk=request.POST['object_pk'],
                    user=request.user)
             
            form = self.form_class(request.POST, instance=monitoring)

            if form.is_valid():
            
                # update profile
                if not current_user_profile.wants_newsletter:
                    current_user_profile.wants_newsletter=True
                    current_user_profile.save()

                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class MonitoringStopView(MonitoringToggleBaseView):
    """
    Stop the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.    
    """
    def post(self, request, *args, **kwargs):
        # chek if current user has a profile
        try:
            current_user_profile = request.user.get_profile()
        except ObjectDoesNotExist:
            current_user_profile = False

        if current_user_profile:
            try:
                monitoring = Monitoring.objects.get(
                    content_type=ContentType.objects.get(pk=request.POST['content_type_id']),
                    object_pk=request.POST['object_pk'],
                    user=request.user
                )
                form = MonitoringForm(request.POST, instance=monitoring)
                if form.is_valid():
                    monitoring.delete()
                    return HttpResponseRedirect(self.get_success_url())
                else:
                    return self.form_invalid(form)
            except ObjectDoesNotExist:
                return self.form_invalid()
        else:
            return HttpResponseRedirect(self.get_success_url())


