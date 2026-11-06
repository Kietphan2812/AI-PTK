"""
Export Service - Bộ công cụ xuất bản tài liệu Microsoft Word (.docx) và Excel (.xlsx) cho AI PTK
Hỗ trợ chuyển đổi tự động từ phản hồi của AI (Markdown, bảng biểu, danh sách) sang file chuyên nghiệp.
"""

import io
import re
import datetime
import pandas as pd
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExportService:
    """Dịch vụ tạo và xuất file Word, Excel chuyên nghiệp cho người dùng AI PTK."""

    @staticmethod
    def _set_cell_background(cell, fill_hex: str):
        """Đặt màu nền cho ô trong bảng Word."""
        tcPr = cell._element.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    @classmethod
    def text_to_docx(cls, markdown_text: str, title: str = "TÀI LIỆU AI PTK") -> bytes:
        """Chuyển đổi văn bản phản hồi của AI sang tài liệu Microsoft Word (.docx) được định dạng đẹp."""
        doc = docx.Document()

        # Thiết lập lề trang tiêu chuẩn (2cm)
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Tiêu đề chính
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title)
        title_run.font.size = Pt(20)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(30, 136, 229)  # #1E88E5
        title_p.paragraph_format.space_after = Pt(4)

        # Thông tin bản quyền & thời gian
        tz = datetime.timezone(datetime.timedelta(hours=7))
        now_str = datetime.datetime.now(tz).strftime("%d/%m/%Y lúc %H:%M (Giờ Việt Nam)")
        sub_p = doc.add_paragraph()
        sub_run = sub_p.add_run(f"Được tạo tự động bởi AI PTK | {now_str}")
        sub_run.font.size = Pt(9.5)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(120, 120, 120)
        sub_p.paragraph_format.space_after = Pt(18)

        # Xử lý nội dung Markdown từng dòng
        lines = markdown_text.split("\n")
        in_table = False
        table_rows = []

        def flush_table():
            nonlocal table_rows
            if not table_rows:
                return

            # Lọc bỏ các dòng ngăn cách như |---|---|
            valid_rows = []
            for r in table_rows:
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                    continue
                valid_rows.append(cells)

            if valid_rows:
                max_cols = max(len(r) for r in valid_rows)
                # Đảm bảo mỗi dòng đủ số cột
                norm_rows = []
                for r in valid_rows:
                    padded = r + [""] * (max_cols - len(r))
                    norm_rows.append(padded)

                # Tạo bảng trong Word
                table = doc.add_table(rows=len(norm_rows), cols=max_cols)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.autofit = True

                for i, row_data in enumerate(norm_rows):
                    row = table.rows[i]
                    is_header = (i == 0)
                    for j, cell_text in enumerate(row_data):
                        cell = row.cells[j]
                        cell.text = cell_text
                        p = cell.paragraphs[0]
                        p.paragraph_format.space_before = Pt(3)
                        p.paragraph_format.space_after = Pt(3)

                        if is_header:
                            cls._set_cell_background(cell, "1E88E5")
                            for r in p.runs:
                                r.font.bold = True
                                r.font.color.rgb = RGBColor(255, 255, 255)
                                r.font.size = Pt(10)
                        else:
                            bg_hex = "F8FAFC" if i % 2 == 1 else "FFFFFF"
                            cls._set_cell_background(cell, bg_hex)
                            for r in p.runs:
                                r.font.size = Pt(9.5)

                doc.add_paragraph().paragraph_format.space_after = Pt(6)
            table_rows = []

        for line in lines:
            stripped = line.strip()

            # Nhận diện dòng bảng (| a | b |)
            if stripped.startswith("|") and stripped.endswith("|"):
                in_table = True
                table_rows.append(stripped)
                continue
            else:
                if in_table:
                    flush_table()
                    in_table = False

            # Dòng trống
            if not stripped:
                continue

            # Tiêu đề cấp 1 (# Heading)
            if stripped.startswith("# "):
                h = doc.add_paragraph()
                r = h.add_run(stripped[2:])
                r.font.size = Pt(16)
                r.font.bold = True
                r.font.color.rgb = RGBColor(21, 101, 192)
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(4)

            # Tiêu đề cấp 2 (## Heading)
            elif stripped.startswith("## "):
                h = doc.add_paragraph()
                r = h.add_run(stripped[3:])
                r.font.size = Pt(13.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 136, 229)
                h.paragraph_format.space_before = Pt(10)
                h.paragraph_format.space_after = Pt(3)

            # Tiêu đề cấp 3 (### Heading)
            elif stripped.startswith("### "):
                h = doc.add_paragraph()
                r = h.add_run(stripped[4:])
                r.font.size = Pt(11.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(55, 65, 81)
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(2)

            # Gạch đầu dòng (- hoặc * hoặc •)
            elif stripped.startswith(("- ", "* ", "• ")):
                p = doc.add_paragraph(style="List Bullet")
                content = stripped[2:]
                cls._add_formatted_runs(p, content)
                p.paragraph_format.space_after = Pt(2)

            # Đoạn văn bản thông thường
            else:
                p = doc.add_paragraph()
                cls._add_formatted_runs(p, stripped)
                p.paragraph_format.space_after = Pt(4)

        if in_table:
            flush_table()

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    @staticmethod
    def _add_formatted_runs(paragraph, text: str):
        """Xử lý định dạng in đậm (**text**) trong một đoạn văn."""
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**") and len(part) >= 4:
                run = paragraph.add_run(part[2:-2])
                run.font.bold = True
            else:
                paragraph.add_run(part)

    @classmethod
    def text_to_excel(cls, markdown_text: str, title: str = "BẢNG DỮ LIỆU AI PTK") -> bytes:
        """Chuyển đổi bảng dữ liệu hoặc báo cáo văn bản sang bảng tính Microsoft Excel (.xlsx) chuyên nghiệp."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Du_Lieu_AI_PTK"

        # Định dạng chuẩn
        header_fill = PatternFill(start_color="1E88E5", end_color="1E88E5", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        zebra_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        cell_font = Font(name="Segoe UI", size=10)
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1"),
        )

        # Trích xuất các bảng Markdown (nếu có)
        lines = markdown_text.split("\n")
        table_rows = []
        for line in lines:
            s = line.strip()
            if s.startswith("|") and s.endswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                    continue
                table_rows.append(cells)

        current_row = 1

        # Tiêu đề bảng tính
        ws.merge_cells("A1:E1")
        title_cell = ws["A1"]
        title_cell.value = f"📊 {title.upper()}"
        title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="1E88E5")
        title_cell.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[1].height = 28

        tz = datetime.timezone(datetime.timedelta(hours=7))
        now_str = datetime.datetime.now(tz).strftime("%d/%m/%Y %H:%M")
        ws["A2"].value = f"Nguồn tạo: AI PTK | Thời gian: {now_str}"
        ws["A2"].font = Font(name="Segoe UI", size=9, italic=True, color="64748B")
        current_row = 4

        if table_rows:
            # Ghi bảng dữ liệu trích xuất từ câu trả lời của AI
            for r_idx, row in enumerate(table_rows):
                for c_idx, val in enumerate(row):
                    cell = ws.cell(row=current_row + r_idx, column=c_idx + 1, value=val)
                    cell.border = thin_border
                    if r_idx == 0:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    else:
                        cell.font = cell_font
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                        if r_idx % 2 == 1:
                            cell.fill = zebra_fill
                ws.row_dimensions[current_row + r_idx].height = 22

            # Auto căn chỉnh độ rộng cột
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.row >= current_row and cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

        else:
            # Nếu không có bảng biểu Markdown, xuất báo cáo dạng danh mục và nội dung dòng
            ws.cell(row=current_row, column=1, value="STT").fill = header_fill
            ws.cell(row=current_row, column=1).font = header_font
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=current_row, column=1).border = thin_border

            ws.cell(row=current_row, column=2, value="Nội Dung / Phân Tích").fill = header_fill
            ws.cell(row=current_row, column=2).font = header_font
            ws.cell(row=current_row, column=2).border = thin_border
            ws.row_dimensions[current_row].height = 24

            stt = 1
            for line in lines:
                s = line.strip()
                if not s or s.startswith("---"):
                    continue
                row_num = current_row + stt
                c1 = ws.cell(row=row_num, column=1, value=stt)
                c1.alignment = Alignment(horizontal="center", vertical="top")
                c1.font = cell_font
                c1.border = thin_border

                clean_text = re.sub(r"[*#_`]", "", s)
                c2 = ws.cell(row=row_num, column=2, value=clean_text)
                c2.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                c2.font = cell_font
                c2.border = thin_border

                if stt % 2 == 1:
                    c1.fill = zebra_fill
                    c2.fill = zebra_fill

                ws.row_dimensions[row_num].height = 24
                stt += 1

            ws.column_dimensions["A"].width = 8
            ws.column_dimensions["B"].width = 85

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    @classmethod
    def dataframe_to_excel(cls, df: pd.DataFrame, title: str = "Du_Lieu") -> bytes:
        """Xuất DataFrame sang file Excel với tiêu đề và định dạng màu sắc trang nhã."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title[:30]

        header_fill = PatternFill(start_color="1E88E5", end_color="1E88E5", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        cell_font = Font(name="Segoe UI", size=10)
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1"),
        )

        # Header
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=str(col_name))
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 24

        # Dữ liệu
        for row_idx, row in enumerate(df.itertuples(index=False), 2):
            for col_idx, val in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = cell_font
                cell.border = thin_border
                if row_idx % 2 == 1:
                    cell.fill = zebra_fill
            ws.row_dimensions[row_idx].height = 20

        # Auto width
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
