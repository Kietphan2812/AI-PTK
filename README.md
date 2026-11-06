# 🚀 AI PTK - Platform Tích Hợp Kiến Thức (All-In-One AI Platform)

Hệ thống ứng dụng AI đa năng tích hợp đầy đủ 5 mô-đun cốt lõi:
1. 💬 **Chat AI**: Hội thoại thông minh đa lượt với Google Gemini 2.0 Flash.
2. 📄 **Hỏi Đáp PDF (RAG)**: Băm nhỏ tài liệu, lưu vector vào ChromaDB và truy vấn chính xác kèm trích dẫn nguồn.
3. ✍️ **Sáng Tạo Nội Dung**: Viết Blog SEO, Email, Marketing Copywriting, Post mạng xã hội và Tiểu luận học thuật.
4. 📊 **Phân Tích Dữ Liệu CSV**: Tự động tính toán thống kê, trực quan hóa biểu đồ Plotly tương tác và nhận định từ AI.
5. 🔧 **Tiện Ích AI Nhanh**: Dịch thuật đa ngôn ngữ, sinh mã nguồn, giải thích code, tóm tắt ý chính và soát lỗi văn phạm.

---

## 🛠️ Cấu Trúc Dự Án

```
AI PTK/
├── .env                       # Chứa GEMINI_API_KEY
├── .gitignore
├── README.md
├── backend/                   # Backend FastAPI
│   ├── main.py                # Server FastAPI & API Endpoints
│   ├── config.py              # Cấu hình môi trường
│   ├── requirements.txt       # Thư viện backend
│   ├── models/
│   │   └── schemas.py         # Pydantic Schemas
│   └── services/              # 5 Dịch vụ AI lõi
│       ├── ai_service.py      # Gemini API Wrapper
│       ├── rag_service.py     # Xử lý PDF + ChromaDB Vector Store
│       ├── writer_service.py  # Sinh nội dung văn bản
│       ├── data_service.py    # Phân tích CSV & Plotly Charts
│       └── tools_service.py   # Dịch, code, tóm tắt, sửa lỗi
└── frontend/                  # Giao diện Web Streamlit
    ├── app.py                 # Trang chủ Dashboard
    ├── requirements.txt       # Thư viện frontend
    └── pages/                 # 5 Tab tính năng
        ├── 1_💬_Chat.py
        ├── 2_📄_PDF_QA.py
        ├── 3_✍️_Writer.py
        ├── 4_📊_Data.py
        └── 5_🔧_Tools.py
```

---

## ⚡ Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Bước 1: Cấu hình Gemini API Key
1. Truy cập [Google AI Studio](https://aistudio.google.com/) để lấy API Key miễn phí.
2. Mở file `.env` tại thư mục gốc dự án và dán key:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
```

### Bước 2: Cài đặt thư viện Python
Nên tạo một môi trường ảo (Virtual Environment):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Cài đặt dependencies cho Backend và Frontend:
```powershell
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Bước 3: Khởi chạy hệ thống (Mở 2 cửa sổ terminal)

**Terminal 1 - Chạy Backend FastAPI:**
```powershell
cd backend
uvicorn main:app --reload --port 8000
```
*API docs tự động có tại: http://localhost:8000/docs*

**Terminal 2 - Chạy Frontend Streamlit:**
```powershell
cd frontend
streamlit run app.py --server.port 8501
```
*Giao diện người dùng sẽ tự động mở tại: http://localhost:8501*

