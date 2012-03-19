from django.http import HttpResponseRedirect

from open_municipio.monitoring.forms import MonitoringForm

# FIXME: convert to a CBV
def start(request):
    """
    Start the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.
    """
    if request.method == 'POST':
        form = MonitoringForm(data=request.POST)
        if form.is_valid():  form.save()
    # FIXME: redirects shouldn't rely on the ``Referer`` header,
    # since it might be missing from the HTTP request,
    # depending on client's configuration.  
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# FIXME: convert to a CBV
def stop(request):
    """
    Stop the monitoring process of a content object by a given user.
    
    Monitoring user and target content object are taken from POST data.
    
    Redirect to referrer URL after processing.    
    """
    if request.method == 'POST':
        form = MonitoringForm(data=request.POST)
        if form.is_valid():  form.remove()
    # FIXME: redirects shouldn't rely on the ``Referer`` header,
    # since it might be missing from the HTTP request,
    # depending on client's configuration.  
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
