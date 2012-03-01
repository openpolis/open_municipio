from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.utils import simplejson as json

from open_municipio.taxonomy.models import Tag 


class AutoCompleteView(View):
    pass

class TagAutoCompleteView(AutoCompleteView):
    # TODO: abstract boilerplate logic into base class
    def get(self, request, *args, **kwargs):
        # autocompletion data should be accessed only via AJAX calls
        if request.is_ajax():
            search_string = self.request.GET.get('q', '')
            queryset = Tag.objects.filter(name__icontains=search_string)
            data = [dict(value=tag.id, name=tag.name) for tag in queryset]
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponseBadRequest("Autocompletion data must be accessed via AJAX calls")


    