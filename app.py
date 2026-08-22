import streamlit as st
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
from langdetect import detect
from PIL import Image
import io
import zipfile
import time

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Smart PDF Suite")
st.caption("PDF వ్యూయర్, అడ్వాన్స్‌డ్ స్ప్లిట్టర్, మెర్జర్, పాస్‌వర్డ్ సెక్యూరిటీ మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్టర్.")

tab1, tab2, tab3, tab4 = st.tabs([
    "👁️ & ✂️ PDF Preview & Splitter", 
    "📑 PDF Merger (కలపడం)", 
    "🔒 PDF Lock (పాస్‌వర్డ్ సెట్ చేయడం)",
    "🌐 Multi-Language Text Extractor"
])

# -------------------------------------------------------------
# TAB 1: PDF ప్రివ్యూ & అడ్వాన్స్‌డ్ స్ప్లిట్టింగ్
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
            base_name = uploaded_pdf.name.rsplit(".", 1)[0]
            
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
                    [
                        "1. కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)",
                        "2. కస్టమ్ మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)",
                        "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు ఒక PDF)",
                        "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)"
                    ]
                )

                # ఆప్షన్ 1: కస్టమ్ రేంజ్
                if split_mode == "1. కస్టమ్ పేజీ రేంజ్ (ఒక భాగం)":
                    c1, c2 = st.columns(2)
                    with c1:
                        start_p = st.number_input("నుండి (Start Page)", min_value=1, max_value=total_pages, value=1)
                    with c2:
                        end_p = st.number_input("వరకు (End Page)", min_value=start_p, max_value=total_pages, value=min(start_p+1, total_pages))

                    if st.button("✂️ Generate Single Cut PDF", key="btn_custom"):
                        writer = PdfWriter()
                        for p in range(start_p - 1, end_p):
                            writer.add_page(reader.pages[p])
                        out_buffer = io.BytesIO()
                        writer.write(out_buffer)
                        out_buffer.seek(0)
                        
                        st.balloons()
                        st.download_button(
                            label=f"📥 Download {base_name}_Pages_{start_p}_to_{end_p}.pdf",
                            data=out_buffer,
                            file_name=f"{base_name}_Pages_{start_p}_to_{end_p}.pdf",
                            mime="application/pdf"
                        )

                # ఆప్షన్ 2: కస్టమ్ మల్టిపుల్ రేంజెస్
                elif split_mode == "2. కస్టమ్ మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)":
                    st.caption("ఉదాహరణకు: **1-2, 3-5, 6-10** లేదా **1, 3, 5-8** అని ఇవ్వండి.")
                    ranges_input = st.text_input("పేజీ రేంజ్‌లు టైప్ చేయండి:", value="1-2, 3-5")

                    if st.button("✂️ Split by Custom Ranges", key="btn_multi_range"):
                        zip_buffer = io.BytesIO()
                        ranges = [r.strip() for r in ranges_input.split(",") if r.strip()]
                        
                        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                            for idx, r in enumerate(ranges):
                                try:
                                    if "-" in r:
                                        sp, ep = map(int, r.split("-"))
                                    else:
                                        sp = ep = int(r)

                                    if 1 <= sp <= ep <= total_pages:
                                        writer = PdfWriter()
                                        for p in range(sp - 1, ep):
                                            writer.add_page(reader.pages[p])
                                        
                                        p_buf = io.BytesIO()
                                        writer.write(p_buf)
                                        p_buf.seek(0)
                                        
                                        file_title = f"{base_name}_Part_{idx+1}_Pages_{sp}_to_{ep}.pdf"
                                        zip_file.writestr(file_title, p_buf.getvalue())
                                except:
                                    pass

                        zip_buffer.seek(0)
                        st.balloons()
                        st.download_button(
                            label="📥 Download All Parts (ZIP)",
                            data=zip_buffer,
                            file_name=f"{base_name}_Custom_Split.zip",
                            mime="application/zip"
                        )

                # ఆప్షన్ 3: ఫిక్స్‌డ్ గ్రూప్స్
                elif split_mode == "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు ఒక PDF)":
                    chunk_size = st.number_input("ప్రతి PDFలో ఎన్ని పేజీలు ఉండాలి?", min_value=1, max_value=total_pages, value=2)
                    total_chunks = (total_pages + chunk_size - 1) // chunk_size
                    st.info(f"మొత్తం **{total_chunks}** PDF ఫైళ్లు తయారవుతాయి.")

                    if st.button("✂️ Split by Fixed Chunks", key="btn_chunks"):
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
                        st.balloons()
                        st.download_button(
                            label=f"📥 Download {total_chunks} PDF Files (ZIP)",
                            data=zip_buffer,
                            file_name=f"{base_name}_Groups_of_{chunk_size}.zip",
                            mime="application/zip"
                        )

                # ఆప్షన్ 4: ప్రతి పేజీని విడివిడిగా
                elif split_mode == "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)":
                    st.info(f"ఈ PDFలోని అన్ని **{total_pages}** పేజీలు విడివిడి PDFలుగా మారి ఒకే ZIP ఫైల్‌గా వస్తాయి.")
                    
                    if st.button("✂️ Split Every Single Page", key="btn_all_pages"):
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
                        st.balloons()
                        st.download_button(
                            label=f"📥 Download All {total_pages} Pages (ZIP)",
                            data=zip_buffer,
                            file_name=f"{base_name}_All_Pages.zip",
                            mime="application/zip"
                        )

        except Exception as e:
            diag_status = "Error Occurred"
            diag_errors.append(str(e))
            st.error(f"ప్రాసెసింగ్ లోపం: {e}")

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
# TAB 2: PDF మెర్జర్
# -------------------------------------------------------------
with tab2:
    st.subheader("📑 PDF Merger (కలపడం)")
    st.caption("రెండు లేదా అంతకంటే ఎక్కువ PDF ఫైళ్లను అప్‌లోడ్ చేసి ఒకే ఫైల్‌గా కలపండి.")

    merge_files = st.file_uploader(
        "కలపాల్సిన PDF ఫైళ్లను ఎంచుకోండి", 
        type=["pdf"], 
        accept_multiple_files=True, 
        key="merge_upload"
    )

    if merge_files:
        st.write(f"మొత్తం ఎంచుకున్న ఫైళ్లు: **{len(merge_files)}**")
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

            st.balloons()
            st.success(f"విజయవంతంగా కలిసింది! మొత్తం పేజీలు: **{total_merged_pages}**")
            st.download_button(
                label="📥 Download Merged PDF",
                data=merged_output,
                file_name="DocuFlow_Merged.pdf",
                mime="application/pdf"
            )

# -------------------------------------------------------------
# TAB 3: PDF లాక్ / పాస్‌వర్డ్ సెక్యూరిటీ
# -------------------------------------------------------------
with tab3:
    st.subheader("🔒 PDF Password Protection (లాక్ చేయడం)")
    st.caption("మీ సున్నితమైన PDF డాక్యుమెంట్లకు బలమైన పాస్‌వర్డ్‌ను సెట్ చేసి భద్రపరచండి.")

    lock_file = st.file_uploader("పాస్‌వర్డ్ పెట్టాల్సిన PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="lock_upload")

    if lock_file is not None:
        file_base = lock_file.name.rsplit(".", 1)[0]
        col_pass1, col_pass2 = st.columns(2)
        
        with col_pass1:
            user_password = st.text_input("కొత్త పాస్‌వర్డ్ టైప్ చేయండి:", type="password", key="pwd_input")
        with col_pass2:
            confirm_password = st.text_input("పాస్‌వర్డ్‌ను మళ్లీ టైప్ చేయండి (Confirm):", type="password", key="pwd_confirm")

        if st.button("🔒 Set Password & Protect PDF", key="btn_lock_pdf"):
            if not user_password:
                st.warning("దయచేసి పాస్‌వర్డ్ నమోదు చేయండి.")
            elif user_password != confirm_password:
                st.error("రెండు పాస్‌వర్డ్‌లు సరిపోలడం లేదు (Passwords do not match).")
            else:
                reader = PdfReader(lock_file)
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                # పాస్‌వర్డ్ ఎన్‌క్రిప్షన్ (128-bit AES సెక్యూరిటీ)
                writer.encrypt(user_password)

                locked_buffer = io.BytesIO()
                writer.write(locked_buffer)
                locked_buffer.seek(0)

                st.balloons()
                st.success("✅ PDFకి పాస్‌వర్డ్ విజయవంతంగా సెట్ చేయబడింది!")
                st.download_button(
                    label=f"📥 Download Protected_{file_base}.pdf",
                    data=locked_buffer,
                    file_name=f"Protected_{file_base}.pdf",
                    mime="application/pdf"
                )

# -------------------------------------------------------------
# TAB 4: మల్టీ-లాంగ్వేజ్ టెక్స్ట్ ఎక్స్‌ట్రాక్టర్
# -------------------------------------------------------------
with tab4:
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
