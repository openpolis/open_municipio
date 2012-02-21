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
    A label that can be used to categorize content objects.
    
    Categories differ from tags in that the former are pre-defined at the application level,
    while tags are assigned (and created, if not already existing) on a per-instance basis. 
    """
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), blank=True, unique=True, max_length=100)
    tag_set = models.ManyToManyField(Tag, related_name='category_set', null=True, blank=True)
  
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def slugify(self, tag, i=None):
        slug = slugify(tag)
        if i is not None:
            slug += "_%d" % i
        return slug
     
    def calculate_slug(self):
        """
        Calculate a slug for a given category name.
        
        If a calculated slug already exists in the DB, add a numerical prefix until is OK.
        """
        slug = self.slugify(self.name)
        i = 0
        while True:
            i += 1
            try:
                Category.objects.get(slug=slug)
                slug = self.slugify(self.name, i)
            except Category.DoesNotExist:
                return slug

    def save(self, *args, **kwargs):
        # auto-generate a slug, if needed 
        if not self.pk and not self.slug:
            self.slug = self.calculate_slug()
            return super(Category, self).save(*args, **kwargs)
        
    @property
    def tags(self):
        return self.tag_set.all()
    
