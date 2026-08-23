import io
import os
import urllib.request
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Google Indian Font Setup for Telugu, Hindi & English UTF-8 Rendering
FONT_NAME = "NotoSansUniversal"
FONT_BOLD_NAME = "NotoSansUniversal-Bold"

def ensure_unicode_fonts():
    """భారతీయ భాషల అక్షరాలు (తెలుగు, హిందీ, ఇంగ్లీష్) స్పష్టంగా రావడానికి యూనివర్సల్ ఫాంట్లను సిద్ధం చేస్తుంది"""
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    os.makedirs(font_dir, exist_ok=True)
    
    font_path = os.path.join(font_dir, "NotoSansDevanagari-Regular.ttf")
    font_bold_path = os.path.join(font_dir, "NotoSansDevanagari-Bold.ttf")
    
    try:
        # డౌన్‌లోడ్ ఫాంట్స్ (ఒకసారి మాత్రమే)
        if not os.path.exists(font_path):
            url_reg = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
            urllib.request.urlretrieve(url_reg, font_path)
            
        if not os.path.exists(font_bold_path):
            url_bold = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
            urllib.request.urlretrieve(url_bold, font_bold_path)
            
        # ReportLab లో ఫాంట్లను రిజిస్టర్ చేయడం
        if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
        if FONT_BOLD_NAME not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, font_bold_path))
            
        return FONT_NAME, FONT_BOLD_NAME
    except Exception:
        # ఫాంట్ లోడింగ్ సాధ్యం కాకపోతే డిఫాల్ట్ ఫాంట్స్
        return "Helvetica", "Helvetica-Bold"

def generate_pdf_from_text(title, content, font_size=12, page_size_name="A4", text_align="Left", margin=36):
    """యూనికోడ్ & భారతీయ భాషల సపోర్ట్‌తో టెక్స్ట్‌ను ప్రొఫెషనల్ PDFగా మారుస్తుంది"""
    f_normal, f_bold = ensure_unicode_fonts()
    buf = io.BytesIO()
    
    # పేజ్ సైజు ఎంపిక
    if page_size_name == "A4":
        psize = A4
    elif page_size_name == "Legal":
        psize = legal
    else:
        psize = letter
        
    doc = SimpleDocTemplate(
        buf,
        pagesize=psize,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    align_code = 0  # Left
    if text_align == "Center":
        align_code = 1
    elif text_align == "Right":
        align_code = 2
    elif text_align == "Justify":
        align_code = 4

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=f_bold,
        fontSize=font_size + 8,
        leading=font_size + 14,
        alignment=align_code,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName=f_normal,
        fontSize=font_size,
        leading=font_size + 8,
        alignment=align_code,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    
    story = []
    
    if title.strip():
        story.append(Paragraph(title.replace('\n', '<br/>'), title_style))
        story.append(Spacer(1, 10))
        
    for para in content.split('\n'):
        clean_p = para.strip()
        if clean_p:
            story.append(Paragraph(clean_p, body_style))
        else:
            story.append(Spacer(1, font_size))
            
    doc.build(story)
    buf.seek(0)
    return buf
