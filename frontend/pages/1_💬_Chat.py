"""
Trang 1: Chat AI Đa Não (Multi-Model AI Engine)
Hỗ trợ: Google Gemini, DeepSeek (V3/R1), OpenAI (GPT-4o), Anthropic (Claude 3.5)
"""

import os
import streamlit as st
import requests

st.set_page_config(page_title="Chat AI - AI PTK", page_icon="💬", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">💬 Chatbot Trí Tuệ Nhân Tạo Đa Bộ Não</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Tùy chọn bộ não AI: DeepSeek R1, ChatGPT GPT-4o, Claude 3.5 Sonnet & Google Gemini.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# BỘ CHỌN NÃO AI & TÙY CHỈNH
col_model, col_del = st.columns([5, 1])

with col_model:
    selected_ai_option = st.selectbox(
        "🧠 Chọn bộ não AI bạn muốn trò chuyện:",
        options=[
            ("gemini", None, "⚡ Google Gemini 3.5 (Mặc định - Nhanh & Miễn phí)"),
            ("deepseek", "deepseek-reasoner", "🧠 DeepSeek R1 (Vua suy luận logic & Thuật toán)"),
            ("deepseek", "deepseek-chat", "🧠 DeepSeek V3 (Siêu thông minh & Toàn diện)"),
            ("openai", "gpt-4o", "🤖 ChatGPT - GPT-4o (Đa năng & Sáng tạo)"),
            ("openai", "gpt-4o-mini", "🤖 ChatGPT - GPT-4o Mini (Phản hồi cực nhanh)"),
            ("claude", "claude-3-5-sonnet-20241022", "🎭 Claude 3.5 Sonnet (Đỉnh cao hành văn & Phân tích sâu)"),
        ],
        format_func=lambda x: x[2],
    )
    provider_choice = selected_ai_option[0]
    model_choice = selected_ai_option[1]

with col_del:
    st.write("")
    st.write("")
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Cài đặt Key tùy chọn (nếu dùng DeepSeek, OpenAI, Claude riêng)
with st.expander("🔑 Cài đặt API Key riêng (Tùy chọn - nếu bạn muốn dùng Key riêng của DeepSeek / OpenAI / Claude)"):
    st.caption("Nếu để trống, hệ thống sẽ tự động dùng Key đã cấu hình trong máy chủ / Secrets.")
    user_custom_key = st.text_input(
        f"Nhập API Key cho {provider_choice.upper()} (nếu có):",
        type="password",
        placeholder="sk-... hoặc key của bạn",
        key=f"custom_key_{provider_choice}",
    )

st.write("---")

# Hiển thị lịch sử chat
for msg in st.session_state.chat_history:
    role = msg.get("role")
    content = msg.get("parts", "")
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# Ô nhập tin nhắn
if user_prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.chat_history.append({"role": "user", "parts": user_prompt})

    # Xử lý chat qua Service Bridge
    with st.chat_message("assistant"):
        with st.spinner(f"AI ({selected_ai_option[2].split(' ')[1]}) đang suy nghĩ..."):
            try:
                from service_bridge import call_chat
                history_payload = st.session_state.chat_history[:-1]
                reply = call_chat(
                    message=user_prompt,
                    history=history_payload,
                    provider=provider_choice,
                    model=model_choice,
                    custom_key=user_custom_key.strip() if user_custom_key else None,
                )
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "model", "parts": reply})
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
