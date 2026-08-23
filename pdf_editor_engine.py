import io
import fitz  # PyMuPDF

# ---------------- 1. టెక్స్ట్ బ్లాక్స్ గుర్తింపు ----------------
def extract_page_text_blocks(pdf_bytes, page_number_1based):
    """పేజీలోని ప్రతి టెక్స్ట్ బ్లాక్‌ను కోఆర్డినేట్స్‌తో సహా గుర్తిస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p_idx = max(0, min(page_number_1based - 1, len(doc) - 1))
    page = doc[p_idx]
    
    blocks = page.get_text("blocks")
    text_blocks = []
    for b in blocks:
        if b[6] == 0:  # టెక్స్ట్ బ్లాక్
            clean_txt = b[4].strip()
            if clean_txt:
                text_blocks.append({
                    "bbox": (b[0], b[1], b[2], b[3]),
                    "text": clean_txt
                })
    doc.close()
    return text_blocks

# ---------------- 2. సింగిల్ పేజీ ఇన్-ప్లేస్ రీప్లేసర్ (Auto-Fit సపోర్ట్‌తో) ----------------
def replace_text_in_pdf(pdf_bytes, page_number_1based, find_text, replacement_text, font_size=11, font_color=(0, 0, 0), bg_color=(1, 1, 1), auto_fit=True):
    """లేఅవుట్ చెదరకుండా నిర్దిష్ట పేజీలోని టెక్స్ట్‌ను ఆటో-ఫిట్ స్కేలింగ్‌తో రీప్లేస్ చేస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p_idx = max(0, min(page_number_1based - 1, len(doc) - 1))
    page = doc[p_idx]
    
    rects = page.search_for(find_text)
    if rects:
        for r in rects:
            # పాత అక్షరాలపై బ్యాక్‌గ్రౌండ్ మాస్క్ (వైట్‌అవుట్)
            page.draw_rect(r, color=None, fill=bg_color)
            
            # ఆటో-ఫిట్ ఫాంట్ స్కేలర్: బాక్స్ సరిపోకపోతే ఫాంట్ సైజును కుదిస్తుంది
            eff_fs = font_size
            if auto_fit and len(replacement_text) > len(find_text) and len(find_text) > 0:
                ratio = len(find_text) / len(replacement_text)
                eff_fs = max(7, int(font_size * ratio * 1.1))
                
            page.insert_textbox(r, replacement_text, fontsize=eff_fs, color=font_color, align=0)
    else:
        # బ్లాక్ లెవల్ ఫాల్‌బ్యాక్
        blocks = page.get_text("blocks")
        for b in blocks:
            if find_text in b[4]:
                rect = fitz.Rect(b[0], b[1], b[2], b[3])
                page.draw_rect(rect, color=None, fill=bg_color)
                page.insert_textbox(rect, replacement_text, fontsize=font_size, color=font_color, align=0)
                break
                
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return out

# ---------------- 3. బల్క్ ఫైండ్ & రీప్లేస్ (మొత్తం PDF లో ఒకేసారి) ----------------
def bulk_find_and_replace_pdf(pdf_bytes, find_text, replacement_text, font_size=11, font_color=(0, 0, 0), bg_color=(1, 1, 1)):
    """మొత్తం డాక్యుమెంట్‌లోని అన్ని పేజీలలో ఒకే క్లిక్‌తో పదాన్ని లేఅవుట్ మారకుండా రీప్లేస్ చేస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        rects = page.search_for(find_text)
        for r in rects:
            page.draw_rect(r, color=None, fill=bg_color)
            page.insert_textbox(r, replacement_text, fontsize=font_size, color=font_color, align=0)
            
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return out

# ---------------- 4. స్మార్ట్ రెడాక్షన్ / సెక్యూరిటీ మాస్కింగ్ ----------------
def redact_sensitive_text(pdf_bytes, target_text, mask_color=(0, 0, 0)):
    """ఆధార్, ఫోన్ నంబర్లు, వ్యక్తిగత వివరాలను శాశ్వతంగా డిజిటల్ లెవల్‌లో మాస్క్/తొలగిస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        rects = page.search_for(target_text)
        for r in rects:
            # PyMuPDF రెడాక్షన్ అనోటేషన్
            page.add_redact_annot(r, fill=mask_color)
        page.apply_redactions()
        
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return out

# ---------------- 5. డిజిటల్ స్టాంప్స్ (APPROVED, PAID, VERIFIED) ----------------
def apply_digital_stamp(pdf_bytes, page_number_1based, stamp_text="APPROVED", x_pct=70, y_pct=20, stamp_color="Green"):
    """అధికారిక రౌండ్/రెక్టాంగిల్ డిజిటల్ స్టాంపులను ముద్రిస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p_idx = max(0, min(page_number_1based - 1, len(doc) - 1))
    page = doc[p_idx]
    
    color_map = {
        "Green": (0.1, 0.6, 0.2),
        "Red": (0.85, 0.1, 0.1),
        "Blue": (0.1, 0.3, 0.85),
        "Orange": (0.9, 0.4, 0.0)
    }
    col = color_map.get(stamp_color, (0.1, 0.6, 0.2))
    
    w, h = page.rect.width, page.rect.height
    x_pos = (x_pct / 100.0) * w
    y_pos = (y_pct / 100.0) * h
    
    rect = fitz.Rect(x_pos, y_pos, x_pos + 130, y_pos + 38)
    page.draw_rect(rect, color=col, width=2.5, radius=0.2)
    page.insert_textbox(rect, f"\n{stamp_text.upper()}", fontsize=13, color=col, fontname="helv", align=fitz.TEXT_ALIGN_CENTER)
    
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return out

# ---------------- 6. ఇమేజ్ / డిజిటల్ సంతకం ఓవర్‌లే ----------------
def insert_image_or_signature(pdf_bytes, page_number_1based, img_bytes, x_pct=60, y_pct=75, img_width=120, img_height=60):
    """సంతకాలు (Signatures) లేదా ఫోటోలను కచ్చితమైన బాక్స్‌లో ఇన్సర్ట్ చేస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p_idx = max(0, min(page_number_1based - 1, len(doc) - 1))
    page = doc[p_idx]
    
    w, h = page.rect.width, page.rect.height
    x_pos = (x_pct / 100.0) * w
    y_pos = (y_pct / 100.0) * h
    
    rect = fitz.Rect(x_pos, y_pos, x_pos + img_width, y_pos + img_height)
    page.insert_image(rect, stream=img_bytes)
    
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return out

# ---------------- 7. రియల్-టైమ్ ఇమేజ్ రెండరర్ ----------------
def render_page_preview(pdf_bytes, page_number_1based):
    """ఎడిట్ చేసిన పేజీని రియల్ టైమ్ ఇమేజ్‌గా మారుస్తుంది"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p_idx = max(0, min(page_number_1based - 1, len(doc) - 1))
    page = doc[p_idx]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes
