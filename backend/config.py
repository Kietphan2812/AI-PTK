"""
Cấu hình ứng dụng AI PTK (Application Configuration)
=====================================================
Đọc biến môi trường từ file .env ở thư mục gốc dự án.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

# Tự động đọc file .env bằng thư viện chuẩn (không lo thiếu package)
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

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-3.5-flash"

    # Thư mục lưu trữ
    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
    CHROMA_DIR: Path = BACKEND_DIR / "chroma_db"

    # App info
    APP_TITLE: str = "AI PTK – Bộ công cụ AI đa năng"
    APP_VERSION: str = "1.0.0"

    def validate(self) -> None:
        """Kiểm tra cấu hình bắt buộc."""
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY chưa được cấu hình. "
                "Hãy mở file .env và điền API key lấy từ https://aistudio.google.com/"
            )


settings = Settings()
