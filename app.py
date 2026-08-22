import streamlit as st
from pypdf import PdfReader
import pypdfium2 as pdfium
from langdetect import detect
import io
import pdf_engine as engine
import media_engine as media_eng

st.set_page_config(page_title="DocuFlow Studio Pro", page_icon="📄", layout="wide")

# Modern Corporate Styling
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-card {
        background: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 DocuFlow Studio Pro")
st.caption("✨ All-in-One Enterprise PDF & Media Engine | 100% Client-Side & Private")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "👁️ Live Visual Studio", 
    "📑 Merge & ZIP", 
    "🖼️ Image ↔ PDF",
    "🎬 Media ↔ Video/Audio",
    "🔢 Page Numbering",
    "🗜️ PDF Compressor",
    "🗑️ Delete / Reorder",
    "🔒 Security & Text"
])

# ---------------- TAB 1: Live Visual Studio ----------------
with tab1:
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.subheader("👁️ Live Visual Studio")
        u_pdf = st.file_uploader("PDF ఫైల్‌ను అప్‌లోడ్ చేయండి", type=["pdf"], key="main_studio_upload")

    if u_pdf is not None:
        pdf_bytes = u_pdf.getvalue()
        base_name = u_pdf.name.rsplit(".", 1)[0]
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_p = len(reader.pages)

        with col_r:
            st.success(f"డాక్యుమెంట్: **{u_pdf.name}** | మొత్తం పేజీలు: **{total_p}**")
            p_curr = st.number_input("చూస్తున్న పేజీ (Page):", min_value=1, max_value=total_p, value=1, key="main_p_num")

            tool_choice = st.radio("టూల్ ఎంచుకోండి:", ["✂️ Split", "🔄 Rotate", "💧 Watermark"], horizontal=True)

            if tool_choice == "✂️ Split":
                st.write("---")
                mode = st.radio("పద్ధతి:", ["1. కస్టమ్ రేంజ్", "2. మల్టిపుల్ రేంజెస్", "3. ఫిక్స్‌డ్ గ్రూప్స్", "4. అన్ని పేజీలు విడివిడిగా"], key="split_mode_sel")
                if mode == "1. కస్టమ్ రేంజ్":
                    c1, c2 = st.columns(2)
                    sp = c1.number_input("నుండి", 1, total_p, 1)
                    ep = c2.number_input("వరకు", sp, total_p, min(sp+1, total_p))
                    if st.button("✂️ Generate Single Cut PDF"):
                        out = engine.split_single_range(reader, sp, ep)
                        st.balloons()
                        st.download_button(f"📥 Download Cut PDF", out, f"{base_name}_Pages_{sp}_to_{ep}.pdf", "application/pdf")
                elif mode == "2. మల్టిపుల్ రేంజెస్":
                    r_in = st.text_input("రేంజ్‌లు (ఉదా: 1-2, 3-5):", value="1-2, 3-5")
                    if st.button("✂️ Split Custom Ranges"):
                        out = engine.split_custom_ranges_zip(reader, r_in, base_name, total_p)
                        st.balloons()
                        st.download_button("📥 Download ZIP", out, f"{base_name}_Custom_Split.zip", "application/zip")
                elif mode == "3. ఫిక్స్‌డ్ గ్రూప్స్":
                    c_size = st.number_input("ప్రతి PDFలో పేజీలు:", 1, total_p, 2)
                    if st.button("✂️ Split by Groups"):
                        out = engine.split_fixed_chunks_zip(reader, c_size, base_name, total_p)
                        st.balloons()
                        st.download_button("📥 Download Groups ZIP", out, f"{base_name}_Groups_{c_size}.zip", "application/zip")
                elif mode == "4. అన్ని పేజీలు విడివిడిగా":
                    if st.button("✂️ Split All Pages"):
                        out = engine.split_all_single_pages_zip(reader, base_name)
                        st.balloons()
                        st.download_button("📥 Download All Pages ZIP", out, f"{base_name}_All_Pages.zip", "application/zip")

            elif tool_choice == "🔄 Rotate":
                st.write("---")
                rot_mode = st.radio("పరిధి:", ["ఈ పేజీ మాత్రమే (Current Page)", "అన్ని పేజీలు (All Pages)"], horizontal=True)
                angle_choice = st.selectbox("కోణం:", [0, 90, 180, 270], format_func=lambda x: f"{x}° క్లాక్‌వైజ్" if x != 0 else "0° (యథావిధిగా)")
                if st.button("🔄 Rotate PDF"):
                    out = engine.rotate_pdf_pages(pdf_bytes, rot_mode, p_curr, angle_choice)
                    st.balloons()
                    st.download_button("📥 Download Rotated PDF", out, f"Rotated_{base_name}.pdf", "application/pdf")

            elif tool_choice == "💧 Watermark":
                st.write("---")
                wm_text = st.text_input("వాటర్‌మార్క్ టెక్స్ట్:", value="CONFIDENTIAL")
                wm_pos = st.selectbox("స్థానం:", [
                    "Center Diagonal (మధ్యలో - 45° వాలుగా)",
                    "Center Straight (మధ్యలో - నిలువు/అడ్డం 0°)",
                    "Top-Left (ఎగువ ఎడమ)", "Top-Right (ఎగువ కుడి)",
                    "Bottom-Left (దిగువ ఎడమ)", "Bottom-Right (దిగువ కుడి)"
                ])
                c_op, c_fs = st.columns(2)
                opacity = c_op.slider("పారదర్శకత:", 0.05, 0.9, 0.25, 0.05)
                f_size = c_fs.slider("సైజు:", 16, 72, 36)
                wm_target_mode = st.radio("పేజీలు:", ["అన్ని పేజీలకు", "ఎంచుకున్న పేజీలకు"], horizontal=True)
                custom_pages_str = ""
                if wm_target_mode == "ఎంచుకున్న పేజీలకు":
                    custom_pages_str = st.text_input("పేజీ సంఖ్యలు (ఉదా: 1, 3, 5-10):", value="1, 3")
                if st.button("💧 Apply Watermark"):
                    t_set = engine.parse_page_numbers(custom_pages_str, total_p) if wm_target_mode == "ఎంచుకున్న పేజీలకు" else None
                    out = engine.apply_advanced_watermark(pdf_bytes, wm_text, t_set, wm_pos, opacity, f_size)
                    st.balloons()
                    st.download_button("📥 Download Watermarked PDF", out, f"Watermarked_{base_name}.pdf", "application/pdf")

        with col_l:
            try:
                eff_angle = angle_choice if tool_choice == "🔄 Rotate" else 0
                eff_wm = (tool_choice == "💧 Watermark")
                eff_wm_txt = wm_text if eff_wm else ""
                eff_wm_pos = wm_pos if eff_wm else "Center Diagonal (మధ్యలో - 45° వాలుగా)"
                eff_op = opacity if eff_wm else 0.25
                eff_fs = f_size if eff_wm else 36

                rendered_bytes = engine.generate_interactive_preview_page(
                    pdf_bytes, p_curr, eff_angle, eff_wm, eff_wm_txt, eff_wm_pos, eff_op, eff_fs
                )
                preview_doc = pdfium.PdfDocument(rendered_bytes)
                st.image(preview_doc.get_page(0).render(scale=2.0).to_pil(), caption=f"పేజీ {p_curr} / {total_p} (లైవ్ ప్రివ్యూ)", use_container_width=True)
            except Exception as e:
                st.error(f"ప్రివ్యూ లోపం: {e}")

# ---------------- TAB 2: Merge & ZIP ----------------
with tab2:
    st.subheader("📑 PDF Merger & Universal ZIP Packer")
    m_files = st.file_uploader("ఫైళ్లను ఎంచుకోండి (PDF, Docs, Images, Code):", accept_multiple_files=True, key="m_u_tab2")
    if m_files:
        st.info(f"మొత్తం ఎంచుకున్న ఫైళ్లు: **{len(m_files)}**")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            if st.button("🔗 1. Merge into Single PDF"):
                try:
                    out_m, t_p = engine.merge_pdf_files(m_files)
                    st.balloons()
                    st.download_button("📥 Download Merged PDF", out_m, "DocuFlow_Merged.pdf", "application/pdf")
                except Exception as e:
                    st.error(f"మెర్జ్ లోపం: {e}")
        with c_m2:
            if st.button("📦 2. Package into ZIP Archive"):
                z_out = engine.zip_multiple_pdf_files(m_files)
                st.balloons()
                st.download_button("📥 Download All Files ZIP", z_out, "DocuFlow_Archive.zip", "application/zip")

# ---------------- TAB 3: Image ↔ PDF ----------------
with tab3:
    st.subheader("🖼️ Image ↔ PDF Converter")
    conv_choice = st.radio("మోడ్:", ["📷 Images to PDF", "📄 PDF to Images"], horizontal=True)
    if conv_choice == "📷 Images to PDF":
        img_files = st.file_uploader("ఫోటోలను ఎంచుకోండి:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if img_files and st.button("📄 Convert Images to PDF"):
            out_pdf = engine.convert_images_to_pdf(img_files)
            st.balloons()
            st.download_button("📥 Download Converted PDF", out_pdf, "Photos_Document.pdf", "application/pdf")
    else:
        pdf_to_img_f = st.file_uploader("PDF ఫైల్:", type=["pdf"])
        if pdf_to_img_f and st.button("📷 Convert PDF to JPGs"):
            b_n = pdf_to_img_f.name.rsplit(".", 1)[0]
            z_out, count = engine.convert_pdf_to_images_zip(pdf_to_img_f.getvalue(), b_n)
            st.balloons()
            st.download_button("📥 Download JPGs (ZIP)", z_out, f"{b_n}_Images.zip", "application/zip")

# ---------------- TAB 4: Media ↔ Video & Audio ----------------
with tab4:
    st.subheader("🎬 Media ↔ PDF & Audio Slideshow")
    m_dir = st.radio("కన్వర్షన్:", ["🎬 Video/GIF టు PDF (Extract Storyboard)", "🎥 PDF టు MP4 Video / Audio Slideshow"], horizontal=True)
    
    if m_dir == "🎬 Video/GIF టు PDF (Extract Storyboard)":
        media_f = st.file_uploader("వీడియో లేదా GIF ఫైల్ (Max 50MB):", type=["mp4", "mov", "avi", "mkv", "gif"])
        if media_f:
            mb = len(media_f.getvalue()) / (1024 * 1024)
            if mb > 50.0:
                st.error("ఫైల్ సైజు 50MB కంటే తక్కువ ఉండాలి.")
            else:
                ext = media_f.name.rsplit(".", 1)[-1].lower()
                b_name = media_f.name.rsplit(".", 1)[0]
                if ext == "gif":
                    f_sk = st.slider("ఫ్రేమ్ స్కిప్:", 1, 10, 1)
                    if st.button("🎬 Convert GIF to PDF"):
                        out, cnt = media_eng.process_gif_to_pdf(media_f, f_sk)
                        st.balloons()
                        st.download_button("📥 Download PDF", out, f"{b_name}_Storyboard.pdf", "application/pdf")
                else:
                    iv = st.selectbox("ఫ్రేమ్ సమయం:", [0.5, 1.0, 2.0, 5.0], index=1)
                    if st.button("🎬 Convert Video to PDF"):
                        out, cnt, dur = media_eng.process_video_to_pdf(media_f, iv)
                        st.balloons()
                        st.download_button("📥 Download PDF Notes", out, f"{b_name}_Notes.pdf", "application/pdf")
    else:
        pdf_f = st.file_uploader("వీడియోగా మార్చాల్సిన PDF ఫైల్:", type=["pdf"], key="pdf_vid_u")
        if pdf_f:
            p_bname = pdf_f.name.rsplit(".", 1)[0]
            sec_p = st.slider("ప్రతి పేజీ వ్యవధి (సెకన్లు):", 0.5, 5.0, 2.0, 0.5)
            
            st.markdown("#### 🎵 ఆడియో జోడించడం (Optional Voiceover / Music)")
            aud_file = st.file_uploader("ఆడియో ఫైల్ (MP3 / WAV):", type=["mp3", "wav"], key="aud_u")
            
            if aud_file:
                st.audio(aud_file, format="audio/mp3")
                
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                if st.button("🎞️ Convert to Animated GIF"):
                    g_out, p_cnt = media_eng.convert_pdf_to_animated_gif(pdf_f.getvalue(), sec_p)
                    st.balloons()
                    st.download_button("📥 Download GIF", g_out, f"{p_bname}.gif", "image/gif")
            with c_v2:
                if st.button("🎥 Generate MP4 Video with Audio"):
                    with st.spinner("వీడియో మరియు ఆడియో అనుసంధానించబడుతున్నాయి..."):
                        a_bytes = aud_file.getvalue() if aud_file else None
                        a_ext = aud_file.name.rsplit(".", 1)[-1].lower() if aud_file else "mp3"
                        v_out, p_cnt = media_eng.convert_pdf_to_mp4_video(pdf_f.getvalue(), sec_p, a_bytes, a_ext)
                        st.balloons()
                        st.download_button("📥 Download Video (MP4)", v_out, f"{p_bname}_Video.mp4", "video/mp4")

# ---------------- TAB 5: Page Numbering ----------------
with tab5:
    st.subheader("🔢 PDF Page Numbering (పేజీ సంఖ్యలు ముద్రించడం)")
    st.caption("PDF లోని ప్రతి పేజీపై ఆటోమేటిక్‌గా పేజీ సంఖ్యలను వేయండి.")
    num_f = st.file_uploader("PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="num_f_u")
    if num_f:
        b_n = num_f.name.rsplit(".", 1)[0]
        c_n1, c_n2 = st.columns(2)
        p_style = c_n1.selectbox("నంబర్ స్టైల్:", ["Page X of Y", "Page X (కేవలం నంబర్)"])
        p_pos = c_n2.selectbox("స్థానం:", ["Bottom-Center", "Bottom-Right", "Bottom-Left", "Top-Right", "Top-Center"])
        f_sz = st.slider("నంబర్ ఫాంట్ సైజు:", 8, 16, 10)
        
        if st.button("🔢 Apply Page Numbers"):
            out = engine.add_page_numbers(num_f.getvalue(), p_style, p_pos, f_sz)
            st.balloons()
            st.success("✅ పేజీ నంబర్లు విజయవంతంగా ముద్రించబడ్డాయి!")
            st.download_button("📥 Download Numbered PDF", out, f"Numbered_{b_n}.pdf", "application/pdf")

# ---------------- TAB 6: PDF Compressor ----------------
with tab6:
    st.subheader("🗜️ PDF File Compressor (సైజు తగ్గించడం)")
    st.caption("PDF నాణ్యత దెబ్బతినకుండా ఫైల్ సైజును ఆప్టిమైజ్ చేసి తగ్గించండి.")
    comp_f = st.file_uploader("కంప్రెస్ చేయాల్సిన PDF:", type=["pdf"], key="comp_f_u")
    if comp_f:
        orig_mb = len(comp_f.getvalue()) / (1024 * 1024)
        st.info(f"ప్రస్తుత ఫైల్ సైజు: **{orig_mb:.2f} MB**")
        q_val = st.slider("నాణ్యత స్థాయి (Quality Level):", 30, 90, 65, 5, help="తక్కువ క్వాలిటీ = చాలా చిన్న ఫైల్ సైజు")
        
        if st.button("🗜️ Compress PDF"):
            with st.spinner("PDF ఆప్టిమైజ్ అవుతోంది..."):
                c_out = engine.compress_pdf_file(comp_f.getvalue(), q_val)
                new_mb = len(c_out.getvalue()) / (1024 * 1024)
                saved_pct = max(0, int((orig_mb - new_mb) / orig_mb * 100)) if orig_mb > 0 else 0
                st.balloons()
                st.success(f"✅ కంప్రెషన్ పూర్తయింది! కొత్త సైజు: **{new_mb:.2f} MB** (దాదాపు **{saved_pct}%** తగ్గింది)")
                st.download_button("📥 Download Compressed PDF", c_out, f"Compressed_{comp_f.name}", "application/pdf")

# ---------------- TAB 7: Delete / Reorder ----------------
with tab7:
    st.subheader("🗑️ & 🔀 Delete or Reorder Pages")
    del_file = st.file_uploader("PDF ఫైల్:", type=["pdf"], key="del_reorder_u")
    if del_file:
        del_bytes = del_file.getvalue()
        b_name = del_file.name.rsplit(".", 1)[0]
        r_del = PdfReader(io.BytesIO(del_bytes))
        t_pages = len(r_del.pages)
        st.info(f"మొత్తం పేజీలు: **{t_pages}**")
        p_act = st.radio("ఆప్షన్:", ["🗑️ పేజీలను తొలగించడం", "🔀 వరుస క్రమం మార్చడం"], horizontal=True)
        if p_act == "🗑️ పేజీలను తొలగించడం":
            del_in = st.text_input("డిలీట్ చేయాల్సిన పేజీలు (ఉదా: 2, 5, 8-10):", value="2")
            if st.button("🗑️ Delete Pages"):
                d_set = engine.parse_page_numbers(del_in, t_pages)
                if d_set and len(d_set) < t_pages:
                    out, kept = engine.delete_pdf_pages(del_bytes, d_set)
                    st.balloons()
                    st.download_button("📥 Download Clean PDF", out, f"Clean_{b_name}.pdf", "application/pdf")
        else:
            def_ord = ", ".join(str(i) for i in range(1, t_pages + 1))
            ord_in = st.text_input("కొత్త ఆర్డర్:", value=def_ord)
            if st.button("🔀 Reorder Pages"):
                n_ord = [int(x.strip()) for x in ord_in.split(",") if x.strip()]
                out = engine.reorder_pdf_pages(del_bytes, n_ord)
                st.balloons()
                st.download_button("📥 Download Reordered PDF", out, f"Reordered_{b_name}.pdf", "application/pdf")

# ---------------- TAB 8: Security & Text ----------------
with tab8:
    st.subheader("🔒 Security & 🌐 Multi-Language Text")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown("#### 🔒 Lock / Unlock")
        s_act = st.radio("సెక్యూరిటీ:", ["Lock PDF", "Unlock PDF"], horizontal=True)
        sec_f = st.file_uploader("PDF ఫైల్:", type=["pdf"], key="sec_tab8_u")
        if sec_f:
            pwd = st.text_input("పాస్‌వర్డ్:", type="password", key="sec_p_t8")
            if s_act == "Lock PDF" and st.button("🔒 Set Lock"):
                if pwd:
                    out = engine.lock_pdf(sec_f, pwd)
                    st.download_button("📥 Download Locked PDF", out, f"Protected_{sec_f.name}", "application/pdf")
            elif s_act == "Unlock PDF" and st.button("🔓 Unlock"):
                out, stt = engine.unlock_pdf(sec_f, pwd)
                if stt == "SUCCESS":
                    st.download_button("📥 Download Unlocked PDF", out, f"Unlocked_{sec_f.name}", "application/pdf")
                else:
                    st.error("తప్పు పాస్‌వర్డ్!")

    with c_s2:
        st.markdown("#### 🌐 Text Extractor")
        txt_f = st.file_uploader("టెక్స్ట్ తీయాల్సిన PDF:", type=["pdf"], key="txt_tab8_u")
        if txt_f:
            r = PdfReader(txt_f)
            raw = "\n\n".join([p.extract_text() or "" for p in r.pages])
            te, en, hi = [], [], []
            for p in raw.split("\n\n"):
                ps = p.strip()
                if len(ps) > 5:
                    try:
                        l = detect(ps)
                        if l == 'te': te.append(ps)
                        elif l == 'en': en.append(ps)
                        elif l == 'hi': hi.append(ps)
                    except: pass
            st.download_button("Download Telugu (.txt)", "\n\n".join(te), "telugu.txt")
            st.download_button("Download English (.txt)", "\n\n".join(en), "english.txt")
