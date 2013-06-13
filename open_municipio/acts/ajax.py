from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from open_municipio.acts.models import Speech

@dajaxice_register
def load_speeches(req,sitem_pk):
    d = Dajax()

    items = Speech.objects.filter(sitting_item__pk=sitem_pk)

    options = "<option value='%s'>%s</option>" % (-1, "&lt;Primo&gt;", )

    if len(items) > 0:
        for i in items:
            options = "%s<option value='%s'>%s</option>" % (options, i.pk, i)
        options = "%s<option value='%s' selected='selected'>%s</option>" % (options, 0, "&lt;Ultimo&gt;", )

    d.assign("#seqorder", "innerHTML", options)
    return d.json()
