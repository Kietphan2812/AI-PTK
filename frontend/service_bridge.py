"""
Service Bridge - Cầu nối thông minh hỗ trợ Multi-Model & Vision:
Điều phối tác vụ văn bản và hình ảnh đến Google Gemini, DeepSeek, OpenAI ChatGPT, Anthropic Claude.
"""

import os
import sys
import tempfile
import requests
from pathlib import Path

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

_ai_service = None
_rag_service = None
_writer_service = None
_data_service = None
_tools_service = None


def _get_services():
    global _ai_service, _rag_service, _writer_service, _data_service, _tools_service
    import importlib
    try:
        import services.ai_service
        importlib.reload(services.ai_service)
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


# 1. Chat Đa Mô Hình & Vision
def call_chat(
    message: str,
    history: list,
    provider: str = "gemini",
    model: str = None,
    custom_key: str = None,
    image_bytes: bytes = None,
    image_mime: str = "image/jpeg",
    *args,
    **kwargs,
) -> str:
    try:
        import importlib
        import services.ai_service
        importlib.reload(services.ai_service)
        ai = services.ai_service.AIService()
        return ai.chat(
            message=message,
            history=history,
            provider=provider,
            model=model,
            custom_key=custom_key,
            image_bytes=image_bytes,
            image_mime=image_mime,
            *args,
            **kwargs,
        )
    except Exception as e:
        try:
            ai, _, _, _, _ = _get_services()
            if ai:
                return ai.chat(
                    message=message,
                    history=history,
                    provider=provider,
                    model=model,
                    custom_key=custom_key,
                    image_bytes=image_bytes,
                    image_mime=image_mime,
                    *args,
                    **kwargs,
                )
        except Exception as fallback_err:
            return f"Lỗi xử lý AI: {str(fallback_err)}"
        return f"Lỗi kết nối AI Service: {str(e)}"


# 2. RAG
def call_rag_upload(filename: str, file_bytes: bytes) -> dict:
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
    _, rag, _, _, _ = _get_services()
    if rag:
        try:
            ans, src = rag.query(query, filename)
            return {"answer": ans, "sources": src}
        except Exception as e:
            return {"answer": f"Lỗi truy vấn: {str(e)}", "sources": []}
    return {"answer": "Chưa khởi tạo kho vector tài liệu.", "sources": []}


def call_rag_list() -> list:
    _, rag, _, _, _ = _get_services()
    if rag:
        try:
            return rag.list_documents()
        except Exception:
            return []
    return []


# 3. Writer
def call_writer(task_type: str, topic: str, tone: str, language: str, extra: str) -> str:
    _, _, writer, _, _ = _get_services()
    if writer:
        return writer.generate_content(task_type, topic, tone, language, extra)
    return "Lỗi tạo nội dung."


# 4. Data
def call_data_analyze(filename: str, file_bytes: bytes) -> dict:
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
    _, _, _, _, tools = _get_services()
    if tools:
        return tools.process(tool_type, text, target_lang, code_lang)
    return "Lỗi xử lý công cụ."


# 6. Xuất bản tài liệu Word (.docx) & Excel (.xlsx)
def export_to_docx(markdown_text: str, title: str = "Tài liệu AI PTK") -> bytes:
    try:
        import importlib
        import services.export_service
        importlib.reload(services.export_service)
        return services.export_service.ExportService.text_to_docx(markdown_text, title=title)
    except Exception as e:
        print(f"[Bridge] Lỗi xuất Word: {e}")
        try:
            import services.export_service
            return services.export_service.ExportService._pure_python_docx(markdown_text, title=title)
        except Exception as e2:
            return f"Lỗi: {e2}".encode("utf-8")


def export_to_excel(markdown_text_or_df, title: str = "Dữ liệu AI PTK") -> bytes:
    try:
        import importlib
        import services.export_service
        importlib.reload(services.export_service)
        import pandas as pd
        if isinstance(markdown_text_or_df, pd.DataFrame):
            return services.export_service.ExportService.dataframe_to_excel(markdown_text_or_df, title=title)
        return services.export_service.ExportService.text_to_excel(str(markdown_text_or_df), title=title)
    except Exception as e:
        print(f"[Bridge] Lỗi xuất Excel: {e}")
        try:
            import services.export_service
            return services.export_service.ExportService._pure_python_xlsx(
                ["Nội Dung"], [[str(markdown_text_or_df)]], sheet_name="Du_Lieu_AI_PTK"
            )
        except Exception as e2:
            return f"Lỗi: {e2}".encode("utf-8")

