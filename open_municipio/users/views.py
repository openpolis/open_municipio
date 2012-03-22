from django.contrib.auth.models import User
from django.views.generic import DetailView

class UserDetailView(DetailView):

    def get_object(self):
        # object lookup using username
        object = User.objects.get(username=self.kwargs['username'])

        # Return the object
        return object
