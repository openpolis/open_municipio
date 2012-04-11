from django import template

from voting.models import Vote

register = template.Library()


class VotesForObjectNode(template.Node):
    """
    Django-voting provides score and total number of votes within a
    dict. We use that to retrieve number of upvotes and downvotes.

    This is the node class used by function ``do_votes_for_object``,
    see later.
    """
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''

        dict_score = Vote.objects.get_score(object)

        s = dict_score['score']
        n = dict_score['num_votes']

        # Some advanced Maths here :-)
        upvotes = (n + s) / 2
        downvotes = (n - s) / 2

        context[self.context_var] = {'upvotes': upvotes, 'downvotes': downvotes}
        return ''


def do_votes_for_object(parser, token):
    """
    Retrieves the number of up-votes and down-votes for an object and
    stores them in a context variable which has ``upvotes`` and
    ``downvotes`` properties.

    Example usage::

        {% votes_for_object widget as num_votes %}

        {{ num_votes.upvotes }} positive vote{{ num_votes.upvotes|pluralize }} and
        {{ num_votes.downvotes }} negative vote{{ num_votes.downvotes|pluralize }}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return VotesForObjectNode(bits[1], bits[3])


register.tag('votes_for_object', do_votes_for_object)
