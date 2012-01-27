from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.models import Tag


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
    
