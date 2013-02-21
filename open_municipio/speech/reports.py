import reportengine
from reportengine.outputformats import *

from django.utils.translation import ugettext_lazy as _

from open_senigallia.speech.models import Speech


class SpeechReport(reportengine.ModelReport):
    """
    A report of all speeches
    """
    verbose_name = _("Report of recent speeches")
    slug = "speech-report"
    namespace = "system"
    description = "Listing the speeches of a given day"
    labels = ( 'title', 'begin_time', 'event_act', )
    model = Speech
    list_filter = [ 'title', ]
    per_page = 10
    output_formats = [ AdminOutputFormat(), XMLOutputFormat(root_tag="speeches", row_tag="speech")]

reportengine.register(SpeechReport)
