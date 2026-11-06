"""
Service Bridge - Cầu nối thông minh:
Tự động gọi Backend API nếu có server, hoặc tự động chạy Services trực tiếp (Standalone / Cloud) nếu không có Backend riêng.
Giúp ứng dụng deploy 1-click lên Streamlit Cloud miễn phí 100% không cần thẻ tín dụng.
"""

import os
import sys
import tempfile
import requests
from pathlib import Path

# Thêm đường dẫn backend & root vào sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if (CURRENT_DIR / "backend").exists():
    PROJECT_ROOT = CURRENT_DIR
else:
    PROJECT_ROOT = CURRENT_DIR.parent

BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Khởi tạo services trực tiếp (fallback)
_ai_service = None
_rag_service = None
_writer_service = None
_data_service = None
_tools_service = None


def _get_services():
    global _ai_service, _rag_service, _writer_service, _data_service, _tools_service
    if _ai_service is None:
        try:
            from services.ai_service import AIService
            _ai_service = AIService()
        except Exception as e:
            print(f"[Bridge] AI Service error: {e}")

    if _rag_service is None and _ai_service:
        try:
            from services.rag_service import RAGService
            _rag_service = RAGService(ai_service=_ai_service)
        except Exception as e:
            print(f"[Bridge] RAG Service error: {e}")

    if _writer_service is None and _ai_service:
        try:
            from services.writer_service import WriterService
            _writer_service = WriterService(ai_service=_ai_service)
        except Exception as e:
            print(f"[Bridge] Writer Service error: {e}")

    if _data_service is None and _ai_service:
        try:
            from services.data_service import DataService
            _data_service = DataService(ai_service=_ai_service)
        except Exception as e:
            print(f"[Bridge] Data Service error: {e}")

    if _tools_service is None and _ai_service:
        try:
            from services.tools_service import ToolsService
            _tools_service = ToolsService(ai_service=_ai_service)
        except Exception as e:
            print(f"[Bridge] Tools Service error: {e}")

    return _ai_service, _rag_service, _writer_service, _data_service, _tools_service


def is_backend_online() -> bool:
    try:
        r = requests.get(f"{API_URL}/api/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


# 1. Chat
def call_chat(message: str, history: list) -> str:
    if is_backend_online():
        try:
            res = requests.post(f"{API_URL}/api/chat", json={"message": message, "history": history}, timeout=60)
            if res.status_code == 200:
                return res.json().get("response", "")
        except Exception:
            pass

    ai, _, _, _, _ = _get_services()
    if ai:
        return ai.chat(message, history)
    return "Lỗi: Không thể khởi tạo dịch vụ AI."


# 2. RAG
def call_rag_upload(filename: str, file_bytes: bytes) -> dict:
    if is_backend_online():
        try:
            files = {"file": (filename, file_bytes, "application/pdf")}
            res = requests.post(f"{API_URL}/api/rag/upload", files=files, timeout=120)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass

    _, rag, _, _, _ = _get_services()
    if rag:
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "wb") as f:
                f.write(file_bytes)
            chunks = rag.process_pdf(temp_path, filename)
            return {"filename": filename, "chunks": chunks, "message": f"Đã lập chỉ mục {chunks} đoạn văn bản."}
        except Exception as e:
            return {"filename": filename, "chunks": 0, "message": f"Lỗi xử lý file: {str(e)}"}
    return {"filename": filename, "chunks": 0, "message": "Tính năng RAG chưa khả dụng."}


def call_rag_query(query: str, filename: str) -> dict:
    if is_backend_online():
        try:
            res = requests.post(f"{API_URL}/api/rag/query", json={"query": query, "filename": filename}, timeout=60)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass

    _, rag, _, _, _ = _get_services()
    if rag:
        try:
            ans, src = rag.query(query, filename)
            return {"answer": ans, "sources": src}
        except Exception as e:
            return {"answer": f"Lỗi truy vấn: {str(e)}", "sources": []}
    return {"answer": "Chưa khởi tạo kho vector tài liệu.", "sources": []}


def call_rag_list() -> list:
    if is_backend_online():
        try:
            r = requests.get(f"{API_URL}/api/rag/documents", timeout=3)
            if r.status_code == 200:
                return r.json().get("documents", [])
        except Exception:
            pass

    _, rag, _, _, _ = _get_services()
    if rag:
        try:
            return rag.list_documents()
        except Exception:
            return []
    return []


# 3. Writer
def call_writer(task_type: str, topic: str, tone: str, language: str, extra: str) -> str:
    if is_backend_online():
        try:
            res = requests.post(
                f"{API_URL}/api/writer/generate",
                json={"task_type": task_type, "topic": topic, "tone": tone, "language": language, "extra_instructions": extra},
                timeout=90,
            )
            if res.status_code == 200:
                return res.json().get("content", "")
        except Exception:
            pass

    _, _, writer, _, _ = _get_services()
    if writer:
        return writer.generate_content(task_type, topic, tone, language, extra)
    return "Lỗi tạo nội dung."


# 4. Data
def call_data_analyze(filename: str, file_bytes: bytes) -> dict:
    if is_backend_online():
        try:
            files = {"file": (filename, file_bytes, "text/csv")}
            res = requests.post(f"{API_URL}/api/data/analyze", files=files, timeout=90)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass

    _, _, _, data_svc, _ = _get_services()
    if data_svc:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        return data_svc.analyze_csv(temp_path)
    return {"summary": "Lỗi", "columns": [], "row_count": 0, "ai_insights": "Lỗi phân tích", "chart_html": ""}


# 5. Tools
def call_tools_process(tool_type: str, text: str, target_lang: str = "English", code_lang: str = "Python") -> str:
    if is_backend_online():
        try:
            res = requests.post(
                f"{API_URL}/api/tools/process",
                json={"tool_type": tool_type, "text": text, "target_language": target_lang, "programming_language": code_lang},
                timeout=60,
            )
            if res.status_code == 200:
                return res.json().get("result", "")
        except Exception:
            pass

    _, _, _, _, tools = _get_services()
    if tools:
        return tools.process(tool_type, text, target_lang, code_lang)
    return "Lỗi xử lý công cụ."

