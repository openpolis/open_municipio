from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from taggit.models import Tag, GenericTaggedItemBase, TaggedItemBase

class TaggedItem(GenericTaggedItemBase, TaggedItemBase):
    """
    A intermediate model to record associations between tags and content model instances.
    
    It's a `custom version`_ of ``taggit.models.TaggedItem``, adding a few tagging metadata:
    
    * ``tagger``: the user (an ``auth.User`` instance)  who tagged the item
    * ``tagging_time``: a timestamp specifying when an item was tagged
    
    .. _`custom version`: http://readthedocs.org/docs/django-taggit/en/latest/custom_tagging.html
    """
    tagger = models.ForeignKey(User, null=True, blank=True, editable=False)
    tagging_time = models.DateTimeField(null=True, auto_now_add=True)
    
    class Meta:
        verbose_name = _("tagged item")
        verbose_name_plural = _("tagged items")


class Category(models.Model):
    """
    A label that can be used to categorize application objects.
    
    Categories differ from tags in that the former are pre-defined at the application level,
    while tags are assigned (and created, if not already existing) on a per-instance basis. 
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    tag_set = models.ManyToManyField(Tag, related_name='category_set')
  
    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    @property
    def tags(self):
        return self.tag_set.all()
    
