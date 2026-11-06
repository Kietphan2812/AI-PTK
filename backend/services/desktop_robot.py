"""
Desktop Robot - Hệ thống điều khiển máy tính tự động bằng AI (RPA & PC Control)
Chạy trên máy tính cá nhân (Windows): Nhận lệnh bằng tiếng Việt để mở Word, gõ chữ, lưu file, mở Excel, Chrome...
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from services.export_service import ExportService


class DesktopRobot:
    """Robot điều khiển phần mềm và hệ điều hành Windows theo lệnh của người dùng."""

    def __init__(self):
        self.desktop_dir = Path.home() / "Desktop"
        self.documents_dir = Path.home() / "Documents"

    def open_word_and_type(self, text: str = "Chào Kiệt nhé", filename: str = "ChaoKiet.docx") -> dict:
        """
        Thực hiện chính xác yêu cầu:
        1. Tạo tài liệu Word với nội dung người dùng yêu cầu (ví dụ: 'Chào Kiệt nhé')
        2. Tự động lưu file ngay trên màn hình Desktop của máy tính
        3. Tự động mở phần mềm Microsoft Word lên màn hình trước mắt người dùng
        """
        if not filename.endswith(".docx"):
            filename += ".docx"

        file_path = self.desktop_dir / filename
        title_doc = "TÀI LIỆU TỰ ĐỘNG - AI PTK"
        formatted_md = f"# {title_doc}\n\n{text}"

        docx_bytes = ExportService.text_to_docx(formatted_md, title=title_doc)
        with open(file_path, "wb") as f:
            f.write(docx_bytes)

        # Mở trực tiếp phần mềm Microsoft Word trên máy tính
        try:
            os.startfile(str(file_path))
            return {
                "success": True,
                "message": f"✅ Đã tự động tạo file Word, lưu tại '{file_path}' và mở phần mềm Microsoft Word lên màn hình cho bạn!",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Đã lưu file tại '{file_path}' nhưng lỗi khi tự mở Word: {e}",
                "file_path": str(file_path),
            }

    def open_excel_and_save(self, table_text: str, filename: str = "BangDuLieu.xlsx") -> dict:
        """Tự động tạo bảng tính Excel, lưu ra Desktop và mở phần mềm Excel lên màn hình."""
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        file_path = self.desktop_dir / filename
        xlsx_bytes = ExportService.text_to_excel(table_text, title="BẢNG DỮ LIỆU TỰ ĐỘNG")
        with open(file_path, "wb") as f:
            f.write(xlsx_bytes)

        try:
            os.startfile(str(file_path))
            return {
                "success": True,
                "message": f"✅ Đã tự động tạo file Excel, lưu tại '{file_path}' và mở Microsoft Excel lên màn hình!",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Đã lưu file tại '{file_path}' nhưng lỗi khi tự mở Excel: {e}",
                "file_path": str(file_path),
            }

    def launch_application(self, app_name: str) -> dict:
        """Tự động mở các phần mềm thông dụng trên máy tính."""
        app_map = {
            "word": "winword",
            "excel": "excel",
            "notepad": "notepad",
            "chrome": "start chrome",
            "calculator": "calc",
            "máy tính": "calc",
            "explorer": "explorer",
            "cmd": "start cmd",
        }
        cmd = app_map.get(app_name.lower().strip(), app_name)
        try:
            subprocess.Popen(cmd, shell=True)
            return {"success": True, "message": f"✅ Đã tự động bật phần mềm '{app_name}' trên máy tính!"}
        except Exception as e:
            return {"success": False, "message": f"Không thể bật '{app_name}': {e}"}

