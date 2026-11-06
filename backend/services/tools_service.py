"""
Tools Service - Bộ công cụ tiện ích AI: Dịch thuật, Viết Code, Giải thích Code, Tóm tắt, Sửa ngữ pháp
"""

from services.ai_service import AIService


class ToolsService:
    """Xử lý các tác vụ AI nhanh thường gặp."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()

    def process(
        self,
        tool_type: str,
        text: str,
        target_language: str = "English",
        programming_language: str = "Python",
    ) -> str:
        tt = tool_type.lower()
        if tt == "translate":
            prompt = f"""Bạn là một chuyên gia biên dịch ngôn ngữ.
Hãy dịch đoạn văn bản dưới đây sang {target_language}.
Yêu cầu: Dịch chính xác nghĩa, tự nhiên theo ngữ cảnh bản ngữ, giữ nguyên định dạng gốc và không thêm bình luận ngoài lề.

Văn bản cần dịch:
\"\"\"
{text}
\"\"\"
"""
        elif tt == "code_generate":
            prompt = f"""Bạn là kỹ sư phần mềm cao cấp.
Hãy viết mã nguồn bằng ngôn ngữ {programming_language} đáp ứng yêu cầu sau:
\"{text}\"

Yêu cầu:
- Viết code tối ưu, sạch sẽ, có comment giải thích bằng tiếng Việt.
- Xử lý các edge cases và lỗi tiềm ẩn.
- Kèm theo ví dụ chạy thử (test/usage example).
- Đặt code trong khối markdown ```{programming_language.lower()} ... ```.
"""
        elif tt == "code_explain":
            prompt = f"""Bạn là chuyên gia lập trình và giảng viên IT.
Hãy giải thích chi tiết đoạn code sau bằng tiếng Việt:
```
{text}
```

Yêu cầu:
1. Mục đích tổng quan của đoạn code.
2. Phân tích chi tiết từng khối logic / thuật toán quan trọng.
3. Độ phức tạp thời gian & không gian (Big-O) nếu có.
4. Đánh giá chất lượng và đề xuất các điểm tối ưu (nếu có).
"""
        elif tt == "summarize":
            prompt = f"""Bạn là chuyên gia phân tích và tóm tắt thông tin.
Hãy tóm tắt văn bản sau bằng tiếng Việt theo định dạng:
1. Thông điệp cốt lõi (1-2 câu).
2. Các điểm chính (Bullet points nổi bật).
3. Kết luận hoặc bài học rút ra.

Văn bản:
\"\"\"
{text}
\"\"\"
"""
        elif tt == "grammar_fix":
            prompt = f"""Bạn là biên tập viên ngôn ngữ chuyên nghiệp.
Hãy soát lỗi ngữ pháp, chính tả, cách dùng từ và dấu câu cho văn bản sau:
\"\"\"
{text}
\"\"\"

Yêu cầu:
1. Bản văn bản đã sửa hoàn chỉnh, trau chuốt và mạch lạc.
2. Bảng liệt kê các lỗi phát hiện (Lỗi cũ -> Đã sửa -> Lý do sửa).
"""
        else:
            prompt = f"Hãy xử lý văn bản sau theo yêu cầu {tool_type}:\n{text}"

        return self.ai_service.generate(prompt)

