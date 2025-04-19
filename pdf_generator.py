from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(keywords, content, pdf_filename="report.pdf"):
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.drawString(100, 750, "SEO Report")
    c.drawString(100, 730, "Keywords:")
    c.drawString(100, 710, ", ".join(keywords))
    c.drawString(100, 690, "Relevant Content:")
    c.drawString(100, 670, content)  # This might need better formatting for long content
    c.save()
    return pdf_filename
