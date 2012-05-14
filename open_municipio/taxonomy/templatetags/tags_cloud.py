from django import template
from math import log10

register = template.Library()
def do_tags_cloud(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, tag_list = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return TagsCloudNode(tag_list)

class TagsCloudNode(template.Node):
    def __init__(self, tag_list):
        self.tag_list = template.Variable(tag_list)

    def scale_counter(self, count):
        """
        Default topic count scaling for tag links
        """
        return round(log10(count + 1) * 100)

    def render(self, context):
        try:

            tag_list = self.tag_list.resolve(context)

            if not tag_list:
                return ''

            context = {
                'bolder': 900,
                'thinner': 100,
                'smallest': 8,
                'largest': 22,
                'unit': 'pt',
                'font_step': 1,
                'min_count': 0,
                'max_count': 0,
                # init scaled counters
                'tags': [{
                    'tag'   : tag,
                    'count' : self.scale_counter(tag.count)
                } for tag in tag_list]
            }

            context['min_count'] = min(context['tags'], key=lambda x: x['count'])['count']
            context['max_count'] = max(context['tags'], key=lambda x: x['count'])['count']

            spread = context['max_count'] - context['min_count']
            if spread <= 0: spread = 1
            font_spread = context['largest'] - context['smallest']
            if font_spread < 0: font_spread = 1
            context['font_step'] = font_spread / spread

            weight_spread = context['bolder'] - context['thinner']
            if font_spread < 0: font_spread = 100
            context['weight_step'] = weight_spread / spread


            cloud = ''
            for item in context['tags']:
                cloud += '<li><a href="%s" class="tag-%s tag-%s" style="font-size: %s%s; font-weight:%s">%s</a></li>' % (
                    item['tag'].get_absolute_url(),
                    item['tag'].__class__.__name__.lower(),
                    item['tag'].pk,
                    round(context['smallest'] + ( (item['count'] - context['min_count']) * context['font_step'] ),2),
                    context['unit'],
                    int (context['thinner'] + ( (item['count'] - context['min_count']) * context['weight_step'] )),
                    item['tag'].name
                )
            return '<ul class="tags-cloud">%s</ul>' % cloud
        except template.VariableDoesNotExist:
            return ''

register.tag('tags_cloud', do_tags_cloud)