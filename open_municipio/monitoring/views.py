from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.generic import FormView
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from open_municipio.monitoring.forms import MonitoringForm


class MonitoringToggleBaseView(FormView):
    form_class = MonitoringForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MonitoringToggleBaseView, self).dispatch(*args, **kwargs)
       
    def form_invalid(self, form):
        msg = "It appears that the monitoring form has been tampered with !"
        return HttpResponseBadRequest(msg)
    
    def get_success_url(self):
        # FIXME: redirects shouldn't rely on the ``Referer`` header,
        # since it might be missing from the HTTP request,
        # depending on client's configuration.  
        return self.request.META['HTTP_REFERER']
    
    def get(self, *args, **kwargs):
        msg = "This view can be accessed only via POST"
        return HttpResponseNotAllowed(msg)
        

class MonitoringStartView(MonitoringToggleBaseView):
    """
    Start the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.
    """
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
       

class MonitoringStopView(MonitoringToggleBaseView):
    """
    Stop the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.    
    """
    
    def form_valid(self, form):
        form.remove()
        return HttpResponseRedirect(self.get_success_url())