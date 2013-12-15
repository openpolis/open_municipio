from django import template

register = template.Library()

@register.filter
def get_absent_label(politician):
    return "%s assenze (%.2f %s)" % (politician.n_absent_votations, politician.perc_absences,"%")

@register.filter
def get_rebel_label(politician):
    return "%s ribellioni (%.2f %s)" % (politician.n_rebel_votations, politician.perc_rebel,"%")
