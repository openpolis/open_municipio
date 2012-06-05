from django.template import Library

register = Library()

@register.filter
def partition(input, n):
    """
    @url http://djangosnippets.org/snippets/1501/

    Break a list into sublists of length ``n``. That is,
    ``partition(range(10), 4)`` gives::

        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10]]
    """
    try:
        n = int(n)
        input = list(input)
    except (ValueError, TypeError):
        return [input]
    return [input[i:i+n] for i in range(0, len(input), n)]

@register.filter
def split(input, part=None):
    """
    Break a list in two sublists
    ``split([1,2,3,4,5])`` gives::

        [[1,3,5],[2,4]]
    """
    try:
        input = list(input)
    except (ValueError, TypeError):
        return [input]
    splitted = [[],[]]
    for index, el in enumerate(input):
        splitted[index % 2].append(el)
    if not part:
        return splitted
    return splitted[0] if part == 'first' else splitted[1]

@register.filter
def to_list(input):
    return [input]