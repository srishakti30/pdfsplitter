import io
import zipfile
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image

def parse_page_numbers(input_str, total_pages):
    """యూజర్ ఎంటర్ చేసిన పేజీ నంబర్లను సెట్‌గా మారుస్తుంది"""
    pages = set()
    if not input_str or not input_str.strip():
        return pages
    parts = input_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                start = max(1, min(start, total_pages))
                end = max(1, min(end, total_pages))
                if start <= end:
                    pages.update(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                val = int(part)
                if 1 <= val <= total_pages:
                    pages.add(val)
            except ValueError:
                pass
    return pages

def split_single_range(reader, start_p, end_p):
    writer = PdfWriter()
    for i in range(start_p - 1, end_p):
        writer.add_page(reader.pages[i])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def split_custom_ranges_zip(reader, ranges_str, base_name, total_p):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_f:
        parts = [p.strip() for p in ranges_str.split(",") if p.strip()]
        for idx, part in enumerate(parts):
            if "-" in part:
                s, e = map(int, part.split("-"))
            else:
                s = e = int(part)
            s = max(1, min(s, total_p))
            e = max(1, min(e, total_p))
            if s <= e:
                w = PdfWriter()
                for p_i in range(s - 1, e):
                    w.add_page(reader.pages[p_i])
                b = io.BytesIO()
                w.write(b)
                zip_f.writestr(f"{base_name}_Range_{s}_to_{e}.pdf", b.getvalue())
    zip_buf.seek(0)
    return zip_buf.getvalue()

def split_fixed_chunks_zip(reader, chunk_size, base_name, total_p):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_f:
        chunk_idx = 1
        for i in range(0, total_p, chunk_size):
            w = PdfWriter()
            for j in range(i, min(i + chunk_size, total_p)):
                w.add_page(reader.pages[j])
            b = io.BytesIO()
            w.write(b)
            zip_f.writestr(f"{base_name}_Part_{chunk_idx}.pdf", b.getvalue())
            chunk_idx += 1
    zip_buf.seek(0)
    return zip_buf.getvalue()

def split_all_single_pages_zip(reader, base_name):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for i, page in enumerate(reader.pages):
            w = PdfWriter()
            w.add_page(page)
            b = io.BytesIO()
            w.write(b)
            zip_f.writestr(f"{base_name}_Page_{i+1}.pdf", b.getvalue())
    zip_buf.seek(0)
    return zip_buf.getvalue()

def rotate_pdf_pages(pdf_bytes, rot_mode, target_page, angle):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        if rot_mode == "ఈ పేజీ మాత్రమే (Current Page)" and p_num == target_page:
            page.rotate(angle)
        elif rot_mode == "అన్ని పేజీలు (All Pages)":
            page.rotate(angle)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def apply_advanced_watermark(pdf_bytes, wm_text, target_pages_set=None, position="Center Diagonal", opacity=0.3, font_size=36, color_hex="#ef4444"):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    # Convert Hex color to RGB
    h = str(color_hex).lstrip('#')
    rgb = tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) if len(h) == 6 else (1, 0, 0)

    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        if target_pages_set is None or p_num in target_pages_set:
            pw = float(page.mediabox.width)
            ph = float(page.mediabox.height)

            wm_buf = io.BytesIO()
            c = canvas.Canvas(wm_buf, pagesize=(pw, ph))
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(colors.Color(rgb[0], rgb[1], rgb[2], alpha=opacity))

            if "Diagonal" in position:
                c.saveState()
                c.translate(pw / 2, ph / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, wm_text)
                c.restoreState()
            elif "Straight" in position:
                c.drawCentredString(pw / 2, ph / 2, wm_text)
            elif "Top-Left" in position:
                c.drawString(40, ph - 50, wm_text)
            elif "Top-Right" in position:
                c.drawRightString(pw - 40, ph - 50, wm_text)
            elif "Bottom-Left" in position:
                c.drawString(40, 40, wm_text)
            elif "Bottom-Right" in position:
                c.drawRightString(pw - 40, 40, wm_text)

            c.save()
            wm_buf.seek(0)
            wm_reader = PdfReader(wm_buf)
            page.merge_page(wm_reader.pages[0])

        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def generate_interactive_preview_page(pdf_bytes, page_num, angle=0, apply_wm=False, wm_text="", wm_pos="Center Diagonal", opacity=0.3, font_size=36, color_hex="#ef4444"):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    page = reader.pages[page_num - 1]
    if angle != 0:
        page.rotate(angle)

    if apply_wm and wm_text.strip():
        pw = float(page.mediabox.width)
        ph = float(page.mediabox.height)
        h = str(color_hex).lstrip('#')
        rgb = tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) if len(h) == 6 else (1, 0, 0)

        wm_buf = io.BytesIO()
        c = canvas.Canvas(wm_buf, pagesize=(pw, ph))
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(colors.Color(rgb[0], rgb[1], rgb[2], alpha=opacity))

        if "Diagonal" in wm_pos:
            c.saveState()
            c.translate(pw / 2, ph / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, wm_text)
            c.restoreState()
        elif "Straight" in wm_pos:
            c.drawCentredString(pw / 2, ph / 2, wm_text)
        elif "Top-Left" in wm_pos:
            c.drawString(40, ph - 50, wm_text)
        elif "Top-Right" in wm_pos:
            c.drawRightString(pw - 40, ph - 50, wm_text)
        elif "Bottom-Left" in wm_pos:
            c.drawString(40, 40, wm_text)
        elif "Bottom-Right" in wm_pos:
            c.drawRightString(pw - 40, 40, wm_text)

        c.save()
        wm_buf.seek(0)
        wm_reader = PdfReader(wm_buf)
        page.merge_page(wm_reader.pages[0])

    writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def convert_pdf_to_word_docx(pdf_bytes):
    from pdf2docx import Converter
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f_in:
        f_in.write(pdf_bytes)
        in_path = f_in.name
    out_path = in_path.replace(".pdf", ".docx")
    try:
        cv = Converter(in_path)
        cv.convert(out_path, start=0, end=None)
        cv.close()
        with open(out_path, "rb") as f_out:
            docx_bytes = f_out.read()
        return docx_bytes
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(out_path): os.remove(out_path)

def merge_pdf_files(uploaded_files):
    writer = PdfWriter()
    total_pages = 0
    for f in uploaded_files:
        r = PdfReader(io.BytesIO(f.getvalue()))
        for page in r.pages:
            writer.add_page(page)
            total_pages += 1
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue(), total_pages

def zip_multiple_pdf_files(uploaded_files):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for f in uploaded_files:
            zip_f.writestr(f.name, f.getvalue())
    zip_buf.seek(0)
    return zip_buf.getvalue()

def convert_images_to_pdf(uploaded_images):
    pil_images = [Image.open(io.BytesIO(img.getvalue())).convert("RGB") for img in uploaded_images]
    out = io.BytesIO()
    if pil_images:
        pil_images[0].save(out, format="PDF", save_all=True, append_images=pil_images[1:], quality=95)
    out.seek(0)
    return out.getvalue()

def convert_pdf_to_images_zip(pdf_bytes, base_name):
    doc = pdfium.PdfDocument(pdf_bytes)
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for idx, page in enumerate(doc):
            pil_img = page.render(scale=2.0).to_pil()
            b = io.BytesIO()
            pil_img.save(b, format="JPEG", quality=90)
            zip_f.writestr(f"{base_name}_Page_{idx+1}.jpg", b.getvalue())
    zip_buf.seek(0)
    return zip_buf.getvalue(), len(doc)

def add_page_numbers(pdf_bytes, style="Page X of Y", position="Bottom-Center", font_size=10):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total_p = len(reader.pages)
    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        pw = float(page.mediabox.width)
        ph = float(page.mediabox.height)
        txt = f"Page {p_num} of {total_p}" if "of" in style else f"Page {p_num}"
        
        num_buf = io.BytesIO()
        c = canvas.Canvas(num_buf, pagesize=(pw, ph))
        c.setFont("Helvetica", font_size)
        c.setFillColor(colors.HexColor("#334155"))

        if "Bottom-Center" in position:
            c.drawCentredString(pw / 2, 25, txt)
        elif "Bottom-Right" in position:
            c.drawRightString(pw - 30, 25, txt)
        elif "Bottom-Left" in position:
            c.drawString(30, 25, txt)
        elif "Top-Right" in position:
            c.drawRightString(pw - 30, ph - 25, txt)
        elif "Top-Center" in position:
            c.drawCentredString(pw / 2, ph - 25, txt)

        c.save()
        num_buf.seek(0)
        n_reader = PdfReader(num_buf)
        page.merge_page(n_reader.pages[0])
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def compress_pdf_file(pdf_bytes, quality=65):
    doc = pdfium.PdfDocument(pdf_bytes)
    comp_pil_images = []
    scale_factor = 1.0 if quality > 60 else 0.8
    for page in doc:
        comp_pil_images.append(page.render(scale=scale_factor).to_pil())
    out = io.BytesIO()
    if comp_pil_images:
        comp_pil_images[0].save(out, format="PDF", save_all=True, append_images=comp_pil_images[1:], quality=quality, optimize=True)
    out.seek(0)
    return out

def delete_pdf_pages(pdf_bytes, pages_to_delete_set):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    kept = 0
    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        if p_num not in pages_to_delete_set:
            writer.add_page(page)
            kept += 1
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue(), kept

def reorder_pdf_pages(pdf_bytes, new_order_list):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for p_num in new_order_list:
        if 1 <= p_num <= len(reader.pages):
            writer.add_page(reader.pages[p_num - 1])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def lock_pdf(uploaded_file, password):
    r = PdfReader(uploaded_file)
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    w.encrypt(password)
    out = io.BytesIO()
    w.write(out)
    out.seek(0)
    return out.getvalue()

def unlock_pdf(uploaded_file, password):
    r = PdfReader(uploaded_file)
    if r.is_encrypted:
        try:
            r.decrypt(password)
        except:
            return None, "FAIL"
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    out = io.BytesIO()
    w.write(out)
    out.seek(0)
    return out.getvalue(), "SUCCESS"
