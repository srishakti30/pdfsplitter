import streamlit as st
from pypdf import PdfReader
import pypdfium2 as pdfium
from langdetect import detect
import io
import pdf_engine as engine

st.set_page_config(page_title="DocuFlow Studio", page_icon="📄", layout="wide")

st.title("📄 DocuFlow Studio | Ultimate PDF Suite")
st.caption("స్మార్ట్ వ్యూయర్, స్ప్లిట్టర్, మెర్జర్, వాటర్‌మార్క్, రొటేటర్, లాక్ & అన్‌లాక్ మరియు టెక్స్ట్ ఎక్స్‌ట్రాక్టర్.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👁️ & ✂️ Splitter", 
    "📑 Merger", 
    "💧 Watermark",
    "🔄 Page Rotator",
    "🔒 & 🔓 Lock / Unlock",
    "🌐 Text Extractor"
])

# ---------------- TAB 1: Preview & Splitter ----------------
with tab1:
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.subheader("👁️ Live Preview")
        u_pdf = st.file_uploader("PDF అప్‌లోడ్ చేయండి", type=["pdf"], key="split_u")

    if u_pdf:
        pdf_bytes = u_pdf.getvalue()
        base_name = u_pdf.name.rsplit(".", 1)[0]
        pdf_doc = pdfium.PdfDocument(pdf_bytes)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_p = len(reader.pages)

        with col_l:
            p_num = st.number_input("చూడాల్సిన పేజీ:", min_value=1, max_value=total_p, value=1)
            pil_img = pdf_doc.get_page(p_num - 1).render(scale=2.0).to_pil()
            st.image(pil_img, caption=f"పేజీ {p_num} / {total_p}", use_container_width=True)

        with col_r:
            st.subheader("⚙️ Split Settings")
            st.success(f"మొత్తం పేజీలు: **{total_p}**")
            mode = st.radio("పద్ధతి:", [
                "1. కస్టమ్ రేంజ్ (ఒక భాగం)",
                "2. మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)",
                "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు)",
                "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)"
            ])

            if mode == "1. కస్టమ్ రేంజ్ (ఒక భాగం)":
                c1, c2 = st.columns(2)
                sp = c1.number_input("నుండి", 1, total_p, 1)
                ep = c2.number_input("వరకు", sp, total_p, min(sp+1, total_p))
                if st.button("✂️ Generate Single Cut PDF"):
                    out = engine.split_single_range(reader, sp, ep)
                    st.balloons()
                    st.download_button(f"📥 Download {base_name}_Pages_{sp}_{ep}.pdf", out, f"{base_name}_Pages_{sp}_to_{ep}.pdf", "application/pdf")

            elif mode == "2. మల్టిపుల్ రేంజెస్ (కావలసిన భాగాలుగా)":
                st.caption("ఉదా: **1-2, 3-5, 6-10**")
                r_in = st.text_input("రేంజ్‌లు నమోదు చేయండి:", value="1-2, 3-5")
                if st.button("✂️ Split by Custom Ranges"):
                    out = engine.split_custom_ranges_zip(reader, r_in, base_name, total_p)
                    st.balloons()
                    st.download_button("📥 Download ZIP", out, f"{base_name}_Custom_Split.zip", "application/zip")

            elif mode == "3. ఫిక్స్‌డ్ గ్రూప్స్ (ప్రతి N పేజీలకు)":
                c_size = st.number_input("ప్రతి PDFలో పేజీల సంఖ్య:", 1, total_p, 2)
                if st.button("✂️ Split by Chunks"):
                    out = engine.split_fixed_chunks_zip(reader, c_size, base_name, total_p)
                    st.balloons()
                    st.download_button("📥 Download ZIP", out, f"{base_name}_Groups_{c_size}.zip", "application/zip")

            elif mode == "4. ప్రతి పేజీని విడివిడిగా (1 Page = 1 PDF)":
                if st.button("✂️ Split Every Page"):
                    out = engine.split_all_single_pages_zip(reader, base_name)
                    st.balloons()
                    st.download_button("📥 Download All Pages ZIP", out, f"{base_name}_All_Pages.zip", "application/zip")

# ---------------- TAB 2: Merger ----------------
with tab2:
    st.subheader("📑 PDF Merger")
    m_files = st.file_uploader("కలపాల్సిన ఫైళ్లు:", type=["pdf"], accept_multiple_files=True, key="m_u")
    if m_files and st.button("🔗 Merge All PDFs"):
        out, total = engine.merge_pdf_files(m_files)
        st.balloons()
        st.success(f"విజయవంతంగా కలిసింది! మొత్తం పేజీలు: {total}")
        st.download_button("📥 Download Merged PDF", out, "DocuFlow_Merged.pdf", "application/pdf")

# ---------------- TAB 3: Advanced Watermark ----------------
with tab3:
    st.subheader("💧 Advanced PDF Watermark")
    st.caption("అన్ని పేజీలకు లేదా మీరు ఎంచుకున్న పేజీలకు మాత్రమే వాటర్‌మార్క్ మరియు కావలసిన స్థానాన్ని సెట్ చేయండి.")
    
    wm_file = st.file_uploader("PDF అప్‌లోడ్ చేయండి", type=["pdf"], key="wm_u")
    if wm_file:
        b_name = wm_file.name.rsplit(".", 1)[0]
        r_temp = PdfReader(wm_file)
        t_pages = len(r_temp.pages)
        st.info(f"మొత్తం పేజీల సంఖ్య: **{t_pages}**")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            wm_text = st.text_input("వాటర్‌మార్క్ టెక్స్ట్:", value="CONFIDENTIAL")
            wm_target_mode = st.radio("ఏ పేజీలకు వాటర్‌మార్క్ కావాలి?", ["అన్ని పేజీలకు (All Pages)", "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)"], horizontal=True)
            custom_pages_str = ""
            if wm_target_mode == "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)":
                custom_pages_str = st.text_input("పేజీ నంబర్లు నమోదు చేయండి (ఉదా: 1, 3, 5-10):", value="1, 3")

        with col_w2:
            wm_pos = st.selectbox("వాటర్‌మార్క్ స్థానం (Position):", [
                "Center Diagonal (మధ్యలో - 45° వాలుగా)",
                "Center Straight (మధ్యలో - నిలువు/అడ్డం 0°)",
                "Top-Left (ఎగువ ఎడమ)",
                "Top-Right (ఎగువ కుడి)",
                "Bottom-Left (దిగువ ఎడమ)",
                "Bottom-Right (దిగువ కుడి)"
            ])
            c_op, c_fs = st.columns(2)
            opacity = c_op.slider("పారదర్శకత (Opacity):", 0.05, 0.9, 0.20, 0.05)
            f_size = c_fs.slider("ఫాంట్ సైజు:", 16, 72, 36)

        if st.button("💧 Apply Custom Watermark", key="btn_wm_apply"):
            target_set = None
            if wm_target_mode == "ఎంచుకున్న పేజీలకు మాత్రమే (Custom Pages)":
                target_set = engine.parse_page_numbers(custom_pages_str, t_pages)
                if not target_set:
                    st.warning("దయచేసి సరైన పేజీ నంబర్లు నమోదు చేయండి.")
            
            if wm_target_mode == "అన్ని పేజీలకు (All Pages)" or target_set:
                out = engine.apply_advanced_watermark(wm_file, wm_text, target_set, wm_pos, opacity, f_size)
                st.balloons()
                st.success("✅ వాటర్‌మార్క్ విజయవంతంగా అప్లై చేయబడింది!")
                st.download_button(f"📥 Download Watermarked_{b_name}.pdf", out, f"Watermarked_{b_name}.pdf", "application/pdf")

# ---------------- TAB 4: Page Rotator with Live Preview ----------------
with tab4:
    st.subheader("🔄 PDF Page Rotator (లైవ్ ప్రివ్యూతో)")
    st.caption("పేజీలు ఎలా తిరుగుతున్నాయో స్క్రీన్‌పై ప్రత్యక్షంగా చూస్తూ రొటేట్ చేయండి.")
    
    rot_file = st.file_uploader("తిప్పాల్సిన PDF అప్‌లోడ్ చేయండి", type=["pdf"], key="rot_u")
    if rot_file:
        r_base = rot_file.name.rsplit(".", 1)[0]
        rot_bytes = rot_file.getvalue()
        rot_doc = pdfium.PdfDocument(rot_bytes)
        t_pages = len(rot_doc)

        col_rot_l, col_rot_r = st.columns([1.2, 1])

        with col_rot_r:
            st.subheader("⚙️ Rotation Settings")
            st.info(f"మొత్తం పేజీలు: **{t_pages}**")
            rot_mode = st.radio("రొటేట్ పరిధి:", ["అన్ని పేజీలు (All Pages)", "నిర్దిష్ట పేజీ మాత్రమే (Single Page)"], horizontal=True, key="rot_mode_sel")
            
            p_to_view = 1
            if rot_mode == "నిర్దిష్ట పేజీ మాత్రమే (Single Page)":
                p_to_view = st.number_input("ఏ పేజీని తిప్పాలి?", min_value=1, max_value=t_pages, value=1, key="rot_p_num")
            else:
                p_to_view = st.number_input("ప్రివ్యూ చూడాల్సిన పేజీ:", min_value=1, max_value=t_pages, value=1, key="rot_p_view_all")

            angle_choice = st.selectbox("తిప్పాల్సిన కోణం (Angle):", [90, 180, 270], format_func=lambda x: f"{x}° క్లాక్‌వైజ్", key="rot_angle_sel")

            if st.button("🔄 Rotate & Save PDF", key="btn_do_rotate"):
                out = engine.rotate_pdf_pages(rot_file, rot_mode, p_to_view, angle_choice)
                st.balloons()
                st.success("✅ పేజీలు విజయవంతంగా తిప్పబడ్డాయి!")
                st.download_button(f"📥 Download Rotated_{r_base}.pdf", out, f"Rotated_{r_base}.pdf", "application/pdf")

        with col_rot_l:
            st.subheader("👁️ Live Rotation Preview")
            # ప్రివ్యూ కోసం ఎంచుకున్న కోణంలో తిప్పి చూపించడం
            page_obj = rot_doc.get_page(p_to_view - 1)
            pil_rot_img = page_obj.render(scale=2.0, rotation=angle_choice).to_pil()
            st.image(pil_rot_img, caption=f"పేజీ {p_to_view} (రొటేట్ అయిన తర్వాత {angle_choice}° వ్యూ)", use_container_width=True)

# ---------------- TAB 5: Lock / Unlock ----------------
with tab5:
    st.subheader("🔒 & 🔓 PDF Security (లాక్ & అన్‌లాక్)")
    sec_act = st.radio("ఆప్షన్:", ["🔒 లాక్ చేయడం (Set Password)", "🔓 అన్‌లాక్ చేయడం (Remove Password)"], horizontal=True)
    
    if sec_act == "🔒 లాక్ చేయడం (Set Password)":
        l_f = st.file_uploader("లాక్ చేయాల్సిన PDF:", type=["pdf"], key="l_u")
        if l_f:
            f_b = l_f.name.rsplit(".", 1)[0]
            p1, p2 = st.columns(2)
            pwd1 = p1.text_input("పాస్‌వర్డ్:", type="password", key="p1")
            pwd2 = p2.text_input("ధృవీకరణ:", type="password", key="p2")
            if st.button("🔒 Set Password"):
                if pwd1 and pwd1 == pwd2:
                    out = engine.lock_pdf(l_f, pwd1)
                    st.balloons()
                    st.success("✅ లాక్ చేయబడింది!")
                    st.download_button("📥 Download Protected PDF", out, f"Protected_{f_b}.pdf", "application/pdf")
                else:
                    st.error("పాస్‌వర్డ్ సరిపోలలేదు.")
    else:
        u_f = st.file_uploader("పాస్‌వర్డ్ ఉన్న PDF:", type=["pdf"], key="u_u")
        if u_f:
            f_b = u_f.name.rsplit(".", 1)[0]
            cur_pwd = st.text_input("ప్రస్తుత పాస్‌వర్డ్:", type="password", key="u_p")
            if st.button("🔓 Unlock PDF") and cur_pwd:
                out, status = engine.unlock_pdf(u_f, cur_pwd)
                if status == "SUCCESS":
                    st.balloons()
                    st.success("✅ అన్‌లాక్ చేయబడింది!")
                    st.download_button("📥 Download Unlocked PDF", out, f"Unlocked_{f_b}.pdf", "application/pdf")
                elif status == "WRONG_PASSWORD":
                    st.error("❌ తప్పు పాస్‌వర్డ్!")
                else:
                    st.info("ఈ PDFకి పాస్‌వర్డ్ లేదు.")

# ---------------- TAB 6: Multi-Lang Extractor ----------------
with tab6:
    st.subheader("🌐 Multi-Language Text Extractor")
    lang_f = st.file_uploader("PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="lang_u")
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
        c1.text_area("తెలుగు", "\n\n".join(te[:3]), height=150)
        c1.download_button("Download Telugu", "\n\n".join(te), "telugu.txt")
        c2.text_area("English", "\n\n".join(en[:3]), height=150)
        c2.download_button("Download English", "\n\n".join(en), "english.txt")
        c3.text_area("Hindi", "\n\n".join(hi[:3]), height=150)
        c3.download_button("Download Hindi", "\n\n".join(hi), "hindi.txt")
