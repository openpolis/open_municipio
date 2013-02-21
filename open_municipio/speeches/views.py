from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.http import HttpResponse

def generate_speech_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

#    p = canvas.Canvas(response)
#    p.drawString(100, 100, "Hello world")
#    p.showPage()
#    p.save()

    doc = SimpleDocTemplate(response, pagesize=A4)
    OutlinePDF = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    print "%s" % styles
    for i in range(1,10):
        OutlinePDF.append(Paragraph("<b>Ciao</b>", styles["Normal"]))
        OutlinePDF.append(Spacer(1,12))
    doc.build(OutlinePDF)
    return response
