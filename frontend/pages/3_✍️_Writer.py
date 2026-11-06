"""
Trang 3: Sáng Tạo Nội Dung Đa Định Dạng
"""

import os
import streamlit as st
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Writer - AI PTK", page_icon="✍️", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #8E24AA 0%, #4A148C 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">✍️ Sáng Tạo Nội Dung Chuyên Nghiệp</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Tự động viết Blog, Email, Marketing Copy, Bài đăng mạng xã hội và Báo cáo theo nhiều phong cách.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ Cấu hình nội dung")

    task_type = st.selectbox(
        "Định dạng bài viết:",
        options=[
            ("blog", "📝 Bài viết Blog chuẩn SEO"),
            ("email", "✉️ Email công việc & kinh doanh"),
            ("marketing", "🎯 Bài quảng cáo & bán hàng (Copywriting)"),
            ("social_media", "📱 Bài đăng mạng xã hội (Facebook, LinkedIn)"),
            ("essay", "🎓 Bài tiểu luận / Báo cáo học thuật"),
        ],
        format_func=lambda x: x[1],
    )[0]

    topic = st.text_input("Chủ đề hoặc tiêu đề chính:", placeholder="Ví dụ: Xu hướng ứng dụng AI trong giáo dục năm 2026")

    col_tone, col_lang = st.columns(2)
    with col_tone:
        tone = st.selectbox(
            "Giọng điệu (Tone):",
            options=["Chuyên nghiệp, uy tín", "Thân thiện, gần gũi", "Thuyết phục, nhiệt huyết", "Trang trọng, học thuật", "Hài hước, dí dỏm"],
        )
    with col_lang:
        language = st.selectbox("Ngôn ngữ đầu ra:", options=["Tiếng Việt", "English", "Japanese", "French"])

    extra_instructions = st.text_area(
        "Yêu cầu bổ sung (tùy chọn):",
        placeholder="Ví dụ: Nêu rõ 3 lợi ích chính, kèm số liệu dẫn chứng, kêu gọi hành động đăng ký dùng thử...",
        height=100,
    )

    btn_generate = st.button("✨ Bắt đầu tạo nội dung", use_container_width=True, type="primary")

with col2:
    st.subheader("📄 Kết quả bản thảo")
    if "writer_result" not in st.session_state:
        st.session_state.writer_result = ""
    if "writer_topic" not in st.session_state:
        st.session_state.writer_topic = ""

    if btn_generate:
        if not topic.strip():
            st.warning("Vui lòng nhập chủ đề bài viết.")
        else:
            with st.spinner("AI đang soạn thảo nội dung..."):
                try:
                    from service_bridge import call_writer
                    st.session_state.writer_result = call_writer(task_type, topic, tone, language, extra_instructions)
                    st.session_state.writer_topic = topic
                except Exception as e:
                    st.error(f"Lỗi tạo nội dung: {str(e)}")

    if st.session_state.writer_result:
        content = st.session_state.writer_result
        curr_topic = st.session_state.writer_topic or "Bai_Viet_AI_PTK"
        st.markdown(content)
        st.write("---")

        st.markdown("#### 📥 Xuất bản tài liệu:")
        from service_bridge import export_to_docx, export_to_excel
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            docx_data = export_to_docx(content, title=curr_topic)
            st.download_button(
                label="📄 Xuất Word (.docx)",
                data=docx_data,
                file_name=f"{curr_topic[:25].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with exp_col2:
            xlsx_data = export_to_excel(content, title=curr_topic)
            st.download_button(
                label="📊 Xuất Excel (.xlsx)",
                data=xlsx_data,
                file_name=f"{curr_topic[:25].replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with exp_col3:
            st.download_button(
                label="📝 Tải Text (.txt)",
                data=content.encode("utf-8"),
                file_name=f"{curr_topic[:25].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
    else:
        st.info("Nhập thông tin bên trái và nhấn nút 'Bắt đầu tạo nội dung' để xem kết quả tại đây.")

