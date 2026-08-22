import streamlit as st
from pypdf import PdfReader, PdfWriter
from langdetect import detect
import io
import base64

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Smart PDF Tools")
st.write("పిడిఎఫ్ ప్రివ్యూ చూస్తూ పేజీలను కట్ చేయడం మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్ట్ చేసే టూల్.")

def display_pdf(file_bytes):
    """అప్‌లోడ్ చేసిన PDFని వెబ్‌సైట్ స్క్రీన్‌పైనే చూపించే వ్యూయర్"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✂️ PDF Preview & Splitter", "🌐 Multi-Language Text Extractor"])

# -------------------------------------------------------------
# TAB 1: లైవ్ PDF వ్యూయర్ మరియు స్ప్లిట్టర్
# -------------------------------------------------------------
with tab1:
    st.subheader("📄 PDF Live Preview & Splitter")
    st.caption("ఎడమవైపు ఒరిజినల్ PDFని స్క్రోల్ చేస్తూ చూసి, కుడివైపు ఏ పేజీలు కావాలో కట్ చేసుకోండి.")

    uploaded_pdf = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="splitter_upload")

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.getvalue()
        reader = PdfReader(uploaded_pdf)
        total_pages = len(reader.pages)

        # స్క్రీన్‌ను రెండు భాగాలుగా విభజించడం (ఎడమవైపు వ్యూయర్, కుడివైపు కంట్రోల్స్)
        col_preview, col_controls = st.columns([1.2, 1], gap="large")

        with col_preview:
            st.markdown("#### 👁️ PDF Live View")
            display_pdf(pdf_bytes)

        with col_controls:
            st.markdown("#### ⚙️ Split Settings")
            st.success(f"మొత్తం పేజీల సంఖ్య: **{total_pages}**")

            split_mode = st.radio(
                "విభజన పద్ధతిని ఎంచుకోండి:",
                ["కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)", "2 భాగాలుగా విడదీయడం", "3 భాగాలుగా విడదీయడం"]
            )

            st.markdown("---")

            # ఆప్షన్ 1: కస్టమ్ రేంజ్
            if split_mode == "కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)":
                c1, c2 = st.columns(2)
                with c1:
                    start_p = st.number_input("నుండి (Start Page)", min_value=1, max_value=total_pages, value=1)
                with c2:
                    end_p = st.number_input("వరకు (End Page)", min_value=start_p, max_value=total_pages, value=min(start_p + 1, total_pages))

                if st.button("✂️ Generate Cut PDF", key="btn_custom", use_container_width=True):
                    writer = PdfWriter()
                    for p in range(start_p - 1, end_p):
                        writer.add_page(reader.pages[p])
                    
                    out_buffer = io.BytesIO()
                    writer.write(out_buffer)
                    out_buffer.seek(0)
                    
                    st.download_button(
                        label=f"📥 Download Pages {start_p}-{end_p} (PDF)",
                        data=out_buffer,
                        file_name=f"Pages_{start_p}_to_{end_p}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            # ఆప్షన్ 2: 2 భాగాలు
            elif split_mode == "2 భాగాలుగా విడదీయడం":
                split_point = st.slider("మొదటి భాగం ముగింపు పేజీ:", min_value=1, max_value=total_pages - 1, value=total_pages // 2 if total_pages > 1 else 1)
                st.info(f"👉 Part 1: పేజీలు 1 - {split_point}\n👉 Part 2: పేజీలు {split_point + 1} - {total_pages}")

                if st.button("✂️ Split into 2 PDFs", key="btn_two_parts", use_container_width=True):
                    # Part 1
                    w1 = PdfWriter()
                    for p in range(0, split_point):
                        w1.add_page(reader.pages[p])
                    buf1 = io.BytesIO()
                    w1.write(buf1)
                    buf1.seek(0)

                    # Part 2
                    w2 = PdfWriter()
                    for p in range(split_point, total_pages):
                        w2.add_page(reader.pages[p])
                    buf2 = io.BytesIO()
                    w2.write(buf2)
                    buf2.seek(0)

                    st.download_button(label=f"📥 Download Part 1 (1-{split_point})", data=buf1, file_name=f"Part_1_Pages_1_{split_point}.pdf", mime="application/pdf", use_container_width=True)
                    st.download_button(label=f"📥 Download Part 2 ({split_point+1}-{total_pages})", data=buf2, file_name=f"Part_2_Pages_{split_point+1}_{total_pages}.pdf", mime="application/pdf", use_container_width=True)

            # ఆప్షన్ 3: 3 భాగాలు
            elif split_mode == "3 భాగాలుగా విడదీయడం":
                if total_pages < 3:
                    st.warning("ఈ PDFలో 3 కంటే తక్కువ పేజీలు ఉన్నాయి.")
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        p1_end = st.number_input("Part 1 ముగింపు పేజీ", min_value=1, max_value=total_pages - 2, value=1)
                    with c2:
                        p2_end = st.number_input("Part 2 ముగింపు పేజీ", min_value=p1_end + 1, max_value=total_pages - 1, value=p1_end + 1)

                    st.info(f"👉 Part 1: 1 - {p1_end}\n👉 Part 2: {p1_end + 1} - {p2_end}\n👉 Part 3: {p2_end + 1} - {total_pages}")

                    if st.button("✂️ Split into 3 PDFs", key="btn_three_parts", use_container_width=True):
                        # Part 1
                        w1 = PdfWriter()
                        for p in range(0, p1_end):
                            w1.add_page(reader.pages[p])
                        b1 = io.BytesIO()
                        w1.write(b1)
                        b1.seek(0)

                        # Part 2
                        w2 = PdfWriter()
                        for p in range(p1_end, p2_end):
                            w2.add_page(reader.pages[p])
                        b2 = io.BytesIO()
                        w2.write(b2)
                        b2.seek(0)

                        # Part 3
                        w3 = PdfWriter()
                        for p in range(p2_end, total_pages):
                            w3.add_page(reader.pages[p])
                        b3 = io.BytesIO()
                        w3.write(b3)
                        b3.seek(0)

                        st.download_button(label=f"📥 Download Part 1 (1-{p1_end})", data=b1, file_name="Part_1.pdf", mime="application/pdf", use_container_width=True)
                        st.download_button(label=f"📥 Download Part 2 ({p1_end+1}-{p2_end})", data=b2, file_name="Part_2.pdf", mime="application/pdf", use_container_width=True)
                        st.download_button(label=f"📥 Download Part 3 ({p2_end+1}-{total_pages})", data=b3, file_name="Part_3.pdf", mime="application/pdf", use_container_width=True)

# -------------------------------------------------------------
# TAB 2: భాషల వారీగా టెక్స్ట్ ఎక్స్‌ట్రాక్టర్
# -------------------------------------------------------------
with tab2:
    st.subheader("🌐 Multi-Language Text Extractor")
    st.caption("PDFలోని టెక్స్ట్‌ను గుర్తించి భాషల వారీగా విభజిస్తుంది.")

    uploaded_lang_file = st.file_uploader("PDFని అప్‌లోడ్ చేయండి", type=["pdf"], key="lang_upload")

    if uploaded_lang_file is not None:
        reader_lang = PdfReader(uploaded_lang_file)
        all_text = ""
        for page in reader_lang.pages:
            t = page.extract_text()
            if t:
                all_text += t + "\n\n"

        paragraphs = all_text.split("\n\n")
        lang1_text, lang2_text, lang3_text = [], [], []

        for para in paragraphs:
            cleaned = para.strip()
            if len(cleaned) > 5:
                try:
                    l = detect(cleaned)
                    if l == 'te':
                        lang1_text.append(cleaned)
                    elif l == 'en':
                        lang2_text.append(cleaned)
                    elif l == 'hi':
                        lang3_text.append(cleaned)
                except:
                    pass

        st.success("విభజన పూర్తయింది!")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("తెలుగు (Telugu)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang1_text[:3]), height=150, key="te_prev")
            st.download_button("Download Telugu Text", data="\n\n".join(lang1_text), file_name="telugu_text.txt", mime="text/plain")
        with c2:
            st.subheader("ఇంగ్లీష్ (English)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang2_text[:3]), height=150, key="en_prev")
            st.download_button("Download English Text", data="\n\n".join(lang2_text), file_name="english_text.txt", mime="text/plain")
        with c3:
            st.subheader("హిందీ / ఇతర (Hindi/Other)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang3_text[:3]), height=150, key="hi_prev")
            st.download_button("Download Hindi Text", data="\n\n".join(lang3_text), file_name="hindi_text.txt", mime="text/plain")
