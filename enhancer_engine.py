import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

def restore_and_enhance_photo(img_bytes, mode):
    """
    100% ఆఫ్‌లైన్ మొబైల్-ఫ్రెండ్లీ ఫోటో రీస్టోరేషన్ & ఆర్ట్ ఇంజిన్
    """
    nparr = np.frombuffer(img_bytes, np.uint8)
    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 1. 🎨 Pencil Sketch & Line Art (చేత్తో గీసిన పెన్సిల్ ఆర్ట్)
    if mode.startswith("1."):
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256.0)
        res_rgb = cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)

    # 2. 🧹 B&W Scratch & Spot Cleaner (మచ్చలు, గీతలు తొలగింపు)
    elif mode.startswith("2."):
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
        denoised = cv2.fastNlMeansDenoising(gray, None, 15, 7, 21)
        smooth = cv2.medianBlur(denoised, 3)
        res_rgb = cv2.cvtColor(smooth, cv2.COLOR_GRAY2RGB)

    # 3. 💎 True HD Super-Clarity & Smart Sharpness (అప్‌గ్రేడెడ్ HD ఇంజిన్)
    elif mode.startswith("3."):
        # Bilateral Filtering to keep edges sharp while removing surface blur
        smoothed = cv2.bilateralFilter(cv_img, d=9, sigmaColor=75, sigmaSpace=75)
        
        # LAB CLAHE Color Balancing
        lab = cv2.cvtColor(smoothed, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        bgr_enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # High-Pass Unsharp Masking Kernel (Crystal Edge Detailing)
        gaussian = cv2.GaussianBlur(bgr_enhanced, (0, 0), 2.0)
        unsharp = cv2.addWeighted(bgr_enhanced, 1.6, gaussian, -0.6, 0)
        
        rgb = cv2.cvtColor(unsharp, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        
        # Tone & Contrast Punch
        pil_img = ImageEnhance.Contrast(pil_img).enhance(1.25)
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(2.0)
        res_rgb = np.array(pil_img)

    # 4. 🌈 Soft Warm / Vintage Colorize Tint (పాత ఫోటోకు లైట్ కలర్ టచ్)
    elif mode.startswith("4."):
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
        sepia_bg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        sepia_img = cv2.transform(sepia_bg, sepia_filter)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        res_rgb = cv2.cvtColor(sepia_img, cv2.COLOR_BGR2RGB)

    else:
        res_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

    pil_res = Image.fromarray(res_rgb)
    out_buf = io.BytesIO()
    pil_res.save(out_buf, format="JPEG", quality=95)
    out_buf.seek(0)
    return out_buf, pil_res
