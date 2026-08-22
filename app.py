import streamlit as st
from pypdf import PdfReader, PdfWriter
from langdetect import detect
import io

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Smart PDF Tools")
st.write("పిడిఎఫ్ ఫైళ్లను కట్ చేయడం, విడదీయడం మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్ట్ చేసే ఆల్-ఇన్-వన్ టూల్.")

tab1, tab2 = st.tabs(["✂️ PDF Splitter (ఒరిజినల్ డిజైన్/ఇమేజెస్‌తో)", "🌐 Multi-Language Text Extractor"])

# -------------------------------------------------------------
# TAB 1: ఒరిజినల్ ఫార్మాట్ ఏమాత్రం పాడవకుండా PDF కట్ చేయడం
# -------------------------------------------------------------
with tab1:
    st.subheader("✂️ PDF Page Range Splitter")
    st.caption("ఇమేజెస్, ఫాంట్స్, డిజైన్ ఏవీ మారకుండా అసలు రూపంలోనే PDFని కట్ చేసి కొత్త PDFలుగా డౌన్‌లోడ్ చేసుకోండి.")

    uploaded_pdf = st.file_uploader("కట్ చేయాల్సిన PDF ఫైల్‌ను అప్‌లోడ్ చేయండి", type=["pdf"], key="splitter_upload")

    if uploaded_pdf is not None:
        reader = PdfReader(uploaded_pdf)
        total_pages = len(reader.pages)
        st.success(f"అప్‌లోడ్ విజయవంతమైంది! ఈ డాక్యుమెంట్‌లో మొత్తం **{total_pages}** పేజీలు ఉన్నాయి.")

        st.markdown("---")
        split_mode = st.radio(
            "ఎలా కట్ చేయాలనుకుంటున్నారు?",
            ["కస్టమ్ పేజీ రేంజ్ (ఒక భాగాన్ని కట్ చేయడం)", "2 సమాన/ప్రత్యేక భాగాలుగా విడదీయడం", "3 భాగాలుగా విడదీయడం"],
            horizontal=True
        )

        # ఆప్షన్ 1: ఒకే నిర్దిష్ట రేంజ్ కట్ చేయడం
        if split_mode == "కస్టమ్ పేజీ రేంజ్ (ఒక భాగాన్ని కట్ చేయడం)":
            col_a, col_b = st.columns(2)
            with col_a:
                start_p = st.number_input("ప్రారంభ పేజీ (Start Page)", min_value=1, max_value=total_pages, value=1)
            with col_b:
                end_p = st.number_input("ముగింపు పేజీ (End Page)", min_value=start_p, max_value=total_pages, value=min(start_p+1, total_pages))

            if st.button("Generate Cut PDF", key="btn_custom"):
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
                    mime="application/pdf"
                )

        # ఆప్షన్ 2: 2 భాగాలుగా విడదీయడం
        elif split_mode == "2 సమాన/ప్రత్యేక భాగాలుగా విడదీయడం":
            split_point = st.slider("మొదటి భాగం ఎక్కడ ముగియాలి? (పేజీ సంఖ్య)", min_value=1, max_value=total_pages - 1, value=total_pages // 2 if total_pages > 1 else 1)
            st.info(f"👉 భాగం 1: పేజీలు 1 నుండి {split_point} వరకు | భాగం 2: పేజీలు {split_point + 1} నుండి {total_pages} వరకు")

            if st.button("Split into 2 PDFs", key="btn_two_parts"):
                # పార్ట్ 1
                w1 = PdfWriter()
                for p in range(0, split_point):
                    w1.add_page(reader.pages[p])
                buf1 = io.BytesIO()
                w1.write(buf1)
                buf1.seek(0)

                # పార్ట్ 2
                w2 = PdfWriter()
                for p in range(split_point, total_pages):
                    w2.add_page(reader.pages[p])
                buf2 = io.BytesIO()
                w2.write(buf2)
                buf2.seek(0)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label=f"📥 Download Part 1 (Pages 1-{split_point})",
                        data=buf1,
                        file_name=f"Part_1_Pages_1_{split_point}.pdf",
                        mime="application/pdf"
                    )
                with col2:
                    st.download_button(
                        label=f"📥 Download Part 2 (Pages {split_point+1}-{total_pages})",
                        data=buf2,
                        file_name=f"Part_2_Pages_{split_point+1}_{total_pages}.pdf",
                        mime="application/pdf"
                    )

        # ఆప్షన్ 3: 3 భాగాలుగా విడదీయడం
        elif split_mode == "3 భాగాలుగా విడదీయడం":
            if total_pages < 3:
                st.warning("ఈ PDFలో 3 కంటే తక్కువ పేజీలు ఉన్నాయి. కాబట్టి 3 భాగాలుగా విభజించలేము.")
            else:
                col_x, col_y = st.columns(2)
                with col_x:
                    p1_end = st.number_input("మొదటి భాగం ముగింపు పేజీ", min_value=1, max_value=total_pages - 2, value=1)
                with col_y:
                    p2_end = st.number_input("రెండవ భాగం ముగింపు పేజీ", min_value=p1_end + 1, max_value=total_pages - 1, value=p1_end + 1)

                st.info(f"👉 భాగం 1: 1 నుండి {p1_end} | భాగం 2: {p1_end + 1} నుండి {p2_end} | భాగం 3: {p2_end + 1} నుండి {total_pages}")

                if st.button("Split into 3 PDFs", key="btn_three_parts"):
                    # పార్ట్ 1
                    w1 = PdfWriter()
                    for p in range(0, p1_end):
                        w1.add_page(reader.pages[p])
                    buf1 = io.BytesIO()
                    w1.write(buf1)
                    buf1.seek(0)

                    # పార్ట్ 2
                    w2 = PdfWriter()
                    for p in range(p1_end, p2_end):
                        w2.add_page(reader.pages[p])
                    buf2 = io.BytesIO()
                    w2.write(buf2)
                    buf2.seek(0)

                    # పార్ట్ 3
                    w3 = PdfWriter()
                    for p in range(p2_end, total_pages):
                        w3.add_page(reader.pages[p])
                    buf3 = io.BytesIO()
                    w3.write(buf3)
                    buf3.seek(0)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(label=f"📥 Part 1 (1-{p1_end})", data=buf1, file_name="Part_1.pdf", mime="application/pdf")
                    with col2:
                        st.download_button(label=f"📥 Part 2 ({p1_end+1}-{p2_end})", data=buf2, file_name="Part_2.pdf", mime="application/pdf")
                    with col3:
                        st.download_button(label=f"📥 Part 3 ({p2_end+1}-{total_pages})", data=buf3, file_name="Part_3.pdf", mime="application/pdf")


# -------------------------------------------------------------
# TAB 2: భాషల వారీగా టెక్స్ట్ విడదీయడం
# -------------------------------------------------------------
with tab2:
    st.subheader("🌐 Multi-Language Text Extractor")
    st.caption("ఒకే పేజీలో కలిసి ఉన్న వివిధ భాషల టెక్స్ట్‌ను గుర్తించి విడదీస్తుంది.")

    uploaded_lang_file = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="lang_upload")

    if uploaded_lang_file is not None:
        st.info("టెక్స్ట్ మరియు భాషల ప్రాసెసింగ్ జరుగుతోంది...")
        reader = PdfReader(uploaded_lang_file)
        all_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                all_text += t + "\n\n"

        paragraphs = all_text.split("\n\n")
        lang1_text, lang2_text, lang3_text, other_text = [], [], [], []

        for para in paragraphs:
            cleaned = para.strip()
            if len(cleaned) > 5:
                try:
                    lang = detect(cleaned)
                    if lang == 'te':
                        lang1_text.append(cleaned)
                    elif lang == 'en':
                        lang2_text.append(cleaned)
                    elif lang == 'hi':
                        lang3_text.append(cleaned)
                    else:
                        other_text.append(cleaned)
                except:
                    other_text.append(cleaned)

        st.success("విభజన పూర్తయింది!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("తెలుగు (Telugu)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang1_text[:3]), height=150, key="prev_te")
            st.download_button("Download Telugu Text", data="\n\n".join(lang1_text), file_name="telugu_content.txt", mime="text/plain")

        with col2:
            st.subheader("ఇంగ్లీష్ (English)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang2_text[:3]), height=150, key="prev_en")
            st.download_button("Download English Text", data="\n\n".join(lang2_text), file_name="english_content.txt", mime="text/plain")

        with col3:
            st.subheader("హిందీ / ఇతర (Hindi/Other)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang3_text[:3]), height=150, key="prev_hi")
            st.download_button("Download Hindi Text", data="\n\n".join(lang3_text), file_name="hindi_content.txt", mime="text/plain")
