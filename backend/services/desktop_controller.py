"""
Desktop Controller - Hệ thống điều phối Robot tự động hóa máy tính Windows (RPA & PC Control)
Chuyên trách dịch lệnh tiếng Việt thành các hành động điều khiển chuột, bàn phím, phần mềm và tập tin.
"""

import os
import sys
import time
import datetime
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

        # 1. NHẬN DIỆN LỆNH NOTEPAD / GHI CHÚ
        if any(w in cmd_lower for w in ["notepad", "sổ tay", "ghi chú", "note"]):
            return self._handle_notepad_command(user_command)

        # 2. NHẬN DIỆN LỆNH WORD (Mở Word, gõ nội dung, lưu file)
        elif any(w in cmd_lower for w in ["word", "văn bản", "soạn thảo", "đơn", "tài liệu"]):
            return self._handle_word_command(user_command)

        # 3. NHẬN DIỆN LỆNH EXCEL (Mở Excel, tạo bảng tính, lưu file)
        elif any(w in cmd_lower for w in ["excel", "bảng tính", "bảng số liệu", "thu chi"]):
            return self._handle_excel_command(user_command)

        # 4. NHẬN DIỆN LỆNH CHROME / TRÌNH DUYỆT (Mở web, tìm kiếm Google, Youtube)
        elif any(w in cmd_lower for w in ["chrome", "web", "tìm kiếm", "google", "youtube", "tra cứu"]):
            return self._handle_browser_command(user_command)

        # 5. NHẬN DIỆN LỆNH MỞ PHẦN MỀM THÔNG DỤNG
        elif any(w in cmd_lower for w in ["mở", "bật", "khởi động"]):
            return self._handle_open_app_command(user_command)

        # 6. LỆNH TỰ DO: DÙNG AI PHÂN TÍCH Ý ĐỊNH VÀ THỰC THI
        else:
            return self._handle_ai_dynamic_action(user_command)

    def _clean_command_content(self, command: str, keywords: list) -> str:
        """Trích xuất phần nội dung người dùng muốn viết khi không có mạng/AI."""
        cleaned = command
        for kw in keywords:
            cleaned = re.sub(kw, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^(và|hãy|giúp tôi|hộ tôi|làm ơn)?\s*(ghi|viết|tạo|soạn|gõ)\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(
            r"\s*(nhé|nha|nhé rồi lưu lại|rồi lưu lại|lưu lại|lưu ra desktop|giùm nhé|giúp nhé)\.?$",
            "",
            cleaned,
            flags=re.IGNORECASE
        ).strip()
        return cleaned

    def _handle_word_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở Word, soạn nội dung chi tiết theo lệnh người dùng và tự lưu file ra Desktop."""
        now = datetime.datetime.now()
        now_str = now.strftime("Thứ %A, ngày %d/%m/%Y, lúc %H:%M:%S")

        prompt = (
            f"Bạn là chuyên gia soạn thảo văn bản AI PTK chuyên nghiệp.\n"
            f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
            f"Thời gian hiện tại: {now_str}.\n"
            "Hãy hoàn thành CHÍNH XÁC mọi yêu cầu người dùng đặt ra trong lệnh trên:\n"
            "- Nếu người dùng ghi rõ từ khóa/câu chữ (ví dụ: 'Chào Kiệt', 'thêm 3333', 'ngày tháng'), BẮT BUỘC phải đưa đầy đủ các thông tin đó vào văn bản.\n"
            "- Hãy trình bày văn bản chuẩn đẹp theo định dạng Markdown (Tiêu đề, lời chào, các đoạn văn, ngày tháng nếu có yêu cầu, bảng biểu nếu cần).\n"
            "- Dòng cuối cùng ghi: FILENAME: <tên_file_ngắn_gọn_không_dấu.docx>\n"
            "Viết trực tiếp nội dung văn bản ngay lập tức, không giải thích bên ngoài."
        )

        ai_reply = ""
        try:
            ai_reply = self.ai.generate(prompt=prompt)
        except Exception:
            ai_reply = ""

        is_ai_valid = bool(
            ai_reply
            and len(ai_reply.strip()) > 20
            and "Chưa cấu hình" not in ai_reply
            and "bận (" not in ai_reply
        )

        if is_ai_valid:
            # Lọc bỏ dòng ghi chú cuối nếu có
            content_to_write = re.sub(r"👉\s*Bạn có thể bấm nút.*?$", "", ai_reply, flags=re.DOTALL).strip()
            # Tìm tên file do AI gợi ý
            fname_m = re.search(r"FILENAME:\s*([^\s\n]+\.docx)", content_to_write, re.IGNORECASE)
            if fname_m:
                base_slug = Path(fname_m.group(1)).stem
                content_to_write = re.sub(r"FILENAME:\s*[^\s\n]+\.docx", "", content_to_write, flags=re.IGNORECASE).strip()
            else:
                base_slug = "TaiLieu_AI_PTK"
        else:
            # Xử lý offline thông minh: trích xuất chính xác những gì người dùng yêu cầu
            raw_content = self._clean_command_content(
                command,
                ["mở phần mềm word", "mở word", "vào word", "soạn thảo", "viết vào word", "ghi vào word", "tạo file word", "mở file word"]
            )
            date_addon = ""
            if any(k in command.lower() for k in ["ngày", "tháng", "năm", "thời gian", "hôm nay", "bây giờ"]):
                date_addon = f"\n\n📅 **Thời gian ghi nhận:** {now_str}"

            content_to_write = (
                f"# VĂN BẢN TỰ ĐỘNG - AI PTK\n\n"
                f"**Kính gửi:** Phan Tấn Kiệt\n\n"
                f"### NỘI DUNG VĂN BẢN:\n"
                f"{raw_content}{date_addon}\n\n"
                f"---\n"
                f"*Tài liệu được soạn thảo tự động theo lệnh cá nhân trên hệ thống AI PTK.*"
            )
            slug_words = re.findall(r"[a-zA-Z0-9]+", raw_content)
            base_slug = "_".join(slug_words[:3]) if slug_words else "VanBan"

        # Đảm bảo tên file luôn có timestamp để KHÔNG BAO GIỜ bị lỗi 'Permission denied' do file cũ đang mở
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        target_path = self.desktop_dir / f"{base_slug}_{timestamp}.docx"

        # Tạo file Word bằng ExportService
        docx_bytes = ExportService.text_to_docx(content_to_write, title="TÀI LIỆU AI PTK")

        # Cơ chế chống khóa file thông minh
        for attempt in range(10):
            try:
                with open(target_path, "wb") as f:
                    f.write(docx_bytes)
                break
            except PermissionError:
                target_path = self.desktop_dir / f"{base_slug}_{timestamp}_{attempt+1}.docx"

        # Mở ứng dụng Microsoft Word hiển thị ngay trước mắt người dùng
        try:
            os.startfile(str(target_path))
            preview_snippet = content_to_write.replace("#", "").strip()[:80].replace("\n", " ")
            return {
                "success": True,
                "action": "word_created_and_opened",
                "message": f"🎉 Đã soạn thảo Word thành công: \"{preview_snippet}...\", lưu tại Desktop ({target_path.name}) và mở Microsoft Word cho bạn!",
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
        now = datetime.datetime.now()
        now_str = now.strftime("%d/%m/%Y %H:%M:%S")

        prompt = (
            f"Bạn là chuyên gia bảng tính Excel AI PTK.\n"
            f"Người dùng ra lệnh tạo bảng Excel: '{command}'.\n"
            f"Thời gian: {now_str}.\n"
            "Hãy tạo bảng dữ liệu Markdown đầy đủ (| Cột 1 | Cột 2 | ...) phù hợp với yêu cầu.\n"
            "Dòng cuối cùng ghi: FILENAME: <ten_file.xlsx>\n"
            "Bắt đầu bảng dữ liệu ngay lập tức, không giải thích bên ngoài."
        )

        ai_reply = ""
        try:
            ai_reply = self.ai.generate(prompt=prompt)
        except Exception:
            ai_reply = ""

        is_ai_valid = bool(
            ai_reply
            and "|" in ai_reply
            and "Chưa cấu hình" not in ai_reply
        )

        if is_ai_valid:
            table_content = ai_reply
            fname_m = re.search(r"FILENAME:\s*([^\s\n]+\.xlsx)", ai_reply, re.IGNORECASE)
            base_slug = Path(fname_m.group(1)).stem if fname_m else "BangDuLieu"
        else:
            raw = self._clean_command_content(
                command,
                ["mở phần mềm excel", "mở excel", "vào excel", "bảng tính", "tạo bảng", "tạo file excel"]
            )
            table_content = (
                f"| STT | Danh Mục / Yêu Cầu | Ghi Chú | Thời Gian |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| 1 | {raw or 'Dữ liệu quản lý'} | Tự động tạo bởi AI PTK | {now_str} |\n"
                f"| 2 | Tổng kết | Hoàn tất | {now_str} |"
            )
            base_slug = "BangDuLieu"

        timestamp = now.strftime("%Y%m%d_%H%M%S")
        target_path = self.desktop_dir / f"{base_slug}_{timestamp}.xlsx"

        xlsx_bytes = ExportService.text_to_excel(table_content, title="BẢNG DỮ LIỆU AI PTK")

        for attempt in range(10):
            try:
                with open(target_path, "wb") as f:
                    f.write(xlsx_bytes)
                break
            except PermissionError:
                target_path = self.desktop_dir / f"{base_slug}_{timestamp}_{attempt+1}.xlsx"

        try:
            os.startfile(str(target_path))
            return {
                "success": True,
                "action": "excel_created_and_opened",
                "message": f"🎉 Đã tự động tạo bảng tính Excel '{target_path.name}', lưu tại Desktop và mở Microsoft Excel lên màn hình!",
                "file_path": str(target_path),
            }
        except Exception as e:
            return {
                "success": True,
                "action": "excel_saved",
                "message": f"Đã lưu bảng tính tại '{target_path}', lỗi khi tự mở Excel: {e}",
                "file_path": str(target_path),
            }

    def _handle_notepad_command(self, command: str) -> dict:
        """Xử lý tác vụ ghi chú Notepad."""
        now = datetime.datetime.now()
        raw = self._clean_command_content(
            command,
            ["mở notepad", "mở sổ tay", "mở ghi chú", "vào notepad", "ghi chú"]
        )
        content = (
            f"=== GHI CHÚ NHANH - AI PTK ===\n"
            f"Thời gian: {now.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"Nội dung:\n{raw}\n"
        )
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        target_path = self.desktop_dir / f"GhiChu_{timestamp}.txt"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        try:
            os.startfile(str(target_path))
            return {
                "success": True,
                "action": "notepad_created_and_opened",
                "message": f"📝 Đã tạo ghi chú Notepad tại '{target_path.name}' và mở lên màn hình!",
                "file_path": str(target_path),
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi mở Notepad: {e}"}

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
