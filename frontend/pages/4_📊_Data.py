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

if "data_analysis_result" not in st.session_state:
    st.session_state.data_analysis_result = None
if "data_file_name" not in st.session_state:
    st.session_state.data_file_name = ""

if uploaded_csv is not None:
    if st.button("📈 Bắt đầu phân tích dữ liệu", type="primary", use_container_width=True):
        with st.spinner("Đang tính toán thống kê và chạy mô hình phân tích..."):
            try:
                from service_bridge import call_data_analyze
                st.session_state.data_analysis_result = call_data_analyze(uploaded_csv.name, uploaded_csv.getvalue())
                st.session_state.data_file_name = uploaded_csv.name
            except Exception as e:
                st.error(f"Lỗi phân tích: {str(e)}")

    if st.session_state.data_analysis_result:
        data = st.session_state.data_analysis_result
        file_base = st.session_state.data_file_name.rsplit(".", 1)[0] if st.session_state.data_file_name else "Data"

        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng số dòng dữ liệu", f"{data.get('row_count'):,}")
        c2.metric("Tổng số cột", len(data.get("columns", [])))
        c3.metric("Trạng thái", "Phân tích hoàn tất")

        # Nút xuất Word & Excel
        st.write("---")
        st.markdown("#### 📥 Xuất báo cáo & Dữ liệu:")
        from service_bridge import export_to_docx, export_to_excel
        import io
        import pandas as pd

        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            insights_text = f"# BÁO CÁO PHÂN TÍCH DỮ LIỆU: {st.session_state.data_file_name}\n\n" + data.get("ai_insights", "") + f"\n\n## Thống kê mô tả:\n{data.get('summary', '')}"
            docx_data = export_to_docx(insights_text, title=f"Báo Cáo {file_base}")
            st.download_button(
                label="📄 Xuất Báo Cáo Phân Tích ra Word (.docx)",
                data=docx_data,
                file_name=f"Bao_Cao_{file_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

        with exp_c2:
            try:
                uploaded_csv.seek(0)
                df = pd.read_csv(uploaded_csv)
                xlsx_data = export_to_excel(df, title=f"{file_base[:25]}")
                st.download_button(
                    label="📊 Xuất Bảng Dữ Liệu ra Excel (.xlsx)",
                    data=xlsx_data,
                    file_name=f"Du_Lieu_{file_base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception:
                pass

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
else:
    st.info("Hãy tải lên một tệp CSV để hệ thống thực hiện phân tích tự động.")

