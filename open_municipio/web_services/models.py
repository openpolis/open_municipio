from django.db import models
from django.contrib.contenttypes import generic
from open_municipio.users.models import UserProfile

class SharedItem(models.Model):
    url = models.URLField()
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(UserProfile)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.content_object