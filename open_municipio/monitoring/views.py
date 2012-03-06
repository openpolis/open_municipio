from django.http import HttpResponseRedirect

from open_municipio.monitoring.forms import MonitoringForm

from os import sys

def start(request):
    """
    starts a monitoring
    user_id and content to monitor are taken from request.POST data
    redirects to referer after action
    """
    if request.method == 'POST':
        form = MonitoringForm(data=request.POST)
        if form.is_valid():
            monitoring = form.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def stop(request):
    """
    stops a monitoring, by removing it 
    redirects to referer after action    
    """
    if request.method == 'POST':
        form = MonitoringForm(data=request.POST)
        if form.is_valid():
            form.remove()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
