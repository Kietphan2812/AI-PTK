"""
AI Service - Bộ điều phối Đa Não (Multi-Model AI Engine) & Multimodal Vision
Hỗ trợ đọc và phân tích hình ảnh (Gemini, ChatGPT GPT-4o, Claude 3.5, DeepSeek).
"""

import json
import base64
import urllib.request
import urllib.error
import datetime
from config import settings

GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.5-flash",
]


class AIService:
    """Động cơ AI đa năng hỗ trợ văn bản và hình ảnh."""

    def __init__(self):
        pass

    def _get_system_prompt_text(self) -> str:
        """Tạo chỉ dẫn hệ thống nhận biết thời gian thực cho Kiệt (AI PTK)."""
        tz = datetime.timezone(datetime.timedelta(hours=7))
        now = datetime.datetime.now(tz)
        days_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        weekday = days_vi[now.weekday()]
        now_str = f"{weekday}, ngày {now.strftime('%d/%m/%Y')}, lúc {now.strftime('%H:%M')} (Giờ Việt Nam)"

        return (
            "Bạn là AI PTK – Nền tảng trí tuệ nhân tạo toàn năng được sáng lập và phát triển bởi Kiệt (Phan Tấn Kiệt).\n"
            f"THỜI GIAN HIỆN TẠI: {now_str}.\n"
            "Tính cách & Khả năng làm việc:\n"
            "1. Luôn nhận biết chính xác thứ, ngày, tháng, năm và giờ hiện tại khi được hỏi.\n"
            "2. Có khả năng nhìn và phân tích hình ảnh (đọc chữ, giải toán, nhận diện đồ vật, trích xuất dữ liệu từ ảnh).\n"
            "3. Thân thiện, tôn trọng và tận tâm phục vụ bạn Kiệt cũng như mọi người dùng.\n"
            "4. Giải quyết công việc thực tế từ A đến Z: Khi được giao việc (lập kế hoạch, viết bài, viết code, phân tích dữ liệu, tóm tắt...), hãy làm việc chi tiết, thực tế và rõ ràng, không chỉ nói lý thuyết suông.\n"
            "5. Định dạng câu trả lời đẹp mắt bằng Markdown, dùng bullet points và emoji phù hợp."
        )

    # 1. GOOGLE GEMINI (VISION)
    def _call_gemini(self, contents: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.GEMINI_API_KEY
        if not api_key:
            return "Chưa cấu hình GEMINI_API_KEY. Vui lòng kiểm tra file .env hoặc Streamlit Secrets."

        headers = {"Content-Type": "application/json"}
        payload_dict = {
            "contents": contents,
            "system_instruction": {"parts": [{"text": self._get_system_prompt_text()}]},
        }
        payload = json.dumps(payload_dict).encode("utf-8")
        models_to_try = [model] if model else GEMINI_MODELS

        last_error = ""
        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            req = urllib.request.Request(url, data=payload, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=40) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                    return "Không nhận được phản hồi từ Gemini."
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                if e.code in [429, 404, 503] and len(models_to_try) > 1:
                    last_error = f"{m} ({e.code})"
                    continue
                return f"Lỗi Gemini API ({e.code}): {err_body}"
            except Exception as e:
                last_error = str(e)
                continue

        return f"Gemini tạm thời bận ({last_error}). Vui lòng thử lại sau giây lát."

    # 2. DEEPSEEK (V3 / R1)
    def _call_deepseek(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.DEEPSEEK_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `DEEPSEEK_API_KEY`. Bạn có thể lấy key tại https://platform.deepseek.com/."

        target_model = model or "deepseek-chat"
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        full_messages = [{"role": "system", "content": self._get_system_prompt_text()}] + messages

        payload = json.dumps({
            "model": target_model,
            "messages": full_messages,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "Không nhận được nội dung từ DeepSeek."
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            return f"Lỗi DeepSeek API ({e.code}): {err}"
        except Exception as e:
            return f"Lỗi kết nối DeepSeek: {str(e)}"

    # 3. OPENAI GPT-4o (VISION)
    def _call_openai(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.OPENAI_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `OPENAI_API_KEY`. Bạn có thể lấy key tại https://platform.openai.com/."

        target_model = model or "gpt-4o"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        full_messages = [{"role": "system", "content": self._get_system_prompt_text()}] + messages

        payload = json.dumps({
            "model": target_model,
            "messages": full_messages,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "Không nhận được nội dung từ OpenAI."
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            return f"Lỗi OpenAI API ({e.code}): {err}"
        except Exception as e:
            return f"Lỗi kết nối OpenAI: {str(e)}"

    # 4. ANTHROPIC CLAUDE (VISION)
    def _call_claude(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `ANTHROPIC_API_KEY`. Bạn có thể lấy key tại https://console.anthropic.com/."

        target_model = model or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        claude_msgs = []
        for m in messages:
            role = "assistant" if m.get("role") in ["model", "assistant"] else "user"
            claude_msgs.append({"role": role, "content": m.get("content", "")})

        payload = json.dumps({
            "model": target_model,
            "max_tokens": 4096,
            "system": self._get_system_prompt_text(),
            "messages": claude_msgs,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                contents = result.get("content", [])
                if contents:
                    return contents[0].get("text", "")
                return "Không nhận được nội dung từ Claude."
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            return f"Lỗi Claude API ({e.code}): {err}"
        except Exception as e:
            return f"Lỗi kết nối Claude: {str(e)}"

    # -------------------------------------------------------------
    # GIAO DIỆN CHUNG (UNIFIED DISPATCHER HỖ TRỢ CẢ HÌNH ẢNH & ĐA NÃO)
    # -------------------------------------------------------------
    def chat(
        self,
        message: str = "",
        history: list = None,
        provider: str = "gemini",
        model: str = None,
        custom_key: str = None,
        image_bytes: bytes = None,
        image_mime: str = "image/jpeg",
        *args,
        **kwargs,
    ) -> str:
        """Hàm chat đa năng điều phối sang nhà cung cấp được chọn (Gemini, DeepSeek, OpenAI, Claude)."""
        if history is None:
            history = []
        if image_bytes is None and "image_bytes" in kwargs:
            image_bytes = kwargs["image_bytes"]
        if "image_mime" in kwargs:
            image_mime = kwargs["image_mime"]
        if "provider" in kwargs:
            provider = kwargs["provider"]
        if not model and "model" in kwargs:
            model = kwargs["model"]
        if not custom_key and "custom_key" in kwargs:
            custom_key = kwargs["custom_key"]

        # Chuẩn hóa image_mime
        if image_mime in ["image/jpg", "jpg"]:
            image_mime = "image/jpeg"
        elif not image_mime:
            image_mime = "image/jpeg"

        prov = (provider or "gemini").lower()

        # Nếu có đính kèm ảnh mà chọn DeepSeek (chưa có Vision), tự động dùng Gemini cho Vision
        if image_bytes and prov == "deepseek":
            prov = "gemini"

        if prov == "gemini":
            contents = []
            for item in history:
                role = "user" if item.get("role") == "user" else "model"
                parts = item.get("parts", "")
                if isinstance(parts, str) and parts.strip():
                    contents.append({"role": role, "parts": [{"text": parts}]})

            # Phần tin nhắn hiện tại
            user_parts = []
            if image_bytes:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                user_parts.append({
                    "inline_data": {
                        "mime_type": image_mime,
                        "data": b64_img,
                    }
                })
            user_parts.append({"text": message if message else "Hãy mô tả và phân tích hình ảnh này chi tiết."})

            contents.append({"role": "user", "parts": user_parts})
            return self._call_gemini(contents, custom_key=custom_key, model=model)

        elif prov == "openai":
            messages = []
            for item in history:
                role = "user" if item.get("role") == "user" else "assistant"
                content = item.get("parts", "")
                if isinstance(content, str) and content.strip():
                    messages.append({"role": role, "content": content})

            if image_bytes:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                user_content = [
                    {"type": "text", "text": message if message else "Phân tích hình ảnh này."},
                    {"type": "image_url", "image_url": {"url": f"data:{image_mime};base64,{b64_img}"}},
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": message})

            return self._call_openai(messages, custom_key=custom_key, model=model)

        elif prov == "claude":
            messages = []
            for item in history:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                content = item.get("parts", "")
                if isinstance(content, str) and content.strip():
                    messages.append({"role": role, "content": content})

            if image_bytes:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                user_content = [
                    {"type": "text", "text": message if message else "Phân tích hình ảnh này."},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_mime,
                            "data": b64_img,
                        },
                    },
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": message})

            return self._call_claude(messages, custom_key=custom_key, model=model)

        else:
            return self.chat(
                message=message,
                history=history,
                provider="gemini",
                custom_key=custom_key,
                image_bytes=image_bytes,
                image_mime=image_mime,
                *args,
                **kwargs,
            )

    def generate(
        self,
        prompt: str,
        provider: str = "gemini",
        model: str = None,
        custom_key: str = None,
        *args,
        **kwargs,
    ) -> str:
        return self.chat(
            message=prompt,
            history=[],
            provider=provider,
            model=model,
            custom_key=custom_key,
            *args,
            **kwargs,
        )
