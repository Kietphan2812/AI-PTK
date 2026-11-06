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
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    res = requests.post(f"{API_URL}/api/rag/upload", files=files, timeout=120)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"✅ {data.get('message')}")
                        st.info(f"📁 Tên tài liệu: `{data.get('filename')}` | 🔢 Số đoạn phân mảnh: `{data.get('chunks')}`")
                    else:
                        st.error(f"Lỗi: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Lỗi kết nối: {str(e)}")

with col2:
    st.subheader("🔍 2. Đặt câu hỏi trên tài liệu")

    # Lấy danh sách tài liệu hiện có
    doc_list = []
    try:
        r = requests.get(f"{API_URL}/api/rag/documents", timeout=5)
        if r.status_code == 200:
            doc_list = r.json().get("documents", [])
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
                        res = requests.post(
                            f"{API_URL}/api/rag/query",
                            json={"query": question, "filename": selected_doc},
                            timeout=60,
                        )
                        if res.status_code == 200:
                            ans_data = res.json()
                            st.markdown("### 💡 Câu trả lời từ AI:")
                            st.markdown(ans_data.get("answer", ""))

                            sources = ans_data.get("sources", [])
                            if sources:
                                with st.expander(f"📚 Xem {len(sources)} đoạn trích nguồn được AI tham khảo"):
                                    for idx, s in enumerate(sources, 1):
                                        st.markdown(f"**Trích đoạn {idx}:**")
                                        st.caption(s)
                                        st.write("---")
                        else:
                            st.error(f"Lỗi: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Lỗi truy vấn: {str(e)}")
    else:
        st.info("Chưa có tài liệu nào trong hệ thống. Hãy tải lên một file PDF ở cột bên trái.")

