"""
AI PTK - Giao diện chính Streamlit
"""

import os
import streamlit as st
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI PTK - Nền tảng AI Đa Năng",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1E88E5 0%, #7C4DFF 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .main-header p {
        font-size: 1.15rem;
        opacity: 0.95;
    }
    .feature-card {
        background-color: #ffffff;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        border-color: #1E88E5;
    }
    .feature-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 8px;
    }
    .feature-desc {
        color: #64748B;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="main-header">
        <h1>🚀 AI PTK - Platform Tích Hợp Kiến Thức</h1>
        <p>Hệ thống trợ lý AI All-In-One: Chatbot, RAG PDF, Sáng tạo nội dung, Phân tích dữ liệu & Tiện ích thông minh</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar info
with st.sidebar:
    st.image("https://api.iconify.design/fluent-emoji:rocket.svg", width=64)
    st.title("AI PTK v1.0")
    st.write("---")

    # Kiểm tra Backend
    try:
        res = requests.get(f"{API_URL}/api/health", timeout=2)
        if res.status_code == 200:
            health = res.json()
            st.success("🟢 Backend: Đang kết nối")
            st.caption(f"Model: `{health.get('model')}`")
            if not health.get("api_key_configured"):
                st.warning("⚠️ Chưa điền `GEMINI_API_KEY` trong file `.env`!")
        else:
            st.warning("🟡 Backend không phản hồi chuẩn")
    except Exception:
        st.error("🔴 Không thể kết nối Backend!")
        st.caption("Hãy mở terminal và chạy: `cd backend && uvicorn main:app --reload`")

    st.write("---")
    st.info("👈 **Chọn tính năng ở thanh menu bên trái** để bắt đầu trải nghiệm.")

# Danh sách tính năng
st.subheader("💡 Khám phá các tính năng chính")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Chat AI Trực Quan</div>
            <div class="feature-desc">Trò chuyện đa lượt với Gemini 2.0 Flash thông minh, ghi nhớ ngữ cảnh hội thoại, giải đáp mọi thắc mắc.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Hỏi Đáp PDF (RAG)</div>
            <div class="feature-desc">Tải tài liệu PDF lên, hệ thống tự động băm nhỏ, lưu trữ vector trong ChromaDB và tra cứu câu trả lời chuẩn xác kèm trích dẫn.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">✍️</div>
            <div class="feature-title">Sáng Tạo Nội Dung</div>
            <div class="feature-desc">Viết Blog chuẩn SEO, Email công việc, Copywriting bán hàng, Post mạng xã hội và Báo cáo chuyên sâu theo nhiều giọng điệu.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
col4, col5 = st.columns(2)

with col4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Phân Tích Dữ Liệu CSV</div>
            <div class="feature-desc">Kéo thả file CSV, tự động tính toán thống kê mô tả, vẽ biểu đồ tương tác Plotly và nhận báo cáo chuyên sâu từ AI.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔧</div>
            <div class="feature-title">Bộ Tiện Ích AI Nhanh</div>
            <div class="feature-desc">Dịch thuật chuẩn ngữ cảnh, tự động sinh code & giải thích thuật toán, tóm tắt ý chính và chỉnh sửa ngữ pháp chuẩn xác.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        Phát triển cho dự án <b>AI PTK</b> • Sử dụng FastAPI, Streamlit, ChromaDB & Google Gemini 2.0 Flash
    </div>
    """,
    unsafe_allow_html=True,
)

