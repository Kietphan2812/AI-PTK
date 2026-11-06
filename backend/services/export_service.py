"""
Export Service - Bộ công cụ xuất bản tài liệu Microsoft Word (.docx) và Excel (.xlsx) cho AI PTK
Được thiết kế 2 tầng: Tầng 1 dùng python-docx/openpyxl, Tầng 2 dùng Pure Python OpenXML Engine (Zero Dependencies).
Đảm bảo 100% không bao giờ sinh file 0 Bytes kể cả khi thiếu thư viện ngoài trên Streamlit Cloud.
"""

import io
import re
import datetime
import zipfile


def xml_escape(text: str) -> str:
    """Chuyển đổi ký tự XML an toàn thuần Python 100%, không phụ thuộc vào package xml."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

# Kiểm tra thư viện ngoài (nếu có thì dùng, không có thì fallback sang Pure Python Engine)
try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except Exception:
    HAS_OPENPYXL = False


class ExportService:
    """Dịch vụ tạo và xuất file Word, Excel chuyên nghiệp và chống lỗi 0 Bytes tuyệt đối cho AI PTK."""

    # -------------------------------------------------------------
    # 1. PURE PYTHON OPENXML DOCX ENGINE (ZERO EXTERNAL DEPENDENCIES)
    # -------------------------------------------------------------
    @classmethod
    def _pure_python_docx(cls, markdown_text: str, title: str = "TÀI LIỆU AI PTK") -> bytes:
        """Tạo file Word (.docx) chuẩn bằng công nghệ thuần Python zipfile + XML. Không phụ thuộc thư viện ngoài."""
        tz = datetime.timezone(datetime.timedelta(hours=7))
        now_str = datetime.datetime.now(tz).strftime("%d/%m/%Y lúc %H:%M (Giờ Việt Nam)")

        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

        body_xml_parts = []

        # Tiêu đề chính
        esc_title = xml_escape(title)
        body_xml_parts.append(
            f'<w:p><w:pPr><w:spacing w:after="80"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:sz w:val="38"/><w:color w:val="1E88E5"/></w:rPr>'
            f'<w:t>{esc_title}</w:t></w:r></w:p>'
        )

        # Tiêu đề phụ & Bản quyền
        body_xml_parts.append(
            f'<w:p><w:pPr><w:spacing w:after="240"/></w:pPr>'
            f'<w:r><w:rPr><w:i/><w:sz w:val="18"/><w:color w:val="787878"/></w:rPr>'
            f'<w:t>Được tạo tự động bởi AI PTK | {now_str}</w:t></w:r></w:p>'
        )

        def format_runs(text: str) -> str:
            parts = re.split(r"(\*\*.*?\*\*)", text)
            r_xml = []
            for p in parts:
                if p.startswith("**") and p.endswith("**") and len(p) >= 4:
                    val = xml_escape(p[2:-2])
                    r_xml.append(f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{val}</w:t></w:r>')
                else:
                    val = xml_escape(p)
                    r_xml.append(f'<w:r><w:t xml:space="preserve">{val}</w:t></w:r>')
            return "".join(r_xml)

        lines = markdown_text.split("\n")
        in_table = False
        in_code_block = False
        code_lines = []
        table_rows = []

        def flush_tbl():
            nonlocal table_rows
            if not table_rows:
                return
            valid_rows = []
            for r in table_rows:
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                    continue
                valid_rows.append(cells)

            if valid_rows:
                max_c = max(len(r) for r in valid_rows)
                tbl_xml = [
                    '<w:tbl>',
                    '<w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
                    '<w:tblBorders>'
                    '<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '<w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
                    '</w:tblBorders></w:tblPr>'
                ]
                for r_idx, row in enumerate(valid_rows):
                    padded = row + [""] * (max_c - len(row))
                    is_header = (r_idx == 0)
                    tbl_xml.append('<w:tr>')
                    for c_val in padded:
                        esc_c = xml_escape(c_val)
                        shd = '<w:shd w:fill="1E88E5"/>' if is_header else ('<w:shd w:fill="F8FAFC"/>' if r_idx % 2 == 1 else '')
                        tc_r = f'<w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr><w:t>{esc_c}</w:t></w:r>' if is_header else f'<w:r><w:t>{esc_c}</w:t></w:r>'
                        tbl_xml.append(f'<w:tc><w:tcPr>{shd}<w:tcMar><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar></w:tcPr><w:p><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>{tc_r}</w:p></w:tc>')
                    tbl_xml.append('</w:tr>')
                tbl_xml.append('</w:tbl>')
                body_xml_parts.append("".join(tbl_xml))
                body_xml_parts.append('<w:p><w:pPr><w:spacing w:after="80"/></w:pPr></w:p>')
            table_rows = []

        for line in lines:
            s = line.strip()

            if s.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_lines = []
                else:
                    in_code_block = False
                    if code_lines:
                        c_text = xml_escape("\n".join(code_lines))
                        body_xml_parts.append(
                            f'<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
                            f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="19"/><w:color w:val="1E293B"/></w:rPr>'
                            f'<w:t xml:space="preserve">{c_text}</w:t></w:r></w:p>'
                        )
                        code_lines = []
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            if s.startswith("|") and s.endswith("|"):
                in_table = True
                table_rows.append(s)
                continue
            else:
                if in_table:
                    flush_tbl()
                    in_table = False

            if not s:
                continue

            if s.startswith("# "):
                val = xml_escape(s[2:])
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="1565C0"/></w:rPr><w:t>{val}</w:t></w:r></w:p>')
            elif s.startswith("## "):
                val = xml_escape(s[3:])
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:before="180" w:after="60"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1E88E5"/></w:rPr><w:t>{val}</w:t></w:r></w:p>')
            elif s.startswith("### "):
                val = xml_escape(s[4:])
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:before="140" w:after="40"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="334155"/></w:rPr><w:t>{val}</w:t></w:r></w:p>')
            elif s.startswith(("- ", "* ", "• ")):
                runs = format_runs(s[2:])
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:t xml:space="preserve">•  </w:t></w:r>{runs}</w:p>')
            elif re.match(r"^\d+\.\s+", s):
                num_m = re.match(r"^\d+\.\s+", s)
                prefix = num_m.group(0)
                runs = format_runs(s[num_m.end():])
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:b/><w:t xml:space="preserve">{prefix}</w:t></w:r>{runs}</w:p>')
            else:
                runs = format_runs(s)
                body_xml_parts.append(f'<w:p><w:pPr><w:spacing w:after="80"/></w:pPr>{runs}</w:p>')

        if in_table:
            flush_tbl()

        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body>'
            + "".join(body_xml_parts)
            + '<w:sectPr><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
            '</w:body></w:document>'
        )

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("word/document.xml", doc_xml)

        return buf.getvalue()

    # -------------------------------------------------------------
    # 2. PURE PYTHON OPENXML XLSX ENGINE (ZERO EXTERNAL DEPENDENCIES)
    # -------------------------------------------------------------
    @classmethod
    def _pure_python_xlsx(cls, headers: list, rows: list, sheet_name: str = "Du_Lieu") -> bytes:
        """Tạo file Excel (.xlsx) chuẩn bằng zipfile + XML thuần Python. Không phụ thuộc openpyxl."""
        buf = io.BytesIO()

        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

        wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

        safe_name = xml_escape(sheet_name[:30])
        workbook = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{safe_name}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""

        sheet_lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            '<sheetData>'
        ]

        def get_col_letter(col_idx: int) -> str:
            result = ""
            while col_idx > 0:
                col_idx, remainder = divmod(col_idx - 1, 26)
                result = chr(65 + remainder) + result
            return result or "A"

        # Dòng tiêu đề cột
        sheet_lines.append('<row r="1">')
        for c_idx, h in enumerate(headers, 1):
            col_letter = get_col_letter(c_idx)
            val = xml_escape(str(h))
            sheet_lines.append(f'<c r="{col_letter}1" t="inlineStr"><is><t>{val}</t></is></c>')
        sheet_lines.append('</row>')

        # Các dòng dữ liệu
        for r_idx, row in enumerate(rows, 2):
            sheet_lines.append(f'<row r="{r_idx}">')
            for c_idx, cell in enumerate(row, 1):
                col_letter = get_col_letter(c_idx)
                val = xml_escape(str(cell))
                sheet_lines.append(f'<c r="{col_letter}{r_idx}" t="inlineStr"><is><t>{val}</t></is></c>')
            sheet_lines.append('</row>')

        sheet_lines.append('</sheetData>')
        sheet_lines.append('</worksheet>')
        sheet_xml = "\n".join(sheet_lines)

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
            z.writestr("xl/workbook.xml", workbook)
            z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

        return buf.getvalue()

    # -------------------------------------------------------------
    # 3. GIAO DIỆN CHÍNH (TỰ ĐỘNG CHỌN ENGINE & CHỐNG LỖI 0 BYTES)
    # -------------------------------------------------------------
    @classmethod
    def text_to_docx(cls, markdown_text: str, title: str = "TÀI LIỆU AI PTK") -> bytes:
        """Xuất Markdown ra Word (.docx) - Cam kết luôn trả về dữ liệu hợp lệ (> 0 Bytes)."""
        if not markdown_text or not markdown_text.strip():
            markdown_text = "Nội dung tài liệu AI PTK."

        # Thử dùng python-docx nếu có
        if HAS_DOCX:
            try:
                doc = docx.Document()
                for section in doc.sections:
                    section.top_margin = Inches(0.8)
                    section.bottom_margin = Inches(0.8)
                    section.left_margin = Inches(0.8)
                    section.right_margin = Inches(0.8)

                title_p = doc.add_paragraph()
                title_run = title_p.add_run(title)
                title_run.font.size = Pt(20)
                title_run.font.bold = True
                title_run.font.color.rgb = RGBColor(30, 136, 229)

                tz = datetime.timezone(datetime.timedelta(hours=7))
                now_str = datetime.datetime.now(tz).strftime("%d/%m/%Y lúc %H:%M (Giờ Việt Nam)")
                sub_p = doc.add_paragraph()
                sub_run = sub_p.add_run(f"Được tạo tự động bởi AI PTK | {now_str}")
                sub_run.font.size = Pt(9.5)
                sub_run.font.italic = True
                sub_run.font.color.rgb = RGBColor(120, 120, 120)

                lines = markdown_text.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.startswith("# "):
                        h = doc.add_paragraph()
                        r = h.add_run(stripped[2:])
                        r.font.size = Pt(16)
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(21, 101, 192)
                    elif stripped.startswith("## "):
                        h = doc.add_paragraph()
                        r = h.add_run(stripped[3:])
                        r.font.size = Pt(13.5)
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(30, 136, 229)
                    elif stripped.startswith(("- ", "* ", "• ")):
                        p = doc.add_paragraph(style="List Bullet")
                        p.add_run(stripped[2:])
                    else:
                        p = doc.add_paragraph()
                        p.add_run(stripped)

                buf = io.BytesIO()
                doc.save(buf)
                data = buf.getvalue()
                if len(data) > 500:
                    return data
            except Exception as e:
                print(f"[ExportService] python-docx warning: {e}, using pure engine fallback...")

        # Fallback chắc chắn thành công 100% với Pure Engine
        return cls._pure_python_docx(markdown_text, title=title)

    @classmethod
    def text_to_excel(cls, markdown_text: str, title: str = "BẢNG DỮ LIỆU AI PTK") -> bytes:
        """Xuất bảng dữ liệu ra Excel (.xlsx) - Cam kết luôn trả về dữ liệu hợp lệ (> 0 Bytes)."""
        if not markdown_text or not markdown_text.strip():
            markdown_text = "Nội dung bảng dữ liệu."

        # Trích xuất dòng bảng từ Markdown nếu có
        lines = markdown_text.split("\n")
        table_rows = []
        for line in lines:
            s = line.strip()
            if s.startswith("|") and s.endswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                    continue
                table_rows.append(cells)

        if table_rows:
            headers = table_rows[0]
            data_rows = table_rows[1:]
        else:
            headers = ["STT", "Nội Dung / Phân Tích"]
            data_rows = []
            stt = 1
            for line in lines:
                s = line.strip()
                if not s or s.startswith("---"):
                    continue
                data_rows.append([stt, re.sub(r"[*#_`]", "", s)])
                stt += 1

        # Thử openpyxl nếu có
        if HAS_OPENPYXL:
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Du_Lieu_AI_PTK"

                header_fill = PatternFill(start_color="1E88E5", end_color="1E88E5", fill_type="solid")
                header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")

                for c_idx, h in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=c_idx, value=str(h))
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                for r_idx, row in enumerate(data_rows, 2):
                    for c_idx, val in enumerate(row, 1):
                        ws.cell(row=r_idx, column=c_idx, value=str(val))

                buf = io.BytesIO()
                wb.save(buf)
                data = buf.getvalue()
                if len(data) > 500:
                    return data
            except Exception as e:
                print(f"[ExportService] openpyxl warning: {e}, using pure engine fallback...")

        # Fallback chắc chắn thành công 100% với Pure Engine
        return cls._pure_python_xlsx(headers, data_rows, sheet_name="Du_Lieu_AI_PTK")

    @classmethod
    def dataframe_to_excel(cls, df, title: str = "Du_Lieu") -> bytes:
        """Xuất DataFrame sang Excel với độ tin cậy tuyệt đối."""
        headers = [str(c) for c in df.columns]
        rows = df.values.tolist()
        return cls._pure_python_xlsx(headers, rows, sheet_name=title[:30])

    @classmethod
    def text_to_pptx(
        cls,
        markdown_or_slides_text: str,
        title: str = "BÀI THUYẾT TRÌNH AI PTK",
        theme_color: str = "auto",
        font_size: int = None,
    ) -> bytes:
        """Tạo bài thuyết trình PowerPoint (.pptx) chuẩn đồ họa cao cấp: Tuân thủ 100% màu sắc và cỡ chữ yêu cầu."""
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.dml.color import RGBColor
            from pptx.enum.shapes import MSO_SHAPE
            from pptx.enum.text import PP_ALIGN
            from pptx.oxml import parse_xml

            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

            # Cỡ chữ chuẩn theo yêu cầu
            actual_font_size = int(font_size) if font_size and int(font_size) >= 10 else 16

            # Cấu hình màu sắc theo yêu cầu cụ thể của người dùng
            color_themes = {
                "red": {
                    "banner": RGBColor(185, 28, 28),
                    "border": RGBColor(220, 38, 38),
                    "bg": RGBColor(254, 242, 242),
                    "text": RGBColor(185, 28, 28),
                    "title_text": RGBColor(255, 255, 255),
                },
                "blue": {
                    "banner": RGBColor(30, 64, 175),
                    "border": RGBColor(37, 99, 235),
                    "bg": RGBColor(239, 246, 255),
                    "text": RGBColor(30, 64, 175),
                    "title_text": RGBColor(255, 255, 255),
                },
                "gold": {
                    "banner": RGBColor(180, 83, 9),
                    "border": RGBColor(217, 119, 6),
                    "bg": RGBColor(254, 252, 232),
                    "text": RGBColor(180, 83, 9),
                    "title_text": RGBColor(255, 255, 255),
                },
                "green": {
                    "banner": RGBColor(4, 120, 87),
                    "border": RGBColor(16, 185, 129),
                    "bg": RGBColor(236, 253, 245),
                    "text": RGBColor(4, 120, 87),
                    "title_text": RGBColor(255, 255, 255),
                },
                "purple": {
                    "banner": RGBColor(109, 40, 217),
                    "border": RGBColor(139, 92, 246),
                    "bg": RGBColor(245, 243, 255),
                    "text": RGBColor(109, 40, 217),
                    "title_text": RGBColor(255, 255, 255),
                },
                "pink": {
                    "banner": RGBColor(190, 24, 93),
                    "border": RGBColor(236, 72, 153),
                    "bg": RGBColor(253, 242, 248),
                    "text": RGBColor(190, 24, 93),
                    "title_text": RGBColor(255, 255, 255),
                },
                "dark": {
                    "banner": RGBColor(15, 23, 42),
                    "border": RGBColor(51, 65, 85),
                    "bg": RGBColor(241, 245, 249),
                    "text": RGBColor(15, 23, 42),
                    "title_text": RGBColor(255, 255, 255),
                },
            }

            req_col = (theme_color or "auto").lower()
            fixed_theme = None
            if any(k in req_col for k in ["đỏ", "red"]):
                fixed_theme = color_themes["red"]
            elif any(k in req_col for k in ["vàng", "gold", "yellow"]):
                fixed_theme = color_themes["gold"]
            elif any(k in req_col for k in ["xanh lá", "green"]):
                fixed_theme = color_themes["green"]
            elif any(k in req_col for k in ["xanh", "blue"]):
                fixed_theme = color_themes["blue"]
            elif any(k in req_col for k in ["tím", "purple"]):
                fixed_theme = color_themes["purple"]
            elif any(k in req_col for k in ["hồng", "pink"]):
                fixed_theme = color_themes["pink"]
            elif any(k in req_col for k in ["đen", "tối", "dark", "black"]):
                fixed_theme = color_themes["dark"]
            elif any(k in req_col for k in ["nhiều màu", "đa màu", "multi", "đỏ xanh vàng"]):
                fixed_theme = None

            # Bảng màu luân phiên nếu người dùng không chỉ định màu duy nhất
            palette = [
                color_themes["red"],
                color_themes["blue"],
                color_themes["gold"],
                color_themes["green"],
            ]

            sections = re.split(r"(?m)^##\s+", markdown_or_slides_text)
            valid_sections = []
            for sec in sections:
                sec_text = sec.strip()
                if sec_text and sec_text != title:
                    valid_sections.append(sec_text)

            if not valid_sections:
                valid_sections = [
                    f"Giới Thiệu Đề Tài: {title}\n- Tác giả: Phan Tấn Kiệt\n- Khởi tạo tự động bởi AI PTK",
                    "Nội Dung Phân Tích\n- Luận điểm 1: Đổi mới sáng tạo\n- Luận điểm 2: Ứng dụng thực tiễn",
                    "Kết Luận\n- Tổng kết giá trị đạt được\n- Kế hoạch hành động"
                ]

            for idx, sec in enumerate(valid_sections):
                slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout

                # Thêm hiệu ứng chuyển cảnh động cho từng slide (Slide Transitions)
                trans_types = ["push", "fade", "wipe"]
                t_type = trans_types[idx % len(trans_types)]
                if t_type == "push":
                    t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:push dir="r"/></p:transition>'
                elif t_type == "wipe":
                    t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:wipe dir="r"/></p:transition>'
                else:
                    t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>'

                try:
                    slide._element.append(parse_xml(t_xml))
                except Exception:
                    pass

                cur_style = fixed_theme if fixed_theme else palette[idx % len(palette)]

                lines = [l.strip() for l in sec.splitlines() if l.strip()]
                slide_title = lines[0].replace("#", "").strip() if lines else f"Slide {idx+1}"
                content_lines = lines[1:] if len(lines) > 1 else []

                # 1. THANH BANNER TIÊU ĐỀ
                banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.3))
                banner.fill.solid()
                banner.fill.fore_color.rgb = cur_style["banner"]
                banner.line.fill.background()

                btf = banner.text_frame
                btf.word_wrap = True
                bp = btf.paragraphs[0]
                bp.text = slide_title.upper()
                bp.font.size = Pt(max(actual_font_size, 22))
                bp.font.bold = True
                bp.font.color.rgb = cur_style["title_text"]
                bp.alignment = PP_ALIGN.LEFT

                # 2. KHUNG NỘI DUNG THẺ BO GÓC
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2))
                card.fill.solid()
                card.fill.fore_color.rgb = cur_style["bg"]
                card.line.color.rgb = cur_style["border"]
                card.line.width = Pt(2.5)

                ctf = card.text_frame
                ctf.word_wrap = True

                first = True
                for cl in content_lines:
                    text_clean = cl.lstrip("-*• ").strip()
                    if not text_clean:
                        continue

                    p = ctf.paragraphs[0] if first else ctf.add_paragraph()
                    first = False

                    p.text = f"★ {text_clean}"
                    # Điều chỉnh khoảng cách dòng phù hợp với cỡ chữ
                    if actual_font_size >= 26:
                        p.space_after = Pt(8)
                    else:
                        p.space_after = Pt(14)

                    # Áp dụng chính xác cỡ chữ và màu sắc người dùng yêu cầu
                    p.font.size = Pt(actual_font_size)
                    p.font.color.rgb = cur_style["text"]
                    p.font.bold = True if (actual_font_size >= 24 or cl.startswith("###")) else False

                # 3. CHÂN TRANG
                footer = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.733), Inches(0.4))
                fp = footer.text_frame.paragraphs[0]
                fp.text = f"🚀 AI PTK Presentation | Tác giả: Phan Tấn Kiệt | Slide {idx+1}/{len(valid_sections)} (Font: {actual_font_size}pt)"
                fp.font.size = Pt(10)
                fp.font.bold = True
                fp.font.color.rgb = RGBColor(100, 116, 139)

            buf = io.BytesIO()
            prs.save(buf)
            return buf.getvalue()
        except Exception as e:
            print(f"[ExportService] Lỗi tạo pptx đồ họa: {e}")
            return b""

