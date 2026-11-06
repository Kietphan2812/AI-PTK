"""
Trang 4: Phân Tích Dữ Liệu CSV Tự Động
"""

import os
import streamlit as st
import streamlit.components.v1 as components
import requests

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Data Analytics - AI PTK", page_icon="📊", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #00897B 0%, #004D40 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">📊 Phân Tích Dữ Liệu CSV & AI Insights</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Tải lên tệp CSV để tự động thống kê, trực quan hóa biểu đồ Plotly và nhận báo cáo phân tích thông minh từ AI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_csv = st.file_uploader("Chọn file dữ liệu dạng CSV", type=["csv"])

if uploaded_csv is not None:
    if st.button("📈 Bắt đầu phân tích dữ liệu", type="primary", use_container_width=True):
        with st.spinner("Đang tính toán thống kê và chạy mô hình phân tích..."):
            try:
                from service_bridge import call_data_analyze
                data = call_data_analyze(uploaded_csv.name, uploaded_csv.getvalue())

                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Tổng số dòng dữ liệu", f"{data.get('row_count'):,}")
                c2.metric("Tổng số cột", len(data.get("columns", [])))
                c3.metric("Trạng thái", "Phân tích hoàn tất")

                st.write("---")

                # Tabs hiển thị
                tab1, tab2, tab3 = st.tabs(["🤖 Báo Cáo AI Insights", "📈 Biểu Đồ Trực Quan", "📋 Thống Kê Chi Tiết"])

                with tab1:
                    st.markdown("### 💡 Đánh giá & Phát hiện từ AI:")
                    st.markdown(data.get("ai_insights", ""))

                with tab2:
                    st.markdown("### 📊 Trực quan hoá biểu đồ:")
                    chart_html = data.get("chart_html", "")
                    if chart_html:
                        components.html(chart_html, height=520, scrolling=True)
                    else:
                        st.info("Không có biểu đồ phù hợp được sinh ra.")

                with tab3:
                    st.markdown("### 📋 Thông tin thống kê mô tả:")
                    st.text(data.get("summary", ""))

            except Exception as e:
                st.error(f"Lỗi phân tích: {str(e)}")
else:
    st.info("Hãy tải lên một tệp CSV để hệ thống thực hiện phân tích tự động.")

