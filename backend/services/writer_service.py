"""
Writer Service - Trợ lý viết nội dung chuyên nghiệp
"""

from services.ai_service import AIService


class WriterService:
    """Tạo nội dung đa dạng: Blog, Email, Marketing, Social Media, Luận văn."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()

    def generate_content(
        self,
        task_type: str,
        topic: str,
        tone: str = "chuyên nghiệp",
        language: str = "Tiếng Việt",
        extra_instructions: str = "",
    ) -> str:
        type_guides = {
            "blog": "Bài viết Blog chuẩn SEO: Tiêu đề cuốn hút, mở bài hook người đọc, thân bài chia các đề mục H2/H3 rõ ràng kèm ví dụ, kết luận và CTA.",
            "email": "Email chuyên nghiệp: Subject line súc tích, lời chào chuẩn mực, nội dung đi thẳng vào vấn đề, call-to-action rõ ràng, lời kết và chữ ký mẫu.",
            "marketing": "Bài viết Marketing / Bán hàng: Tiêu đề hấp dẫn theo công thức AIDA hoặc PAS, khơi gợi nỗi đau/nhu cầu, giải pháp nổi bật với bullet points lợi ích, cam kết và CTA chuyển đổi cao.",
            "social_media": "Post mạng xã hội (Facebook/LinkedIn/Threads): Câu mở đầu viral, icon/emoji phù hợp, nội dung ngắn gọn súc tích, kêu gọi bình luận/chia sẻ, 5-10 hashtags thịnh hành.",
            "essay": "Bài tiểu luận / Báo cáo học thuật: Đặt vấn đề sâu sắc, luận điểm phân tích logic kèm dẫn chứng, phản biện đa chiều, tổng kết và định hướng nghiên cứu."
        }

        guide = type_guides.get(task_type.lower(), "Bài viết chất lượng cao, có cấu trúc chặt chẽ và thông tin xác thực.")

        prompt = f"""Bạn là một chuyên gia viết nội dung xuất sắc.
Hãy tạo nội dung theo yêu cầu sau:

- Loại nội dung: {task_type}
- Hướng dẫn định dạng: {guide}
- Chủ đề: {topic}
- Giọng điệu (tone): {tone}
- Ngôn ngữ: {language}
- Yêu cầu bổ sung: {extra_instructions if extra_instructions else "Không có"}

Đảm bảo văn phong tự nhiên, trình bày đẹp bằng Markdown, cấu trúc mạch lạc và hấp dẫn.
"""
        return self.ai_service.generate(prompt)

