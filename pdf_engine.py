import io
import os
import tempfile
import zipfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from PIL import Image
import pypdfium2 as pdfium
from pdf2docx import Converter

def split_single_range(reader, start_p, end_p):
    writer = PdfWriter()
    for p in range(start_p - 1, end_p):
        writer.add_page(reader.pages[p])
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def split_custom_ranges_zip(reader, ranges_str, base_name, total_pages):
    zip_buffer = io.BytesIO()
    ranges = [r.strip() for r in ranges_str.split(",") if r.strip()]
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for idx, r in enumerate(ranges):
            try:
                sp, ep = map(int, r.split("-")) if "-" in r else (int(r), int(r))
                if 1 <= sp <= ep <= total_pages:
                    writer = PdfWriter()
                    for p in range(sp - 1, ep):
                        writer.add_page(reader.pages[p])
                    p_buf = io.BytesIO()
                    writer.write(p_buf)
                    p_buf.seek(0)
                    zip_file.writestr(f"{base_name}_Part_{idx+1}_Pages_{sp}_to_{ep}.pdf", p_buf.getvalue())
            except:
                pass
    zip_buffer.seek(0)
    return zip_buffer

def split_fixed_chunks_zip(reader, chunk_size, base_name, total_pages):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for chunk_i in range(0, total_pages, chunk_size):
            sp = chunk_i + 1
            ep = min(chunk_i + chunk_size, total_pages)
            writer = PdfWriter()
            for p in range(chunk_i, ep):
                writer.add_page(reader.pages[p])
            p_buf = io.BytesIO()
            writer.write(p_buf)
            p_buf.seek(0)
            zip_file.writestr(f"{base_name}_Pages_{sp}_to_{ep}.pdf", p_buf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def split_all_single_pages_zip(reader, base_name):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            p_buf = io.BytesIO()
            writer.write(p_buf)
            p_buf.seek(0)
            zip_file.writestr(f"{base_name}_Page_{i+1:03d}.pdf", p_buf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def merge_pdf_files(file_list):
    merger = PdfWriter()
    total_pages = 0
    for f in file_list:
        r = PdfReader(f)
        total_pages += len(r.pages)
        for page in r.pages:
            merger.add_page(page)
    merged_output = io.BytesIO()
    merger.write(merged_output)
    merged_output.seek(0)
    return merged_output, total_pages

def zip_multiple_pdf_files(file_list):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        for f in file_list:
            z.writestr(f.name, f.getvalue())
    zip_buf.seek(0)
    return zip_buf

def lock_pdf(file_obj, password):
    reader = PdfReader(file_obj)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def unlock_pdf(file_obj, password):
    reader = PdfReader(file_obj)
    if not reader.is_encrypted:
        return None, "NOT_ENCRYPTED"
    status = reader.decrypt(password)
    if status == 0:
        return None, "WRONG_PASSWORD"
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf, "SUCCESS"

def rotate_pdf_pages(file_bytes, mode, target_page_1based, angle):
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if mode == "అన్ని పేజీలు (All Pages)":
            page.rotate(angle)
        elif mode == "ఈ పేజీ మాత్రమే (Current Page)":
            if (idx + 1) == target_page_1based:
                page.rotate(angle)
        writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def parse_page_numbers(input_str, total_pages):
    target_pages = set()
    parts = [p.strip() for p in input_str.split(",") if p.strip()]
    for p in parts:
        try:
            if "-" in p:
                start, end = map(int, p.split("-"))
                for x in range(start, end + 1):
                    if 1 <= x <= total_pages:
                        target_pages.add(x)
            else:
                x = int(p)
                if 1 <= x <= total_pages:
                    target_pages.add(x)
        except:
            pass
    return target_pages

def create_wm_layer(width, height, text, position, opacity, font_size):
    wm_buf = io.BytesIO()
    c = canvas.Canvas(wm_buf, pagesize=(width, height))
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(Color(0.4, 0.4, 0.4, alpha=opacity))
    c.saveState()
    margin_x, margin_y = 40, 40
    if position == "Center Diagonal (మధ్యలో - 45° వాలుగా)":
        c.translate(width / 2.0, height / 2.0)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
    elif position == "Center Straight (మధ్యలో - నిలువు/అడ్డం 0°)":
        c.translate(width / 2.0, height / 2.0)
        c.drawCentredString(0, 0, text)
    elif position == "Top-Left (ఎగువ ఎడమ)":
        c.drawString(margin_x, height - margin_y - font_size, text)
    elif position == "Top-Right (ఎగువ కుడి)":
        c.drawRightString(width - margin_x, height - margin_y - font_size, text)
    elif position == "Bottom-Left (దిగువ ఎడమ)":
        c.drawString(margin_x, margin_y, text)
    elif position == "Bottom-Right (దిగువ కుడి)":
        c.drawRightString(width - margin_x, margin_y, text)
    else:
        c.translate(width / 2.0, height / 2.0)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    wm_buf.seek(0)
    return wm_buf

def apply_advanced_watermark(file_bytes, text, target_pages_set, position, opacity=0.2, font_size=36):
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        current_page_num = idx + 1
        if target_pages_set is None or current_page_num in target_pages_set:
            box = page.mediabox
            width, height = float(box.width), float(box.height)
            wm_buf = create_wm_layer(width, height, text, position, opacity, font_size)
            wm_reader = PdfReader(wm_buf)
            page.merge_page(wm_reader.pages[0])
        writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def generate_interactive_preview_page(file_bytes, page_1based, angle, wm_enabled, wm_text, wm_pos, opacity, font_size):
    reader = PdfReader(io.BytesIO(file_bytes))
    target_idx = max(0, min(page_1based - 1, len(reader.pages) - 1))
    page = reader.pages[target_idx]
    if angle != 0:
        page.rotate(angle)
    if wm_enabled and wm_text.strip():
        box = page.mediabox
        width, height = float(box.width), float(box.height)
        wm_buf = create_wm_layer(width, height, wm_text, wm_pos, opacity, font_size)
        wm_reader = PdfReader(wm_buf)
        page.merge_page(wm_reader.pages[0])
    writer = PdfWriter()
    writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf.getvalue()

def convert_images_to_pdf(uploaded_image_files):
    images = []
    for f in uploaded_image_files:
        img = Image.open(f)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)
    buf = io.BytesIO()
    if images:
        images[0].save(buf, format="PDF", save_all=True, append_images=images[1:])
    buf.seek(0)
    return buf

def convert_pdf_to_images_zip(pdf_bytes, base_name):
    doc = pdfium.PdfDocument(pdf_bytes)
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        for i, page in enumerate(doc):
            pil_img = page.render(scale=2.0).to_pil()
            img_buf = io.BytesIO()
            pil_img.save(img_buf, format="JPEG", quality=92)
            z.writestr(f"{base_name}_page_{i+1:03d}.jpg", img_buf.getvalue())
    zip_buf.seek(0)
    return zip_buf, len(doc)

def delete_pdf_pages(file_bytes, delete_pages_set):
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    kept_count = 0
    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        if p_num not in delete_pages_set:
            writer.add_page(page)
            kept_count += 1
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf, kept_count

def reorder_pdf_pages(file_bytes, new_order_list):
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    total = len(reader.pages)
    for p_num in new_order_list:
        if 1 <= p_num <= total:
            writer.add_page(reader.pages[p_num - 1])
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

# ----------- PAGE NUMBERING & COMPRESSION -----------
def add_page_numbers(file_bytes, style="Page X of Y", position="Bottom-Center", font_size=10):
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    for idx, page in enumerate(reader.pages):
        current_p = idx + 1
        box = page.mediabox
        pw, ph = float(box.width), float(box.height)
        
        num_str = f"Page {current_p} of {total_pages}" if style == "Page X of Y" else f"Page {current_p}"
        
        num_buf = io.BytesIO()
        c = canvas.Canvas(num_buf, pagesize=(pw, ph))
        c.setFont("Helvetica", font_size)
        c.setFillColor(Color(0.2, 0.2, 0.2, alpha=0.8))
        
        margin_y = 25
        if position == "Bottom-Center":
            c.drawCentredString(pw / 2.0, margin_y, num_str)
        elif position == "Bottom-Right":
            c.drawRightString(pw - 35, margin_y, num_str)
        elif position == "Bottom-Left":
            c.drawString(35, margin_y, num_str)
        elif position == "Top-Right":
            c.drawRightString(pw - 35, ph - 30, num_str)
        elif position == "Top-Center":
            c.drawCentredString(pw / 2.0, ph - 30, num_str)
            
        c.save()
        num_buf.seek(0)
        
        num_reader = PdfReader(num_buf)
        page.merge_page(num_reader.pages[0])
        writer.add_page(page)
        
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def compress_pdf_file(file_bytes, image_quality=70):
    doc = pdfium.PdfDocument(file_bytes)
    compressed_images = []
    for page in doc:
        pil_img = page.render(scale=1.5).to_pil()
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        compressed_images.append(pil_img)
        
    out_buf = io.BytesIO()
    if compressed_images:
        compressed_images[0].save(
            out_buf,
            format="PDF",
            save_all=True,
            append_images=compressed_images[1:],
            quality=image_quality,
            optimize=True
        )
    out_buf.seek(0)
    return out_buf

# ----------- 100% OFFLINE PDF ➜ WORD (.DOCX) CONVERTER -----------
def convert_pdf_to_word_docx(pdf_bytes):
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = os.path.join(temp_dir, "source.pdf")
    temp_docx_path = os.path.join(temp_dir, "output.docx")
    
    try:
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_bytes)
            f.flush()
            os.fsync(f.fileno())
            
        cv = Converter(temp_pdf_path)
        cv.convert(temp_docx_path, start=0, end=None, multi_processing=False)
        cv.close()
        
        with open(temp_docx_path, "rb") as f:
            docx_bytes = f.read()
            
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            
    return docx_bytes
