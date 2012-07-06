from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from taggit.models import TagBase, ItemBase

from open_municipio.monitoring.models import Monitoring, MonitorizedItem
from open_municipio.om_utils.models import SlugModel
from open_municipio.taxonomy.managers import post_tagging, post_untagging


class Tag(TagBase, MonitorizedItem):

    # cached value of how many act uses it
    count = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return 'om_tag_detail', (), { 'slug': self.slug }


class TaggedAct(ItemBase):
    """
    A intermediate model to record associations between tags and ``Act`` model instances.
    
    It's a `custom version`_ of ``taggit.TaggedItem``, adding a few tagging metadata:
    
    * ``tagger``: the user (an ``auth.User`` instance) who tagged the act
    * ``tagging_time``: a timestamp specifying when the act was tagged
    
    Note that, contrarily to ``taggit.TaggedItem``, this model ONLY allows tagging of ``Act`` 
    instances. 
    
    .. _`custom version`: http://readthedocs.org/docs/django-taggit/en/latest/custom_tagging.html
    """
    content_object = models.ForeignKey('acts.Act')
    tag = models.ForeignKey(Tag, related_name='tagged_acts', blank=True, null=True)
    tagger = models.ForeignKey(User, null=True, blank=True, editable=False)
    tagging_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    category = models.ForeignKey('Category')
                                       
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

    def __unicode__(self):
        template = u"%(object)s tagged in %(category)s"
        if self.tag is not None:
            template += u" with %(tag)s"

        return ugettext(template) % {
            "object": self.content_object,
            "tag": self.tag,
            "category": self.category
        }


class Category(SlugModel, MonitorizedItem):
    """
    A label that can be used to categorize content objects.
    
    Categories differ from tags in that the former are pre-defined at the application level,
    while tags are assigned (and created, if not already existing) on a per-instance basis. 
    """
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    tag_set = models.ManyToManyField(Tag, related_name='category_set', null=True, blank=True)
    # cached value of how many act uses it
    count = models.IntegerField(default=0)
  
    # manager to handle the list of monitoring having as content_object this instance
#    monitoring_set = generic.GenericRelation(Monitoring, object_id_field='object_pk')
  
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __unicode__(self):
        return u'%s' % self.name
    
    @permalink
    def get_absolute_url(self):
        return 'om_category_detail', (), { 'slug': self.slug }

    @property
    def tags(self):
        return self.tag_set.all()


@receiver(post_tagging, sender=TaggedAct)
def new_tagging(**kwargs):
    """
    Increment counter of related location
    """
    tags = kwargs.get('tags', [])
    for tag in tags:
        tag.count += 1
        tag.save()

    category = kwargs.get('category')
    category.count += 1
    category.save()

    # link category and tags
    category.tag_set.add( *tags )

#    print "New tagging: %s[%s] ->\n" % (category,category.count)
#    for tag in tags:
#        print "\t%s[%s]\n" % (tag, tag.count)

@receiver(post_untagging, sender=TaggedAct)
def remove_tagging(**kwargs):
    """
    Decrement counter of related location
    """
    tags = kwargs.get('tags', [])
    for tag in tags:
        tag.count = max(0, tag.count - 1)
        tag.save()

    category = kwargs.get('category')
    category.count = max(0, category.count - 1)
    category.save()

#    print "Removed tagging: %s[%s] ->\n" % (category,category.count)
#    for tag in tags:
#        print "\t%s[%s]\n" % (tag, tag.count)


def reset_counters():
    for model in [Category, Tag]:
        model.objects.update(count=0)

    act_cat_cache = {}
    for ta in TaggedAct.objects.all():
        if ta.tag:
            ta.tag.count += 1
            ta.tag.save()
        if not act_cat_cache.has_key(ta.content_object):
            act_cat_cache[ta.content_object] = []
        if ta.category in act_cat_cache.get(ta.content_object):
            continue
        ta.category.count += 1
        ta.category.save()
        act_cat_cache.get(ta.content_object).append(ta.category)

def tagging_stats():
    print "------\nTAGGING STATS:\n"
    print "Categories: \n"
    print [("%s[%s]" % (x, x.count)) for x in Category.objects.all()]
    print "\nTags: \n"
    print [("%s[%s]" % (x, x.count)) for x in Tag.objects.all()]
    print "\n-----"
