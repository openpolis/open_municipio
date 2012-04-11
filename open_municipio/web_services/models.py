from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from model_utils import Choices
from open_municipio.users.models import UserProfile

class Sharing(models.Model):
    SERVICES = Choices(
        ('FACEBOOK', 'facebook'),
        ('TWITTER', 'twitter'),
        ('GOOGLE_PLUS', 'google_plus')
    )

    url = models.URLField()
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(UserProfile)
    service = models.CharField(max_length=50, choices=SERVICES )
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


    class Meta:
        unique_together = ("user", "service", "content_type", "object_id")