from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from django.contrib.contenttypes.models import ContentType 
from django.contrib.auth.decorators import user_passes_test


class ToggleBookmarkView(View):
 
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ToggleBookmarkView, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        obj_pk = int(self.kwargs.get('object_pk'))
        obj_content_type = ContentType.objects.get(pk=int(self.kwargs.get('content_type_id')))
        model = obj_content_type.model_class()
        object = get_object_or_404(model, pk=obj_pk)
        return object
    
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        # toggle object's key status
        # we assume the model to have a ``is_key`` boolean field
        # FIXME: make this more generic! 
        object.is_key = not object.is_key 
        object.save()

        return HttpResponse();
