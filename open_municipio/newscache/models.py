# -*- coding: utf-8 -*-
from django.db import models
from django.template.loader import get_template
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.conf import settings

from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils import Choices
from model_utils.models import TimeStampedModel

from open_municipio.acts.signals import act_presented, act_signed, act_status_changed

import re

#
# Newscache
#
class News(TimeStampedModel):
    """
    This model stores news generated by different events.

    An example:

    gen = Transition.objects.get(pk=1)
    rel = Deliberation.objects.get(pk=3)
    n = News(generating_object=gen, related_object=rel)
    n.save()

    """
    NEWS_TYPE = Choices(
        ('INST', 'institutional', _('institutional')),
        ('COMM', 'community', _('community'))
    )

    news_type = models.CharField(choices=NEWS_TYPE, default=NEWS_TYPE.institutional, max_length=4)

    priority = models.PositiveSmallIntegerField(verbose_name=_('priority'), default=3)

    # generating object generic relation
    generating_content_type   = models.ForeignKey(ContentType,
                                                  verbose_name=_('generating content type'),
                                                  related_name="generating_content_type_set_for_%(class)s")
    generating_object_pk      = models.PositiveIntegerField(_('object ID'))
    generating_object         = generic.GenericForeignKey(ct_field="generating_content_type",
                                                          fk_field="generating_object_pk")

    # related object generic relation
    related_content_type      = models.ForeignKey(ContentType,
                                                  verbose_name=_('related content type'),
                                                  related_name="related_content_type_set_for_%(class)s")
    related_object_pk         = models.PositiveIntegerField(_('object ID'))
    related_object            = generic.GenericForeignKey(ct_field="related_content_type",
                                                          fk_field="related_object_pk")

    text                      = models.TextField(verbose_name=_('text'), max_length=512)


    class Meta:
        verbose_name = _('cached news')
        verbose_name_plural = _('cached news')

    def __unicode__(self):
        return u'%s - %s - %s' % (self.id, self.created.strftime('%d/%m/%Y - %H:%I'), self.text)

    @classmethod
    def get_text_for_news(cls, context, template_file):
        """
        Generic class-method that dispatches text generation for the news
        to the proper template, given a context.

        Renders a template file, using a context, and returns it.
        
        Used by signal handlers to generate textual representation of the news.
        """
        template = get_template(template_file)
        return re.sub("\s+", " ", template.render(context).strip())

    
class NewsTargetMixin(models.Model):
    """
    A mix-in class for models which are valid targets for news generation. 
    """
    # A manager that can be used to retrieve the QuerySet of news items targeting this content object
    related_news_set = generic.GenericRelation(News,
                                           content_type_field='related_content_type',
                                           object_id_field='related_object_pk')
    @property
    def related_news(self):
        """
        Retunrn the QuerySet of news items targeting this content object.
        """
        return self.related_news_set.all()
    
    class Meta:
        abstract = True



## Signal handlers
@receiver(act_presented)
def act_presented_create_news_item(sender, **kwargs):
    """
    Generates a news item when an act has been presented,
    i.e. created within our DB.

    This news item is only generated  when a new act has been created, 
    (not when an act has been updated) and only after the fixture-loading phase.
    """
    # the ``sender`` of this signal is an ``Act`` instance
    act = sender.downcast()
    # define context for the news item's textual representation
    ctx = Context({})
    # create a news item about a new act having been presented
    News.objects.create(
        generating_object=act, 
        related_object=act, 
        priority=1,
        text=News.get_text_for_news(ctx, 'newscache/act_published.html')
        )


@receiver(act_signed)        
def new_signature_create_news_item(sender, **kwargs):
    """
    Generate a news item when an act has been signed by a politician.
    
    Note that news items are not generated when the ORM is operating 
    in raw mode (i.e. during the fixture-loading phase). 
    """
    # the ``sender`` of this signal is an ``ActSupport`` instance
    act_support = sender
    act = act_support.act.downcast()
    signer = act_support.charge
    # define context for the news item's textual representation 
    ctx = Context({
                   'current_site': Site.objects.get(id=settings.SITE_ID),
                   'signature': act_support, 
                   'act': act, 
                   'signer': signer 
                   })
    # create a news item about an act being signed
    News.objects.create(
        generating_object=act_support, 
        related_object=act, 
        priority=3,
        text=News.get_text_for_news(ctx, 'newscache/act_signed.html')
    )
    # create a news item about a politician having signed an act
    News.objects.create(
        generating_object=act_support, 
        related_object=signer, 
        priority=1,
        text=News.get_text_for_news(ctx, 'newscache/user_signed.html')
    )
    
@receiver(act_status_changed)        
def act_changed_status_create_news_item(sender, **kwargs):
    """
    Generate a news item when an act changes its current status.
    
    Note that news items are not generated when the ORM is operating 
    in raw mode (i.e. during the fixture-loading phase). 
    """
    # the ``sender`` of this signal is a ``Transition`` instance
    transition = sender
    act = transition.act.downcast()
    # act presentation is already handled by the 
    # ``act_presented_create_news_item`` handler
    if transition.target_status != 'PRESENTED':   
        ctx = Context({ 
                       'current_site': Site.objects.get(id=settings.SITE_ID),
                        'transition': transition, 
                        'act': act 
                        })
        # create a news item about an act having changed its status
        News.objects.create(
                generating_object=transition, 
                related_object=act, 
                priority=2,
                text=News.get_text_for_news(ctx, 'newscache/act_changed_status.html')
            )