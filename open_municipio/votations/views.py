from open_municipio.votations.models import Votation
from django.views.generic import View

from django.http import HttpResponse


# Create your views here.

# Bookmark management
class VotationToggleBookmark(View):
    model = Votation

    def post(self, request, *args, **kwargs):
        votation_id = int(self.kwargs.get('pk'))
        votation = get_object_or_404(Act, pk=votation_id)
        votation.is_key = not votation.is_key
        votation.save()

        return HttpResponse();
