"""
RAG Service - Retrieval Augmented Generation cho file PDF
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
import chromadb
from config import settings
from services.ai_service import AIService


class RAGService:
    """Xử lý đọc PDF, cắt đoạn, lưu vào ChromaDB và truy vấn ngữ cảnh."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()
        os.makedirs(settings.CHROMA_DIR, exist_ok=True)
        # ChromaDB PersistentClient nhận path dạng str
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))

    def _sanitize_name(self, filename: str) -> str:
        """Chuyển tên file thành tên collection ChromaDB hợp lệ (3-63 ký tự alphanumeric / _ / -)."""
        clean = re.sub(r"[^a-zA-Z0-9_\-]", "_", filename)
        clean = clean.strip("_-")
        if not clean or not clean[0].isalpha():
            clean = "col_" + clean
        if len(clean) < 3:
            clean = clean + "_rag"
        return clean[:63]

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Đọc nội dung text từ file PDF."""
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Cắt đoạn văn bản theo chunk_size và overlap."""
        chunks = []
        start = 0
        text = text.strip()
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def process_pdf(self, file_path: str, filename: str) -> int:
        """Đọc PDF, tạo vector store trong ChromaDB."""
        text = self._extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("Không thể trích xuất văn bản từ file PDF (có thể là file scan hoặc bị khóa).")

        chunks = self._split_text(text, chunk_size=500, overlap=50)
        if not chunks:
            raise ValueError("Tài liệu trống sau khi trích xuất.")

        col_name = self._sanitize_name(filename)
        # Nếu collection đã tồn tại thì xóa để nạp lại mới
        try:
            self.chroma_client.delete_collection(name=col_name)
        except Exception:
            pass

        collection = self.chroma_client.create_collection(
            name=col_name,
            metadata={"filename": filename}
        )

        ids = [f"chk_{i}" for i in range(len(chunks))]
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        )
        return len(chunks)

    def query(self, query: str, filename: str) -> Tuple[str, List[str]]:
        """Truy vấn câu trả lời dựa trên nội dung tài liệu."""
        col_name = self._sanitize_name(filename)
        try:
            collection = self.chroma_client.get_collection(name=col_name)
        except Exception:
            return f"Không tìm thấy tài liệu '{filename}'. Hãy upload trước.", []

        results = collection.query(query_texts=[query], n_results=4)
        retrieved_docs = results.get("documents", [[]])[0]

        if not retrieved_docs:
            return "Không tìm thấy nội dung liên quan trong tài liệu.", []

        context = "\n---\n".join(retrieved_docs)
        prompt = f"""Bạn là trợ lý hỏi đáp tài liệu thông minh. Dưới đây là ngữ cảnh trích xuất từ tài liệu "{filename}":
{context}

---
Dựa vào ngữ cảnh trên, hãy trả lời câu hỏi sau một cách chi tiết, chính xác và trung thực:
Câu hỏi: {query}

Nếu trong ngữ cảnh không có thông tin để trả lời, hãy nói rõ là tài liệu không đề cập đến vấn đề này.
"""
        answer = self.ai_service.generate(prompt)
        return answer, retrieved_docs

    def list_documents(self) -> List[str]:
        """Liệt kê danh sách các tài liệu đã có trong kho vector."""
        try:
            cols = self.chroma_client.list_collections()
            doc_names = []
            for col in cols:
                meta = getattr(col, "metadata", {}) or {}
                doc_name = meta.get("filename", col.name)
                doc_names.append(doc_name)
            return doc_names
        except Exception:
            return []

