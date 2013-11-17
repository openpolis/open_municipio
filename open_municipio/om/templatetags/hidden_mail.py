from django.template import Library

register = Library()

@register.filter
def hide_mail(address_clear):
    hidden = address_clear.replace("@","[chioccia]").replace(".","[punto]")
    return hidden

