from open_municipio.votations.models import Votation
from django.views.generic import View

from django.http import HttpResponse

## Bookmark management
class VotationToggleBookmark(View):
    model = Votation

    def get(self, request, *args, **kwargs):
# TODO the get method is only for debugging purposes
        return self.post(self, request, args, kwargs)

    def post(self, request, *args, **kwargs):
        vote_id = int(self.kwargs.get('pk'))
        vote = get_object_or_404(Votation, pk=vote_id)
        vote.is_key = ! vote.is_key
        vote.save()

        return HttpResponse();
