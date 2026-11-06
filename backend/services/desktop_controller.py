"""
Desktop Controller - Hệ thống điều phối Robot tự động hóa máy tính Windows (RPA & PC Control)
Chuyên trách dịch lệnh tiếng Việt thành các hành động điều khiển chuột, bàn phím, phần mềm và tập tin.
"""

import os
import sys
import time
import subprocess
import json
import re
from pathlib import Path

try:
    import pyautogui
    import pyperclip
    pyautogui.FAILSAFE = True
    HAS_GUI = True
except Exception:
    HAS_GUI = False

from services.export_service import ExportService
from services.ai_service import AIService


class DesktopController:
    """Bộ điều khiển máy tính thông minh tích hợp trí tuệ nhân tạo."""

    def __init__(self, ai_service: AIService = None):
        self.ai = ai_service or AIService()
        self.desktop_dir = Path.home() / "Desktop"
        self.documents_dir = Path.home() / "Documents"

    def execute_command(self, user_command: str) -> dict:
        """Nhận lệnh tiếng Việt của người dùng và tự động thực thi trên máy tính."""
        cmd_lower = user_command.lower().strip()

        # 1. NHẬN DIỆN LỆNH WORD (Mở Word, gõ nội dung, lưu file)
        if any(w in cmd_lower for w in ["word", "văn bản", "soạn thảo", "đơn"]):
            return self._handle_word_command(user_command)

        # 2. NHẬN DIỆN LỆNH EXCEL (Mở Excel, tạo bảng tính, lưu file)
        elif any(w in cmd_lower for w in ["excel", "bảng tính", "bảng số liệu", "thu chi"]):
            return self._handle_excel_command(user_command)

        # 3. NHẬN DIỆN LỆNH CHROME / TRÌNH DUYỆT (Mở web, tìm kiếm Google)
        elif any(w in cmd_lower for w in ["chrome", "web", "tìm kiếm", "google", "youtube"]):
            return self._handle_browser_command(user_command)

        # 4. NHẬN DIỆN LỆNH MỞ PHẦN MỀM THÔNG DỤNG
        elif any(w in cmd_lower for w in ["mở", "bật", "khởi động"]):
            return self._handle_open_app_command(user_command)

        # 5. LỆNH TỰ DO: DÙNG AI PHÂN TÍCH Ý ĐỊNH VÀ THỰC THI
        else:
            return self._handle_ai_dynamic_action(user_command)

    def _handle_word_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở Word, gõ nội dung và tự lưu file ra Desktop."""
        # Trích xuất nội dung cần gõ bằng AI
        prompt = (
            f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
            "Hãy trích xuất:\n"
            "1. Nội dung văn bản chính cần gõ vào Word (nếu người dùng ghi rõ như 'Chào Kiệt nhé', hãy trích xuất đúng nội dung đó. Nếu người dùng bảo viết đơn từ/hợp đồng, hãy tự soạn thảo đầy đủ nội dung).\n"
            "2. Tên file ngắn gọn (không dấu, cách nhau bằng gạch dưới, kết thúc .docx).\n"
            "Trả về JSON định dạng: {\"content\": \"...\", \"filename\": \"...\"} không kèm giải thích."
        )
        ai_reply = self.ai.generate(prompt=prompt)
        content_to_write = "Chào Kiệt nhé!"
        file_name = "TaiLieu_AI_PTK.docx"

        try:
            match = re.search(r"\{.*\}", ai_reply, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                content_to_write = data.get("content", content_to_write)
                file_name = data.get("filename", file_name)
        except Exception:
            if "chào kiệt" in command.lower():
                content_to_write = "Chào Kiệt nhé!"
                file_name = "ChaoKiet.docx"

        if not file_name.endswith(".docx"):
            file_name += ".docx"

        target_path = self.desktop_dir / file_name

        # Tạo file Word bằng ExportService
        docx_bytes = ExportService.text_to_docx(content_to_write, title="TÀI LIỆU AI PTK")
        with open(target_path, "wb") as f:
            f.write(docx_bytes)

        # Mở ứng dụng Microsoft Word hiển thị ngay trước mắt người dùng
        try:
            os.startfile(str(target_path))
            return {
                "success": True,
                "action": "word_created_and_opened",
                "message": f"🎉 Đã tự động tạo file Word với nội dung: '{content_to_write}', lưu tại Desktop và mở Microsoft Word lên màn hình cho bạn!",
                "file_path": str(target_path),
            }
        except Exception as e:
            return {
                "success": True,
                "action": "word_saved",
                "message": f"Đã tạo file tại '{target_path}', nhưng lỗi khi tự động bật Word: {e}",
                "file_path": str(target_path),
            }

    def _handle_excel_command(self, command: str) -> dict:
        """Xử lý tác vụ: Tạo bảng tính Excel, điền dữ liệu và tự mở file."""
        prompt = (
            f"Người dùng ra lệnh tạo bảng Excel: '{command}'.\n"
            "Hãy tạo bảng dữ liệu Markdown đầy đủ (| Cột 1 | Cột 2 | ...) phù hợp với yêu cầu.\n"
            "Kèm dòng cuối: FILENAME: <ten_file.xlsx>"
        )
        ai_reply = self.ai.generate(prompt=prompt)

        file_name = "BangDuLieu_AI_PTK.xlsx"
        fname_m = re.search(r"FILENAME:\s*([^\s\n]+\.xlsx)", ai_reply, re.IGNORECASE)
        if fname_m:
            file_name = fname_m.group(1).strip()

        target_path = self.desktop_dir / file_name
        xlsx_bytes = ExportService.text_to_excel(ai_reply, title="BẢNG DỮ LIỆU AI PTK")
        with open(target_path, "wb") as f:
            f.write(xlsx_bytes)

        try:
            os.startfile(str(target_path))
            return {
                "success": True,
                "action": "excel_created_and_opened",
                "message": f"🎉 Đã tự động tạo bảng tính Excel, lưu tại '{target_path}' và mở Microsoft Excel lên màn hình!",
                "file_path": str(target_path),
            }
        except Exception as e:
            return {
                "success": True,
                "action": "excel_saved",
                "message": f"Đã lưu bảng tính tại '{target_path}', lỗi khi tự mở Excel: {e}",
                "file_path": str(target_path),
            }

    def _handle_browser_command(self, command: str) -> dict:
        """Tự động mở trình duyệt Chrome và tìm kiếm thông tin."""
        search_query = re.sub(r"^(mở chrome|tìm kiếm|tra cứu|tìm|mở web)\s*", "", command, flags=re.IGNORECASE).strip()
        if not search_query:
            url = "https://www.google.com"
            msg = "Đã tự động mở trình duyệt Google Chrome!"
        elif search_query.startswith("http"):
            url = search_query
            msg = f"Đã tự động mở trang web: {url}"
        else:
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            msg = f"Đã tự động mở Chrome và tìm kiếm: '{search_query}'!"

        try:
            subprocess.Popen(f'start "" "{url}"', shell=True)
            return {"success": True, "action": "browser_opened", "message": msg, "url": url}
        except Exception as e:
            return {"success": False, "action": "browser_error", "message": f"Lỗi mở trình duyệt: {e}"}

    def _handle_open_app_command(self, command: str) -> dict:
        """Tự động mở phần mềm máy tính (Notepad, Calculator, Word, Excel, Explorer...)."""
        cmd_l = command.lower()
        app_dict = {
            "notepad": ("notepad", "Sổ tay ghi chú (Notepad)"),
            "máy tính": ("calc", "Máy tính cầm tay (Calculator)"),
            "calculator": ("calc", "Máy tính cầm tay (Calculator)"),
            "word": ("winword", "Microsoft Word"),
            "excel": ("excel", "Microsoft Excel"),
            "chrome": ("start chrome", "Google Chrome"),
            "thư mục": ("explorer", "Quản lý tệp tin (File Explorer)"),
            "desktop": (f'explorer "{self.desktop_dir}"', "Màn hình Desktop"),
        }
        for key, (exe_name, disp_name) in app_dict.items():
            if key in cmd_l:
                try:
                    subprocess.Popen(exe_name, shell=True)
                    return {"success": True, "action": "app_launched", "message": f"✅ Đã tự động bật phần mềm: {disp_name}!"}
                except Exception as e:
                    return {"success": False, "action": "launch_error", "message": f"Không thể bật {disp_name}: {e}"}

        # Nếu không nhận diện được app cụ thể, dùng AI dịch lệnh
        return self._handle_ai_dynamic_action(command)

    def _handle_ai_dynamic_action(self, command: str) -> dict:
        """Dùng AI phân tích lệnh tự do và tạo file/hành động tương ứng."""
        prompt = (
            f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
            "Hãy phân tích và hoàn thành yêu cầu một cách thực tế và chu đáo nhất."
        )
        reply = self.ai.generate(prompt=prompt)
        return {
            "success": True,
            "action": "ai_response",
            "message": f"🤖 AI PTK đã xử lý yêu cầu: {reply[:150]}...",
            "details": reply,
        }
