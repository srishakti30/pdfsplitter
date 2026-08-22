import io
import zipfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

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

def rotate_pdf_pages(file_obj, mode, target_page_1based, angle):
    reader = PdfReader(file_obj)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if mode == "అన్ని పేజీలు (All Pages)":
            page.rotate(angle)
        elif mode == "నిర్దిష్ట పేజీ మాత్రమే (Single Page)":
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

def apply_advanced_watermark(file_obj, text, target_pages_set, position, opacity=0.2, font_size=36):
    reader = PdfReader(file_obj)
    writer = PdfWriter()
    
    for idx, page in enumerate(reader.pages):
        current_page_num = idx + 1
        
        # పేజీ నంబర్ మ్యాచ్ అయితేనే వాటర్‌మార్క్ వేయడం
        if target_pages_set is None or current_page_num in target_pages_set:
            box = page.mediabox
            width, height = float(box.width), float(box.height)
            
            wm_buf = io.BytesIO()
            c = canvas.Canvas(wm_buf, pagesize=(width, height))
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(Color(0.4, 0.4, 0.4, alpha=opacity))
            c.saveState()
            
            margin_x = 40
            margin_y = 40
            
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
            
            wm_reader = PdfReader(wm_buf)
            page.merge_page(wm_reader.pages[0])
            
        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf
