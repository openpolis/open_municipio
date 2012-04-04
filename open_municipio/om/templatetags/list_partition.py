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
