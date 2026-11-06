"""
Trang 1: Chat AI Đa Não (Multi-Model) & Thị Giác AI (Vision)
Hỗ trợ: Gửi câu hỏi kèm hình ảnh (giải toán, đọc chữ, mô tả ảnh) với Gemini, ChatGPT GPT-4o, Claude 3.5 Sonnet, DeepSeek.
"""

import os
import streamlit as st
import requests

st.set_page_config(page_title="Chat AI - AI PTK", page_icon="💬", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">💬 Chatbot Trí Tuệ Nhân Tạo & Thị Giác (Vision)</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Hỗ trợ trò chuyện thông minh và đọc/phân tích hình ảnh (giải bài tập, đọc tài liệu, nhận diện ảnh).</p>
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
            ("gemini", None, "⚡ Google Gemini 3.5 (Hỗ trợ nhìn ảnh cực tốt - Miễn phí)"),
            ("deepseek", "deepseek-reasoner", "🧠 DeepSeek R1 (Vua suy luận logic & Thuật toán)"),
            ("deepseek", "deepseek-chat", "🧠 DeepSeek V3 (Siêu thông minh & Toàn diện)"),
            ("openai", "gpt-4o", "🤖 ChatGPT - GPT-4o (Hỗ trợ nhìn ảnh & Đa năng)"),
            ("openai", "gpt-4o-mini", "🤖 ChatGPT - GPT-4o Mini (Phản hồi cực nhanh)"),
            ("claude", "claude-3-5-sonnet-20241022", "🎭 Claude 3.5 Sonnet (Hỗ trợ nhìn ảnh & Văn phong đỉnh cao)"),
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

# Khung đính kèm ảnh & Cài đặt Key
col_attach, col_key = st.columns([1, 1])

with col_attach:
    uploaded_image = st.file_uploader(
        "📷 Đính kèm hình ảnh để AI đọc/phân tích (tùy chọn):",
        type=["png", "jpg", "jpeg", "webp"],
        key="chat_uploader_image",
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Ảnh đã chọn - AI sẽ đọc ảnh này khi bạn gửi câu hỏi", width=220)

with col_key:
    with st.expander("🔑 Cài đặt API Key riêng (Tùy chọn)"):
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
    img_data = msg.get("image")
    with st.chat_message("user" if role == "user" else "assistant"):
        if img_data:
            st.image(img_data, width=300)
        st.markdown(content)

# Ô nhập tin nhắn
if user_prompt := st.chat_input("Nhập câu hỏi hoặc yêu cầu AI phân tích ảnh..."):
    # Đọc ảnh nếu người dùng đính kèm
    current_img_bytes = None
    current_img_mime = None
    if uploaded_image:
        current_img_bytes = uploaded_image.getvalue()
        current_img_mime = uploaded_image.type

    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        if current_img_bytes:
            st.image(current_img_bytes, width=300)
        st.markdown(user_prompt)

    st.session_state.chat_history.append({
        "role": "user",
        "parts": user_prompt,
        "image": current_img_bytes,
    })

    # Xử lý chat qua Service Bridge
    with st.chat_message("assistant"):
        spinner_label = "AI đang nhìn ảnh và suy nghĩ..." if current_img_bytes else f"AI ({selected_ai_option[2].split(' ')[1]}) đang suy nghĩ..."
        with st.spinner(spinner_label):
            try:
                from service_bridge import call_chat
                # Lịch sử dạng text (chỉ gửi text các câu trước)
                history_payload = []
                for h in st.session_state.chat_history[:-1]:
                    history_payload.append({"role": h["role"], "parts": h["parts"]})

                reply = call_chat(
                    message=user_prompt,
                    history=history_payload,
                    provider=provider_choice,
                    model=model_choice,
                    custom_key=user_custom_key.strip() if user_custom_key else None,
                    image_bytes=current_img_bytes,
                    image_mime=current_img_mime,
                )
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "model", "parts": reply})
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
