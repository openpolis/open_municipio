from django import template

from open_municipio.newscache.models import News

register = template.Library()


class NewsForObjectNode(template.Node):
    """
    The tag retrieve all news for the given object and modifies the context
    """
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''

        context[self.context_var] = object.downcast().related_news_set.all().order_by('-created').reverse()[0:3]
        return ''


def do_news_for_object(parser, token):
    """
    Retrieves the number of up-votes and down-votes for an object and
    stores them in a context variable which has ``upvotes`` and
    ``downvotes`` properties.

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
