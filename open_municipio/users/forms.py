from django.forms.models import ModelForm
from open_municipio.users.models import UserProfile

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'person')
