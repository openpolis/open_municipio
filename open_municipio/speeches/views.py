from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.http import HttpResponse

from open_municipio.speeches.models import Speech

from PyRTF import Document, Section, Paragraph as RTF_Paragraph, TEXT, Renderer

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
