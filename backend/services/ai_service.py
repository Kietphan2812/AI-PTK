"""
AI Service - Tương tác trực tiếp với Google Gemini API
Trang bị System Instruction thông minh, nhận biết thời gian thực và cá nhân hóa cho Kiệt (AI PTK).
"""

import json
import urllib.request
import urllib.error
import datetime
from config import settings


class AIService:
    """Lớp xử lý gọi mô hình Gemini (thông minh, nhận biết thời gian thực, chủ động)."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.initialized = bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def _ensure_initialized(self):
        if not self.initialized:
            settings.validate()
            self.api_key = settings.GEMINI_API_KEY
            self.model_name = settings.GEMINI_MODEL
            self.initialized = True

    def _get_system_instruction(self) -> dict:
        """Tạo chỉ dẫn hệ thống, cung cấp thời gian thực và định vị AI PTK."""
        tz = datetime.timezone(datetime.timedelta(hours=7))
        now = datetime.datetime.now(tz)
        days_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        weekday = days_vi[now.weekday()]
        now_str = f"{weekday}, ngày {now.strftime('%d/%m/%Y')}, lúc {now.strftime('%H:%M')} (Giờ Việt Nam)"

        prompt = (
            "Bạn là AI PTK – Trợ lý trí tuệ nhân tạo toàn năng được sáng lập và phát triển bởi Kiệt (Phan Tấn Kiệt).\n"
            f"THỜI GIAN HIỆN TẠI: {now_str}.\n"
            "Tính cách & Phong cách làm việc:\n"
            "1. Luôn nhận biết chính xác thứ, ngày, tháng, năm và giờ hiện tại khi được hỏi.\n"
            "2. Thân thiện, tôn trọng và tận tâm phục vụ bạn Kiệt cũng như mọi người dùng.\n"
            "3. Giải quyết công việc thực tế từ A đến Z: Khi được giao việc (lập kế hoạch, viết bài, viết code, phân tích dữ liệu, tóm tắt...), hãy làm việc chi tiết, thực tế và rõ ràng, không chỉ nói lý thuyết suông.\n"
            "4. Định dạng câu trả lời đẹp mắt bằng Markdown, dùng bullet points và emoji phù hợp."
        )
        return {"parts": [{"text": prompt}]}

    def _call_rest_api(self, contents: list) -> str:
        """Gọi trực tiếp Google Gemini REST API."""
        api_key = settings.GEMINI_API_KEY or self.api_key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        payload_dict = {
            "contents": contents,
            "system_instruction": self._get_system_instruction(),
        }
        payload = json.dumps(payload_dict).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return "Không nhận được nội dung từ AI."
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            return f"Lỗi Gemini API ({e.code}): {msg}"
        except Exception as e:
            return f"Lỗi kết nối API: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Gửi prompt đơn lẻ và nhận kết quả."""
        try:
            self._ensure_initialized()
            contents = [{"parts": [{"text": prompt}]}]
            return self._call_rest_api(contents)
        except Exception as e:
            return f"Lỗi: {str(e)}"

    def chat(self, message: str, history: list) -> str:
        """Trò chuyện nhiều lượt với lịch sử hội thoại."""
        try:
            self._ensure_initialized()

            contents = []
            for item in history:
                role = "user" if item.get("role") == "user" else "model"
                parts = item.get("parts", "")
                if isinstance(parts, str) and parts.strip():
                    contents.append({"role": role, "parts": [{"text": parts}]})

            contents.append({"role": "user", "parts": [{"text": message}]})

            return self._call_rest_api(contents)
        except Exception as e:
            return f"Lỗi chat: {str(e)}"
