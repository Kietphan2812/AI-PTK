"""
Trang 2: Hỏi Đáp Tài Liệu PDF (RAG)
"""

import os
import streamlit as st
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="PDF Q&A - AI PTK", page_icon="📄", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #43A047 0%, #1B5E20 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">📄 Tra Cứu & Hỏi Đáp Tài Liệu PDF (RAG)</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Tải tài liệu PDF lên để phân tích, băm đoạn vector vào ChromaDB và truy vấn chính xác kèm trích dẫn.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 1. Tải lên tài liệu PDF")
    uploaded_file = st.file_uploader("Chọn file PDF từ máy tính của bạn", type=["pdf"])

    if uploaded_file is not None:
        if st.button("🚀 Bắt đầu lập chỉ mục tài liệu", use_container_width=True, type="primary"):
            with st.spinner("Đang trích xuất văn bản và phân mảnh vào ChromaDB..."):
                try:
                    from service_bridge import call_rag_upload
                    data = call_rag_upload(uploaded_file.name, uploaded_file.getvalue())
                    st.success(f"✅ {data.get('message')}")
                    st.info(f"📁 Tên tài liệu: `{data.get('filename')}` | 🔢 Số đoạn phân mảnh: `{data.get('chunks')}`")
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")

with col2:
    st.subheader("🔍 2. Đặt câu hỏi trên tài liệu")

    # Lấy danh sách tài liệu hiện có
    doc_list = []
    try:
        from service_bridge import call_rag_list
        doc_list = call_rag_list()
    except Exception:
        pass

    if doc_list:
        selected_doc = st.selectbox("Chọn tài liệu cần tra cứu:", options=doc_list)
        question = st.text_area("Nhập câu hỏi của bạn về tài liệu này:", placeholder="Tóm tắt các ý chính trong tài liệu...")

        if st.button("🔎 Tra cứu câu trả lời", use_container_width=True, type="primary"):
            if not question.strip():
                st.warning("Vui lòng nhập câu hỏi.")
            else:
                with st.spinner("Đang tìm kiếm ngữ cảnh phù hợp và sinh câu trả lời..."):
                    try:
                        from service_bridge import call_rag_query, export_to_docx, export_to_excel
                        ans_data = call_rag_query(question, selected_doc)
                        answer_text = ans_data.get("answer", "")
                        st.markdown("### 💡 Câu trả lời từ AI:")
                        st.markdown(answer_text)

                        # Nút xuất Word & Excel
                        st.write("---")
                        c_exp1, c_exp2 = st.columns(2)
                        with c_exp1:
                            docx_bytes = export_to_docx(answer_text, title=f"Trả lời tra cứu: {selected_doc}")
                            st.download_button(
                                label="📄 Xuất câu trả lời ra Word (.docx)",
                                data=docx_bytes,
                                file_name=f"Tra_Luu_{selected_doc[:15]}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                            )
                        with c_exp2:
                            xlsx_bytes = export_to_excel(answer_text, title=f"Tra cứu: {selected_doc}")
                            st.download_button(
                                label="📊 Xuất ra Excel (.xlsx)",
                                data=xlsx_bytes,
                                file_name=f"Tra_Luu_{selected_doc[:15]}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                            )

                        sources = ans_data.get("sources", [])
                        if sources:
                            with st.expander(f"📚 Xem {len(sources)} đoạn trích nguồn được AI tham khảo"):
                                for idx, s in enumerate(sources, 1):
                                    st.markdown(f"**Trích đoạn {idx}:**")
                                    st.caption(s)
                                    st.write("---")
                    except Exception as e:
                        st.error(f"Lỗi truy vấn: {str(e)}")
    else:
        st.info("Chưa có tài liệu nào trong hệ thống. Hãy tải lên một file PDF ở cột bên trái.")

