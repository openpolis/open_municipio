from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.http import HttpResponse

from open_municipio.speeches.models import Speech

#from rtfng import *

def generate_speech_event_report_rtf(request, event_pk):
#    response = HttpResponse(content_type='application/rtf')
#    response['Content-Disposition'] = 'attachment; filename="report.rtf"'
#
#    ev_sp = Speech.objects.filter(event_act__event__pk=event_pk)
#
#    doc = Document()
#    ss = doc.Stylesheet
#    intro = Section()
#    intro.append("Questo documento raccoglie gli interventi in aula della seduta di Consiglio Comunale tenutasi in data %s" (env_sp[0].event_act.event.date))
#    doc.Sections.append(intro)
#
#    doc.build(OutlinePDF)
    return response


def generate_speech_event_report_pdf(request, event_pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    ev_sp = Speech.objects.filter(event_act__event__pk=event_pk)

    doc = SimpleDocTemplate(response, pagesize=A4)
    OutlinePDF = []
    styles = getSampleStyleSheet()

    OutlinePDF.append(Paragraph("Interventi Consiglio Comunale %s" % ev_sp[0].event_act.event.date, styles["Heading1"]))

    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    OutlinePDF.append(Paragraph("Questo documento raccoglie gli interventi in aula della seduta di consiglio tenutasi in data %s" % (ev_sp[0].event_act.event.date), styles["Normal"]))
    OutlinePDF.append(Spacer(1,12))

    for s in ev_sp:
        OutlinePDF.append(Paragraph("<b>%s</b>" % (s.title), styles["Normal"]))
        OutlinePDF.append(Paragraph("Alle ore %s, %s ha detto quanto segue:" % (s.begin_time, s.speaker), styles["Normal"]))
        OutlinePDF.append(Spacer(1,12))
    OutlinePDF.append(Paragraph("%s" % s.text, styles["Normal"]))
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
