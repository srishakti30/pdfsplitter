import io
import tempfile
import os
import cv2
from PIL import Image

def process_video_to_pdf(uploaded_file, interval_sec=1.0, max_frames=200):
    """
    MP4, MOV, AVI, MKV వీడియో ఫైళ్ల నుండి ఫ్రేమ్స్‌ను వేరు చేసి PDFగా మారుస్తుంది.
    """
    # తాత్కాలిక ఫైల్‌గా సేవ్ చేయడం (OpenCV రీడ్ చేయడం కోసం)
    suffix = "." + uploaded_file.name.rsplit(".", 1)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_f:
        temp_f.write(uploaded_file.getvalue())
        temp_path = temp_f.name

    extracted_images = []
    try:
        cap = cv2.VideoCapture(temp_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps if fps > 0 else 0
        
        frame_step = max(1, int(fps * interval_sec))
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_step == 0:
                # BGR నుండి RGB కి మార్చడం
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                extracted_images.append(pil_img)
                
                # మెమరీ రక్షణ కోసం గరిష్ట పరిమితి
                if len(extracted_images) >= max_frames:
                    break
            frame_idx += 1
        cap.release()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # PDFగా మార్చడం
    pdf_buf = io.BytesIO()
    if extracted_images:
        extracted_images[0].save(pdf_buf, format="PDF", save_all=True, append_images=extracted_images[1:])
    pdf_buf.seek(0)
    
    return pdf_buf, len(extracted_images), duration_sec

def process_gif_to_pdf(uploaded_file, frame_skip=1):
    """
    యానిమేటెడ్ GIF ఫైల్ నుండి ఫ్రేమ్‌లను వేరు చేసి PDFగా మారుస్తుంది.
    """
    gif_img = Image.open(uploaded_file)
    n_frames = getattr(gif_img, "n_frames", 1)
    
    extracted_frames = []
    for f_idx in range(0, n_frames, frame_skip):
        gif_img.seek(f_idx)
        extracted_frames.append(gif_img.convert("RGB"))
        
    pdf_buf = io.BytesIO()
    if extracted_frames:
        extracted_frames[0].save(pdf_buf, format="PDF", save_all=True, append_images=extracted_frames[1:])
    pdf_buf.seek(0)
    
    return pdf_buf, len(extracted_frames)
