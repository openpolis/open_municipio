from django import template
from django.conf import settings

from events.models import Event


def do_future_events(parser, token):
    """
    Returns upcoming events.

    Usage:

    * ``{% get_future_events as <template_var> %}`` - returns all the
      upcoming events

    * ``{% get_future_events <type> <pk> as <template_var> %}`` -
      events are filtered; type can be act, politician, institution,
      category or tag

    Template example:

    {% load event_tags %}
    {% get_future_events act current_act.id as act_events %}
    {% for event in act_events %}
      {{ event.date }}
    {% endfor %}
    """
    bits = token.split_contents()
    if len(bits) == 3:
        return AllEventsNode(bits[2])
    if len(bits) == 5:
        return SelectedEventsNode(bits[1], bits[2], bits[4])
    raise template.TemplateSyntaxError("Usage: ``{% get_future_events as <template_var> %}`` or ``{% get_future_events <type> <pk> as <template_var> %}``")


class AllEventsNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = Event.future.all()
        return ''


class SelectedEventsNode(template.Node):
    def __init__(self, filter, pk, varname):
        if not filter in ['act', 'tag', 'category', 'politician', 'institution',]:
            raise ValueError('Invalid value for filter: %s' % filter)
        self.filter = filter
        self.pk = pk
        self.varname = varname

    def render(self, context):
        context[self.varname] = getattr(Event.future, 'get_by_%s' %  self.filter)(self.pk)
        return ''


register = template.Library()
register.tag('get_future_events', do_future_events)
