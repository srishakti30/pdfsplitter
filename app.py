import streamlit as st
from pypdf import PdfReader
from langdetect import detect
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Multi-Language PDF Splitter", layout="centered")

st.title("📄 Multi-Language PDF Splitter")
st.write("3 భాషలు కలిసి ఉన్న PDFని అప్‌లోడ్ చేసి వేర్వేరుగా డౌన్‌లోడ్ చేసుకోండి.")

uploaded_file = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"])

def create_pdf(text_lines):
    """టెక్స్ట్ నుండి కొత్త PDFని సృష్టించే ఫంక్షన్"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    for line in text_lines:
        # సింపుల్ టెక్స్ట్ రాపింగ్
        if y < 50:
            p.showPage()
            y = 750
        p.drawString(50, y, line[:90])
        y -= 20
    p.save()
    buffer.seek(0)
    return buffer

if uploaded_file is not None:
    st.info("ఫైల్ ప్రాసెస్ అవుతోంది...")
    
    reader = PdfReader(uploaded_file)
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n\n"
            
    paragraphs = all_text.split("\n\n")
    
    lang1_text = []
    lang2_text = []
    lang3_text = []
    other_text = []
    
    # భాషలను గుర్తించడం
    for para in paragraphs:
        cleaned = para.strip()
        if len(cleaned) > 5:
            try:
                lang = detect(cleaned)
                if lang == 'te':        # తెలుగు
                    lang1_text.append(cleaned)
                elif lang == 'en':      # ఇంగ్లీష్
                    lang2_text.append(cleaned)
                elif lang == 'hi':      # హిందీ
                    lang3_text.append(cleaned)
                else:
                    other_text.append(cleaned)
            except:
                other_text.append(cleaned)
                
    st.success("విభజన పూర్తయింది!")
    
    # డౌన్‌లోడ్ బటన్లు
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("తెలుగు (Telugu)")
        st.text_area("ప్రివ్యూ", "\n\n".join(lang1_text[:3]), height=150)
        st.download_button(
            label="Download Telugu Text",
            data="\n\n".join(lang1_text),
            file_name="telugu_content.txt",
            mime="text/plain"
        )
        
    with col2:
        st.subheader("ఇంగ్లీష్ (English)")
        st.text_area("ప్రివ్యూ", "\n\n".join(lang2_text[:3]), height=150)
        st.download_button(
            label="Download English Text",
            data="\n\n".join(lang2_text),
            file_name="english_content.txt",
            mime="text/plain"
        )
        
    with col3:
        st.subheader("హిందీ / ఇతర (Hindi/Other)")
        st.text_area("ప్రివ్యూ", "\n\n".join(lang3_text[:3]), height=150)
        st.download_button(
            label="Download Hindi Text",
            data="\n\n".join(lang3_text),
            file_name="hindi_content.txt",
            mime="text/plain"
        )
