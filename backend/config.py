"""
Cấu hình ứng dụng AI PTK (Application Configuration)
=====================================================
Hỗ trợ đa nền tảng AI: Google Gemini, DeepSeek, OpenAI ChatGPT, Anthropic Claude.
Đọc biến môi trường từ file .env ở thư mục gốc hoặc từ Streamlit Cloud secrets.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

# Quét tất cả các vị trí có thể chứa file .env (kể cả khi chạy file .exe độc lập)
candidate_env_paths = [
    PROJECT_ROOT / ".env",
    Path.cwd() / ".env",
    Path(sys.executable).resolve().parent / ".env",
    Path(sys.executable).resolve().parent.parent / ".env",
    Path(r"D:\AI PTK\.env"),
    Path.home() / "Desktop" / "AI PTK" / ".env",
    BACKEND_DIR.parent / ".env",
]

for p in candidate_env_paths:
    if p.is_file():
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        k = key.strip()
                        if k not in os.environ or not os.environ[k]:
                            os.environ[k] = val.strip()
        except Exception:
            pass


class Settings:
    """Lớp cấu hình chính cho toàn bộ các nhà cung cấp AI."""

    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    OPENAI_MODEL: str = "gpt-4o"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Thư mục lưu trữ
    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
    CHROMA_DIR: Path = BACKEND_DIR / "chroma_db"

    # App info
    APP_TITLE: str = "AI PTK – Bộ công cụ AI đa năng"
    APP_VERSION: str = "2.0.0"

    def _get_key(self, env_name: str) -> str:
        key = os.getenv(env_name, "")
        if not key or "your_" in key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and env_name in st.secrets:
                    key = str(st.secrets[env_name])
            except Exception:
                pass
        return key

    @property
    def GEMINI_API_KEY(self) -> str:
        return self._get_key("GEMINI_API_KEY")

    @property
    def DEEPSEEK_API_KEY(self) -> str:
        return self._get_key("DEEPSEEK_API_KEY")

    @property
    def OPENAI_API_KEY(self) -> str:
        return self._get_key("OPENAI_API_KEY")

    @property
    def ANTHROPIC_API_KEY(self) -> str:
        return self._get_key("ANTHROPIC_API_KEY")

    def validate(self) -> None:
        """Kiểm tra có ít nhất 1 API key được cấu hình."""
        if not any([self.GEMINI_API_KEY, self.DEEPSEEK_API_KEY, self.OPENAI_API_KEY, self.ANTHROPIC_API_KEY]):
            raise ValueError(
                "Chưa cấu hình API Key nào (Gemini, DeepSeek, OpenAI hoặc Claude). "
                "Hãy điền ít nhất 1 key trong file .env hoặc trong Streamlit Secrets."
            )


settings = Settings()
