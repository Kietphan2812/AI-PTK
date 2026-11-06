"""
RAG Service - Retrieval Augmented Generation cho file PDF
Tự động dùng ChromaDB nếu có, hoặc dùng In-Memory Vector Store siêu nhẹ nếu chạy trên Cloud
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2

try:
    import chromadb
    HAS_CHROMADB = True
except Exception:
    HAS_CHROMADB = False

from config import settings
from services.ai_service import AIService


class RAGService:
    """Xử lý đọc PDF, cắt đoạn và truy vấn ngữ cảnh thông minh."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()
        self.in_memory_docs: Dict[str, List[str]] = {}

        self.chroma_client = None
        if HAS_CHROMADB:
            try:
                os.makedirs(settings.CHROMA_DIR, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
            except Exception as e:
                print(f"[RAG] ChromaDB init fallback to memory: {e}")
                self.chroma_client = None

    def _sanitize_name(self, filename: str) -> str:
        clean = re.sub(r"[^a-zA-Z0-9_\-]", "_", filename)
        clean = clean.strip("_-")
        if not clean or not clean[0].isalpha():
            clean = "col_" + clean
        if len(clean) < 3:
            clean = clean + "_rag"
        return clean[:63]

    def _extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
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
        text = self._extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("Không thể trích xuất văn bản từ file PDF (có thể là file scan hoặc bị khóa).")

        chunks = self._split_text(text, chunk_size=500, overlap=50)
        if not chunks:
            raise ValueError("Tài liệu trống sau khi trích xuất.")

        # Lưu vào in-memory store
        self.in_memory_docs[filename] = chunks

        # Nếu có ChromaDB, lưu thêm vào ChromaDB
        if self.chroma_client:
            try:
                col_name = self._sanitize_name(filename)
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
            except Exception as e:
                print(f"[RAG] ChromaDB add fallback: {e}")

        return len(chunks)

    def query(self, query: str, filename: str) -> Tuple[str, List[str]]:
        chunks = self.in_memory_docs.get(filename, [])

        # Nếu có ChromaDB và chưa có trong memory
        if not chunks and self.chroma_client:
            try:
                col_name = self._sanitize_name(filename)
                collection = self.chroma_client.get_collection(name=col_name)
                results = collection.query(query_texts=[query], n_results=4)
                retrieved_docs = results.get("documents", [[]])[0]
                if retrieved_docs:
                    chunks = retrieved_docs
            except Exception:
                pass

        if not chunks:
            return f"Không tìm thấy tài liệu '{filename}'. Hãy upload trước.", []

        # Xếp hạng đoạn phù hợp theo từ khóa câu hỏi
        query_words = set(re.findall(r"\w+", query.lower()))
        scored_chunks = []
        for chk in chunks:
            chk_words = set(re.findall(r"\w+", chk.lower()))
            overlap = len(query_words.intersection(chk_words))
            scored_chunks.append((overlap, chk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c[1] for c in scored_chunks[:4]]

        context = "\n---\n".join(top_chunks)
        prompt = f"""Bạn là trợ lý hỏi đáp tài liệu thông minh. Dưới đây là ngữ cảnh trích xuất từ tài liệu "{filename}":
{context}

---
Dựa vào ngữ cảnh trên, hãy trả lời câu hỏi sau một cách chi tiết, chính xác và trung thực bằng tiếng Việt:
Câu hỏi: {query}

Nếu trong ngữ cảnh không có thông tin để trả lời, hãy nói rõ là tài liệu không đề cập đến vấn đề này.
"""
        answer = self.ai_service.generate(prompt)
        return answer, top_chunks

    def list_documents(self) -> List[str]:
        names = list(self.in_memory_docs.keys())
        if self.chroma_client:
            try:
                cols = self.chroma_client.list_collections()
                for col in cols:
                    meta = getattr(col, "metadata", {}) or {}
                    doc_name = meta.get("filename", col.name)
                    if doc_name not in names:
                        names.append(doc_name)
            except Exception:
                pass
        return names
