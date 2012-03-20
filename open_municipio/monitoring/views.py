from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from open_municipio.monitoring.forms import MonitoringForm

from os import sys
from open_municipio.monitoring.models import Monitoring

def start(request):
    """
    starts a monitoring
    user_id and content to monitor are taken from request.POST data
    redirects to referer after action
    """

    # chek if current user has a profile
    try:
        current_user_profile = request.user.get_profile()
    except ObjectDoesNotExist:
        current_user_profile = False

    # starts a monitoring, by creating an instance,
    # only if non-existing
    if request.method == 'POST' and current_user_profile:
        try:
            monitoring = Monitoring.objects.get(
                content_type=ContentType.objects.get(pk=request.POST['content_type_id']),
                object_pk=request.POST['object_pk'],
                user=request.user
            )
        except ObjectDoesNotExist:
            monitoring = Monitoring(
                content_type_id=request.POST['content_type_id'],
                object_pk=request.POST['object_pk'],
                user=request.user
            )
            form = MonitoringForm(request.POST, instance=monitoring)
            form.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def stop(request):
    """
    stops a monitoring, by removing it 
    redirects to referer after action    
    """
    # chek if current user has a profile
    try:
        current_user_profile = request.user.get_profile()
    except ObjectDoesNotExist:
        current_user_profile = False

    if request.method == 'POST' and current_user_profile:
        monitoring = Monitoring.objects.get(
            content_type=ContentType.objects.get(pk=request.POST['content_type_id']),
            object_pk=request.POST['object_pk'],
            user=request.user
        )
        form = MonitoringForm(request.POST, instance=monitoring)
        if form.is_valid():
            monitoring.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
