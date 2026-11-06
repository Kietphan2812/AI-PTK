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
import urllib.request
import urllib.parse
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

        # 1. NHẬN DIỆN LỆNH YOUTUBE / PHÁT NHẠC / XEM VIDEO (Ưu tiên cao nhất)
        if any(w in cmd_lower for w in ["youtube", "bài nhạc", "bài hát", "phát nhạc", "bật nhạc", "nghe nhạc", "phát bài", "remix", "rimex", "mv", "video"]):
            return self._handle_youtube_command(user_command)

        # 2. NHẬN DIỆN LỆNH NOTEPAD / GHI CHÚ
        elif any(w in cmd_lower for w in ["notepad", "sổ tay", "ghi chú", "note"]):
            return self._handle_notepad_command(user_command)

        # 3. NHẬN DIỆN LỆNH WORD (Mở Word, gõ nội dung, lưu file)
        elif any(w in cmd_lower for w in ["word", "văn bản", "soạn thảo", "đơn", "tài liệu"]):
            return self._handle_word_command(user_command)

        # 4. NHẬN DIỆN LỆNH EXCEL (Mở Excel, tạo bảng tính, lưu file)
        elif any(w in cmd_lower for w in ["excel", "bảng tính", "bảng số liệu", "thu chi"]):
            return self._handle_excel_command(user_command)

        # 5. NHẬN DIỆN LỆNH CHROME / TRÌNH DUYỆT (Mở web, tìm kiếm Google)
        elif any(w in cmd_lower for w in ["chrome", "web", "tìm kiếm", "google", "tra cứu", "lên mạng"]):
            return self._handle_browser_command(user_command)

        # 6. NHẬN DIỆN LỆNH MỞ PHẦN MỀM THÔNG DỤNG
        elif any(w in cmd_lower for w in ["mở", "bật", "khởi động"]):
            return self._handle_open_app_command(user_command)

        # 7. LỆNH TỰ DO: DÙNG AI PHÂN TÍCH Ý ĐỊNH VÀ THỰC THI
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

    def _handle_youtube_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở YouTube, tìm kiếm bài hát/video và TỰ ĐỘNG PHÁT BÀI NHẠC trực tiếp."""
        # 1. Trích xuất tên bài hát/nội dung
        ai_query = ""
        try:
            p = (
                f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
                "Hãy trích xuất TÊN BÀI HÁT / THỂ LOẠI NHẠC / NỘI DUNG YOUTUBE mà người dùng muốn nghe (ví dụ: 'nhạc remix', 'Sơn Tùng M-TP', 'nhạc trẻ remix').\n"
                "Chỉ trả về cụm từ tìm kiếm ngắn gọn, không giải thích."
            )
            ai_query = self.ai.generate(prompt=p).strip()
            ai_query = re.sub(r'["\']', '', ai_query).strip()
            if len(ai_query) > 50 or "Chưa cấu hình" in ai_query or "\n" in ai_query:
                ai_query = ""
        except Exception:
            ai_query = ""

        if not ai_query:
            c = command.lower()
            drop_phrases = [
                "mở gg chrome", "mở google chrome", "mở chrome", "mở trình duyệt",
                "tim youtube..com", "tìm youtube..com", "vào youtube..com", "youtube..com",
                "tim youtube.com", "tìm youtube.com", "vào youtube.com", "youtube.com",
                "tim youtube", "tìm youtube", "vào youtube", "lên youtube", "youtube",
                "rồi tìm 1 bài nhạc", "rồi tìm bài nhạc", "rồi tìm 1 bài", "rồi tìm bài", "rồi tìm",
                "tìm 1 bài nhạc", "tìm bài nhạc", "tìm 1 bài", "tìm bài", "tìm kiếm", "tìm",
                "bấm vô phát bài nhạc luôn", "bấm vô phát bài luôn", "bấm phát bài nhạc luôn",
                "bấm vô phát luôn", "bấm phát luôn", "phát bài nhạc luôn", "phát bài hát luôn",
                "phát nhạc luôn", "phát luôn", "nghe luôn", "bật bài nhạc", "bật bài hát",
                "bật nhạc", "nghe nhạc", "phát bài", "phát", "bật", "nghe", "xem",
                "luôn nhé", "luôn nha", "luôn đi", "nhé", "nha", "đi", "luôn",
                "bấm vô", "bấm vào", "click vào"
            ]
            for p in drop_phrases:
                c = c.replace(p, " ")
            c = re.sub(r"\s+", " ", c).strip()
            c = c.replace("rimex", "remix")
            ai_query = c or "nhạc remix"

        # 2. Tìm ID video trên YouTube để PHÁT NGAY LẬP TỨC
        enc = urllib.parse.quote(ai_query)
        search_url = f"https://www.youtube.com/results?search_query={enc}"
        target_url = search_url
        video_found = False

        try:
            req = urllib.request.Request(
                search_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode("utf-8")
            vids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
            if vids:
                target_url = f"https://www.youtube.com/watch?v={vids[0]}"
                video_found = True
        except Exception:
            pass

        # 3. Mở Google Chrome hoặc trình duyệt mặc định với video đó
        try:
            subprocess.Popen(f'start chrome "{target_url}"', shell=True)
        except Exception:
            subprocess.Popen(f'start "" "{target_url}"', shell=True)

        if video_found:
            msg = f"🎵 Đã tự động mở YouTube và ĐANG PHÁT BÀI NHẠC: '{ai_query}' ngay lập tức cho bạn!"
        else:
            msg = f"🎵 Đã tự động mở YouTube tìm kiếm bài nhạc: '{ai_query}'!"

        return {
            "success": True,
            "action": "youtube_played",
            "message": msg,
            "url": target_url,
            "query": ai_query
        }

    def _handle_word_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở Word, soạn nội dung chi tiết theo lệnh người dùng và tự lưu file ra Desktop."""
        now = datetime.datetime.now()
        now_str = now.strftime("Thứ %A, ngày %d/%m/%Y, lúc %H:%M:%S")

        prompt = (
            f"Bạn là chuyên gia soạn thảo văn bản AI PTK chuyên nghiệp.\n"
            f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
            f"Thời gian hiện tại: {now_str}.\n"
            "Hãy hoàn thành CHÍNH XÁC mọi yêu cầu người dùng đặt ra trong lệnh trên:\n"
            "- Nếu người dùng ghi rõ từ khóa/câu chữ (ví dụ: 'Chào Kiệt', 'thêm 3333', 'ngày tháng', 'ghi tên Kiệt 100 lần'), BẮT BUỘC phải đưa đầy đủ các thông tin đó vào văn bản.\n"
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
            content_to_write = re.sub(r"👉\s*Bạn có thể bấm nút.*?$", "", ai_reply, flags=re.DOTALL).strip()
            fname_m = re.search(r"FILENAME:\s*([^\s\n]+\.docx)", content_to_write, re.IGNORECASE)
            if fname_m:
                base_slug = Path(fname_m.group(1)).stem
                content_to_write = re.sub(r"FILENAME:\s*[^\s\n]+\.docx", "", content_to_write, flags=re.IGNORECASE).strip()
            else:
                base_slug = "TaiLieu_AI_PTK"
        else:
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

        timestamp = now.strftime("%Y%m%d_%H%M%S")
        target_path = self.desktop_dir / f"{base_slug}_{timestamp}.docx"

        docx_bytes = ExportService.text_to_docx(content_to_write, title="TÀI LIỆU AI PTK")

        for attempt in range(10):
            try:
                with open(target_path, "wb") as f:
                    f.write(docx_bytes)
                break
            except PermissionError:
                target_path = self.desktop_dir / f"{base_slug}_{timestamp}_{attempt+1}.docx"

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
        """Tự động mở trình duyệt Chrome, trang web cụ thể hoặc tìm kiếm Google."""
        cmd_l = command.lower()

        # Kiểm tra các trang web phổ biến
        direct_sites = {
            "facebook": "https://www.facebook.com",
            "fb": "https://www.facebook.com",
            "tiktok": "https://www.tiktok.com",
            "shopee": "https://shopee.vn",
            "lazada": "https://lazada.vn",
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com",
            "vnexpress": "https://vnexpress.net",
            "dantri": "https://dantri.com.vn",
            "canva": "https://www.canva.com",
            "zalo": "https://chat.zalo.me",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com",
            "github": "https://github.com",
        }
        for site_key, site_url in direct_sites.items():
            if site_key in cmd_l:
                try:
                    subprocess.Popen(f'start chrome "{site_url}"', shell=True)
                except Exception:
                    subprocess.Popen(f'start "" "{site_url}"', shell=True)
                return {
                    "success": True,
                    "action": "website_opened",
                    "message": f"🌐 Đã tự động mở trang web {site_key.title()}: {site_url}",
                    "url": site_url,
                }

        # Trích xuất từ khóa tìm kiếm Google
        clean_kw = command
        for prefix in [
            "mở gg chrome", "mở google chrome", "mở chrome", "mở web", "mở trình duyệt",
            "tìm kiếm trên google", "tìm kiếm google", "tìm trên google",
            "tìm kiếm", "tra cứu", "tìm", "lên mạng tìm"
        ]:
            clean_kw = re.sub(prefix, "", clean_kw, flags=re.IGNORECASE)
        clean_kw = re.sub(r"^(và|hãy|giúp tôi|hộ tôi)?\s*", "", clean_kw, flags=re.IGNORECASE).strip()

        if not clean_kw:
            url = "https://www.google.com"
            msg = "Đã tự động mở trình duyệt Google Chrome!"
        elif clean_kw.startswith("http"):
            url = clean_kw
            msg = f"Đã tự động mở trang web: {url}"
        else:
            enc = urllib.parse.quote(clean_kw)
            url = f"https://www.google.com/search?q={enc}"
            msg = f"🔍 Đã mở Google Chrome và tìm kiếm: '{clean_kw}'!"

        try:
            subprocess.Popen(f'start chrome "{url}"', shell=True)
        except Exception:
            subprocess.Popen(f'start "" "{url}"', shell=True)

        return {"success": True, "action": "browser_opened", "message": msg, "url": url}

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
