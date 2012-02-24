from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

class InlineEditView(View):
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InlineEditView, self).dispatch(*args, **kwargs)
    
    def parse_id(self, id):
        """
        Parse the ``id`` attribute of an HTML page element in order 
        to extract relevant information.
        
        It assumes an ``id`` having the following format:
        
        <app name>-<model name>-<pk>-<field name>
        
        Return the 4-tuple ``(<app name>, <model name>, <pk>, <field name>)``.
        """
        return id.split('-')
    
    def check_perms(self, instance, field_name):
        # TODO: implement a finer-grained access control policy
        # e.g. by checking permission ``can_edit`` for the given model instance 
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        # TODO: refine error checking logic
        try:
            # retrieve the model instance to be modified
            id = self.request.POST.get('id')
            value= self.request.POST.get('value')
            (app_name, model_name, instance_pk, field_name) = self.parse_id(id)
            model = models.get_model(app_name, model_name)
            instance = model._default_manager.get(pk=instance_pk)
            # check that the user is allowed to modify this model field
            if self.check_perms(instance, field_name):
                setattr(instance, field_name, value)
                instance.save() 
                return HttpResponse(value)
            else: # permission check failed !
                return HttpResponseForbidden
        except Exception, e :
            return HttpResponseBadRequest(e)

    def put(self, request, *args, **kwargs): 
        return self.post(request, *args, **kwargs)      