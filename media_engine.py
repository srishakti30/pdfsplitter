import io
import tempfile
import os
import cv2
import numpy as np
from PIL import Image
import pypdfium2 as pdfium

def process_video_to_pdf(uploaded_file, interval_sec=1.0, max_frames=200):
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
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                extracted_images.append(pil_img)
                if len(extracted_images) >= max_frames:
                    break
            frame_idx += 1
        cap.release()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    pdf_buf = io.BytesIO()
    if extracted_images:
        extracted_images[0].save(pdf_buf, format="PDF", save_all=True, append_images=extracted_images[1:])
    pdf_buf.seek(0)
    return pdf_buf, len(extracted_images), duration_sec

def process_gif_to_pdf(uploaded_file, frame_skip=1):
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

def convert_pdf_to_animated_gif(pdf_bytes, seconds_per_page=1.5):
    doc = pdfium.PdfDocument(pdf_bytes)
    pil_pages = [page.render(scale=1.5).to_pil() for page in doc]
    gif_buf = io.BytesIO()
    if pil_pages:
        duration_ms = int(seconds_per_page * 1000)
        pil_pages[0].save(
            gif_buf,
            format="GIF",
            save_all=True,
            append_images=pil_pages[1:],
            duration=duration_ms,
            loop=0
        )
    gif_buf.seek(0)
    return gif_buf, len(pil_pages)

def convert_pdf_to_mp4_video(pdf_bytes, seconds_per_page=2.0, audio_file_bytes=None, audio_ext="mp3"):
    """
    PDF ని MP4 వీడియోగా మారుస్తుంది. ఆడియో ఉంటే బ్యాక్‌గ్రౌండ్ మ్యూజిక్/వాయిస్ జోడిస్తుంది.
    """
    doc = pdfium.PdfDocument(pdf_bytes)
    pil_pages = [page.render(scale=1.5).to_pil() for page in doc]
    if not pil_pages:
        return None, 0

    w, h = pil_pages[0].size
    w = w if w % 2 == 0 else w - 1
    h = h if h % 2 == 0 else h - 1

    temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_video_path = temp_video.name
    temp_video.close()

    try:
        video_fps = 10.0
        frames_per_page = int(video_fps * seconds_per_page)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, video_fps, (w, h))

        for page_img in pil_pages:
            resized_page = page_img.resize((w, h))
            cv_img = cv2.cvtColor(np.array(resized_page), cv2.COLOR_RGB2BGR)
            for _ in range(frames_per_page):
                out.write(cv_img)
        out.release()

        # ఆడియో లేకపోతే నేరుగా వీడియో రిటర్న్ చేయడం
        if not audio_file_bytes:
            with open(temp_video_path, "rb") as f:
                mp4_bytes = f.read()
            buf = io.BytesIO(mp4_bytes)
            buf.seek(0)
            return buf, len(pil_pages)

        # ఆడియో ఉన్నప్పుడు moviepy తో ఆడియో కలపడం
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            temp_audio = tempfile.NamedTemporaryFile(suffix=f".{audio_ext}", delete=False)
            temp_audio.write(audio_file_bytes)
            temp_audio_path = temp_audio.name
            temp_audio.close()

            temp_final_out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_final_path = temp_final_out.name
            temp_final_out.close()

            video_clip = VideoFileClip(temp_video_path)
            audio_clip = AudioFileClip(temp_audio_path)

            # వీడియో సమయానికి ఆడియోను కట్ లేదా లూప్ చేయడం
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
            
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(temp_final_path, codec="libx264", audio_codec="aac", fps=10, logger=None)

            video_clip.close()
            audio_clip.close()
            final_clip.close()

            with open(temp_final_path, "rb") as f:
                final_bytes = f.read()

            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            if os.path.exists(temp_final_path): os.remove(temp_final_path)

            buf = io.BytesIO(final_bytes)
            buf.seek(0)
            return buf, len(pil_pages)
        except Exception:
            # Moviepy ఫెయిల్ అయితే సాధారణ వీడియో ఇవ్వడం
            with open(temp_video_path, "rb") as f:
                mp4_bytes = f.read()
            buf = io.BytesIO(mp4_bytes)
            buf.seek(0)
            return buf, len(pil_pages)

    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
