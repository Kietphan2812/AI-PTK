"""
AI Service - Bộ điều phối Đa Não (Multi-Model AI Engine)
Hỗ trợ: Google Gemini, DeepSeek (V3/R1), OpenAI (ChatGPT GPT-4o), Anthropic (Claude 3.5 Sonnet)
Tất cả đều dùng chuẩn HTTP REST API của Python, không phụ thuộc thư viện ngoài nặng nề.
"""

import json
import urllib.request
import urllib.error
import datetime
from config import settings

GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
]


class AIService:
    """Động cơ AI đa năng hỗ trợ Gemini, DeepSeek, OpenAI và Claude."""

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
            "Tính cách & Phong cách làm việc:\n"
            "1. Luôn nhận biết chính xác thứ, ngày, tháng, năm và giờ hiện tại khi được hỏi.\n"
            "2. Thân thiện, tôn trọng và tận tâm phục vụ bạn Kiệt cũng như mọi người dùng.\n"
            "3. Giải quyết công việc thực tế từ A đến Z: Khi được giao việc (lập kế hoạch, viết bài, viết code, phân tích dữ liệu, tóm tắt...), hãy làm việc chi tiết, thực tế và rõ ràng, không chỉ nói lý thuyết suông.\n"
            "4. Định dạng câu trả lời đẹp mắt bằng Markdown, dùng bullet points và emoji phù hợp."
        )

    # -------------------------------------------------------------
    # 1. GOOGLE GEMINI
    # -------------------------------------------------------------
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
                with urllib.request.urlopen(req, timeout=30) as response:
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

        return f"Gemini tạm thời không phản hồi ({last_error}). Vui lòng thử lại sau giây lát."

    # -------------------------------------------------------------
    # 2. DEEPSEEK (V3 / R1)
    # -------------------------------------------------------------
    def _call_deepseek(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.DEEPSEEK_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `DEEPSEEK_API_KEY`. Bạn có thể lấy key miễn phí tại https://platform.deepseek.com/ và điền vào ô cài đặt."

        target_model = model or "deepseek-chat"  # Hoặc deepseek-reasoner
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Thêm system prompt vào đầu danh sách messages
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

    # -------------------------------------------------------------
    # 3. OPENAI (CHATGPT GPT-4o)
    # -------------------------------------------------------------
    def _call_openai(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.OPENAI_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `OPENAI_API_KEY`. Bạn có thể lấy key tại https://platform.openai.com/ và điền vào ô cài đặt."

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

    # -------------------------------------------------------------
    # 4. ANTHROPIC CLAUDE (CLAUDE 3.5 SONNET)
    # -------------------------------------------------------------
    def _call_claude(self, messages: list, custom_key: str = None, model: str = None) -> str:
        api_key = custom_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            return "⚠️ Bạn chưa cấu hình `ANTHROPIC_API_KEY`. Bạn có thể lấy key tại https://console.anthropic.com/ và điền vào ô cài đặt."

        target_model = model or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        # Claude yêu cầu format: messages=[{"role": "user"|"assistant", "content": ...}]
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
    # GIAO DIỆN CHUNG (UNIFIED DISPATCHER)
    # -------------------------------------------------------------
    def chat(
        self,
        message: str,
        history: list,
        provider: str = "gemini",
        model: str = None,
        custom_key: str = None,
    ) -> str:
        """Hàm chat đa năng điều phối sang nhà cung cấp được chọn."""
        prov = (provider or "gemini").lower()

        if prov == "gemini":
            contents = []
            for item in history:
                role = "user" if item.get("role") == "user" else "model"
                parts = item.get("parts", "")
                if isinstance(parts, str) and parts.strip():
                    contents.append({"role": role, "parts": [{"text": parts}]})
            contents.append({"role": "user", "parts": [{"text": message}]})
            return self._call_gemini(contents, custom_key=custom_key, model=model)

        else:
            # Format chuẩn cho DeepSeek, OpenAI, Claude
            messages = []
            for item in history:
                role = "user" if item.get("role") == "user" else "assistant"
                content = item.get("parts", "")
                if isinstance(content, str) and content.strip():
                    messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})

            if prov == "deepseek":
                return self._call_deepseek(messages, custom_key=custom_key, model=model)
            elif prov == "openai":
                return self._call_openai(messages, custom_key=custom_key, model=model)
            elif prov == "claude":
                return self._call_claude(messages, custom_key=custom_key, model=model)
            else:
                return self._call_gemini(contents, custom_key=custom_key, model=model)

    def generate(
        self,
        prompt: str,
        provider: str = "gemini",
        model: str = None,
        custom_key: str = None,
    ) -> str:
        """Hàm sinh nội dung đơn lẻ với nhà cung cấp được chọn."""
        return self.chat(
            message=prompt,
            history=[],
            provider=provider,
            model=model,
            custom_key=custom_key,
        )
