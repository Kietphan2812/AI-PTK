"""
Trang 1: Chat AI Đa Lượt
"""

import os
import streamlit as st
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Chat AI - AI PTK", page_icon="💬", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">💬 Chatbot Trí Tuệ Nhân Tạo</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Trò chuyện tương tác với mô hình Gemini 2.0 Flash, lưu giữ ngữ cảnh hội thoại.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col_left, col_right = st.columns([6, 1])
with col_right:
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Hiển thị lịch sử chat
for msg in st.session_state.chat_history:
    role = msg.get("role")
    content = msg.get("parts", "")
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# Ô nhập tin nhắn
if user_prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    # Hiển thị tin nhắn người dùng ngay lập tức
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Đưa vào history
    st.session_state.chat_history.append({"role": "user", "parts": user_prompt})

    # Gọi API Backend
    with st.chat_message("assistant"):
        with st.spinner("AI đang suy nghĩ..."):
            try:
                # Gửi toàn bộ history trước đó (ngoại trừ tin nhắn hiện tại)
                history_payload = st.session_state.chat_history[:-1]
                response = requests.post(
                    f"{API_URL}/api/chat",
                    json={"message": user_prompt, "history": history_payload},
                    timeout=60,
                )
                if response.status_code == 200:
                    reply = response.json().get("response", "")
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "model", "parts": reply})
                else:
                    err_msg = response.json().get("detail", "Lỗi từ máy chủ.")
                    st.error(f"⚠️ {err_msg}")
            except requests.exceptions.ConnectionError:
                st.error("🔴 Không thể kết nối tới Backend (http://localhost:8000). Hãy kiểm tra xem server đã khởi động chưa.")
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")

