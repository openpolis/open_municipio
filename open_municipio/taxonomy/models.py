from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from taggit.models import TagBase, TaggedItemBase


class Tag(TagBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedAct(TaggedItemBase):
    """
    A intermediate model to record associations between tags and ``Act`` model instances.
    
    It's a `custom version`_ of ``taggit.models.TaggedItem``, adding a few tagging metadata:
    
    * ``tagger``: the user (an ``auth.models.User`` instance)  who tagged the act
    * ``tagging_time``: a timestamp specifying when an act was tagged
    
    Note that, contrarily to ``taggit.models.TaggedItem``, this model ONLY allows tagging of ``Act`` 
    instances. 
    
    .. _`custom version`: http://readthedocs.org/docs/django-taggit/en/latest/custom_tagging.html
    """
    content_object = models.ForeignKey('Act')
    tag = models.ForeignKey(Tag, related_name='tagged_acts')
    tagger = models.ForeignKey(User, null=True, blank=True, editable=False)
    tagging_time = models.DateTimeField(null=True, auto_now_add=True)    
                                       
    class Meta:
        verbose_name = _("tagged act")
        verbose_name_plural = _("tagged acts")
    
    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


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
    
    

class Location(models.Model):
    """
    A concise description of a town's location.
    
    ``Location`` instances may be used as labels to provide a geographic-aware taxonomy 
    for content objects (particularly, ``Act`` instances).       
    """
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), blank=True, unique=True, max_length=100)
    address = models.CharField(verbose_name=_('Address'), max_length=100, blank=True)
    # FIXME: choose the right number of significant digits
    latitude = models.FloatField(verbose_name=_('Latitude'), blank=True, null=True)
    # FIXME: choose the right number of significant digits
    longitude = models.FloatField(verbose_name=_('Longitude'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def slugify(self, name, i=None):
        slug = slugify(name)
        if i is not None:
            slug += "_%d" % i
        return slug
     
    def calculate_slug(self):
        """
        Calculate a slug for a given location name.
        
        If a calculated slug already exists in the DB, add a numerical prefix until is OK.
        """
        slug = self.slugify(self.name)
        i = 0
        while True:
            i += 1
            try:
                Location.objects.get(slug=slug)
                slug = self.slugify(self.name, i)
            except Location.DoesNotExist:
                return slug

    def save(self, *args, **kwargs):
        # auto-generate a slug, if needed 
        if not self.pk and not self.slug:
            self.slug = self.calculate_slug()
        return super(Location, self).save(*args, **kwargs)
