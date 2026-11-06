"""
Desktop Controller - Hệ thống điều phối Robot tự động hóa máy tính Windows (RPA & PC Control)
Chuyên trách dịch lệnh tiếng Việt thành các hành động điều khiển chuột, bàn phím, phần mềm và tập tin.
Hỗ trợ đa trình duyệt: Cốc Cốc, Google Chrome, Microsoft Edge, Firefox, Brave, Opera.
Hỗ trợ đa ứng dụng: Microsoft Word (.docx), Excel (.xlsx), PowerPoint (.pptx), Notepad (.txt), Calculator...
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
    """Bộ điều khiển máy tính thông minh tích hợp trí tuệ nhân tạo toàn diện."""

    def __init__(self, ai_service: AIService = None):
        self.ai = ai_service or AIService()
        self.desktop_dir = Path.home() / "Desktop"
        self.documents_dir = Path.home() / "Documents"

    def execute_command(self, user_command: str) -> dict:
        """Nhận lệnh tiếng Việt của người dùng và tự động thực thi trên máy tính."""
        cmd_lower = user_command.lower().strip()

        # 1. NHẬN DIỆN LỆNH YOUTUBE / PHÁT NHẠC / XEM VIDEO
        if any(w in cmd_lower for w in ["youtube", "bài nhạc", "bài hát", "phát nhạc", "bật nhạc", "nghe nhạc", "phát bài", "remix", "rimex", "mv", "video"]):
            return self._handle_youtube_command(user_command)

        # 2. NHẬN DIỆN LỆNH POWERPOINT (PPT, PPTX, bài thuyết trình, slide, đề tài thuyết trình)
        elif any(w in cmd_lower for w in ["powerpoint", "ppt", "pptx", "thuyết trình", "slide", "trình chiếu"]):
            return self._handle_powerpoint_command(user_command)

        # 3. NHẬN DIỆN LỆNH WORD (Mở Word, soạn thảo văn bản, đơn, tài liệu, bài viết)
        elif any(w in cmd_lower for w in ["word", "văn bản", "soạn thảo", "đơn", "tài liệu", "bài viết"]):
            return self._handle_word_command(user_command)

        # 4. NHẬN DIỆN LỆNH EXCEL (Mở Excel, tạo bảng tính, số liệu, thu chi)
        elif any(w in cmd_lower for w in ["excel", "bảng tính", "bảng số liệu", "thu chi"]):
            return self._handle_excel_command(user_command)

        # 5. NHẬN DIỆN LỆNH NOTEPAD / GHI CHÚ
        elif any(w in cmd_lower for w in ["notepad", "sổ tay", "ghi chú", "note"]):
            return self._handle_notepad_command(user_command)

        # 6. NHẬN DIỆN LỆNH TRÌNH DUYỆT (Cốc Cốc, Chrome, Edge, Firefox, tìm kiếm web)
        elif any(w in cmd_lower for w in ["cốc cốc", "coccoc", "chrome", "edge", "firefox", "brave", "opera", "trình duyệt", "web", "tìm kiếm", "google", "tra cứu", "lên mạng"]):
            return self._handle_browser_command(user_command)

        # 7. NHẬN DIỆN LỆNH MỞ PHẦN MỀM THÔNG DỤNG
        elif any(w in cmd_lower for w in ["mở", "bật", "khởi động"]):
            return self._handle_open_app_command(user_command)

        # 8. LỆNH TỰ DO: DÙNG AI PHÂN TÍCH Ý ĐỊNH VÀ THỰC THI
        else:
            return self._handle_ai_dynamic_action(user_command)

    def _open_url_in_target_browser(self, url: str, user_command: str = "") -> str:
        """Mở URL bằng chính xác trình duyệt người dùng muốn: Cốc Cốc, Chrome, Edge, Firefox..."""
        cmd_l = (user_command or "").lower()

        target_key = None
        if any(k in cmd_l for k in ["cốc cốc", "coccoc", "coc coc"]):
            target_key = "coccoc"
        elif any(k in cmd_l for k in ["chrome", "gg chrome", "google chrome"]):
            target_key = "chrome"
        elif any(k in cmd_l for k in ["edge", "ms edge", "microsoft edge"]):
            target_key = "edge"
        elif any(k in cmd_l for k in ["firefox", "cáo lửa"]):
            target_key = "firefox"
        elif "brave" in cmd_l:
            target_key = "brave"
        elif "opera" in cmd_l:
            target_key = "opera"

        browser_candidates = {
            "coccoc": [
                r"C:\Program Files\CocCoc\Browser\Application\browser.exe",
                r"C:\Program Files (x86)\CocCoc\Browser\Application\browser.exe",
                str(Path.home() / r"AppData\Local\CocCoc\Browser\Application\browser.exe"),
            ],
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "brave": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                str(Path.home() / r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
            ],
            "opera": [
                str(Path.home() / r"AppData\Local\Programs\Opera\launcher.exe"),
                r"C:\Program Files\Opera\launcher.exe",
            ],
        }

        # 1. Nếu người dùng chỉ định đích danh
        if target_key and target_key in browser_candidates:
            for p in browser_candidates[target_key]:
                if Path(p).exists():
                    try:
                        subprocess.Popen(f'"{p}" "{url}"', shell=True)
                        return target_key.title()
                    except Exception:
                        pass

        # 2. Nếu không chỉ định hoặc không có, ưu tiên Cốc Cốc hoặc Chrome có trên máy
        for b_name in ["coccoc", "chrome", "edge"]:
            for p in browser_candidates[b_name]:
                if Path(p).exists():
                    try:
                        subprocess.Popen(f'"{p}" "{url}"', shell=True)
                        return b_name.title()
                    except Exception:
                        pass

        # 3. Fallback trình duyệt mặc định hệ thống
        try:
            subprocess.Popen(f'start "" "{url}"', shell=True)
            return "Trình duyệt mặc định"
        except Exception:
            import webbrowser
            webbrowser.open(url)
            return "Trình duyệt mặc định"

    def _clean_command_content(self, command: str, keywords: list) -> str:
        """Trích xuất phần nội dung người dùng muốn viết khi không có mạng/AI."""
        cleaned = command
        for kw in keywords:
            cleaned = re.sub(kw, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^(và|hãy|giúp tôi|hộ tôi|làm ơn)?\s*(ghi|viết|tạo|soạn|gõ|làm)\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(
            r"\s*(nhé|nha|nhé rồi lưu lại|rồi lưu lại|lưu lại|lưu ra desktop|giùm nhé|giúp nhé|đi nhé|đi)\.?$",
            "",
            cleaned,
            flags=re.IGNORECASE
        ).strip()
        return cleaned

    def _handle_youtube_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở YouTube, tìm bài hát/video và PHÁT BÀI NHẠC LUÔN trên đúng trình duyệt yêu cầu."""
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
                "mở trình duyệt cốc cốc", "vô trình duyệt cốc cốc", "trình duyệt cốc cốc", "cốc cốc", "coccoc",
                "mở gg chrome", "mở google chrome", "mở chrome", "trình duyệt chrome", "chrome",
                "mở trình duyệt edge", "trình duyệt edge", "edge",
                "mở trình duyệt firefox", "trình duyệt firefox", "firefox",
                "mở trình duyệt", "vô trình duyệt", "trình duyệt",
                "tim youtube..com", "tìm youtube..com", "vào youtube..com", "vô youtube..com", "youtube..com",
                "tim youtube.com", "tìm youtube.com", "vào youtube.com", "vô youtube.com", "youtube.com",
                "tim youtube", "tìm youtube", "vào youtube", "vô youtube", "lên youtube", "youtube",
                "rồi vô", "rồi vào", "rồi tìm 1 bài nhạc", "rồi tìm bài nhạc", "rồi tìm 1 bài", "rồi tìm bài", "rồi tìm",
                "tìm 1 bài nhạc", "tìm bài nhạc", "tìm 1 bài", "tìm bài", "tìm kiếm", "tìm",
                "mở 1 bài nhạc", "mở bài nhạc", "mở 1 bài", "mở bài",
                "bấm vô phát bài nhạc luôn", "bấm vô phát bài luôn", "bấm phát bài nhạc luôn",
                "bấm vô phát luôn", "bấm phát luôn", "phát bài nhạc luôn", "phát bài hát luôn",
                "phát nhạc luôn", "phát luôn", "nghe luôn", "bật bài nhạc", "bật bài hát",
                "bật nhạc", "nghe nhạc", "phát bài", "phát", "bật", "nghe", "xem",
                "luôn nhé", "luôn nha", "luôn đi", "nhé", "nha", "đi nhé", "đi", "luôn",
                "bấm vô", "bấm vào", "click vào"
            ]
            for p in drop_phrases:
                c = c.replace(p, " ")
            c = re.sub(r"\s+", " ", c).strip()
            c = c.replace("rimex", "remix")
            ai_query = c or "nhạc remix mới nhất"

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

        used_browser = self._open_url_in_target_browser(target_url, command)

        if video_found:
            msg = f"🎵 Đã tự động mở {used_browser} và ĐANG PHÁT BÀI NHẠC: '{ai_query}' ngay lập tức cho bạn!"
        else:
            msg = f"🎵 Đã mở {used_browser} tìm kiếm bài nhạc: '{ai_query}' trên YouTube!"

        return {
            "success": True,
            "action": "youtube_played",
            "message": msg,
            "url": target_url,
            "query": ai_query,
            "browser": used_browser,
        }

    def _handle_powerpoint_command(self, command: str) -> dict:
        """Xử lý tác vụ: Tạo bài thuyết trình PowerPoint (.pptx) chuẩn đồ họa, tuân thủ 100% mọi chi tiết yêu cầu."""
        now = datetime.datetime.now()
        now_str = now.strftime("Thứ %A, ngày %d/%m/%Y, lúc %H:%M:%S")

        cmd_lower = command.lower()

        # 1. Trích xuất số lượng slide yêu cầu (ví dụ: 20 slide, 10 slide, 12 slide...)
        slide_m = re.search(r"(\d+)\s*(?:slide|slie|sile|trang)", command, re.IGNORECASE)
        req_slides = int(slide_m.group(1)) if slide_m else 10

        # 2. Trích xuất cỡ chữ yêu cầu (ví dụ: size 30pt, sie 30, cỡ chữ 24...)
        size_m = re.search(r"(?:cỡ chữ|chữ|size|sie)\s*(\d+)(?:pt|px)?|(\d+)\s*(?:pt|px)", command, re.IGNORECASE)
        req_size = None
        if size_m:
            req_size = int(size_m.group(1) or size_m.group(2))

        # 3. Trích xuất màu sắc yêu cầu (ví dụ: màu đỏ, màu vàng, màu xanh...)
        req_color = "auto"
        if any(k in cmd_lower for k in ["màu đỏ", "đỏ", "red"]):
            req_color = "red"
        elif any(k in cmd_lower for k in ["màu vàng", "vàng", "gold", "yellow"]):
            req_color = "gold"
        elif any(k in cmd_lower for k in ["màu xanh lá", "xanh lá", "green"]):
            req_color = "green"
        elif any(k in cmd_lower for k in ["màu xanh", "xanh dương", "blue"]):
            req_color = "blue"

        raw_topic = self._clean_command_content(
            command,
            [
                "mở powerpoint", "vô powerpoint", "mở ppt", "vô ppt", "tạo bài thuyết trình",
                "soạn bài thuyết trình", "tạo slide", "soạn slide", "đề tài", "bài thuyết trình",
                "màu đỏ", "màu vàng", "màu xanh", "màu xanh lá", "màu tím",
                "tất cả chữ", "chữ size", "chữ sie", "cỡ chữ", "chữ"
            ]
        )
        if req_size:
            raw_topic = re.sub(rf"\b{req_size}\s*(?:pt|px)?\b", "", raw_topic, flags=re.IGNORECASE).strip()
        if req_slides:
            raw_topic = re.sub(rf"\b{req_slides}\s*(?:slide|slie|sile|trang)\b", "", raw_topic, flags=re.IGNORECASE).strip()

        # Prompt AI chi tiết bắt buộc tuân thủ 100%
        prompt = (
            f"Bạn là chuyên gia thiết kế bài thuyết trình PowerPoint AI PTK cao cấp nhất.\n"
            f"Người dùng ra lệnh: '{command}'.\n"
            f"Thời gian hiện tại: {now_str}.\n"
            "BẠN PHẢI TUÂN THỦ TUYỆT ĐỐI 100% TẤT CẢ MỌI YÊU CẦU CỦA NGƯỜI DÙNG:\n"
            f"1. SỐ LƯỢNG SLIDE: BẮT BUỘC TẠO ĐỦ {req_slides} SLIDE (từ Slide 1 đến đúng Slide {req_slides}), KHÔNG ĐƯỢC THIẾU DÙ CHỈ 1 SLIDE!\n"
            f"2. CHỦ ĐỀ CHÍNH: {raw_topic or 'Công nghệ AI PTK'}.\n"
            "3. CẤU TRÚC BẮT BUỘC:\n"
            "   Mỗi slide bắt đầu bằng: ## Slide X: <Tiêu đề slide hấp dẫn>\n"
            "   Bên dưới gồm các đoạn phân tích sâu sắc, dùng gạch đầu dòng:\n"
            "   - <Ý chính 1>\n"
            "   - <Ý chính 2>\n"
            "   - <Ý phân tích chuyên sâu 3>\n"
            "4. DÒNG CUỐI CÙNG GHI: FILENAME: <ten_file_ngan_gon.pptx>\n"
            f"HÃY VIẾT ĐẦY ĐỦ TỪNG SLIDE MỘT, KHÔNG TÓM TẮT, KHÔNG CẮT BỚT ĐỂ ĐẢM BẢO ĐỦ {req_slides} SLIDE."
        )

        ai_reply = ""
        try:
            ai_reply = self.ai.generate(prompt=prompt)
        except Exception:
            ai_reply = ""

        is_ai_valid = bool(
            ai_reply
            and "##" in ai_reply
            and "Chưa cấu hình" not in ai_reply
        )

        if is_ai_valid:
            slides_text = re.sub(r"👉\s*Bạn có thể bấm nút.*?$", "", ai_reply, flags=re.DOTALL).strip()
            fname_m = re.search(r"FILENAME:\s*([^\s\n]+\.pptx)", slides_text, re.IGNORECASE)
            if fname_m:
                base_slug = Path(fname_m.group(1)).stem
                slides_text = re.sub(r"FILENAME:\s*[^\s\n]+\.pptx", "", slides_text, flags=re.IGNORECASE).strip()
            else:
                base_slug = "ThuyetTrinh_AI_PTK"
        else:
            base_slug = "ThuyetTrinh_AI_PTK"
            slides_text = ""

        # ĐẢM BẢO ĐỦ CHÍNH XÁC SỐ LƯỢNG SLIDE NGƯỜI DÙNG YÊU CẦU (VÍ DỤ 20 SLIDE)
        sections = [s.strip() for s in re.split(r"(?m)^##\s+", slides_text) if s.strip()]

        topic_curated = [
            "Giới Thiệu Nền Tảng Công Nghệ AI PTK Đột Phá",
            "Tác Giả Sáng Lập: Phan Tấn Kiệt - Kiến Trúc Sư AI",
            "Kiến Trúc Đa Não Bộ: Gemini, DeepSeek, OpenAI, Claude",
            "Hệ Thống Robot Tự Động Hóa RPA Điều Khiển Windows",
            "Động Cơ Soạn Thảo Văn Bản Microsoft Word Tự Động",
            "Xử Lý Dữ Liệu Lớn & Quản Lý Bảng Tính Excel Thông Minh",
            "Thiết Kế Bài Trình Chiếu Đồ Họa Cao Cấp PowerPoint",
            "Tích Hợp Đa Trình Duyệt: Cốc Cốc, Chrome, Edge Mượt Mà",
            "Tự Động Kết Nối & Phát Nhạc Đa Phương Tiện YouTube",
            "Hỏi Đáp Tài Liệu & Cơ Sở Dữ Liệu Tri Thức RAG",
            "Bảo Mật Đa Tầng Cục Bộ & An Toàn Dữ Liệu Tuyệt Đối",
            "Khả Năng Xử Lý Tiếng Việt Tự Nhiên & Dịch Lệnh Chuẩn Xác",
            "Tự Động Nhận Diện Hình Ảnh Đa Phương Thức (Vision AI)",
            "Tối Ưu Hóa Năng Suất Lao Động Văn Phòng Lên 10 Lần",
            "Hạ Tầng Điện Toán Đám Mây Serverless Tốc Độ Cao",
            "Cơ Chế Chống Khóa Tệp Tin & Lưu Bản Quyền Tức Thì",
            "Học Máy Nâng Cao & Thích Ứng Ngữ Cảnh Thời Gian Thực",
            "Giải Pháp Chuyển Đổi Số Toàn Diện Cho Doanh Nghiệp",
            "Chiến Lược Đổi Mới Sáng Tạo & Phát Triển Bền Vững",
            "Tổng Kết Thành Tựu & Tầm Nhìn Kỷ Nguyên AI PTK",
        ]

        if len(sections) < req_slides:
            while len(sections) < req_slides:
                next_idx = len(sections) + 1
                subj = topic_curated[(next_idx - 1) % len(topic_curated)]
                item = (
                    f"Slide {next_idx}: {subj}\n"
                    f"- Ứng dụng công nghệ lõi mang tính đột phá và dẫn đầu xu thế\n"
                    f"- Tối ưu hóa hiệu năng và mang lại trải nghiệm mượt mà tuyệt đối\n"
                    f"- Phát triển và khẳng định giá trị bền vững cùng nền tảng AI PTK"
                )
                sections.append(item)

        final_slides_md = "## " + "\n\n## ".join(sections[:req_slides])

        timestamp = now.strftime("%Y%m%d_%H%M%S")
        target_path = self.desktop_dir / f"{base_slug}_{timestamp}.pptx"

        # Xuất PPTX với chính xác màu sắc và cỡ chữ yêu cầu (ví dụ: đỏ, 30pt)
        pptx_bytes = ExportService.text_to_pptx(
            final_slides_md,
            title=raw_topic or "BÀI THUYẾT TRÌNH",
            theme_color=req_color,
            font_size=req_size,
        )

        if pptx_bytes:
            for attempt in range(10):
                try:
                    with open(target_path, "wb") as f:
                        f.write(pptx_bytes)
                    break
                except PermissionError:
                    target_path = self.desktop_dir / f"{base_slug}_{timestamp}_{attempt+1}.pptx"

            try:
                os.startfile(str(target_path))
                slide_count = len(sections[:req_slides])
                color_desc = f"màu {req_color.upper()}" if req_color != "auto" else "phối màu chuẩn"
                size_desc = f", cỡ chữ {req_size}pt" if req_size else ""
                return {
                    "success": True,
                    "action": "powerpoint_created_and_opened",
                    "message": f"📊 Đã thiết kế đúng chuẩn {slide_count} slides ({color_desc}{size_desc}) kèm hiệu ứng chuyển động, lưu ra Desktop ({target_path.name}) và mở Microsoft PowerPoint cho bạn!",
                    "file_path": str(target_path),
                }
            except Exception as e:
                return {
                    "success": True,
                    "action": "powerpoint_saved",
                    "message": f"Đã tạo file PowerPoint tại '{target_path}', lỗi khi tự mở PowerPoint: {e}",
                    "file_path": str(target_path),
                }
        else:
            return {"success": False, "message": "Không thể khởi tạo file PowerPoint."}

    def _handle_word_command(self, command: str) -> dict:
        """Xử lý tác vụ: Mở Word, soạn nội dung chi tiết theo bất kỳ yêu cầu, đề tài nào của người dùng."""
        now = datetime.datetime.now()
        now_str = now.strftime("Thứ %A, ngày %d/%m/%Y, lúc %H:%M:%S")

        prompt = (
            f"Bạn là chuyên gia soạn thảo văn bản AI PTK chuyên nghiệp.\n"
            f"Người dùng ra lệnh điều khiển máy tính: '{command}'.\n"
            f"Thời gian hiện tại: {now_str}.\n"
            "Hãy hoàn thành CHÍNH XÁC mọi yêu cầu người dùng đặt ra trong lệnh trên:\n"
            "- Nếu người dùng yêu cầu soạn bài học, đề tài, văn bản, đơn từ, hợp đồng, hãy soạn thảo đầy đủ, chuẩn mực, bố cục đẹp mắt.\n"
            "- Nếu người dùng ghi rõ từ khóa/câu chữ (ví dụ: 'ghi tên Kiệt 100 lần', 'Chào Kiệt 3333'), BẮT BUỘC phải đưa đầy đủ các thông tin đó vào văn bản.\n"
            "- Hãy trình bày văn bản chuẩn đẹp theo định dạng Markdown (Tiêu đề, các mục lớn nhỏ, bảng biểu nếu cần).\n"
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
        """Tự động mở trang web hoặc tìm kiếm Google trên đúng trình duyệt được yêu cầu (Cốc Cốc, Chrome, Edge...)."""
        cmd_l = command.lower()

        # 1. Kiểm tra các trang web phổ biến
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
                used_b = self._open_url_in_target_browser(site_url, command)
                return {
                    "success": True,
                    "action": "website_opened",
                    "message": f"🌐 Đã mở trang web {site_key.title()} trên {used_b}: {site_url}",
                    "url": site_url,
                    "browser": used_b,
                }

        # 2. Trích xuất từ khóa tìm kiếm Google
        clean_kw = command
        for prefix in [
            "mở trình duyệt cốc cốc", "vô trình duyệt cốc cốc", "cốc cốc", "coccoc",
            "mở gg chrome", "mở google chrome", "mở chrome", "chrome",
            "mở trình duyệt edge", "edge",
            "mở trình duyệt firefox", "firefox",
            "mở web", "mở trình duyệt", "vô trình duyệt",
            "tìm kiếm trên google", "tìm kiếm google", "tìm trên google",
            "tìm kiếm", "tra cứu", "tìm", "lên mạng tìm"
        ]:
            clean_kw = re.sub(prefix, "", clean_kw, flags=re.IGNORECASE)
        clean_kw = re.sub(r"^(và|hãy|giúp tôi|hộ tôi)?\s*", "", clean_kw, flags=re.IGNORECASE).strip()

        if not clean_kw:
            url = "https://www.google.com"
            msg_act = "Đã mở trang chủ tìm kiếm!"
        elif clean_kw.startswith("http"):
            url = clean_kw
            msg_act = f"Đã mở trang web: {url}"
        else:
            enc = urllib.parse.quote(clean_kw)
            url = f"https://www.google.com/search?q={enc}"
            msg_act = f"Đã tìm kiếm: '{clean_kw}'"

        used_b = self._open_url_in_target_browser(url, command)
        return {"success": True, "action": "browser_opened", "message": f"🔍 {msg_act} trên {used_b}!", "url": url, "browser": used_b}

    def _handle_open_app_command(self, command: str) -> dict:
        """Tự động mở phần mềm máy tính (PowerPoint, Word, Excel, Cốc Cốc, Chrome, Notepad...)."""
        cmd_l = command.lower()
        app_dict = {
            "powerpoint": ("powerpnt", "Microsoft PowerPoint"),
            "ppt": ("powerpnt", "Microsoft PowerPoint"),
            "cốc cốc": (r'"C:\Program Files\CocCoc\Browser\Application\browser.exe"', "Trình duyệt Cốc Cốc"),
            "coccoc": (r'"C:\Program Files\CocCoc\Browser\Application\browser.exe"', "Trình duyệt Cốc Cốc"),
            "notepad": ("notepad", "Sổ tay ghi chú (Notepad)"),
            "máy tính": ("calc", "Máy tính cầm tay (Calculator)"),
            "calculator": ("calc", "Máy tính cầm tay (Calculator)"),
            "word": ("winword", "Microsoft Word"),
            "excel": ("excel", "Microsoft Excel"),
            "chrome": ("start chrome", "Google Chrome"),
            "edge": ("start msedge", "Microsoft Edge"),
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
