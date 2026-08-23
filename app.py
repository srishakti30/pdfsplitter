import streamlit as st
from pypdf import PdfReader
import pypdfium2 as pdfium
from langdetect import detect
import io
import time
import base64
from PIL import Image

# Custom Modular Engines
import pdf_engine as engine
import media_engine as media_eng
import pdf_editor_engine as editor_eng
import enhancer_engine as enhance_eng

st.set_page_config(page_title="DocuFlow Studio Pro", page_icon="📄", layout="wide", initial_sidebar_state="collapsed")

# Modern Styling & Realistic On-Image Laser Scan Effect
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
    .tool-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        min-height: 125px;
        margin-bottom: 12px;
    }
    .tool-card h4 { margin-top: 0px; color: #38bdf8; }
    .tool-card p { font-size: 13px; color: #94a3b8; margin-bottom: 0px; }

    /* Laser Scanner Container directly on the image */
    .photo-scan-container {
        position: relative;
        display: inline-block;
        width: 100%;
        max-width: 550px;
        border-radius: 10px;
        overflow: hidden;
        border: 2px solid #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .photo-scan-container img {
        width: 100%;
        height: auto;
        display: block;
    }
    .laser-beam {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: #38bdf8;
        box-shadow: 0 0 15px #38bdf8, 0 0 25px #00f0ff, 0 0 35px #ffffff;
        animation: laserScan 1.6s infinite alternate ease-in-out;
    }
    @keyframes laserScan {
        0% { top: 0%; opacity: 0.8; }
        100% { top: 97%; opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

def set_page(p_name):
    st.session_state.active_page = p_name

st.title("📄 DocuFlow Studio Pro")
st.caption("✨ Enterprise PDF & Media Engine | 100% Client-Side & Private")

# ---------------- HOME DASHBOARD (11 POWER TOOLS) ----------------
if st.session_state.active_page == "Home":
    st.markdown("### 🧰 All Tools Dashboard")
    
    tools_list = [
        {"id": "visual", "icon": "👁️", "title": "Live Visual Studio", "desc": "పేజీ ప్రివ్యూతో స్ప్లిట్, రొటేట్, వాటర్‌మార్క్"},
        {"id": "enhancer", "icon": "🪄", "title": "Photo & Art Restorer", "desc": "పాత ఫోటోల రీస్టోరేషన్, లేజర్ స్కానర్ & HD క్లారిటీ"},
        {"id": "editor", "icon": "📝", "title": "PDF Content Editor", "desc": "లేఅవుట్ పాడవకుండా టెక్స్ట్ రీప్లేస్, స్టాంపులు"},
        {"id": "pdf2word", "icon": "📄", "title": "PDF ➜ Word (.docx)", "desc": "PDFని నేరుగా Microsoft Wordగా మార్చడం"},
        {"id": "merge", "icon": "📑", "title": "Merge & ZIP", "desc": "PDF ఫైళ్ల అనుసంధానం & ZIP ప్యాకర్"},
        {"id": "img2pdf", "icon": "🖼️", "title": "Image ↔ PDF", "desc": "ఫోటోల నుండి PDF & PDF నుండి JPGs"},
        {"id": "media", "icon": "🎬", "title": "Media ↔ Video/Audio", "desc": "వీడియో నోట్స్ & ఆడియో స్లైడ్‌షోలు"},
        {"id": "num", "icon": "🔢", "title": "Page Numbering", "desc": "ఆటోమేటిక్ పేజీ సంఖ్యల ముద్రణ"},
        {"id": "compress", "icon": "🗜️", "title": "PDF Compressor", "desc": "నాణ్యత తగ్గకుండా ఫైల్ సైజు కుదింపు"},
        {"id": "reorder", "icon": "🗑️", "title": "Delete / Reorder", "desc": "పేజీల తొలగింపు & ఆర్డర్ మార్పిడి"},
        {"id": "security", "icon": "🔒", "title": "Security & Text", "desc": "పాస్‌వర్డ్ లాక్/అన్‌లాక్ & టెక్స్ట్ ఎక్స్‌ట్రాక్టర్"}
    ]

    for row_start in range(0, len(tools_list), 4):
        cols = st.columns(4)
        for i in range(4):
            idx = row_start + i
            if idx < len(tools_list):
                t = tools_list[idx]
                with cols[i]:
                    st.markdown(f"""
                    <div class="tool-card">
                        <h4>{t['icon']} {t['title']}</h4>
                        <p>{t['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {t['title']}", key=f"btn_{t['id']}"):
                        set_page(t['id'])
                        st.rerun()

# ---------------- TOOL SCREENS ----------------
else:
    c_back, _ = st.columns([1, 4])
    if c_back.button("⬅️ Back to All Tools (హోమ్ పేజీకి వెళ్లు)"):
        set_page("Home")
        st.rerun()
    st.write("---")

    # 1. Live Visual Studio
    if st.session_state.active_page == "visual":
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

    # 2. 🪄 Photo & Vintage Art Restorer (MOBILE-FRIENDLY & DIRECT LASER SCAN)
    elif st.session_state.active_page == "enhancer":
        st.subheader("🪄 Vintage Photo Restoration & Laser Scanner Studio")
        st.caption("పాతకాలం నాటి ఫోటోలు, మచ్చలు పడిన చిత్రాలు, ముఖాల HD క్లారిటీ మరియు పెన్సిల్ స్కెచ్ ఆర్ట్‌ను లైవ్ లేజర్ స్కానింగ్‌తో పునరుద్ధరించండి.")
        
        e_img = st.file_uploader("ఫోటోను అప్‌లోడ్ చేయండి (JPG / PNG):", type=["jpg", "jpeg", "png"], key="enh_img_u")
        
        if e_img:
            img_bytes = e_img.getvalue()
            b_name_i = e_img.name.rsplit(".", 1)[0]
            base64_orig = base64.b64encode(img_bytes).decode("utf-8")
            
            # Vertical Mobile-Optimized Flow
            st.markdown("##### 🖼️ ఒరిజినల్ ఫోటో (Input)")
            scan_container = st.empty()
            
            # Show original photo inside standard view
            scan_container.markdown(f"""
            <div class="photo-scan-container">
                <img src="data:image/jpeg;base64,{base64_orig}" />
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            col_ctrl1, col_ctrl2 = st.columns([1.2, 1.1])
            with col_ctrl1:
                enh_mode = st.selectbox("పునరుద్ధరణ మోడ్ (Restoration Mode):", [
                    "3. 💎 True HD Super-Clarity & Smart Sharpness (ముఖాలు స్పష్టంగా & అల్ట్రా HD)",
                    "1. 🎨 Pencil Sketch & Line Art (చేత్తో గీసిన పెన్సిల్ ఆర్ట్)",
                    "2. 🧹 B&W Scratch & Spot Cleaner (మచ్చలు, గీతలు తొలగింపు)",
                    "4. 🌈 Soft Warm / Vintage Colorize Tint (పాత ఫోటోకు లైట్ కలర్ టచ్)"
                ])
            with col_ctrl2:
                st.write("")
                st.write("")
                scan_btn = st.button("🚀 Run Live Laser Scan & Restore Photo")
                
            if scan_btn:
                # 1. Show Laser Beam Scanning Directly on the uploaded photo
                scan_container.markdown(f"""
                <div class="photo-scan-container">
                    <div class="laser-beam"></div>
                    <img src="data:image/jpeg;base64,{base64_orig}" />
                </div>
                """, unsafe_allow_html=True)
                
                # Smooth Progress Bar Simulation
                prog = st.progress(0)
                for p in range(1, 101, 15):
                    time.sleep(0.12)
                    prog.progress(p)
                
                # 2. Process Enhanced Photo
                out_img_buf, pil_res_img = enhance_eng.restore_and_enhance_photo(img_bytes, enh_mode)
                
                # Reset original scan container
                scan_container.markdown(f"""
                <div class="photo-scan-container" style="border-color: #10b981;">
                    <img src="data:image/jpeg;base64,{base64_orig}" />
                </div>
                """, unsafe_allow_html=True)
                prog.empty()
                
                # 3. Display Restored Output Right Below
                st.write("---")
                st.markdown("##### ✨ ప్రాసెస్ చేసిన అద్భుతమైన ఫలితం (Restored Result)")
                st.image(pil_res_img, caption="✅ స్కాన్ పూర్తయింది - మీ ఫోటో సిద్ధంగా ఉంది!", use_container_width=True)
                st.balloons()
                
                st.download_button(
                    "📥 Download Restored HD Photo (.jpg)",
                    out_img_buf.getvalue(),
                    f"Restored_{b_name_i}.jpg",
                    "image/jpeg"
                )

    # 3. PDF Content Editor
    elif st.session_state.active_page == "editor":
        st.subheader("📝 Smart PDF Layout & Advanced In-Place Studio")
        st.caption("టేబుల్స్, గడులు, గుర్తులు పాడవకుండా టెక్స్ట్‌ను మార్చండి, స్టాంపులు వేయండి, సెన్సిటివ్ డేటాను మాస్క్ చేయండి.")
        
        ed_pdf = st.file_uploader("ఎడిట్ చేయాల్సిన PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="ed_pdf_u")
        if ed_pdf:
            ed_bytes = ed_pdf.getvalue()
            reader_check = PdfReader(io.BytesIO(ed_bytes))
            
            if reader_check.is_encrypted:
                st.warning("⚠️ ఈ PDF పాస్‌వర్డ్‌తో లాక్ చేయబడి ఉంది. దయచేసి 'Security & Text' సెక్షన్‌లో దీనిని అన్‌లాక్ చేసి అప్‌లోడ్ చేయండి.")
            else:
                t_ed_pages = len(reader_check.pages)
                
                if "current_edited_pdf" not in st.session_state or st.session_state.get("orig_name") != ed_pdf.name:
                    st.session_state.current_edited_pdf = ed_bytes
                    st.session_state.orig_name = ed_pdf.name

                sub_tool = st.radio(
                    "ఎడిటింగ్ టూల్ ఎంచుకోండి:", 
                    ["1. 🔍 Single Text Replace (సింగిల్ వాక్యం మార్పు)", 
                     "2. ⚡ Bulk Find & Replace (మొత్తం PDF లో ఒకేసారి)", 
                     "3. 🛡️ Data Redaction (ఆధార్/ఫోన్ నంబర్ మాస్కింగ్)", 
                     "4. 🏷️ Digital Stamp (స్టాంపులు)", 
                     "5. ✍️ Image / Signature Overlay (సంతకం చేర్చడం)"], 
                    horizontal=True
                )
                st.write("---")

                c_ed_l, c_ed_r = st.columns([1.1, 1.2])

                with c_ed_l:
                    if sub_tool.startswith("1."):
                        ed_page_num = st.number_input("ఎంచుకున్న పేజీ సంఖ్య (Page Number):", 1, t_ed_pages, 1, key="ed_p_sel1")
                        blocks = editor_eng.extract_page_text_blocks(st.session_state.current_edited_pdf, ed_page_num)
                        
                        if blocks:
                            block_options = [f"{i+1}. {b['text'][:45]}..." if len(b['text']) > 45 else f"{i+1}. {b['text']}" for i, b in enumerate(blocks)]
                            sel_block_idx = st.selectbox("మార్చాల్సిన వాక్యాన్ని ఎంచుకోండి:", range(len(blocks)), format_func=lambda x: block_options[x])
                            default_find = blocks[sel_block_idx]['text']
                            
                            find_val = st.text_area("అసలు టెక్స్ట్ (Original):", value=default_find, height=70)
                            replace_val = st.text_area("కొత్త టెక్స్ట్ / అనువాదం (New Text):", value=default_find, height=70)
                            
                            c1, c2 = st.columns(2)
                            new_fs = c1.slider("ఫాంట్ సైజు:", 8, 24, 11)
                            auto_fit_toggle = c2.checkbox("ఆటో-ఫిట్ స్కేలర్ (Auto-Fit)", value=True)
                            
                            if st.button("✨ Apply In-Place Replace"):
                                st.session_state.current_edited_pdf = editor_eng.replace_text_in_pdf(
                                    st.session_state.current_edited_pdf, ed_page_num, find_val, replace_val, font_size=new_fs, auto_fit=auto_fit_toggle
                                ).getvalue()
                                st.success("✅ రీప్లేస్మెంట్ విజయవంతమైంది!")
                                st.balloons()
                        else:
                            st.info("ఈ పేజీలో టెక్స్ట్ కనుగొనబడలేదు.")

                    elif sub_tool.startswith("2."):
                        b_find = st.text_input("వెతకాల్సిన పదం (Find across All Pages):", value="")
                        b_repl = st.text_input("రీప్లేస్ చేయాల్సిన కొత్త పదం (Replace With):", value="")
                        b_fs = st.slider("ఫాంట్ సైజు:", 8, 20, 11)
                        if st.button("⚡ Replace in Entire PDF"):
                            if b_find:
                                st.session_state.current_edited_pdf = editor_eng.bulk_find_and_replace_pdf(
                                    st.session_state.current_edited_pdf, b_find, b_repl, font_size=b_fs
                                ).getvalue()
                                st.success("✅ మొత్తం PDF లోని అన్ని చోట్లా రీప్లేస్ అయింది!")
                                st.balloons()

                    elif sub_tool.startswith("3."):
                        st.caption("గోప్యంగా ఉంచాల్సిన ఆధార్, పాన్, ఫోన్ నంబర్లు లేదా పేర్లను ఎంటర్ చేయండి.")
                        red_txt = st.text_input("మాస్క్ చేయాల్సిన పదం / నంబర్:", value="")
                        red_col = st.selectbox("మాస్క్ రంగు:", ["నలుపు (Black Mask)", "తెలుపు (White Mask)"])
                        mask_c = (0, 0, 0) if "Black" in red_col else (1, 1, 1)
                        if st.button("🛡️ Apply Security Mask"):
                            if red_txt:
                                st.session_state.current_edited_pdf = editor_eng.redact_sensitive_text(
                                    st.session_state.current_edited_pdf, red_txt, mask_color=mask_c
                                ).getvalue()
                                st.success("✅ డేటా శాశ్వతంగా మాస్క్ చేయబడింది!")
                                st.balloons()

                    elif sub_tool.startswith("4."):
                        ed_page_num = st.number_input("స్టాంప్ వేయాల్సిన పేజీ సంఖ్య:", 1, t_ed_pages, 1, key="ed_p_sel4")
                        st_text = st.selectbox("స్టాంప్ రకం:", ["APPROVED", "VERIFIED", "PAID", "CONFIDENTIAL", "REJECTED"])
                        st_color = st.selectbox("స్టాంప్ రంగు:", ["Green", "Red", "Blue", "Orange"])
                        c_sx, c_sy = st.columns(2)
                        st_x = c_sx.slider("X స్థానం (%):", 5, 90, 70)
                        st_y = c_sy.slider("Y స్థానం (%):", 5, 90, 20)
                        if st.button("🏷️ Apply Digital Stamp"):
                            st.session_state.current_edited_pdf = editor_eng.apply_digital_stamp(
                                st.session_state.current_edited_pdf, ed_page_num, st_text, st_x, st_y, st_color
                            ).getvalue()
                            st.success("✅ స్టాంప్ ముద్రించబడింది!")
                            st.balloons()

                    elif sub_tool.startswith("5."):
                        ed_page_num = st.number_input("సంతకం పెట్టాల్సిన పేజీ సంఖ్య:", 1, t_ed_pages, 1, key="ed_p_sel5")
                        sig_file = st.file_uploader("సంతకం / ఫోటో (PNG / JPG):", type=["png", "jpg", "jpeg"], key="sig_u")
                        c_ix, c_iy = st.columns(2)
                        sig_x = c_ix.slider("X స్థానం (%):", 5, 90, 60)
                        sig_y = c_iy.slider("Y స్థానం (%):", 5, 90, 75)
                        c_iw, c_ih = st.columns(2)
                        sig_w = c_iw.slider("వెడల్పు:", 40, 300, 120)
                        sig_h = c_ih.slider("ఎత్తు:", 20, 200, 60)
                        if sig_file and st.button("✍️ Insert Signature / Image"):
                            st.session_state.current_edited_pdf = editor_eng.insert_image_or_signature(
                                st.session_state.current_edited_pdf, ed_page_num, sig_file.getvalue(), sig_x, sig_y, sig_w, sig_h
                            ).getvalue()
                            st.success("✅ సంతకం ఇన్సర్ట్ చేయబడింది!")
                            st.balloons()

                    st.write("---")
                    st.download_button(
                        "📥 Download Fully Edited PDF",
                        st.session_state.current_edited_pdf,
                        f"Edited_{ed_pdf.name}",
                        "application/pdf"
                    )

                with c_ed_r:
                    st.markdown("#### 👁️ లేఅవుట్ లైవ్ ప్రివ్యూ")
                    active_p = locals().get("ed_page_num", 1)
                    try:
                        p_img = editor_eng.render_page_preview(st.session_state.current_edited_pdf, active_p)
                        st.image(p_img, caption=f"పేజీ {active_p} ప్రివ్యూ (గడులు & చిహ్నాలు రక్షించబడ్డాయి)", use_container_width=True)
                    except Exception as e:
                        st.error(f"ప్రివ్యూ లోపం: {e}")

    # 4. Pure PDF to Word (.docx) Converter
    elif st.session_state.active_page == "pdf2word":
        st.subheader("📄 Accurate PDF to Microsoft Word (.docx) Converter")
        st.caption("టేబుల్స్, గడులు, పారాగ్రాఫ్‌లు, ఇమేజ్‌లు ఏవీ పాడవకుండా PDFని నేరుగా Word డాక్యుమెంట్‌గా మార్చండి (100% ఆఫ్‌లైన్).")
        
        w_pdf_file = st.file_uploader("వర్డ్‌గా మార్చాల్సిన PDF అప్‌లోడ్ చేయండి:", type=["pdf"], key="w_pdf_u")
        if w_pdf_file:
            b_name_w = w_pdf_file.name.rsplit(".", 1)[0]
            st.info(f"ఫైల్: **{w_pdf_file.name}** | పరిమాణం: **{(len(w_pdf_file.getvalue()) / (1024*1024)):.2f} MB**")
            
            if st.button("🚀 Convert to Microsoft Word (.docx)"):
                with st.spinner("PDF లేఅవుట్ & టేబుల్స్ విశ్లేషించబడుతున్నాయి... డాక్యుమెంట్ రీ-కన్‌స్ట్రక్ట్ అవుతోంది..."):
                    try:
                        docx_result_bytes = engine.convert_pdf_to_word_docx(w_pdf_file.getvalue())
                        st.balloons()
                        st.success("✅ విజయవంతంగా Microsoft Word (.docx) గా మార్చబడింది!")
                        st.download_button(
                            "📥 Download Word Document (.docx)",
                            docx_result_bytes,
                            f"{b_name_w}.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as e:
                        st.error(f"కన్వర్షన్ లోపం: {e}")

    # 5. Merge & ZIP
    elif st.session_state.active_page == "merge":
        st.subheader("📑 PDF Merger & Universal ZIP Packer")
        m_files = st.file_uploader("ఫైళ్లను ఎంచుకోండి (PDF, Docs, Images, Code):", accept_multiple_files=True, key="m_u_page")
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

    # 6. Image ↔ PDF
    elif st.session_state.active_page == "img2pdf":
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

    # 7. Media ↔ Video & Audio
    elif st.session_state.active_page == "media":
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

    # 8. Page Numbering
    elif st.session_state.active_page == "num":
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

    # 9. PDF Compressor
    elif st.session_state.active_page == "compress":
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

    # 10. Delete / Reorder
    elif st.session_state.active_page == "reorder":
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

    # 11. Security & Text
    elif st.session_state.active_page == "security":
        st.subheader("🔒 Security & 🌐 Multi-Language Text")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.markdown("#### 🔒 Lock / Unlock")
            s_act = st.radio("సెక్యూరిటీ:", ["Lock PDF", "Unlock PDF"], horizontal=True)
            sec_f = st.file_uploader("PDF ఫైల్:", type=["pdf"], key="sec_tab11_u")
            if sec_f:
                pwd = st.text_input("పాస్‌వర్డ్:", type="password", key="sec_p_t11")
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
            txt_f = st.file_uploader("టెక్స్ట్ తీయాల్సిన PDF:", type=["pdf"], key="txt_tab11_u")
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
