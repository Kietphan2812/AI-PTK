"""
Trang 5: Bộ Tiện Ích AI Nhanh
"""

import os
import streamlit as st
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Tools - AI PTK", page_icon="🔧", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #FB8C00 0%, #E65100 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">🔧 Bộ Tiện Ích AI Thông Minh</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Công cụ nhanh phục vụ học tập và làm việc: Dịch thuật, Viết code, Giải thích thuật toán, Tóm tắt & Sửa văn phạm (Hỗ trợ xuất Word & Excel).</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_export_buttons(text: str, prefix: str):
    """Hiển thị nút tải Word và Excel cho kết quả công cụ."""
    if not text:
        return
    st.write("---")
    try:
        from service_bridge import export_to_docx, export_to_excel
        col_x1, col_x2 = st.columns(2)
        with col_x1:
            docx_bytes = export_to_docx(text, title=f"AI PTK - {prefix}")
            st.download_button(
                label=f"📄 Xuất {prefix} ra Word (.docx)",
                data=docx_bytes,
                file_name=f"{prefix.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_docx_{prefix}",
                use_container_width=True,
            )
        with col_x2:
            xlsx_bytes = export_to_excel(text, title=f"AI PTK - {prefix}")
            st.download_button(
                label=f"📊 Xuất {prefix} ra Excel (.xlsx)",
                data=xlsx_bytes,
                file_name=f"{prefix.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xlsx_{prefix}",
                use_container_width=True,
            )
    except Exception as e:
        st.caption(f"Không thể tạo file xuất: {e}")


tab_trans, tab_codegen, tab_explain, tab_sum, tab_grammar = st.tabs([
    "🌐 Dịch Thuật",
    "💻 Sinh Mã Nguồn",
    "🔍 Giải Thích Code",
    "📑 Tóm Tắt Ý Chính",
    "✏️ Soát Lỗi & Văn Phạm",
])

# 1. Dịch thuật
with tab_trans:
    st.subheader("Dịch thuật chuẩn bản ngữ")
    c1, c2 = st.columns([3, 1])
    with c2:
        target_lang = st.selectbox("Dịch sang ngôn ngữ:", ["English", "Tiếng Việt", "Japanese", "Chinese", "Korean", "French", "German"])
    with c1:
        text_to_translate = st.text_area("Nhập văn bản cần dịch:", height=150, placeholder="Nhập nội dung bất kỳ...")

    if st.button("🚀 Dịch ngay", key="btn_trans", type="primary"):
        if text_to_translate.strip():
            with st.spinner("Đang biên dịch..."):
                try:
                    from service_bridge import call_tools_process
                    res_text = call_tools_process("translate", text_to_translate, target_lang, "")
                    st.markdown("### Kết quả bản dịch:")
                    st.markdown(res_text)
                    render_export_buttons(res_text, f"Ban_Dich_{target_lang}")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# 2. Sinh code
with tab_codegen:
    st.subheader("Sinh mã nguồn theo mô tả")
    col_code1, col_code2 = st.columns([3, 1])
    with col_code2:
        code_lang = st.selectbox("Ngôn ngữ lập trình:", ["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust", "SQL", "HTML/CSS"])
    with col_code1:
        code_desc = st.text_area("Mô tả chức năng cần viết:", height=150, placeholder="Ví dụ: Viết hàm đọc file JSON, trích xuất email hợp lệ và lưu vào file Excel...")

    if st.button("💻 Viết Code", key="btn_codegen", type="primary"):
        if code_desc.strip():
            with st.spinner("AI đang tạo mã nguồn..."):
                try:
                    from service_bridge import call_tools_process
                    res_text = call_tools_process("code_generate", code_desc, "", code_lang)
                    st.markdown("### Mã nguồn được tạo:")
                    st.markdown(res_text)
                    render_export_buttons(res_text, f"Code_{code_lang}")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# 3. Giải thích code
with tab_explain:
    st.subheader("Giải thích logic và đánh giá code")
    code_input = st.text_area("Dán đoạn code cần giải thích:", height=180, placeholder="Dán mã nguồn vào đây...")
    if st.button("🔍 Giải thích", key="btn_explain", type="primary"):
        if code_input.strip():
            with st.spinner("Đang phân tích code..."):
                try:
                    from service_bridge import call_tools_process
                    res_text = call_tools_process("code_explain", code_input)
                    st.markdown(res_text)
                    render_export_buttons(res_text, "Giai_Thich_Code")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# 4. Tóm tắt
with tab_sum:
    st.subheader("Tóm tắt tài liệu & bài báo dài")
    text_to_sum = st.text_area("Nhập văn bản cần tóm tắt:", height=180, placeholder="Dán bài báo, tin tức hoặc báo cáo cần tóm gọn...")
    if st.button("📑 Tóm tắt ngay", key="btn_sum", type="primary"):
        if text_to_sum.strip():
            with st.spinner("Đang chắt lọc ý chính..."):
                try:
                    from service_bridge import call_tools_process
                    res_text = call_tools_process("summarize", text_to_sum)
                    st.markdown(res_text)
                    render_export_buttons(res_text, "Tom_Tat_Noi_Dung")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# 5. Soát lỗi văn phạm
with tab_grammar:
    st.subheader("Chỉnh sửa ngữ pháp, chính tả & nâng cấp hành văn")
    text_grammar = st.text_area("Nhập văn bản cần sửa:", height=180, placeholder="Nhập bài luận, email hoặc văn bản cần trau chuốt...")
    if st.button("✏️ Soát lỗi & Sửa", key="btn_grammar", type="primary"):
        if text_grammar.strip():
            with st.spinner("Đang rà soát lỗi..."):
                try:
                    from service_bridge import call_tools_process
                    res_text = call_tools_process("grammar_fix", text_grammar)
                    st.markdown(res_text)
                    render_export_buttons(res_text, "Sua_Loi_Van_Pham")
                except Exception as e:
                    st.error(f"Lỗi: {e}")


