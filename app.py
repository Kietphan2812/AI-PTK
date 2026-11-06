"""
Root App Entry Point cho Streamlit Cloud & Hosting Providers
Tự động chuyển tiếp vào frontend/app.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

for p in [str(ROOT_DIR), str(FRONTEND_DIR), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Thực thi frontend/app.py
app_path = FRONTEND_DIR / "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

exec(code, {"__name__": "__main__", "__file__": str(app_path)})
