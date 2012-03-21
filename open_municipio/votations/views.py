from open_municipio.votations.models import Votation
from django.views.generic import View

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

# Bookmark management
class VotationToggleBookmark(View):
    model = Votation

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VotationToggleBookmark, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if (not request.user.is_staff):
            raise Exception("Only staff user can access this operation")

        votation_id = int(self.kwargs.get('pk'))
        votation = get_object_or_404(Act, pk=votation_id)
        votation.is_key = not votation.is_key
        votation.save()

        return HttpResponse();
