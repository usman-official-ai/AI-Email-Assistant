from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
import io
from datetime import datetime

def create_pdf(email_content, filename="email.pdf", title="Email Export"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1a1a1a'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#666666'), spaceAfter=20, alignment=TA_CENTER)
    content_style = ParagraphStyle('CustomContent', parent=styles['Normal'], fontSize=12, leading=18, alignment=TA_LEFT, spaceAfter=12, fontName='Helvetica')
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 80, content_style))
    story.append(Spacer(1, 20))
    
    for line in email_content.split('\n'):
        if line.strip():
            story.append(Paragraph(line, content_style))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 12))
    
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data