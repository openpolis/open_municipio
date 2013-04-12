from django.conf import settings
from django.core.urlresolvers import reverse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist 
from django.views.generic import DetailView

from django.http import HttpResponse

from open_municipio.people.models import Person
from open_municipio.speech.models import Speech
from open_municipio.om_search.views import ExtendedFacetedSearchView
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.om_search.forms import RangeFacetedSearchForm


from PyRTF import Document, Section, Paragraph as RTF_Paragraph, TEXT, Renderer

class SpeechSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """
    """
    __name__ = 'SpeechSearchView'

    FACETS_SORTED = []
    FACETS_LABELS = {}

    DATE_INTERVALS_RANGES = {
        '2013':  {'qrange': '[2013-01-01T00:00:00Z TO 2014-01-01T00:00:00Z]', 'r_label': '2013'},
        '2012':  {'qrange': '[2012-01-01T00:00:00Z TO 2013-01-01T00:00:00Z]', 'r_label': '2012'},
        '2011':  {'qrange': '[2011-01-01T00:00:00Z TO 2012-01-01T00:00:00Z]', 'r_label': '2011'},
        '2010':  {'qrange': '[2010-01-01T00:00:00Z TO 2011-01-01T00:00:00Z]', 'r_label': '2010'},
        '2009':  {'qrange': '[2009-01-01T00:00:00Z TO 2010-01-01T00:00:00Z]', 'r_label': '2009'},
        '2008':  {'qrange': '[2008-01-01T00:00:00Z TO 2009-01-01T00:00:00Z]', 'r_label': '2008'},
    }

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(SpeechSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(SpeechSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        extra = super(SpeechSearchView, self).extra_context()
        
        extra['base_url'] = reverse('om_speech_search') + '?' + extra['params'].urlencode()

        person_slug = self.request.GET.get('person', None)
        print "person = %s" % person_slug
        if person_slug:
            try:
                extra['person'] = Person.objects.get(slug=person_slug)
                print "found %s" % extra["person"]
            except ObjectDoesNotExist:
                pass

        paginator = Paginator(self.results, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    
        extra['paginator'] = paginator
        extra['page_obj'] = page_obj
    
        return extra

class SpeechDetailView(DetailView):
    model = Speech
    context_object_name = 'speech'

def generate_speech_event_report_rtf(request, event_pk):
    response = HttpResponse(content_type='application/rtf')
    response['Content-Disposition'] = 'attachment; filename="report.rtf"'

    ev_sp = Speech.objects.filter(event_act__event__pk=event_pk)

    doc = Document()
    ss = doc.StyleSheet

    content = Section()

    # newline
    nl = RTF_Paragraph()

    # build the title
    title_text = "Interventi Consiglio Comunale %s" % ev_sp[0].event_act.event.date
    title = RTF_Paragraph( ss.ParagraphStyles.Heading1 )
    title.append(title_text)
    content.append(title)
    content.append(nl)

    # build an intro
    intro = RTF_Paragraph( ss.ParagraphStyles.Normal )
    intro.append("Questo documento raccoglie gli interventi in aula della seduta di Consiglio Comunale tenutasi in data %s\n" % (ev_sp[0].event_act.event.date))
    content.append(intro)
    content.append(nl)

    # build an entry for each speech
    for s in ev_sp:
        speech_title = RTF_Paragraph ( ss.ParagraphStyles.Normal )
        speech_title.append(TEXT(("%s" % (s.title)).encode("utf-8"), bold=True))

        speech_preamble = RTF_Paragraph( ss.ParagraphStyles.Normal )
        speech_preamble.append(("Alle ore %s, %s ha detto quanto segue:" % (s.begin_time, s.speaker)).encode("utf-8"))

        speech_content = RTF_Paragraph( ss.ParagraphStyles.Normal )
        speech_content.append(TEXT(("%s" % s.text).encode("utf-8"), italic=True))

        content.append(speech_title)
        content.append(speech_preamble)
        content.append(speech_content)
        content.append(nl)

    # merge the document
    doc.SetTitle(title_text)
    doc.Sections.append(content)

    DR = Renderer()
    DR.Write(doc, response)

    return response


def generate_speech_event_report_pdf(request, event_pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    ev_sp = Speech.objects.filter(event_act__event__pk=event_pk)

    doc = SimpleDocTemplate(response, pagesize=A4)
    OutlinePDF = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    OutlinePDF.append(Paragraph("Interventi Consiglio Comunale %s" % ev_sp[0].event_act.event.date, styles["Heading1"]))

    OutlinePDF.append(Paragraph("Questo documento raccoglie gli interventi in aula della seduta di consiglio tenutasi in data %s" % (ev_sp[0].event_act.event.date), styles["Normal"]))
    OutlinePDF.append(Spacer(1,12))

    for s in ev_sp:
        OutlinePDF.append(Paragraph("<b>%s</b>" % (s.title), styles["Normal"]))
        OutlinePDF.append(Paragraph("Alle ore %s, %s ha detto quanto segue:" % (s.begin_time, s.speaker), styles["Normal"]))
        OutlinePDF.append(Paragraph("<i>%s</i>" % s.text, styles["Normal"]))
        OutlinePDF.append(Spacer(1,12))

    doc.build(OutlinePDF)
    return response

def generate_speech_report_pdf(request, pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    s = Speech.objects.get(pk=pk)

    doc = SimpleDocTemplate(response, pagesize=A4)
    OutlinePDF = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
#    print "%s" % styles
#    for i in range(1,10):
    OutlinePDF.append(Paragraph("Il giorno %s, alle ore %s, %s ha detto quanto segue:" % (s.event_act.event.date, s.begin_time, s.speaker), styles["Normal"]))
#        OutlinePDF.append(Spacer(1,12))
    OutlinePDF.append(Paragraph("%s" % s.text, styles["Normal"]))
    doc.build(OutlinePDF)
    return response

