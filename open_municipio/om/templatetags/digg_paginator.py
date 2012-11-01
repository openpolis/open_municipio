# -*- coding: utf-8 -*-

'''
Based on http://blog.localkinegrinds.com/2007/09/06/digg-style-pagination-in-django/
         and http://djangosnippets.org/snippets/2680/

Recreated by Haisheng HU <hanson2010@gmail.com> on Jun 3, 2012
'''

from django import template

register = template.Library()

LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 5
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 4
NUM_PAGES_OUTSIDE_RANGE = 2
ADJACENT_PAGES = 2

def digg_paginator(context):
    '''
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying leading, adjacent and
    trailing page links in addition to those created by the object_list generic
    view.
    '''

    paginator = context['paginator']
    page_obj = context['page_obj']
    pages = paginator.num_pages
    page = page_obj.number
    in_leading_range = in_trailing_range = False
    pages_outside_leading_range = pages_outside_trailing_range = range(0)
    if pages <= LEADING_PAGE_RANGE_DISPLAYED + NUM_PAGES_OUTSIDE_RANGE + 1:
        in_leading_range = in_trailing_range = True
        page_range = [n for n in range(1, pages + 1)]
    elif page <= LEADING_PAGE_RANGE:
        in_leading_range = True
        page_range = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1)]
        pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif page > pages - TRAILING_PAGE_RANGE:
        in_trailing_range = True
        page_range = [n for n in range(pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, pages + 1) if n > 0 and n <= pages]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_range = [n for n in range(page - ADJACENT_PAGES, page + ADJACENT_PAGES + 1) if n > 0 and n <= pages]
        pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]

    # Now try to retain GET params, except for 'page'
    # Add 'django.core.context_processors.request' to settings.TEMPLATE_CONTEXT_PROCESSORS beforehand
    request = context['request']
    params = request.GET.copy()
    if 'page' in params:
        del(params['page'])
    get_params = params.urlencode()

    return {
        'pages': pages,
        'page': page,
        'previous': page_obj.previous_page_number(),
        'next': page_obj.next_page_number(),
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'page_range': page_range,
        'in_leading_range': in_leading_range,
        'in_trailing_range': in_trailing_range,
        'pages_outside_leading_range': pages_outside_leading_range,
        'pages_outside_trailing_range': pages_outside_trailing_range,
        'get_params': get_params,
        }

register.inclusion_tag("commons/digg_paginator.html", takes_context=True)(digg_paginator)

'''
Create digg_paginator.html in template folder as below. Then you can remix it and shine it by CSS.

{% spaceless %}
  {% if has_previous %}
    <li><a href="{% if get_params %}?{{ get_params }}&{% else %}?{% endif %}page={{ previous }}">&laquo; Prev</a></li>
  {% endif %}
  {% if not in_leading_range %}
    {% for p in pages_outside_trailing_range %}
      <li><a href="{% if get_params %}?{{ get_params }}&{% else %}?{% endif %}page={{ p }}">{{ p }}</a></li>
    {% endfor %}
    <li><span class="ellipsis">...</span></li>
  {% endif %}
  {% for p in page_range %}
    {% if p == page %}
      <li><span class="active">{{ p }}</span></li>
    {% else %}
      <li><a href="{% if get_params %}?{{ get_params }}&{% else %}?{% endif %}page={{ p }}">{{ p }}</a></li>
    {% endif %}
  {% endfor %}
  {% if not in_trailing_range %}
    <li><span class="ellipsis">...</span></li>
    {% for p in pages_outside_leading_range reversed %}
      <li><a href="{% if get_params %}?{{ get_params }}&{% else %}?{% endif %}page={{ p }}">{{ p }}</a></li>
    {% endfor %}
  {% endif %}
  {% if has_next %}
    <li><a href="{% if get_params %}?{{ get_params }}&{% else %}?{% endif %}page={{ next }}">Next &raquo;</a></li>
  {% endif %}
{% endspaceless %}
'''