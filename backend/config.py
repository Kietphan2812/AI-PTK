"""
Cấu hình ứng dụng AI PTK (Application Configuration)
=====================================================
Đọc biến môi trường từ file .env ở thư mục gốc hoặc từ Streamlit Cloud secrets.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

# Đọc file .env nếu có (khi chạy local)
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()


class Settings:
    """Lớp cấu hình chính."""

    _gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-3.5-flash"

    # Thư mục lưu trữ
    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
    CHROMA_DIR: Path = BACKEND_DIR / "chroma_db"

    # App info
    APP_TITLE: str = "AI PTK – Bộ công cụ AI đa năng"
    APP_VERSION: str = "1.0.0"

    @property
    def GEMINI_API_KEY(self) -> str:
        key = os.getenv("GEMINI_API_KEY", "")
        if not key or key == "your_gemini_api_key_here":
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"])
            except Exception:
                pass
        return key

    def validate(self) -> None:
        """Kiểm tra cấu hình bắt buộc."""
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY chưa được cấu hình. "
                "Hãy cấu hình trong file .env hoặc trong Streamlit Secrets."
            )


settings = Settings()
