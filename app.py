import streamlit as st
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
from langdetect import detect
from PIL import Image
import io
import time

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Smart PDF Tools")
st.caption("PDF వ్యూయర్, స్ప్లిట్టర్, మెర్జర్ మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్టర్.")

tab1, tab2, tab3 = st.tabs([
    "👁️ & ✂️ PDF Preview & Splitter", 
    "📑 PDF Merger (కలపడం)", 
    "🌐 Multi-Language Text Extractor"
])

# -------------------------------------------------------------
# TAB 1: PDF ప్రివ్యూ & స్ప్లిట్టింగ్
# -------------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("👁️ PDF Live Preview")
        uploaded_pdf = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="splitter_upload")

    diag_status = "No File Uploaded"
    diag_pages = 0
    diag_size_mb = 0.0
    diag_render_time = 0.0
    diag_errors = []

    if uploaded_pdf is not None:
        try:
            start_time = time.time()
            pdf_bytes = uploaded_pdf.getvalue()
            diag_size_mb = len(pdf_bytes) / (1024 * 1024)
            
            pdf_doc = pdfium.PdfDocument(pdf_bytes)
            diag_pages = len(pdf_doc)
            diag_status = "File Loaded Successfully"

            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)

            with col_left:
                page_col1, page_col2 = st.columns([2, 1])
                with page_col1:
                    preview_page = st.number_input("చూడాల్సిన పేజీ సంఖ్య (Page Viewer):", min_value=1, max_value=total_pages, value=1)
                
                page = pdf_doc.get_page(preview_page - 1)
                pil_image = page.render(scale=2.0).to_pil()
                diag_render_time = time.time() - start_time
                
                st.image(pil_image, caption=f"పేజీ {preview_page} / {total_pages}", use_container_width=True)

            with col_right:
                st.subheader("⚙️ Split Settings")
                st.success(f"మొత్తం పేజీల సంఖ్య: **{total_pages}**")

                split_mode = st.radio(
                    "విభజన పద్ధతిని ఎంచుకోండి:",
                    ["కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)", "2 భాగాలుగా విడదీయడం", "3 భాగాలుగా విడదీయడం"]
                )

                if split_mode == "కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)":
                    c1, c2 = st.columns(2)
                    with c1:
                        start_p = st.number_input("నుండి (Start Page)", min_value=1, max_value=total_pages, value=1)
                    with c2:
                        end_p = st.number_input("వరకు (End Page)", min_value=start_p, max_value=total_pages, value=min(start_p+1, total_pages))

                    if st.button("✂️ Generate Cut PDF", key="btn_custom"):
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

                elif split_mode == "2 భాగాలుగా విడదీయడం":
                    split_point = st.slider("మొదటి భాగం ముగింపు పేజీ", min_value=1, max_value=total_pages - 1, value=total_pages // 2 if total_pages > 1 else 1)
                    st.write(f"👉 **పార్ట్ 1:** 1-{split_point} | **పార్ట్ 2:** {split_point + 1}-{total_pages}")

                    if st.button("✂️ Split into 2 PDFs", key="btn_two"):
                        w1, w2 = PdfWriter(), PdfWriter()
                        for p in range(0, split_point):
                            w1.add_page(reader.pages[p])
                        for p in range(split_point, total_pages):
                            w2.add_page(reader.pages[p])
                        
                        b1, b2 = io.BytesIO(), io.BytesIO()
                        w1.write(b1); b1.seek(0)
                        w2.write(b2); b2.seek(0)

                        st.download_button(f"📥 Download Part 1 (1-{split_point})", data=b1, file_name="Part_1.pdf", mime="application/pdf")
                        st.download_button(f"📥 Download Part 2 ({split_point+1}-{total_pages})", data=b2, file_name="Part_2.pdf", mime="application/pdf")

                elif split_mode == "3 భాగాలుగా విడదీయడం":
                    if total_pages < 3:
                        st.warning("ఈ PDFలో 3 కంటే తక్కువ పేజీలు ఉన్నాయి.")
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            p1_end = st.number_input("భాగం 1 ముగింపు పేజీ", min_value=1, max_value=total_pages - 2, value=1)
                        with c2:
                            p2_end = st.number_input("భాగం 2 ముగింపు పేజీ", min_value=p1_end + 1, max_value=total_pages - 1, value=p1_end + 1)

                        st.write(f"👉 **1:** 1-{p1_end} | **2:** {p1_end+1}-{p2_end} | **3:** {p2_end+1}-{total_pages}")

                        if st.button("✂️ Split into 3 PDFs", key="btn_three"):
                            w1, w2, w3 = PdfWriter(), PdfWriter(), PdfWriter()
                            for p in range(0, p1_end):
                                w1.add_page(reader.pages[p])
                            for p in range(p1_end, p2_end):
                                w2.add_page(reader.pages[p])
                            for p in range(p2_end, total_pages):
                                w3.add_page(reader.pages[p])

                            b1, b2, b3 = io.BytesIO(), io.BytesIO(), io.BytesIO()
                            w1.write(b1); b1.seek(0)
                            w2.write(b2); b2.seek(0)
                            w3.write(b3); b3.seek(0)

                            st.download_button(f"📥 Part 1 (1-{p1_end})", data=b1, file_name="Part_1.pdf", mime="application/pdf")
                            st.download_button(f"📥 Part 2 ({p1_end+1}-{p2_end})", data=b2, file_name="Part_2.pdf", mime="application/pdf")
                            st.download_button(f"📥 Part 3 ({p2_end+1}-{total_pages})", data=b3, file_name="Part_3.pdf", mime="application/pdf")

        except Exception as e:
            diag_status = "Error Occurred"
            diag_errors.append(str(e))
            st.error(f"ప్రాసెసింగ్ లోపం: {e}")

    # డయాగ్నోస్టిక్స్ ప్యానెల్
    st.markdown("---")
    with st.expander("🛠️ సిస్టమ్ డయాగ్నోస్టిక్స్ (System Diagnostics)"):
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("ఫైల్ స్థితి", diag_status)
        d_col2.metric("మొత్తం పేజీలు", diag_pages)
        d_col3.metric("ఫైల్ సైజు", f"{diag_size_mb:.2f} MB")
        d_col4.metric("రెండర్ సమయం", f"{diag_render_time:.2f} సెకన్లు")

        if diag_errors:
            st.error("ఎర్రర్ వివరాలు:")
            for err in diag_errors:
                st.code(err)
        else:
            st.success("✅ పిడిఎఫ్ ఇంజిన్ సాధారణంగా పనిచేస్తోంది.")

# -------------------------------------------------------------
# TAB 2: PDF మెర్జర్ (బహుళ ఫైళ్లను కలపడం)
# -------------------------------------------------------------
with tab2:
    st.subheader("📑 PDF Merger (కలపడం)")
    st.caption("రెండు లేదా అంతకంటే ఎక్కువ PDF ఫైళ్లను అప్‌లోడ్ చేసి ఒకే ఫైల్‌గా కలపండి.")

    merge_files = st.file_uploader(
        "కలపాల్సిన PDF ఫైళ్లను ఎంచుకోండి (ఒకేసారి ఎన్ని ఫైళ్లయినా ఎంచుకోవచ్చు)", 
        type=["pdf"], 
        accept_multiple_files=True, 
        key="merge_upload"
    )

    if merge_files:
        st.write(f"మొత్తం ఎంచుకున్న ఫైళ్లు: **{len(merge_files)}**")
        
        # ఎంచుకున్న ఫైళ్ల జాబితా చూపించడం
        for idx, f in enumerate(merge_files):
            st.write(f"{idx + 1}. 📄 {f.name} ({len(f.getvalue()) / 1024:.1f} KB)")

        if st.button("🔗 Merge All PDFs", key="btn_merge_action"):
            merger = PdfWriter()
            total_merged_pages = 0
            
            for f in merge_files:
                r = PdfReader(f)
                total_merged_pages += len(r.pages)
                for page in r.pages:
                    merger.add_page(page)

            merged_output = io.BytesIO()
            merger.write(merged_output)
            merged_output.seek(0)

            st.success(f"విజయవంతంగా కలిసింది! మొత్తం పేజీలు: **{total_merged_pages}**")
            st.download_button(
                label="📥 Download Merged PDF",
                data=merged_output,
                file_name="DocuFlow_Merged.pdf",
                mime="application/pdf"
            )

# -------------------------------------------------------------
# TAB 3: మల్టీ-లాంగ్వేజ్ టెక్స్ట్ ఎక్స్‌ట్రాక్టర్
# -------------------------------------------------------------
with tab3:
    st.subheader("🌐 Multi-Language Text Extractor")
    uploaded_lang_file = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="lang_upload")

    if uploaded_lang_file is not None:
        reader = PdfReader(uploaded_lang_file)
        all_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                all_text += t + "\n\n"

        paragraphs = all_text.split("\n\n")
        lang1_text, lang2_text, lang3_text = [], [], []

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
                except:
                    pass

        st.success("విభజన పూర్తయింది!")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("తెలుగు (Telugu)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang1_text[:3]), height=150, key="v_te")
            st.download_button("Download Telugu Text", data="\n\n".join(lang1_text), file_name="telugu.txt", mime="text/plain")
        with col2:
            st.subheader("ఇంగ్లీష్ (English)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang2_text[:3]), height=150, key="v_en")
            st.download_button("Download English Text", data="\n\n".join(lang2_text), file_name="english.txt", mime="text/plain")
        with col3:
            st.subheader("హిందీ / ఇతర (Hindi)")
            st.text_area("ప్రివ్యూ", "\n\n".join(lang3_text[:3]), height=150, key="v_hi")
            st.download_button("Download Hindi Text", data="\n\n".join(lang3_text), file_name="hindi.txt", mime="text/plain")
