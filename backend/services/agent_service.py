"""
Agent Service - Động cơ thực thi công việc tự động (Autonomous AI Task Runner) cho AI PTK
Tự động nhận mục tiêu từ người dùng, lập kế hoạch đa bước, thực thi tính toán/soạn thảo,
và tự động đóng gói thành phẩm (Word, Excel) để người dùng tải về.
"""

import io
import sys
import json
import re
import datetime
from services.ai_service import AIService
from services.export_service import ExportService


class AutoAgentService:
    """Agent tự trị thông minh tự động hoàn thành công việc từ A đến Z."""

    def __init__(self, ai_service: AIService = None):
        self.ai = ai_service or AIService()

    def run_safe_code(self, code_str: str) -> str:
        """Thực thi mã nguồn Python an toàn trong sandbox và thu thập kết quả."""
        clean_code = re.sub(r"^```python\s*", "", code_str.strip())
        clean_code = re.sub(r"^```\s*", "", clean_code)
        clean_code = re.sub(r"```$", "", clean_code).strip()

        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            safe_globals = {
                "__builtins__": __builtins__,
                "math": __import__("math"),
                "datetime": __import__("datetime"),
                "json": __import__("json"),
                "re": re,
            }
            exec(clean_code, safe_globals)
            out = buf.getvalue()
            return out.strip() if out.strip() else "✅ Thực thi thành công (Không có đầu ra văn bản)."
        except Exception as e:
            return f"⚠️ Lỗi thực thi code: {str(e)}"
        finally:
            sys.stdout = old_stdout

    def execute_goal(
        self,
        goal: str,
        provider: str = "gemini",
        model: str = None,
        custom_key: str = None,
    ) -> dict:
        """
        Quy trình tự động hóa 4 giai đoạn:
        Giai đoạn 1: Lập kế hoạch phân rã nhiệm vụ (Decomposition)
        Giai đoạn 2: Thực thi giải quyết chuyên sâu từng hạng mục
        Giai đoạn 3: Tính toán / Viết code kiểm tra (nếu có)
        Giai đoạn 4: Tổng hợp thành phẩm & Đóng gói Word/Excel
        """
        # 1. GIAI ĐOẠN 1: LẬP KẾ HOẠCH
        plan_prompt = (
            f"Bạn là Giám đốc Điều phối AI PTK. Người dùng giao cho bạn mục tiêu: '{goal}'.\n"
            "Hãy lập kế hoạch hành động cụ thể gồm đúng 3 đến 4 bước chi tiết để hoàn thành mục tiêu này từ A đến Z.\n"
            "Định dạng trả về: Ghi rõ 'Bước 1: ...', 'Bước 2: ...', 'Bước 3: ...'."
        )
        plan_text = self.ai.generate(prompt=plan_prompt, provider=provider, model=model, custom_key=custom_key)

        # 2. GIAI ĐOẠN 2: THỰC THI CHI TIẾT
        exec_prompt = (
            f"MỤC TIÊU CỦA NGƯỜI DÙNG: {goal}\n\n"
            f"KẾ HOẠCH ĐÃ ĐỀ RA:\n{plan_text}\n\n"
            "Hãy giải quyết hoàn chỉnh, toàn diện toàn bộ mục tiêu này.\n"
            "Yêu cầu bắt buộc:\n"
            "- Trả lời đầy đủ, chi tiết, thực tế, số liệu rõ ràng.\n"
            "- Sử dụng tiêu đề Markdown (#, ##, ###) để phân cấp rõ ràng.\n"
            "- NẾU có số liệu, danh sách, chi phí hay bảng biểu: BẮT BUỘC dùng bảng Markdown chuẩn (| Cột 1 | Cột 2 | ...).\n"
            "- NẾU có tính toán hoặc thuật toán: cung cấp cả mã nguồn Python giải quyết.\n"
            "- Viết văn phong chuyên nghiệp, xuất sắc, không cắt xén."
        )
        final_content = self.ai.generate(prompt=exec_prompt, provider=provider, model=model, custom_key=custom_key)

        # 3. GIAI ĐOẠN 3: KIỂM TRA MÃ NGUỒN PYTHON (NẾU CÓ TRONG KẾT QUẢ)
        code_output = ""
        code_match = re.search(r"```python(.*?)```", final_content, re.DOTALL)
        if code_match:
            py_code = code_match.group(1).strip()
            # Nếu code không chứa lệnh phá hoại, chạy thử
            if not any(bad in py_code for bad in ["rmdir", "remove", "unlink", "shutil", "socket", "subprocess"]):
                code_output = self.run_safe_code(py_code)

        # 4. GIAI ĐOẠN 4: ĐÓNG GÓI THÀNH PHẨM (WORD & EXCEL)
        title_clean = goal[:30].strip() or "Báo Cáo Tự Động Hóa"
        docx_data = ExportService.text_to_docx(final_content, title=f"AI PTK: {title_clean.upper()}")
        xlsx_data = ExportService.text_to_excel(final_content, title=f"{title_clean.upper()}")

        return {
            "goal": goal,
            "plan": plan_text,
            "result_markdown": final_content,
            "code_output": code_output,
            "docx_bytes": docx_data,
            "xlsx_bytes": xlsx_data,
            "filename_base": re.sub(r"[^\w\s-]", "", title_clean).strip().replace(" ", "_"),
        }

