import streamlit as st
from pypdf import PdfReader
import pypdfium2 as pdfium
from langdetect import detect
import io
import time
import pdf_engine as engine

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | All-in-One PDF Suite")
st.caption("లైవ్ వ్యూయర్, స్ప్లిట్టర్, రొటేటర్, వాటర్‌మార్క్, మెర్జర్, లాక్ & అన్‌లాక్ మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్టర్.")

tab1, tab2, tab3, tab4 = st.tabs([
    "👁️ Live Visual Studio (Split, Rotate & Watermark)", 
    "📑 PDF Merger (కలపడం)", 
    "🔒 & 🔓 Lock / Unlock (పాస్‌వర్డ్ సెక్యూరిటీ)",
    "🌐 Text Extractor (టెక్స్ట్ వేరు చేయడం)"
])

# -------------------------------------------------------------
# TAB 1: లైవ్ విజువల్ స్టూడియో (Preview, Split, Rotate, Watermark)
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
            
            # పేజీ ఎంపిక
            p_curr = st.number_input("ప్రస్తుతం చూస్తున్న పేజీ సంఖ్య (Select Page):", min_value=1, max_value=total_p, value=1, key="main_p_num")

            # 3 రకాల టూల్స్ ఎంపిక కోసం Sub-Tabs
            tool_choice = st.radio(
                "మీరు ఏమి చేయాలనుకుంటున్నారు?",
                ["✂️ Split (విడదీయడం)", "🔄 Rotate (పేజీలు తిప్పడం)", "💧 Watermark (ముద్ర వేయడం)"],
                horizontal=True
            )

            # ---------------- 1. SPLIT OPTIONS ----------------
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

            # ---------------- 2. ROTATE OPTIONS ----------------
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

            # ---------------- 3. WATERMARK OPTIONS ----------------
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

        # ---------------- LIVE PREVIEW RENDERING (LEFT COLUMN) ----------------
        with col_l:
            try:
                # టూల్ ఆధారంగా ప్రివ్యూ ఎఫెక్ట్స్ లెక్కించడం
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

# ---------------- TAB 2: Merger ----------------
with tab2:
    st.subheader("📑 PDF Merger (కలపడం)")
    st.caption("రెండు లేదా అంతకంటే ఎక్కువ PDF ఫైళ్లను అప్‌లోడ్ చేసి ఒకే ఫైల్‌గా కలపండి.")
    m_files = st.file_uploader("కలపాల్సిన PDF ఫైళ్లు:", type=["pdf"], accept_multiple_files=True, key="m_u_tab2")
    if m_files and st.button("🔗 Merge All PDFs", key="btn_merge_tab2"):
        out, total = engine.merge_pdf_files(m_files)
        st.balloons()
        st.success(f"విజయవంతంగా కలిసింది! మొత్తం పేజీలు: {total}")
        st.download_button("📥 Download Merged PDF", out, "DocuFlow_Merged.pdf", "application/pdf")

# ---------------- TAB 3: Lock / Unlock ----------------
with tab3:
    st.subheader("🔒 & 🔓 PDF Security (లాక్ & అన్‌లాక్)")
    sec_act = st.radio("ఆప్షన్ ఎంచుకోండి:", ["🔒 పాస్‌వర్డ్ సెట్ చేయడం (Lock PDF)", "🔓 పాస్‌వర్డ్ తీసివేయడం (Unlock PDF)"], horizontal=True, key="sec_act_tab3")
    
    if sec_act == "🔒 పాస్‌వర్డ్ సెట్ చేయడం (Lock PDF)":
        l_f = st.file_uploader("లాక్ చేయాల్సిన PDF:", type=["pdf"], key="l_u_tab3")
        if l_f:
            f_b = l_f.name.rsplit(".", 1)[0]
            p1, p2 = st.columns(2)
            pwd1 = p1.text_input("పాస్‌వర్డ్ నమోదు చేయండి:", type="password", key="p1_tab3")
            pwd2 = p2.text_input("పాస్‌వర్డ్‌ను ధృవీకరించండి:", type="password", key="p2_tab3")
            if st.button("🔒 Set Password", key="btn_lock_tab3"):
                if pwd1 and pwd1 == pwd2:
                    out = engine.lock_pdf(l_f, pwd1)
                    st.balloons()
                    st.success("✅ విజయవంతంగా లాక్ చేయబడింది!")
                    st.download_button("📥 Download Protected PDF", out, f"Protected_{f_b}.pdf", "application/pdf")
                else:
                    st.error("రెండు పాస్‌వర్డ్‌లు సరిపోలలేదు.")
    else:
        u_f = st.file_uploader("పాస్‌వర్డ్ ఉన్న PDF:", type=["pdf"], key="u_u_tab3")
        if u_f:
            f_b = u_f.name.rsplit(".", 1)[0]
            cur_pwd = st.text_input("ప్రస్తుత పాస్‌వర్డ్ నమోదు చేయండి:", type="password", key="u_p_tab3")
            if st.button("🔓 Unlock PDF", key="btn_unlock_tab3") and cur_pwd:
                out, status = engine.unlock_pdf(u_f, cur_pwd)
                if status == "SUCCESS":
                    st.balloons()
                    st.success("✅ విజయవంతంగా అన్‌లాక్ చేయబడింది!")
                    st.download_button("📥 Download Unlocked PDF", out, f"Unlocked_{f_b}.pdf", "application/pdf")
                elif status == "WRONG_PASSWORD":
                    st.error("❌ తప్పు పాస్‌వర్డ్! దయచేసి సరైన పాస్‌వర్డ్ ఇవ్వండి.")
                else:
                    st.info("ఈ PDFకి ఎలాంటి పాస్‌వర్డ్ లేదు.")

# ---------------- TAB 4: Multi-Lang Extractor ----------------
with tab4:
    st.subheader("🌐 Multi-Language Text Extractor")
    lang_f = st.file_uploader("PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="lang_u_tab4")
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
