"""
Data Service - Tự động phân tích file CSV, tạo biểu đồ Plotly và AI Insights
"""

import pandas as pd
import plotly.express as px
import plotly.io as pio
from services.ai_service import AIService


class DataService:
    """Xử lý dữ liệu CSV và phân tích chuyên sâu."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()

    def analyze_csv(self, file_path: str) -> dict:
        try:
            df = pd.read_csv(file_path)
        except Exception:
            try:
                df = pd.read_csv(file_path, encoding="latin1")
            except Exception as e:
                return {
                    "summary": f"Không thể đọc file CSV: {str(e)}",
                    "columns": [],
                    "row_count": 0,
                    "ai_insights": "Lỗi đọc dữ liệu.",
                    "chart_html": "",
                }

        # 1. Thống kê cơ bản
        row_count = len(df)
        cols = df.columns.tolist()

        summary_lines = [
            f"Kích thước tập dữ liệu: {row_count} dòng x {len(cols)} cột.",
            "Danh sách các cột và kiểu dữ liệu:",
        ]
        for c, t in df.dtypes.items():
            null_count = df[c].isnull().sum()
            summary_lines.append(f" - {c} ({t}): {null_count} giá trị khuyết thiếu ({null_count/max(row_count,1)*100:.1f}%)")

        num_df = df.select_dtypes(include=["number"])
        if not num_df.empty:
            summary_lines.append("\nThống kê mô tả số lượng (Describe):")
            summary_lines.append(num_df.describe().round(2).to_string())

        summary_text = "\n".join(summary_lines)

        # 2. Tạo biểu đồ thông minh bằng Plotly
        chart_html = ""
        try:
            # Ưu tiên: nếu có cột thời gian/ngày và cột số -> Line chart
            date_col = None
            for c in df.columns:
                if "date" in c.lower() or "time" in c.lower() or "ngay" in c.lower():
                    try:
                        df[c] = pd.to_datetime(df[c])
                        date_col = c
                        break
                    except Exception:
                        pass

            num_cols = num_df.columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            if date_col and num_cols:
                fig = px.line(df.sort_values(by=date_col), x=date_col, y=num_cols[0], title=f"Xu hướng theo thời gian ({num_cols[0]})")
                fig.update_layout(template="plotly_white")
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
            elif num_cols and cat_cols:
                # Group by top categories
                cat = cat_cols[0]
                num = num_cols[0]
                grouped = df.groupby(cat)[num].mean().reset_index().sort_values(by=num, ascending=False).head(10)
                fig = px.bar(grouped, x=cat, y=num, title=f"Giá trị trung bình của {num} theo top {cat}", color=num)
                fig.update_layout(template="plotly_white")
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
            elif len(num_cols) >= 2:
                fig = px.scatter(df.head(1000), x=num_cols[0], y=num_cols[1], title=f"Tương quan giữa {num_cols[0]} và {num_cols[1]}")
                fig.update_layout(template="plotly_white")
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
            elif num_cols:
                fig = px.histogram(df, x=num_cols[0], title=f"Phân phối tần suất {num_cols[0]}", nbins=25)
                fig.update_layout(template="plotly_white")
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
            elif cat_cols:
                top_counts = df[cat_cols[0]].value_counts().head(10).reset_index()
                top_counts.columns = [cat_cols[0], "Số lượng"]
                fig = px.bar(top_counts, x=cat_cols[0], y="Số lượng", title=f"Phân phối danh mục {cat_cols[0]}")
                fig.update_layout(template="plotly_white")
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
        except Exception as e:
            chart_html = f"<div class='alert alert-warning'>Không thể sinh biểu đồ tự động: {str(e)}</div>"

        # 3. AI Insights
        prompt = f"""Bạn là chuyên gia phân tích dữ liệu hàng đầu. Dưới đây là tóm tắt thống kê từ tệp CSV:
{summary_text[:3000]}

Hãy đưa ra bản báo cáo nhận xét chi tiết bằng tiếng Việt:
1. Đánh giá tổng quan chất lượng dữ liệu (độ đầy đủ, tính toàn vẹn).
2. Phát hiện các mẫu (patterns), xu hướng hoặc điểm bất thường đáng chú ý.
3. Đề xuất các quyết định hoặc hành động kinh doanh dựa trên các con số này.
4. Gợi ý các hướng phân tích sâu hơn tiếp theo.

Trình bày chuyên nghiệp, rõ ràng bằng Markdown.
"""
        insights = self.ai_service.generate(prompt)

        return {
            "summary": summary_text,
            "columns": cols,
            "row_count": row_count,
            "ai_insights": insights,
            "chart_html": chart_html,
        }

