"""
AI Service - Tương tác trực tiếp với Google Gemini API
Hỗ trợ cả Google Generative AI SDK và Direct REST API Fallback
"""

import json
import urllib.request
import urllib.error
from config import settings


class AIService:
    """Lớp xử lý gọi mô hình Gemini (bền bỉ, tự động fallback)."""

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

    def _call_rest_api(self, contents: list) -> str:
        """Gọi trực tiếp Google Gemini REST API (cực kỳ ổn định và nhanh)."""
        api_key = settings.GEMINI_API_KEY or self.api_key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"contents": contents}).encode("utf-8")

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

            # Thêm tin nhắn hiện tại
            contents.append({"role": "user", "parts": [{"text": message}]})

            return self._call_rest_api(contents)
        except Exception as e:
            return f"Lỗi chat: {str(e)}"
