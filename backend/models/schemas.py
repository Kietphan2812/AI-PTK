"""
Data schemas using Pydantic for request/response validation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# 1. Chat
class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' hoặc 'model'")
    parts: str = Field(..., description="Nội dung tin nhắn")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Tin nhắn người dùng")
    history: List[Dict[str, Any]] = Field(
        default=[], description="Lịch sử hội thoại [{role, parts}]"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Câu trả lời từ AI")


# 2. RAG
class RAGUploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Câu hỏi cần tra cứu")
    filename: str = Field(..., description="Tên file tài liệu")


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default=[], description="Các đoạn trích nguồn")


# 3. Writer
class WriterRequest(BaseModel):
    task_type: str = Field(..., description="blog, email, marketing, social_media, essay")
    topic: str = Field(..., description="Chủ đề bài viết")
    tone: str = Field(default="chuyên nghiệp", description="Giọng điệu")
    language: str = Field(default="Tiếng Việt", description="Ngôn ngữ")
    extra_instructions: str = Field(default="", description="Yêu cầu bổ sung")


class WriterResponse(BaseModel):
    content: str


# 4. Data Analysis
class DataAnalysisResponse(BaseModel):
    summary: str
    columns: List[str]
    row_count: int
    ai_insights: str
    chart_html: str = ""


# 5. Tools
class ToolRequest(BaseModel):
    tool_type: str = Field(
        ...,
        description="translate, code_generate, code_explain, summarize, grammar_fix",
    )
    text: str = Field(..., description="Văn bản hoặc code đầu vào")
    target_language: str = Field(default="English", description="Ngôn ngữ đích cho dịch")
    programming_language: str = Field(default="Python", description="Ngôn ngữ lập trình")


class ToolResponse(BaseModel):
    result: str

