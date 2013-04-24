from django import forms
from django.utils.safestring import mark_safe

class AdminImageWidget(forms.FileInput):
    """
    An ImageField Widget for admin that shows a thumbnail.
    """

    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append(('<a target="_blank" href="%s">'
                           '<img src="%s" style="height: 28px;" /></a> '
                           % (value.url, value.url)))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class SplitTimeWidget(forms.MultiWidget):
    """
    Widget written to split widget into hours and minutes.
    """
    def __init__(self, attrs=None):
        h_choices = [ ( "-","-") ]
        h_choices += ([(hour,hour) for hour in range(0,24)])

        m_choices = [ ("-","-") ]
        m_choices += ([(minute, str(minute).zfill(2)) \
                            for minute in range(60)])
        widgets = (
                    forms.Select(attrs=attrs, \
                        choices=h_choices), \
                    forms.Select(attrs=attrs, \
                        choices=m_choices), \
                  )
        super(SplitTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.hour, value.minute]
        return ["-","-"]
