from django import template

from open_municipio.newscache.models import News

register = template.Library()


class NewsForObjectNode(template.Node):
    """
    The tag retrieve all news for the given object and modifies the context
    """
    def __init__(self, object, context_var, news_type=None):
        self.object = object
        self.news_type = news_type
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''

        if self.news_type:
            news = object.related_news_set.filter(news_type=self.news_type)
        else:
            news = object.related_news_set.all()

        context[self.context_var] = news.order_by('-created').reverse()[0:15]

        return ''


def do_news_for_object(parser, token):
    """
    Retrieves the news related to an object and
    stores them in a context variable (news).

    Example usage::

        {% news_for_object act as news %}
        {% for n in news %}
            notizia: {{ n.created }} - {{ n.text }}
        {% endfor %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return NewsForObjectNode(bits[1], bits[3])
register.tag('news_for_object', do_news_for_object)

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
            notizia: {{ n.created }} - {{ n.text }}
        {% endfor %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return NewsForObjectNode(bits[1], bits[3], news_type=News.NEWS_TYPE.institutional)
register.tag('institutional_news_for_object', do_institutional_news_for_object)
