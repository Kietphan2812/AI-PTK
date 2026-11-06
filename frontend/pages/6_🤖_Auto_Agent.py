"""
Trang 6: AI Auto-Agent - Hệ Thống Tự Động Hóa Công Việc Từ A Đến Z
Bất kỳ ai vào web ra lệnh, AI sẽ tự động lập kế hoạch, tự thực thi, tự chạy code và xuất file Word/Excel.
"""

import os
import streamlit as st
import time

st.set_page_config(page_title="Auto-Agent - AI PTK", page_icon="🤖", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%); padding: 22px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">🤖 AI PTK Auto-Agent — Tự Động Hóa Công Việc Từ A Đến Z</h2>
        <p style="margin: 6px 0 0 0; opacity: 0.95; font-size: 15px;">
            Nhập bất kỳ mục tiêu nào: AI sẽ <b>tự lập kế hoạch ➔ tự thực thi tính toán & viết code ➔ tự động đóng gói file Word (.docx) và Excel (.xlsx)</b> để bạn tải về ngay!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

# CỘT TÙY CHỈNH & GỢI Ý MẪU
col_main, col_sidebar = st.columns([2.5, 1])

with col_sidebar:
    st.markdown("### 💡 Gợi ý mục tiêu nhanh")
    st.caption("Bấm vào các mẫu dưới đây để tự động điền:")

    presets = [
        "📊 Lập kế hoạch kinh doanh quán cafe, dự toán chi phí khởi nghiệp, dự báo doanh thu 6 tháng đầu và bảng phân bổ vốn",
        "📱 Xây dựng kế hoạch Marketing đa kênh 30 ngày cho sản phẩm thời trang, bảng lịch đăng bài và phân tích ngân sách",
        "💻 Viết chương trình Python tính toán bảng trả góp mua nhà theo dư nợ giảm dần, chạy thử nghiệm với số tiền 2 tỷ đồng",
        "📝 Soạn thảo Quy trình tuyển dụng và đánh giá nhân sự chuẩn chỉnh cho công ty, kèm bảng tiêu chí chấm điểm ứng viên",
    ]

    for p in presets:
        btn_label = p.split(",")[0]
        if st.button(f"👉 {btn_label}", use_container_width=True):
            st.session_state["agent_goal_input"] = p
            st.rerun()

    st.write("---")
    st.markdown("### 🧠 Chọn bộ não điều phối")
    selected_ai = st.selectbox(
        "Mô hình AI:",
        options=[
            ("gemini", None, "⚡ Google Gemini (Cực nhanh & Miễn phí)"),
            ("deepseek", "deepseek-reasoner", "🧠 DeepSeek R1 (Vua tư duy logic)"),
            ("openai", "gpt-4o", "🤖 ChatGPT - GPT-4o"),
            ("claude", "claude-3-5-sonnet-20241022", "🎭 Claude 3.5 Sonnet"),
        ],
        format_func=lambda x: x[2],
    )

    with st.expander("🔑 Cài đặt Key riêng (Tùy chọn)"):
        custom_key_input = st.text_input("Nhập API Key nếu có:", type="password")

with col_main:
    st.markdown("### 🎯 Nhập mục tiêu công việc bạn muốn AI tự động hoàn thành:")

    current_val = st.session_state.get("agent_goal_input", "")
    user_goal = st.text_area(
        "Mục tiêu hoặc bài toán cần AI giải quyết:",
        value=current_val,
        height=130,
        placeholder="Ví dụ: Lập kế hoạch mở quán trà sữa tại TP.HCM, tính toán chi phí đầu tư ban đầu, dự phóng điểm hòa vốn và lập bảng phân bổ ngân sách...",
    )

    btn_auto_run = st.button("🚀 Bắt Đầu Tự Động Hóa Ngay", type="primary", use_container_width=True)

    if btn_auto_run:
        if not user_goal.strip():
            st.warning("Vui lòng nhập mục tiêu để AI Auto-Agent bắt đầu làm việc!")
        else:
            progress_bar = st.progress(0, text="🤖 Khởi động AI Auto-Agent...")
            status_box = st.empty()

            try:
                # Giai đoạn 1: Lập kế hoạch
                progress_bar.progress(25, text="📋 Giai đoạn 1/4: Đang phân tích mục tiêu & lập kế hoạch đa bước...")
                time.sleep(0.5)

                # Giai đoạn 2: Thực thi
                progress_bar.progress(55, text="⚙️ Giai đoạn 2/4: Đang tự động giải quyết từng hạng mục chuyên sâu...")

                from service_bridge import call_agent_execute
                agent_res = call_agent_execute(
                    goal=user_goal.strip(),
                    provider=selected_ai[0],
                    model=selected_ai[1],
                    custom_key=custom_key_input.strip() if custom_key_input else None,
                )

                # Giai đoạn 3: Kiểm tra code
                progress_bar.progress(85, text="💻 Giai đoạn 3/4: Đang chạy thử nghiệm tính toán số liệu...")
                time.sleep(0.4)

                # Giai đoạn 4: Đóng gói
                progress_bar.progress(100, text="📦 Giai đoạn 4/4: Đã đóng gói thành phẩm Word (.docx) & Excel (.xlsx) thành công!")
                time.sleep(0.3)

                st.session_state.agent_result = agent_res
                status_box.success("🎉 Hoàn thành toàn bộ công việc từ A đến Z!")
            except Exception as e:
                st.error(f"Lỗi trong quá trình tự động hóa: {str(e)}")

# HIỂN THỊ KẾT QUẢ CÔNG VIỆC HOÀN THÀNH
if st.session_state.agent_result:
    res = st.session_state.agent_result
    st.write("---")
    st.markdown("## 🏆 BÁO CÁO THÀNH PHẨM TỰ ĐỘNG HÓA")

    # KHU VỰC TẢI FILE THÀNH PHẨM (WORD & EXCEL)
    st.markdown("### 📥 Tải về thành phẩm hoàn chỉnh:")
    d_col1, d_col2, d_col3 = st.columns(3)
    fname = res.get("filename_base", "Thanh_Pham_AI")

    with d_col1:
        if res.get("docx_bytes"):
            st.download_button(
                label="📄 Tải Báo Cáo Word (.docx)",
                data=res.get("docx_bytes"),
                file_name=f"{fname}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
    with d_col2:
        if res.get("xlsx_bytes"):
            st.download_button(
                label="📊 Tải Bảng Tính Excel (.xlsx)",
                data=res.get("xlsx_bytes"),
                file_name=f"{fname}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
    with d_col3:
        st.download_button(
            label="📝 Tải Bản Văn Bản (.txt)",
            data=res.get("result_markdown", "").encode("utf-8"),
            file_name=f"{fname}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.write("")

    # CÁC TAB CHI TIẾT
    tab_res, tab_plan, tab_code = st.tabs([
        "📄 Báo Cáo Thực Thi Toàn Diện",
        "📋 Kế Hoạch 4 Bước Đã Phân Rã",
        "💻 Kết Quả Thực Thi Mã Nguồn (Code Output)",
    ])

    with tab_res:
        st.markdown(res.get("result_markdown", ""))

    with tab_plan:
        st.markdown("#### Các bước chiến lược AI đã tự động đề xuất và thực hiện:")
        st.markdown(res.get("plan", ""))

    with tab_code:
        code_out = res.get("code_output", "")
        if code_out:
            st.markdown("#### Kết quả chạy thử nghiệm Python Sandbox:")
            st.code(code_out, language="text")
        else:
            st.info("Mục tiêu này không yêu cầu chạy thuật toán số liệu riêng.")
