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
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Công cụ nhanh phục vụ học tập và làm việc: Dịch thuật, Viết code, Giải thích thuật toán, Tóm tắt & Sửa văn phạm.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
                    res = requests.post(f"{API_URL}/api/tools/process", json={"tool_type": "translate", "text": text_to_translate, "target_language": target_lang})
                    if res.status_code == 200:
                        st.markdown("### Kết quả bản dịch:")
                        st.markdown(res.json().get("result"))
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
                    res = requests.post(f"{API_URL}/api/tools/process", json={"tool_type": "code_generate", "text": code_desc, "programming_language": code_lang})
                    if res.status_code == 200:
                        st.markdown("### Mã nguồn được tạo:")
                        st.markdown(res.json().get("result"))
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
                    res = requests.post(f"{API_URL}/api/tools/process", json={"tool_type": "code_explain", "text": code_input})
                    if res.status_code == 200:
                        st.markdown(res.json().get("result"))
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
                    res = requests.post(f"{API_URL}/api/tools/process", json={"tool_type": "summarize", "text": text_to_sum})
                    if res.status_code == 200:
                        st.markdown(res.json().get("result"))
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
                    res = requests.post(f"{API_URL}/api/tools/process", json={"tool_type": "grammar_fix", "text": text_grammar})
                    if res.status_code == 200:
                        st.markdown(res.json().get("result"))
                except Exception as e:
                    st.error(f"Lỗi: {e}")

