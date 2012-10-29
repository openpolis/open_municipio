from django import template

from open_municipio.newscache.models import News
from open_municipio.people.models import Person, InstitutionCharge, municipality

from django.db.models.query import EmptyQuerySet

from logging import getLogger

register = template.Library()



class NewsForObjectNode(template.Node):
    """
    The tag retrieves all news for the given object and modifies the context
    """
    logger = getLogger('debugging')

    def __init__(self, object, context_var, news_type=None):
        self.object = object
        self.news_type = news_type
        self.context_var = context_var

    def render(self, context):
        try:
            self.logger.debug(self.object)
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''


        # extract all news
        # if obect is a Person, extract news related to all current and past charges
        if isinstance(object, Person):
            news = EmptyQuerySet()
            for c in object.all_institution_charges:
                news |= c.related_news
        elif isinstance(object, basestring):
            if object == 'politicians_all':
                news = EmptyQuerySet()
                for c in InstitutionCharge.objects.all():
                    news |= c.related_news
            if object == 'politicians_council':
                news = EmptyQuerySet()
                for c in municipality.council.charges:
                    news |= c.related_news
            if object == 'politicians_gov':
                news = EmptyQuerySet()
                for c in municipality.gov.charges:
                    news |= c.related_news
        else:
            news = object.related_news

        # filter only news of a given type (INST or COMM) (if given)
        if self.news_type:
            news = news.filter(news_type=self.news_type)

        # sort news by news_date, descending order
        context[self.context_var] = sorted(news, key=lambda n: n.news_date, reverse=True)[0:15]

        return ''



def do_community_news_for_object(parser, token):
    """
    Retrieves the community news related to an object,
    stores them in a context variable (news).

    Example usage::

        {% community_news_for_object act as c_news %}
        {% for n in c_news %}
            notizia: {{ n.created }} - {{ n.text }}
        {% endfor %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return NewsForObjectNode(bits[1], bits[3], news_type=News.NEWS_TYPE.community)
register.tag('community_news_for_object', do_community_news_for_object)

def do_institutional_news_for_object(parser, token):
    """
    Retrieves the institutional news related to an object,
    stores them in a context variable (news).

    Example usage::

        {% institutional_news_for_object act as i_news %}
        {% for n in i_news %}
            notizia: {{ n.news_date }} - {{ n.text }}
        {% endfor %}
        # bits[1] = act
        # bits[3] = i_news
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return NewsForObjectNode(bits[1], bits[3], news_type=News.NEWS_TYPE.institutional)
register.tag('institutional_news_for_object', do_institutional_news_for_object)


