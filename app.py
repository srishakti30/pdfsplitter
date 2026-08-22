import streamlit as st
from pypdf import PdfReader
import pypdfium2 as pdfium
from langdetect import detect
import io
import pdf_engine as engine

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Ultimate PDF Suite")
st.caption("స్మార్ట్ వ్యూయర్, స్ప్లిట్టర్, రొటేటర్, వాటర్‌మార్క్, మెర్జర్, జిప్ ప్యాకర్, ఇమేజ్ కన్వర్టర్, పేజ్ డిలీట్/రీఆర్డర్, లాక్ & అన్‌లాక్.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👁️ Live Visual Studio", 
    "📑 PDF Merger & ZIP Packer", 
    "🖼️ Image ↔ PDF Converter",
    "🗑️ & 🔀 Delete / Reorder Pages",
    "🔒 & 🔓 Lock / Unlock",
    "🌐 Text Extractor"
])

# -------------------------------------------------------------
# TAB 1: Live Visual Studio (Split, Rotate, Watermark)
# -------------------------------------------------------------
with tab1:
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.subheader("👁️ Live Interactive Preview")
        u_pdf = st.file_uploader("PDF ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type=["pdf"], key="main_studio_upload")

    if u_pdf is not None:
        pdf_bytes = u_pdf.getvalue()
        base_name = u_pdf.name.rsplit(".", 1)[0]
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_p = len(reader.pages)

        with col_r:
            st.success(f"డాక్యుమెంట్: **{u_pdf.name}** | మొత్తం పేజీలు: **{total_p}**")
            p_curr = st.number_input("ప్రస్తుతం చూస్తున్న పేజీ సంఖ్య (Page Viewer):", min_value=1, max_value=total_p, value=1, key="main_p_num")

            tool_choice = st.radio(
                "మీరు ఏమి చేయాలనుకుంటున్నారు?",
                ["✂️ Split (విడదీయడం)", "🔄 Rotate (పేజీలు తిప్పడం)", "💧 Watermark (ముద్ర వేయడం)"],
                horizontal=True
            )

            # 1. SPLIT
            if tool_choice == "✂️ Split (విడదీయడం)":
                st.write("---")
                st.markdown("#### ✂️ PDF విభజన సెట్టింగ్స్")
                mode = st.radio("పద్ధతిని ఎంచుకోండి:", [
                    "1. కస్టమ్ రేంజ్ (ఒక భాగం)",
                    "2. మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)",
                    "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు)",
                    "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)"
                ], key="split_mode_sel")

                if mode == "1. కస్టమ్ రేంజ్ (ఒక భాగం)":
                    c1, c2 = st.columns(2)
                    sp = c1.number_input("నుండి (Start)", 1, total_p, 1)
                    ep = c2.number_input("వరకు (End)", sp, total_p, min(sp+1, total_p))
                    if st.button("✂️ Generate Cut PDF", key="btn_sp_custom"):
                        out = engine.split_single_range(reader, sp, ep)
                        st.balloons()
                        st.download_button(f"📥 Download {base_name}_Pages_{sp}_{ep}.pdf", out, f"{base_name}_Pages_{sp}_to_{ep}.pdf", "application/pdf")

                elif mode == "2. మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)":
                    st.caption("ఉదాహరణకు: **1-2, 3-5, 6-10**")
                    r_in = st.text_input("రేంజ్‌లు నమోదు చేయండి:", value="1-2, 3-5", key="m_range_input")
                    if st.button("✂️ Split by Custom Ranges", key="btn_sp_multi"):
                        out = engine.split_custom_ranges_zip(reader, r_in, base_name, total_p)
                        st.balloons()
                        st.download_button("📥 Download All Parts (ZIP)", out, f"{base_name}_Custom_Split.zip", "application/zip")

                elif mode == "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు)":
                    c_size = st.number_input("ప్రతి PDFలో ఎన్ని పేజీలు ఉండాలి?", 1, total_p, 2, key="c_size_input")
                    if st.button("✂️ Split by Groups", key="btn_sp_chunks"):
                        out = engine.split_fixed_chunks_zip(reader, c_size, base_name, total_p)
                        st.balloons()
                        st.download_button("📥 Download Groups (ZIP)", out, f"{base_name}_Groups_{c_size}.zip", "application/zip")

                elif mode == "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)":
                    if st.button("✂️ Split Every Single Page", key="btn_sp_all"):
                        out = engine.split_all_single_pages_zip(reader, base_name)
                        st.balloons()
                        st.download_button("📥 Download All Pages (ZIP)", out, f"{base_name}_All_Pages.zip", "application/zip")

            # 2. ROTATE
            elif tool_choice == "🔄 Rotate (పేజీలు తిప్పడం)":
                st.write("---")
                st.markdown("#### 🔄 పేజీ రొటేషన్ సెట్టింగ్స్")
                rot_mode = st.radio("రొటేట్ చేయాల్సిన పరిధి:", ["ఈ పేజీ మాత్రమే (Current Page)", "అన్ని పేజీలు (All Pages)"], horizontal=True, key="rot_scope")
                angle_choice = st.selectbox("తిప్పాల్సిన కోణం (Angle):", [0, 90, 180, 270], format_func=lambda x: f"{x}° (యథావిధిగా)" if x == 0 else f"{x}° క్లాక్‌వైజ్", key="rot_angle_interactive")

                if st.button("🔄 Rotate & Download PDF", key="btn_do_rot_apply"):
                    out = engine.rotate_pdf_pages(pdf_bytes, rot_mode, p_curr, angle_choice)
                    st.balloons()
                    st.success("✅ పేజీలు విజయవంతంగా తిప్పబడ్డాయి!")
                    st.download_button(f"📥 Download Rotated_{base_name}.pdf", out, f"Rotated_{base_name}.pdf", "application/pdf")

            # 3. WATERMARK
            elif tool_choice == "💧 Watermark (ముద్ర వేయడం)":
                st.write("---")
                st.markdown("#### 💧 వాటర్‌మార్క్ సెట్టింగ్స్")
                wm_text = st.text_input("వాటర్‌మార్క్ టెక్స్ట్:", value="CONFIDENTIAL", key="wm_text_inter")
                wm_pos = st.selectbox("వాటర్‌మార్క్ స్థానం (Position):", [
                    "Center Diagonal (మధ్యలో - 45° వాలుగా)",
                    "Center Straight (మధ్యలో - నిలువు/అడ్డం 0°)",
                    "Top-Left (ఎగువ ఎడమ)",
                    "Top-Right (ఎగువ కుడి)",
                    "Bottom-Left (దిగువ ఎడమ)",
                    "Bottom-Right (దిగువ కుడి)"
                ], key="wm_pos_inter")

                c_op, c_fs = st.columns(2)
                opacity = c_op.slider("పారదర్శకత (Opacity):", 0.05, 0.9, 0.25, 0.05, key="wm_op_inter")
                f_size = c_fs.slider("ఫాంట్ సైజు:", 16, 72, 36, key="wm_fs_inter")

                st.write("---")
                wm_target_mode = st.radio("ఏ పేజీలకు అప్లై చేయాలి?", ["అన్ని పేజీలకు (All Pages)", "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)"], horizontal=True, key="wm_scope_inter")
                custom_pages_str = ""
                if wm_target_mode == "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)":
                    custom_pages_str = st.text_input("పేజీ నంబర్లు నమోదు చేయండి (ఉదా: 1, 3, 5-10):", value="1, 3", key="wm_custom_p_inter")

                if st.button("💧 Apply Watermark & Download PDF", key="btn_do_wm_apply"):
                    target_set = None
                    if wm_target_mode == "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)":
                        target_set = engine.parse_page_numbers(custom_pages_str, total_p)
                        if not target_set:
                            st.warning("దయచేసి సరైన పేజీ నంబర్లు నమోదు చేయండి.")
                    
                    if wm_target_mode == "అన్ని పేజీలకు (All Pages)" or target_set:
                        out = engine.apply_advanced_watermark(pdf_bytes, wm_text, target_set, wm_pos, opacity, f_size)
                        st.balloons()
                        st.success("✅ వాటర్‌మార్క్ విజయవంతంగా అప్లై చేయబడింది!")
                        st.download_button(f"📥 Download Watermarked_{base_name}.pdf", out, f"Watermarked_{base_name}.pdf", "application/pdf")

        # LIVE PREVIEW RENDERING
        with col_l:
            try:
                eff_angle = angle_choice if tool_choice == "🔄 Rotate (పేజీలు తిప్పడం)" else 0
                eff_wm = (tool_choice == "💧 Watermark (ముద్ర వేయడం)")
                eff_wm_txt = wm_text if eff_wm else ""
                eff_wm_pos = wm_pos if eff_wm else "Center Diagonal (మధ్యలో - 45° వాలుగా)"
                eff_op = opacity if eff_wm else 0.25
                eff_fs = f_size if eff_wm else 36

                rendered_pdf_bytes = engine.generate_interactive_preview_page(
                    pdf_bytes, p_curr, eff_angle, eff_wm, eff_wm_txt, eff_wm_pos, eff_op, eff_fs
                )
                preview_doc = pdfium.PdfDocument(rendered_pdf_bytes)
                pil_img = preview_doc.get_page(0).render(scale=2.0).to_pil()
                st.image(pil_img, caption=f"పేజీ {p_curr} / {total_p} (లైవ్ ప్రివ్యూ)", use_container_width=True)
            except Exception as e:
                st.error(f"ప్రివ్యూ రెండరింగ్ లోపం: {e}")

# -------------------------------------------------------------
# TAB 2: PDF Merger & ZIP Packer (DUAL ACTION)
# -------------------------------------------------------------
with tab2:
    st.subheader("📑 PDF Merger & ZIP Package")
    st.caption("బహుళ PDF ఫైళ్లను అప్‌లోడ్ చేసి ఒకే ఫైల్‌గా కలపండి లేదా విడివిడిగా ఒకే సురక్షిత ZIP ఫైల్‌గా ప్యాక్ చేయండి.")
    
    m_files = st.file_uploader("కలపాల్సిన లేదా ప్యాక్ చేయాల్సిన PDF ఫైళ్లు:", accept_multiple_files=True, key="m_u_tab2")
    if m_files:
        st.info(f"మొత్తం ఎంచుకున్న ఫైళ్లు: **{len(m_files)}**")
        for idx, f in enumerate(m_files):
            st.write(f"{idx + 1}. 📄 {f.name} ({len(f.getvalue()) / 1024:.1f} KB)")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🔗 1. Merge into Single PDF", key="btn_merge_single_tab2"):
                out_m, total_pages_m = engine.merge_pdf_files(m_files)
                st.balloons()
                st.success(f"✅ అన్ని ఫైళ్లు ఒకే డాక్యుమెంట్‌గా మారాయి! మొత్తం పేజీలు: **{total_pages_m}**")
                st.download_button("📥 Download Merged PDF", out_m, "DocuFlow_Merged.pdf", "application/pdf")

        with col_m2:
            if st.button("📦 2. Package into Single ZIP Archive", key="btn_pack_zip_tab2"):
                zip_all_out = engine.zip_multiple_pdf_files(m_files)
                st.balloons()
                st.success(f"✅ మొత్తం **{len(m_files)}** ఫైళ్లు ఒకే ZIP ఆర్కైవ్‌గా ప్యాక్ అయ్యాయి!")
                st.download_button("📥 Download All PDFs ZIP", zip_all_out, "DocuFlow_PDF_Archive.zip", "application/zip")

# -------------------------------------------------------------
# TAB 3: Image ↔ PDF Converter
# -------------------------------------------------------------
with tab3:
    st.subheader("🖼️ Image ↔ PDF Converter")
    st.caption("చిత్రాలను (Photos) PDFగా మార్చండి లేదా PDF లోని పేజీలను హై-క్వాలిటీ చిత్రాలుగా మార్చండి.")

    conv_choice = st.radio("కన్వర్టర్ మోడ్ ఎంచుకోండి:", ["📷 Images to PDF (ఫోటోల నుండి PDF)", "📄 PDF to Images (PDF నుండి ఫోటోలు)"], horizontal=True)

    if conv_choice == "📷 Images to PDF (ఫోటోల నుండి PDF)":
        st.write("---")
        img_files = st.file_uploader("ఫోటోలను ఎంచుకోండి (JPG, PNG):", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="img_to_pdf_u")
        if img_files:
            st.info(f"ఎంచుకున్న ఫోటోల సంఖ్య: **{len(img_files)}**")
            if st.button("📄 Convert Images to Single PDF", key="btn_img_pdf"):
                out_pdf = engine.convert_images_to_pdf(img_files)
                st.balloons()
                st.success("✅ విజయవంతంగా PDFగా మారింది!")
                st.download_button("📥 Download Converted PDF", out_pdf, "Photos_Document.pdf", "application/pdf")

    else:
        st.write("---")
        pdf_to_img_f = st.file_uploader("PDF ఫైల్‌ను అప్‌లోడ్ చేయండి:", type=["pdf"], key="pdf_to_img_u")
        if pdf_to_img_f:
            b_name = pdf_to_img_f.name.rsplit(".", 1)[0]
            if st.button("📷 Convert PDF Pages to JPG Images", key="btn_pdf_img"):
                zip_out, count = engine.convert_pdf_to_images_zip(pdf_to_img_f.getvalue(), b_name)
                st.balloons()
                st.success(f"✅ మొత్తం **{count}** పేజీలు JPG చిత్రాలుగా మారాయి!")
                st.download_button(f"📥 Download All Images (ZIP)", zip_out, f"{b_name}_JPG_Images.zip", "application/zip")

# -------------------------------------------------------------
# TAB 4: Delete & Reorder Pages
# -------------------------------------------------------------
with tab4:
    st.subheader("🗑️ & 🔀 Delete or Reorder Pages")
    st.caption("అనవసరమైన పేజీలను తొలగించండి లేదా పేజీల క్రమాన్ని మార్చండి.")

    del_file = st.file_uploader("PDF ఫైల్‌ను అప్‌లోడ్ చేయండి:", type=["pdf"], key="del_reorder_u")
    if del_file:
        del_bytes = del_file.getvalue()
        b_name = del_file.name.rsplit(".", 1)[0]
        r_del = PdfReader(io.BytesIO(del_bytes))
        t_del_pages = len(r_del.pages)
        st.info(f"మొత్తం పేజీలు: **{t_del_pages}**")

        page_action = st.radio("ఏమి చేయాలనుకుంటున్నారు?", ["🗑️ పేజీలను తొలగించడం (Delete Pages)", "🔀 వరుస క్రమం మార్చడం (Reorder Pages)"], horizontal=True)

        if page_action == "🗑️ పేజీలను తొలగించడం (Delete Pages)":
            st.write("---")
            st.caption("తొలగించాల్సిన పేజీ నంబర్లు నమోదు చేయండి (ఉదా: **2, 5, 8-10**):")
            del_input = st.text_input("డిలీట్ చేయాల్సిన పేజీలు:", value="2", key="del_pages_txt")

            if st.button("🗑️ Delete Pages & Generate PDF", key="btn_do_delete"):
                del_set = engine.parse_page_numbers(del_input, t_del_pages)
                if not del_set:
                    st.warning("దయచేసి సరైన పేజీ నంబర్లు ఇవ్వండి.")
                elif len(del_set) >= t_del_pages:
                    st.error("అన్ని పేజీలను తొలగించలేరు. కనీసం ఒక పేజీ ఉండాలి.")
                else:
                    out, kept = engine.delete_pdf_pages(del_bytes, del_set)
                    st.balloons()
                    st.success(f"✅ పేజీలు తొలగించబడ్డాయి! మిగిలిన పేజీలు: **{kept}**")
                    st.download_button(f"📥 Download Clean_{b_name}.pdf", out, f"Clean_{b_name}.pdf", "application/pdf")

        else:
            st.write("---")
            st.caption(f"కొత్త వరుస క్రమం ఇవ్వండి (1 నుండి {t_del_pages} వరకు గల నంబర్లతో):")
            default_order = ", ".join(str(i) for i in range(1, t_del_pages + 1))
            order_input = st.text_input("కొత్త ఆర్డర్ (ఉదా: 3, 1, 2...):", value=default_order, key="reorder_txt")

            if st.button("🔀 Reorder & Save PDF", key="btn_do_reorder"):
                try:
                    new_order = [int(x.strip()) for x in order_input.split(",") if x.strip()]
                    out = engine.reorder_pdf_pages(del_bytes, new_order)
                    st.balloons()
                    st.success("✅ పేజీల క్రమం విజయవంతంగా మార్చబడింది!")
                    st.download_button(f"📥 Download Reordered_{b_name}.pdf", out, f"Reordered_{b_name}.pdf", "application/pdf")
                except Exception as e:
                    st.error(f"ఆర్డర్ లోపం: {e}")

# -------------------------------------------------------------
# TAB 5: Lock / Unlock
# -------------------------------------------------------------
with tab5:
    st.subheader("🔒 & 🔓 PDF Security (లాక్ & అన్‌లాక్)")
    sec_act = st.radio("ఆప్షన్ ఎంచుకోండి:", ["🔒 పాస్‌వర్డ్ సెట్ చేయడం (Lock PDF)", "🔓 పాస్‌వర్డ్ తీసివేయడం (Unlock PDF)"], horizontal=True, key="sec_act_tab5")
    
    if sec_act == "🔒 పాస్‌వర్డ్ సెట్ చేయడం (Lock PDF)":
        l_f = st.file_uploader("లాక్ చేయాల్సిన PDF:", type=["pdf"], key="l_u_tab5")
        if l_f:
            f_b = l_f.name.rsplit(".", 1)[0]
            p1, p2 = st.columns(2)
            pwd1 = p1.text_input("పాస్‌వర్డ్ నమోదు చేయండి:", type="password", key="p1_tab5")
            pwd2 = p2.text_input("పాస్‌వర్డ్‌ను ధృవీకరించండి:", type="password", key="p2_tab5")
            if st.button("🔒 Set Password", key="btn_lock_tab5"):
                if pwd1 and pwd1 == pwd2:
                    out = engine.lock_pdf(l_f, pwd1)
                    st.balloons()
                    st.success("✅ విజయవంతంగా లాక్ చేయబడింది!")
                    st.download_button("📥 Download Protected PDF", out, f"Protected_{f_b}.pdf", "application/pdf")
                else:
                    st.error("రెండు పాస్‌వర్డ్‌లు సరిపోలలేదు.")
    else:
        u_f = st.file_uploader("పాస్‌వర్డ్ ఉన్న PDF:", type=["pdf"], key="u_u_tab5")
        if u_f:
            f_b = u_f.name.rsplit(".", 1)[0]
            cur_pwd = st.text_input("ప్రస్తుత పాస్‌వర్డ్ నమోదు చేయండి:", type="password", key="u_p_tab5")
            if st.button("🔓 Unlock PDF", key="btn_unlock_tab5") and cur_pwd:
                out, status = engine.unlock_pdf(u_f, cur_pwd)
                if status == "SUCCESS":
                    st.balloons()
                    st.success("✅ విజయవంతంగా అన్‌లాక్ చేయబడింది!")
                    st.download_button("📥 Download Unlocked PDF", out, f"Unlocked_{f_b}.pdf", "application/pdf")
                elif status == "WRONG_PASSWORD":
                    st.error("❌ తప్పు పాస్‌వర్డ్! దయచేసి సరైన పాస్‌వర్డ్ ఇవ్వండి.")
                else:
                    st.info("ఈ PDFకి ఎలాంటి పాస్‌వర్డ్ లేదు.")

# -------------------------------------------------------------
# TAB 6: Multi-Lang Extractor
# -------------------------------------------------------------
with tab6:
    st.subheader("🌐 Multi-Language Text Extractor")
    lang_f = st.file_uploader("PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="lang_u_tab6")
    if lang_f:
        r = PdfReader(lang_f)
        txt = "\n\n".join([p.extract_text() or "" for p in r.pages])
        te, en, hi = [], [], []
        for p in txt.split("\n\n"):
            p_s = p.strip()
            if len(p_s) > 5:
                try:
                    l = detect(p_s)
                    if l == 'te': te.append(p_s)
                    elif l == 'en': en.append(p_s)
                    elif l == 'hi': hi.append(p_s)
                except: pass
        c1, c2, c3 = st.columns(3)
        c1.text_area("తెలుగు (Telugu)", "\n\n".join(te[:3]), height=150)
        c1.download_button("Download Telugu Text", "\n\n".join(te), "telugu.txt")
        c2.text_area("ఇంగ్లీష్ (English)", "\n\n".join(en[:3]), height=150)
        c2.download_button("Download English Text", "\n\n".join(en), "english.txt")
        c3.text_area("హిందీ / ఇతర (Hindi)", "\n\n".join(hi[:3]), height=150)
        c3.download_button("Download Hindi Text", "\n\n".join(hi), "hindi.txt")
