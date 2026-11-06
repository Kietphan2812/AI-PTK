"""
AI PTK – Backend API Server (FastAPI)
=====================================
Chạy:
    cd backend && uvicorn main:app --reload --port 8000
"""

import os
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.schemas import (
    ChatRequest,
    ChatResponse,
    RAGUploadResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    WriterRequest,
    WriterResponse,
    DataAnalysisResponse,
    ToolRequest,
    ToolResponse,
)
from services.ai_service import AIService
from services.rag_service import RAGService
from services.writer_service import WriterService
from services.data_service import DataService
from services.tools_service import ToolsService

# Instances
ai_service: AIService = None  # type: ignore
rag_service: RAGService = None  # type: ignore
writer_service: WriterService = None  # type: ignore
data_service: DataService = None  # type: ignore
tools_service: ToolsService = None  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_service, rag_service, writer_service, data_service, tools_service
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)

    try:
        ai_service = AIService()
        rag_service = RAGService(ai_service=ai_service)
        writer_service = WriterService(ai_service=ai_service)
        data_service = DataService(ai_service=ai_service)
        tools_service = ToolsService(ai_service=ai_service)
        print("✅ Tất cả services AI PTK đã sẵn sàng!")
    except Exception as e:
        print(f"⚠️ Cảnh báo khởi tạo: {e}")

    yield
    print("🛑 Backend đang tắt...")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Bộ công cụ AI PTK: Chat, RAG PDF, Writer, Data Analysis, Tools",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "model": settings.GEMINI_MODEL,
        "api_key_configured": bool(
            settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"
        ),
    }


# 1. Chat
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    try:
        reply = ai_service.chat(message=request.message, history=request.history)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")


# 2. RAG
@app.post("/api/rag/upload", response_model=RAGUploadResponse, tags=["RAG"])
async def rag_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file định dạng .pdf")

    file_path = os.path.join(str(settings.UPLOAD_DIR), file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks_count = rag_service.process_pdf(file_path, file.filename)
        return RAGUploadResponse(
            filename=file.filename,
            chunks=chunks_count,
            message=f"Đã xử lý và lập chỉ mục {chunks_count} đoạn văn bản thành công!",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file PDF: {str(e)}")


@app.post("/api/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
async def rag_query(request: RAGQueryRequest):
    try:
        answer, sources = rag_service.query(query=request.query, filename=request.filename)
        return RAGQueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn RAG: {str(e)}")


@app.get("/api/rag/documents", tags=["RAG"])
async def list_rag_documents():
    try:
        docs = rag_service.list_documents()
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách tài liệu: {str(e)}")


# 3. Writer
@app.post("/api/writer/generate", response_model=WriterResponse, tags=["Writer"])
async def writer_generate(request: WriterRequest):
    try:
        content = writer_service.generate_content(
            task_type=request.task_type,
            topic=request.topic,
            tone=request.tone,
            language=request.language,
            extra_instructions=request.extra_instructions,
        )
        return WriterResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo nội dung: {str(e)}")


# 4. Data
@app.post("/api/data/analyze", response_model=DataAnalysisResponse, tags=["Data"])
async def data_analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file định dạng .csv")

    file_path = os.path.join(str(settings.UPLOAD_DIR), file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = data_service.analyze_csv(file_path)
        return DataAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân tích CSV: {str(e)}")


# 5. Tools
@app.post("/api/tools/process", response_model=ToolResponse, tags=["Tools"])
async def tools_process(request: ToolRequest):
    try:
        output = tools_service.process(
            tool_type=request.tool_type,
            text=request.text,
            target_language=request.target_language,
            programming_language=request.programming_language,
        )
        return ToolResponse(result=output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý tiện ích: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

