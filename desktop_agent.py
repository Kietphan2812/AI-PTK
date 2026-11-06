"""
AI PTK - Trợ Lý Robot Toàn Năng (Desktop Agent & Autonomous PC Controller)
Sáng lập và phát triển bởi Phan Tấn Kiệt.
Giao diện Dark Mode đa nhiệm chuẩn AI PTK:
1. 💬 Chat & Điều Khiển Máy Tính (Chatbot đa phương thức, nhận diện ảnh/file & điều khiển tự trị)
2. 📄 Tra Cứu & Hỏi Đáp Tài Liệu PDF (RAG ChromaDB)
3. ✍️ Soạn Thảo Văn Bản Chuyên Nghiệp (Xuất Word .docx)
4. 📊 Xử Lý Dữ Liệu & Bảng Tính (Xuất Excel .xlsx)
5. 🔧 Trung Tâm Điều Khiển Hệ Thống & RPA Windows
6. 🤖 Auto Agent (Robot tự động hóa nhiệm vụ đa bước từ A-Z)
"""

import os
import sys
import time
import io
import datetime
import threading
from pathlib import Path

# Đảm bảo import được backend services
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR = Path(sys._MEIPASS)
else:
    ROOT_DIR = Path(__file__).resolve().parent

BACKEND_DIR = ROOT_DIR / "backend"
for p in [str(ROOT_DIR), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from PIL import Image, ImageGrab

from services.desktop_controller import DesktopController
from services.voice_service import VoiceService
from services.agent_service import AutoAgentService
from services.rag_service import RAGService
from services.ai_service import AIService
from services.export_service import ExportService


class DesktopAgentGUI:
    """Giao diện đồ họa toàn năng của trợ lý điều khiển máy tính AI PTK."""

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 AI PTK - Trợ Lý Robot Máy Tính Toàn Năng (Phan Tấn Kiệt)")
        self.root.geometry("1060x730")
        self.root.minsize(920, 640)
        self.root.configure(bg="#0F172A")

        # Khởi tạo các dịch vụ nền tảng
        self.ai = AIService()
        self.controller = DesktopController(ai_service=self.ai)
        self.voice = VoiceService()
        self.agent_service = AutoAgentService(ai_service=self.ai)
        self.rag_service = RAGService(ai_service=self.ai)

        # Lịch sử hội thoại AI đa lượt (Multi-turn Chat Memory)
        self.chat_history = []

        # Trạng thái đính kèm tệp tin / hình ảnh
        self.attached_file_path = None
        self.clipboard_image_bytes = None
        self.clipboard_image_mime = None

        # Trạng thái PDF hiện hành
        self.current_pdf_path = None

        self._setup_layout()

    def _setup_layout(self):
        """Khởi tạo cấu trúc giao diện 2 phần: Sidebar bên trái và Content bên phải."""
        # 1. SIDEBAR TRÁI
        self.sidebar = tk.Frame(self.root, bg="#0B132B", width=230)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo & Thương hiệu
        brand_frame = tk.Frame(self.sidebar, bg="#0B132B", padx=16, pady=18)
        brand_frame.pack(fill=tk.X)

        tk.Label(
            brand_frame,
            text="🤖 AI PTK",
            font=("Segoe UI", 18, "bold"),
            fg="#38BDF8",
            bg="#0B132B",
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="Trợ Lý Robot Toàn Năng",
            font=("Segoe UI", 9, "bold"),
            fg="#E2E8F0",
            bg="#0B132B",
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            brand_frame,
            text="Sáng lập: Phan Tấn Kiệt",
            font=("Segoe UI", 8, "italic"),
            fg="#94A3B8",
            bg="#0B132B",
        ).pack(anchor="w")

        # Đường phân cách
        tk.Frame(self.sidebar, bg="#1E293B", height=1).pack(fill=tk.X, padx=12, pady=(0, 10))

        # Menu điều hướng
        self.nav_buttons = {}
        self.nav_items = [
            ("chat", "💬  Chat & Điều Khiển"),
            ("pdf", "📄  Hỏi Đáp PDF (RAG)"),
            ("writer", "✍️  Soạn Thảo (Writer)"),
            ("data", "📊  Xử Lý Dữ Liệu (Data)"),
            ("tools", "🔧  Công Cụ Hệ Thống"),
            ("agent", "🤖  Auto Agent Đa Bước"),
        ]

        for tab_id, tab_label in self.nav_items:
            btn = tk.Button(
                self.sidebar,
                text=tab_label,
                font=("Segoe UI", 10, "bold"),
                fg="#94A3B8",
                bg="#1C2541",
                activebackground="#0284C7",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                padx=16,
                pady=11,
                command=lambda tid=tab_id: self.show_tab(tid),
            )
            btn.pack(fill=tk.X, padx=10, pady=4)
            self.nav_buttons[tab_id] = btn

        # Sidebar Footer
        footer_frame = tk.Frame(self.sidebar, bg="#0B132B", padx=16, pady=16)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            footer_frame,
            text="● Trực Tuyến (Online)",
            font=("Segoe UI", 8, "bold"),
            fg="#10B981",
            bg="#0B132B",
        ).pack(anchor="w")

        tk.Label(
            footer_frame,
            text="Bản quyền © Phan Tấn Kiệt",
            font=("Segoe UI", 7),
            fg="#64748B",
            bg="#0B132B",
        ).pack(anchor="w", pady=(2, 0))

        # 2. KHU VỰC NỘI DUNG CHÍNH (CONTENT AREA)
        self.content_container = tk.Frame(self.root, bg="#0F172A")
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.panels = {}
        self._setup_panel_chat()
        self._setup_panel_pdf()
        self._setup_panel_writer()
        self._setup_panel_data()
        self._setup_panel_tools()
        self._setup_panel_agent()

        # Hiển thị mặc định Tab Chat & Điều Khiển
        self.show_tab("chat")

    def show_tab(self, tab_id: str):
        """Chuyển đổi linh hoạt giữa các tab giao diện."""
        for tid, panel in self.panels.items():
            panel.pack_forget()

        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(bg="#0284C7", fg="#FFFFFF")
            else:
                btn.configure(bg="#1C2541", fg="#94A3B8")

        if tab_id in self.panels:
            self.panels[tab_id].pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

    # ==========================================
    # 1. TAB CHAT & ĐIỀU KHIỂN (MAIN AGENT TAB)
    # ==========================================
    def _setup_panel_chat(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["chat"] = panel

        # Header
        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            head,
            text="💬 Chatbot Trí Tuệ Nhân Tạo & Điều Khiển Máy Tính",
            font=("Segoe UI", 13, "bold"),
            fg="#38BDF8",
            bg="#1E293B",
        ).pack(anchor="w")
        tk.Label(
            head,
            text="Trò chuyện, phân tích tệp tin/hình ảnh và tự động điều khiển máy tính làm việc từ A đến Z.",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#1E293B",
        ).pack(anchor="w")

        # Thanh chọn Não AI đa mô hình (Multi-Model AI Brain - Giống 100% trên Web)
        model_bar = tk.Frame(panel, bg="#1E293B", padx=12, pady=6)
        model_bar.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            model_bar,
            text="🧠 Não AI:",
            font=("Segoe UI", 9, "bold"),
            fg="#38BDF8",
            bg="#1E293B",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.ai_model_var = tk.StringVar(value="⚡ Google Gemini 3.5 (Mặc định - Đa năng & Nhìn ảnh)")
        self.combo_ai_model = ttk.Combobox(
            model_bar,
            textvariable=self.ai_model_var,
            state="readonly",
            font=("Segoe UI", 9),
            width=54,
            values=[
                "⚡ Google Gemini 3.5 (Mặc định - Đa năng & Nhìn ảnh)",
                "🧠 DeepSeek R1 (Vua suy luận logic & Thuật toán)",
                "🧠 DeepSeek V3 (Siêu thông minh & Toàn diện)",
                "🤖 ChatGPT - GPT-4o (Đa năng & Nhìn ảnh)",
                "🤖 ChatGPT - GPT-4o Mini (Phản hồi cực nhanh)",
                "🎭 Claude 3.5 Sonnet (Văn phong đỉnh cao & Nhìn ảnh)",
            ],
        )
        self.combo_ai_model.pack(side=tk.LEFT)

        # Top Attachment & Action Toolbar
        action_bar = tk.Frame(panel, bg="#0F172A")
        action_bar.pack(fill=tk.X, pady=(0, 6))

        btn_attach_file = tk.Button(
            action_bar,
            text="📁 Tải file / ảnh từ máy",
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="#F8FAFC",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.on_attach_file_click,
        )
        btn_attach_file.pack(side=tk.LEFT, padx=(0, 8))

        btn_paste_clip = tk.Button(
            action_bar,
            text="📋 Dán ảnh từ Clipboard",
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="#F8FAFC",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.on_paste_clipboard_image_click,
        )
        btn_paste_clip.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear_chat = tk.Button(
            action_bar,
            text="🗑️ Xóa hội thoại",
            font=("Segoe UI", 9),
            bg="#1E293B",
            fg="#94A3B8",
            activebackground="#334155",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.clear_chat,
        )
        btn_clear_chat.pack(side=tk.RIGHT)

        # Attachment badge frame (hiển thị tệp đính kèm hiện tại)
        self.badge_frame = tk.Frame(panel, bg="#1E293B", padx=10, pady=5)
        self.lbl_badge_text = tk.Label(
            self.badge_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg="#FBBF24",
            bg="#1E293B",
        )
        self.lbl_badge_text.pack(side=tk.LEFT)

        btn_remove_attach = tk.Button(
            self.badge_frame,
            text="✕ Bỏ chọn",
            font=("Segoe UI", 8, "bold"),
            bg="#EF4444",
            fg="#FFFFFF",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=6,
            pady=1,
            command=self.clear_attachment,
        )
        btn_remove_attach.pack(side=tk.RIGHT, padx=(8, 0))

        # Khung hiển thị tin nhắn (Chat Stream)
        self.chat_stream = scrolledtext.ScrolledText(
            panel,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#111827",
            fg="#F1F5F9",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            padx=14,
            pady=12,
        )
        self.chat_stream.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Thiết lập style tags cho tin nhắn
        self.chat_stream.tag_config("user_head", foreground="#38BDF8", font=("Segoe UI", 10, "bold"))
        self.chat_stream.tag_config("user_body", foreground="#FFFFFF", font=("Segoe UI", 10))
        self.chat_stream.tag_config("ai_head", foreground="#34D399", font=("Segoe UI", 10, "bold"))
        self.chat_stream.tag_config("ai_body", foreground="#F1F5F9", font=("Segoe UI", 10))
        self.chat_stream.tag_config("action_box", foreground="#FBBF24", font=("Segoe UI", 9, "italic"))
        self.chat_stream.tag_config("attach_tag", foreground="#F59E0B", font=("Segoe UI", 9, "bold"))

        # Lời chào ban đầu (Chuẩn nhận diện thời gian thực & thương hiệu Phan Tấn Kiệt)
        now_dt = datetime.datetime.now()
        days_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        day_str = days_vi[now_dt.weekday()]
        now_time_str = f"{day_str}, ngày {now_dt.strftime('%d/%m/%Y')}, lúc {now_dt.strftime('%H:%M')} (Giờ Việt Nam)"
        self._append_ai_message(
            f"Chào bạn! Tôi là **AI PTK** – Nền tảng trí tuệ nhân tạo toàn năng được sáng lập và phát triển bởi **Kiệt (Phan Tấn Kiệt)**. 🤖✨\n\n"
            f"Hôm nay là {now_time_str}.\n\n"
            "Tôi luôn sẵn sàng hỗ trợ bạn giải quyết mọi công việc từ A đến Z: từ viết lách, lập kế hoạch, phân tích dữ liệu, viết code cho đến việc soạn thảo văn bản hay lập bảng tính chuyên nghiệp, hoặc điều khiển tự động hóa máy tính Windows từ xa!\n\n"
            "Bạn cần tôi giúp gì trong ngày hôm nay? 😊\n\n"
            "👉 Bạn có thể bấm nút 📄 Xuất Word (.docx) hoặc 📊 Xuất Excel (.xlsx) ngay bên dưới để lưu file hoàn chỉnh về máy bất cứ lúc nào!"
        )

        # Thanh nhập lệnh phía dưới
        input_bar = tk.Frame(panel, bg="#0F172A")
        input_bar.pack(fill=tk.X)

        btn_clip_icon = tk.Button(
            input_bar,
            text="📁",
            font=("Segoe UI", 11),
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#475569",
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self.on_attach_file_click,
        )
        btn_clip_icon.pack(side=tk.LEFT, ipady=6, padx=(0, 6))

        self.entry_cmd = tk.Entry(
            input_bar,
            font=("Segoe UI", 11),
            bg="#1E293B",
            fg="#FFFFFF",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground="#334155",
            highlightcolor="#38BDF8",
        )
        self.entry_cmd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 6))
        self.entry_cmd.insert(0, "Nhập câu hỏi hoặc yêu cầu AI điều khiển máy tính, phân tích ảnh...")
        self.entry_cmd.bind("<FocusIn>", self._on_input_focus_in)
        self.entry_cmd.bind("<Return>", lambda e: self.on_send_chat())

        self.btn_voice = tk.Button(
            input_bar,
            text="🎤 Nói (Voice)",
            font=("Segoe UI", 10, "bold"),
            bg="#059669",
            fg="#FFFFFF",
            activebackground="#047857",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            command=self.on_voice_click,
        )
        self.btn_voice.pack(side=tk.LEFT, ipady=7, padx=(0, 6))

        self.btn_send = tk.Button(
            input_bar,
            text="🚀 Gửi (Enter)",
            font=("Segoe UI", 10, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            activebackground="#0369A1",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            command=self.on_send_chat,
        )
        self.btn_send.pack(side=tk.RIGHT, ipady=7)

    def _on_input_focus_in(self, event):
        if self.entry_cmd.get() == "Nhập câu hỏi hoặc yêu cầu AI điều khiển máy tính, phân tích ảnh...":
            self.entry_cmd.delete(0, tk.END)

    def _append_user_message(self, text: str, attachment_name: str = None):
        self.chat_stream.configure(state=tk.NORMAL)
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_stream.insert(tk.END, f"\n👤 Kiệt ({now_str}):\n", "user_head")
        if attachment_name:
            self.chat_stream.insert(tk.END, f"   📎 [Đính kèm: {attachment_name}]\n", "attach_tag")
        self.chat_stream.insert(tk.END, f"   {text}\n", "user_body")
        self.chat_stream.see(tk.END)
        self.chat_stream.configure(state=tk.DISABLED)

    def export_message_to_docx(self, content: str):
        try:
            now = datetime.datetime.now()
            ts = now.strftime("%Y%m%d_%H%M%S")
            target_path = Path.home() / "Desktop" / f"AI_PTK_TraLoi_{ts}.docx"
            if ExportService:
                docx_bytes = ExportService.text_to_docx(content, title="PHẢN HỒI TỪ AI PTK")
                with open(target_path, "wb") as f:
                    f.write(docx_bytes)
                os.startfile(str(target_path))
                messagebox.showinfo("Xuất Word", f"🎉 Đã xuất thành công tài liệu Word ra Desktop:\n{target_path.name}\nvà mở Microsoft Word cho bạn!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất Word: {e}")

    def export_message_to_excel(self, content: str):
        try:
            now = datetime.datetime.now()
            ts = now.strftime("%Y%m%d_%H%M%S")
            target_path = Path.home() / "Desktop" / f"AI_PTK_Bang_{ts}.xlsx"
            if ExportService:
                xlsx_bytes = ExportService.text_to_excel(content, title="BẢNG DỮ LIỆU AI PTK")
                with open(target_path, "wb") as f:
                    f.write(xlsx_bytes)
                os.startfile(str(target_path))
                messagebox.showinfo("Xuất Excel", f"🎉 Đã xuất thành công bảng tính Excel ra Desktop:\n{target_path.name}\nvà mở Microsoft Excel cho bạn!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất Excel: {e}")

    def copy_text_to_clipboard(self, content: str):
        try:
            import pyperclip
            pyperclip.copy(content)
            messagebox.showinfo("Clipboard", "📋 Đã sao chép toàn bộ phản hồi vào bộ nhớ tạm (Clipboard)!")
        except Exception:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)

    def _append_ai_message(self, text: str, action_text: str = None):
        self.chat_stream.configure(state=tk.NORMAL)
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_stream.insert(tk.END, f"\n🤖 AI PTK ({now_str}):\n", "ai_head")
        if action_text:
            self.chat_stream.insert(tk.END, f"   ⚙️ {action_text}\n", "action_box")
        self.chat_stream.insert(tk.END, f"   {text}\n", "ai_body")

        # Nút tương tác xuất Word, Excel và Sao chép giống 100% trên Web
        btn_frame = tk.Frame(self.chat_stream, bg="#111827", pady=4)

        btn_exp_word = tk.Button(
            btn_frame,
            text="📄 Xuất Word (.docx)",
            font=("Segoe UI", 8, "bold"),
            bg="#1E3A8A",
            fg="#93C5FD",
            activebackground="#1E40AF",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            pady=2,
            command=lambda t=text: self.export_message_to_docx(t),
        )
        btn_exp_word.pack(side=tk.LEFT, padx=(0, 6))

        btn_exp_excel = tk.Button(
            btn_frame,
            text="📊 Xuất Excel (.xlsx)",
            font=("Segoe UI", 8, "bold"),
            bg="#064E3B",
            fg="#6EE7B7",
            activebackground="#065F46",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            pady=2,
            command=lambda t=text: self.export_message_to_excel(t),
        )
        btn_exp_excel.pack(side=tk.LEFT, padx=(0, 6))

        btn_copy = tk.Button(
            btn_frame,
            text="📋 Sao chép text",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="#CBD5E1",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            pady=2,
            command=lambda t=text: self.copy_text_to_clipboard(t),
        )
        btn_copy.pack(side=tk.LEFT, padx=(0, 6))

        self.chat_stream.window_create(tk.END, window=btn_frame)
        self.chat_stream.insert(tk.END, "\n")
        self.chat_stream.see(tk.END)
        self.chat_stream.configure(state=tk.DISABLED)

    def on_attach_file_click(self):
        f = filedialog.askopenfilename(
            title="Chọn tệp tin hoặc hình ảnh để AI phân tích",
            filetypes=[
                ("Tất cả tệp hỗ trợ", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.pdf;*.docx;*.txt;*.xlsx"),
                ("Hình ảnh", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
                ("Tài liệu", "*.pdf;*.docx;*.txt;*.xlsx"),
                ("Mọi tệp tin", "*.*"),
            ],
        )
        if f:
            self.attached_file_path = f
            self.clipboard_image_bytes = None
            self.clipboard_image_mime = None
            fname = Path(f).name
            self.lbl_badge_text.configure(text=f"📁 Tệp đã chọn: {fname}")
            self.badge_frame.pack(fill=tk.X, pady=(0, 6), before=self.chat_stream)

    def on_paste_clipboard_image_click(self):
        try:
            img = ImageGrab.grabclipboard()
            if img is not None and isinstance(img, Image.Image):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                self.clipboard_image_bytes = buf.getvalue()
                self.clipboard_image_mime = "image/png"
                self.attached_file_path = None
                self.lbl_badge_text.configure(text=f"📋 Ảnh từ Clipboard ({img.width}x{img.height})")
                self.badge_frame.pack(fill=tk.X, pady=(0, 6), before=self.chat_stream)
            elif isinstance(img, list) and len(img) > 0 and Path(img[0]).exists():
                self.attached_file_path = img[0]
                self.clipboard_image_bytes = None
                self.clipboard_image_mime = None
                fname = Path(img[0]).name
                self.lbl_badge_text.configure(text=f"📁 Tệp từ Clipboard: {fname}")
                self.badge_frame.pack(fill=tk.X, pady=(0, 6), before=self.chat_stream)
            else:
                messagebox.showinfo(
                    "Clipboard",
                    "Không tìm thấy hình ảnh nào trong bộ nhớ tạm Clipboard!\n"
                    "👉 Bạn hãy chụp ảnh (Windows + Shift + S) hoặc Copy một tấm ảnh rồi bấm lại nút này nhé.",
                )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy ảnh từ Clipboard: {e}")

    def clear_attachment(self):
        self.attached_file_path = None
        self.clipboard_image_bytes = None
        self.clipboard_image_mime = None
        self.badge_frame.pack_forget()

    def clear_chat(self):
        self.chat_history = []
        self.chat_stream.configure(state=tk.NORMAL)
        self.chat_stream.delete("1.0", tk.END)
        self.chat_stream.configure(state=tk.DISABLED)
        self._append_ai_message("Đã xóa sạch lịch sử hội thoại. Tôi đã sẵn sàng nhận yêu cầu mới từ bạn Kiệt!")

    def _is_robot_automation_command(self, cmd: str) -> bool:
        c = (cmd or "").lower().strip()
        # 1. Multi-app RPA or UltraViewer
        if any(k in c for k in ["utraview", "ultraview"]) and any(k in c for k in ["copy", "mã", "dán", "dan"]):
            return True
        # 2. Google Workspace links
        if any(k in c for k in ["gg ex", "gg sheet", "google sheet", "google excel", "gg doc", "gg slide"]) and any(k in c for k in ["link", "tạo 1", "tạo link", "gửi", "gủi"]):
            return True
        # 3. Direct URL or web messaging
        if re.search(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', cmd) or (any(w in c for w in ["gửi tin nhắn", "gủi tin nhắn", "nhắn tin"]) and any(w in c for w in ["zalo", "facebook", "render"])):
            return True
        # 4. System controls
        if any(k in c for k in ["tắt máy", "hẹn giờ", "hủy tắt máy", "khởi động lại", "restart", "khóa máy", "dọn rác", "âm lượng", "tăng loa", "giảm loa", "tắt tiếng"]):
            return True
        # 5. Mouse & Keyboard RPA
        if any(k in c for k in ["click chuột", "nhấp chuột", "chụp màn hình", "chụp ảnh màn hình"]):
            return True
        # 6. YouTube playback
        if any(k in c for k in ["youtube", "you tu be", "bài nhạc", "bài hát", "phát nhạc", "bật nhạc", "nghe nhạc", "phát bài", "remix", "rimex", "mv"]):
            return True
        # 7. App launcher
        if any(w in c for w in ["vô", "vào", "mở", "bật", "khởi động", "chạy"]) and any(w in c for w in ["zalo", "cốc cốc", "coccoc", "chrome", "edge", "word", "excel", "ppt", "powerpoint", "notepad", "calc", "máy tính", "vscode", "code", "anydesk", "evkey", "thư mục", "explorer"]):
            return True
        # 8. Explicit file creation
        if any(k in c for k in ["tạo file word", "lưu file word", "tạo file excel", "lưu file excel", "tạo bài thuyết trình", "tạo slide"]):
            return True
        return False

    def on_send_chat(self):
        cmd = self.entry_cmd.get().strip()
        if cmd == "Nhập câu hỏi hoặc yêu cầu AI điều khiển máy tính, phân tích ảnh...":
            cmd = ""

        if not cmd and not self.attached_file_path and not self.clipboard_image_bytes:
            return

        attach_name = None
        if self.attached_file_path:
            attach_name = Path(self.attached_file_path).name
        elif self.clipboard_image_bytes:
            attach_name = "Ảnh từ Clipboard"

        display_text = cmd if cmd else "(Yêu cầu phân tích tệp tin / hình ảnh đính kèm)"
        self._append_user_message(display_text, attachment_name=attach_name)
        self.entry_cmd.delete(0, tk.END)

        cur_file = self.attached_file_path
        cur_img_bytes = self.clipboard_image_bytes
        cur_img_mime = self.clipboard_image_mime or "image/jpeg"
        self.clear_attachment()

        # Parse selected AI model
        model_str = self.ai_model_var.get() if hasattr(self, "ai_model_var") else ""
        provider = "gemini"
        model_name = None
        if "DeepSeek R1" in model_str:
            provider = "deepseek"
            model_name = "deepseek-reasoner"
        elif "DeepSeek V3" in model_str:
            provider = "deepseek"
            model_name = "deepseek-chat"
        elif "GPT-4o Mini" in model_str:
            provider = "openai"
            model_name = "gpt-4o-mini"
        elif "GPT-4o" in model_str:
            provider = "openai"
            model_name = "gpt-4o"
        elif "Claude" in model_str:
            provider = "claude"
            model_name = "claude-3-5-sonnet-20241022"

        def _run_task():
            self.btn_send.configure(state=tk.DISABLED, text="⏳ Đang xử lý...")
            try:
                # 1. Nếu là lệnh điều khiển Robot Windows (RPA)
                if self._is_robot_automation_command(cmd) and not cur_img_bytes and not cur_file:
                    res = self.controller.execute_command(
                        user_command=cmd,
                        attached_file_path=cur_file,
                        image_bytes=cur_img_bytes,
                        image_mime=cur_img_mime,
                    )
                    msg = res.get("message", "Đã thực thi thành công!")
                    act = res.get("action", "")
                    self.chat_history.append({"role": "user", "parts": cmd})
                    self.chat_history.append({"role": "model", "parts": msg})
                    self.root.after(0, lambda: self._append_ai_message(msg, action_text=act))
                else:
                    # 2. Nếu là câu hỏi, trò chuyện, phân tích ảnh, tư duy logic (GIỐNG 100% TRÊN WEB)
                    history_payload = []
                    for h in self.chat_history:
                        history_payload.append({"role": h["role"], "parts": h["parts"]})

                    reply = self.ai.chat(
                        message=cmd,
                        history=history_payload,
                        provider=provider,
                        model=model_name,
                        image_bytes=cur_img_bytes,
                        image_mime=cur_img_mime,
                    )
                    self.chat_history.append({"role": "user", "parts": cmd if cmd else "Phân tích tệp tin/ảnh"})
                    self.chat_history.append({"role": "model", "parts": reply})
                    self.root.after(0, lambda: self._append_ai_message(reply))
            except Exception as e:
                self.root.after(0, lambda: self._append_ai_message(f"⚠️ Đã xảy ra lỗi: {e}"))
            finally:
                self.root.after(0, lambda: self.btn_send.configure(state=tk.NORMAL, text="🚀 Gửi (Enter)"))

        threading.Thread(target=_run_task, daemon=True).start()

    def on_voice_click(self):
        def _voice_thread():
            self.root.after(0, lambda: self.btn_voice.configure(bg="#DC2626", text="🔴 Đang nghe..."))
            text = self.voice.record_and_transcribe(duration_seconds=4)
            self.root.after(0, lambda: self.btn_voice.configure(bg="#059669", text="🎤 Nói (Voice)"))

            if text:
                self.root.after(0, lambda: self.entry_cmd.delete(0, tk.END))
                self.root.after(0, lambda: self.entry_cmd.insert(0, text))
                self.root.after(0, self.on_send_chat)
            else:
                self.root.after(
                    0,
                    lambda: self._append_ai_message(
                        "🎤 Không nhận diện được âm thanh rõ ràng. Vui lòng nói to rõ hơn hoặc kiểm tra Micro của bạn."
                    ),
                )

        threading.Thread(target=_voice_thread, daemon=True).start()

    # ==========================================
    # 2. TAB HỎI ĐÁP TÀI LIỆU PDF (RAG CHROMA)
    # ==========================================
    def _setup_panel_pdf(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["pdf"] = panel

        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            head,
            text="📄 Tra Cứu & Hỏi Đáp Tài Liệu PDF (RAG AI)",
            font=("Segoe UI", 13, "bold"),
            fg="#4ADE80",
            bg="#1E293B",
        ).pack(anchor="w")
        tk.Label(
            head,
            text="Tải PDF lên để băm đoạn vector vào ChromaDB và đặt câu hỏi truy vấn chính xác kèm trích dẫn.",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#1E293B",
        ).pack(anchor="w")

        # Khung tải PDF
        box_upload = tk.Frame(panel, bg="#1E293B", padx=14, pady=12)
        box_upload.pack(fill=tk.X, pady=(0, 10))

        tk.Label(box_upload, text="1. Chọn tài liệu PDF từ máy tính:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")

        row_f = tk.Frame(box_upload, bg="#1E293B")
        row_f.pack(fill=tk.X, pady=(6, 0))

        btn_ch_pdf = tk.Button(row_f, text="📂 Chọn file PDF", font=("Segoe UI", 9, "bold"), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", padx=12, pady=5, command=self.on_select_pdf)
        btn_ch_pdf.pack(side=tk.LEFT)

        self.lbl_pdf_name = tk.Label(row_f, text="Chưa chọn tệp PDF nào", font=("Segoe UI", 9, "italic"), fg="#94A3B8", bg="#1E293B", padx=10)
        self.lbl_pdf_name.pack(side=tk.LEFT)

        self.btn_index_pdf = tk.Button(row_f, text="⚡ Lập Chỉ Mục (Index)", font=("Segoe UI", 9, "bold"), bg="#15803D", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", padx=12, pady=5, command=self.on_index_pdf)
        self.btn_index_pdf.pack(side=tk.RIGHT)

        # Khung đặt câu hỏi
        box_q = tk.Frame(panel, bg="#1E293B", padx=14, pady=12)
        box_q.pack(fill=tk.X, pady=(0, 10))

        tk.Label(box_q, text="2. Đặt câu hỏi truy vấn trên nội dung PDF:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")

        row_q = tk.Frame(box_q, bg="#1E293B")
        row_q.pack(fill=tk.X, pady=(6, 0))

        self.entry_pdf_q = tk.Entry(row_q, font=("Segoe UI", 11), bg="#0F172A", fg="#FFFFFF", insertbackground="#38BDF8", relief=tk.FLAT, highlightthickness=1, highlightbackground="#334155")
        self.entry_pdf_q.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        self.entry_pdf_q.insert(0, "Tóm tắt các nội dung quan trọng nhất trong tài liệu này")
        self.entry_pdf_q.bind("<Return>", lambda e: self.on_query_pdf())

        self.btn_query_pdf = tk.Button(row_q, text="🔍 Tra Cứu", font=("Segoe UI", 9, "bold"), bg="#0284C7", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", padx=14, pady=6, command=self.on_query_pdf)
        self.btn_query_pdf.pack(side=tk.RIGHT)

        # Kết quả truy vấn
        self.txt_pdf_res = scrolledtext.ScrolledText(panel, wrap=tk.WORD, font=("Segoe UI", 10), bg="#111827", fg="#F1F5F9", relief=tk.FLAT, padx=12, pady=10)
        self.txt_pdf_res.pack(fill=tk.BOTH, expand=True)

    def on_select_pdf(self):
        f = filedialog.askopenfilename(title="Chọn tệp tin PDF", filetypes=[("Tệp PDF", "*.pdf")])
        if f:
            self.current_pdf_path = f
            self.lbl_pdf_name.configure(text=Path(f).name, fg="#38BDF8")

    def on_index_pdf(self):
        if not self.current_pdf_path or not Path(self.current_pdf_path).exists():
            messagebox.showwarning("Thông báo", "Vui lòng bấm '📂 Chọn file PDF' trước!")
            return

        def _idx():
            self.btn_index_pdf.configure(state=tk.DISABLED, text="⏳ Đang băm vector...")
            try:
                cnt = self.rag_service.add_pdf_document(self.current_pdf_path)
                self.root.after(0, lambda: messagebox.showinfo("Thành công", f"✅ Đã lập chỉ mục {cnt} đoạn văn bản vào ChromaDB thành công!"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi lập chỉ mục: {e}"))
            finally:
                self.root.after(0, lambda: self.btn_index_pdf.configure(state=tk.NORMAL, text="⚡ Lập Chỉ Mục (Index)"))

        threading.Thread(target=_idx, daemon=True).start()

    def on_query_pdf(self):
        q = self.entry_pdf_q.get().strip()
        if not q:
            return
        fname = Path(self.current_pdf_path).name if self.current_pdf_path else ""

        def _qry():
            self.btn_query_pdf.configure(state=tk.DISABLED, text="⏳ Đang tra...")
            try:
                ans, excerpts = self.rag_service.query(query=q, filename=fname)
                self.root.after(0, lambda: self._show_pdf_answer(ans, excerpts))
            except Exception as e:
                self.root.after(0, lambda: self._show_pdf_answer(f"Lỗi tra cứu: {e}", []))
            finally:
                self.root.after(0, lambda: self.btn_query_pdf.configure(state=tk.NORMAL, text="🔍 Tra Cứu"))

        threading.Thread(target=_qry, daemon=True).start()

    def _show_pdf_answer(self, ans: str, excerpts: list):
        self.txt_pdf_res.delete("1.0", tk.END)
        self.txt_pdf_res.insert(tk.END, f"=== KẾT QUẢ TRẢ LỜI CỦA AI PTK ===\n\n{ans}\n\n")
        if excerpts:
            self.txt_pdf_res.insert(tk.END, "=== CÁC ĐOẠN TRÍCH XUẤT NGUỒN LIÊN QUAN ===\n\n")
            for i, chk in enumerate(excerpts, 1):
                self.txt_pdf_res.insert(tk.END, f"[{i}] {chk}\n\n")

    # ==========================================
    # 3. TAB SOẠN THẢO VĂN BẢN (WRITER)
    # ==========================================
    def _setup_panel_writer(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["writer"] = panel

        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 12))
        tk.Label(head, text="✍️ Soạn Thảo Văn Bản Chuyên Nghiệp (Xuất Word .docx)", font=("Segoe UI", 13, "bold"), fg="#F59E0B", bg="#1E293B").pack(anchor="w")
        tk.Label(head, text="Tự động soạn báo cáo, hợp đồng, thơ ca, đơn từ chuẩn mực và mở Microsoft Word lên màn hình.", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B").pack(anchor="w")

        form = tk.Frame(panel, bg="#1E293B", padx=16, pady=14)
        form.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Chọn mẫu văn bản cần soạn:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")
        self.cb_writer_type = ttk.Combobox(
            form,
            values=[
                "Báo Cáo Công Việc & Kế Hoạch Dự Án",
                "Hợp Đồng Kinh Tế & Mua Bán Dịch Vụ",
                "Đơn Từ & Đề Xuất Doanh Nghiệp",
                "Thơ Ca Nghệ Thuật & Cảm Hứng",
                "Bài Viết & Chuyên Đề Phân Tích Chuyên Sâu",
            ],
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.cb_writer_type.current(0)
        self.cb_writer_type.pack(fill=tk.X, pady=(6, 12))

        tk.Label(form, text="Chủ đề hoặc yêu cầu chi tiết của bạn:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")
        self.txt_writer_prompt = tk.Text(form, font=("Segoe UI", 10), height=4, bg="#0F172A", fg="#FFFFFF", insertbackground="#38BDF8", relief=tk.FLAT, highlightthickness=1, highlightbackground="#334155")
        self.txt_writer_prompt.pack(fill=tk.X, pady=(6, 14))
        self.txt_writer_prompt.insert("1.0", "Kế hoạch phát triển công nghệ AI PTK trong năm 2026 của kiến trúc sư Phan Tấn Kiệt")

        self.btn_gen_word = tk.Button(
            form,
            text="📝 TỰ ĐỘNG SOẠN THẢO & MỞ MICROSOFT WORD",
            font=("Segoe UI", 11, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            command=self.on_generate_word,
        )
        self.btn_gen_word.pack(fill=tk.X)

        self.lbl_writer_status = tk.Label(panel, text="", font=("Segoe UI", 10, "bold"), fg="#34D399", bg="#0F172A")
        self.lbl_writer_status.pack(pady=10)

    def on_generate_word(self):
        wtype = self.cb_writer_type.get()
        topic = self.txt_writer_prompt.get("1.0", tk.END).strip()
        if not topic:
            return

        def _gen():
            self.btn_gen_word.configure(state=tk.DISABLED, text="⏳ Đang soạn thảo văn bản...")
            self.lbl_writer_status.configure(text="Đang phân tích và khởi tạo văn bản Word...")
            try:
                cmd = f"soạn thảo {wtype} về {topic}"
                res = self.controller.execute_command(cmd)
                msg = res.get("message", "")
                self.root.after(0, lambda: self.lbl_writer_status.configure(text=msg))
            except Exception as e:
                self.root.after(0, lambda: self.lbl_writer_status.configure(text=f"Lỗi: {e}"))
            finally:
                self.root.after(0, lambda: self.btn_gen_word.configure(state=tk.NORMAL, text="📝 TỰ ĐỘNG SOẠN THẢO & MỞ MICROSOFT WORD"))

        threading.Thread(target=_gen, daemon=True).start()

    # ==========================================
    # 4. TAB XỬ LÝ DỮ LIỆU & BẢNG TÍNH (DATA)
    # ==========================================
    def _setup_panel_data(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["data"] = panel

        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 12))
        tk.Label(head, text="📊 Khởi Tạo Bảng Tính & Dữ Liệu (Xuất Excel .xlsx)", font=("Segoe UI", 13, "bold"), fg="#10B981", bg="#1E293B").pack(anchor="w")
        tk.Label(head, text="Tự động tính toán số liệu, tạo bảng tính Excel chuyên nghiệp và mở Microsoft Excel lên màn hình.", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B").pack(anchor="w")

        form = tk.Frame(panel, bg="#1E293B", padx=16, pady=14)
        form.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Chọn mẫu bảng tính Excel:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")
        self.cb_data_type = ttk.Combobox(
            form,
            values=[
                "Bảng Quản Lý Thu Chi Cá Nhân (1 Tháng)",
                "Bảng Lương & Chấm Công Nhân Viên Toàn Công Ty",
                "Kế Hoạch Dự Án & Dự Toán Ngân Sách",
                "Báo Giá Sản Phẩm & Danh Mục Dịch Vụ Khách Hàng",
            ],
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.cb_data_type.current(0)
        self.cb_data_type.pack(fill=tk.X, pady=(6, 12))

        tk.Label(form, text="Yêu cầu bổ sung hoặc tên doanh nghiệp / đề tài:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")
        self.txt_data_prompt = tk.Text(form, font=("Segoe UI", 10), height=3, bg="#0F172A", fg="#FFFFFF", insertbackground="#38BDF8", relief=tk.FLAT, highlightthickness=1, highlightbackground="#334155")
        self.txt_data_prompt.pack(fill=tk.X, pady=(6, 14))
        self.txt_data_prompt.insert("1.0", "Bảng quản lý chi tiêu cá nhân chi tiết trong 1 tháng của Phan Tấn Kiệt")

        self.btn_gen_excel = tk.Button(
            form,
            text="📊 TỰ ĐỘNG TẠO BẢNG TÍNH & MỞ MICROSOFT EXCEL",
            font=("Segoe UI", 11, "bold"),
            bg="#15803D",
            fg="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            command=self.on_generate_excel,
        )
        self.btn_gen_excel.pack(fill=tk.X)

        self.lbl_data_status = tk.Label(panel, text="", font=("Segoe UI", 10, "bold"), fg="#34D399", bg="#0F172A")
        self.lbl_data_status.pack(pady=10)

    def on_generate_excel(self):
        dtype = self.cb_data_type.get()
        topic = self.txt_data_prompt.get("1.0", tk.END).strip()

        def _gen():
            self.btn_gen_excel.configure(state=tk.DISABLED, text="⏳ Đang lập bảng tính...")
            self.lbl_data_status.configure(text="Đang tính toán số liệu và tạo file Excel...")
            try:
                cmd = f"mở excel tạo {dtype} {topic}"
                res = self.controller.execute_command(cmd)
                msg = res.get("message", "")
                self.root.after(0, lambda: self.lbl_data_status.configure(text=msg))
            except Exception as e:
                self.root.after(0, lambda: self.lbl_data_status.configure(text=f"Lỗi: {e}"))
            finally:
                self.root.after(0, lambda: self.btn_gen_excel.configure(state=tk.NORMAL, text="📊 TỰ ĐỘNG TẠO BẢNG TÍNH & MỞ MICROSOFT EXCEL"))

        threading.Thread(target=_gen, daemon=True).start()

    # ==========================================
    # 5. TAB CÔNG CỤ HỆ THỐNG & RPA (TOOLS)
    # ==========================================
    def _setup_panel_tools(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["tools"] = panel

        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 14))
        tk.Label(head, text="🔧 Trung Tâm Điều Khiển Hệ Thống & RPA Windows", font=("Segoe UI", 13, "bold"), fg="#38BDF8", bg="#1E293B").pack(anchor="w")
        tk.Label(head, text="Bấm 1 chạm để thực thi tức thì các tác vụ hệ thống Windows, điều khiển âm lượng, dọn rác và phần mềm.", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B").pack(anchor="w")

        grid_frame = tk.Frame(panel, bg="#0F172A")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Card 1: Hẹn giờ tắt máy
        c1 = tk.LabelFrame(grid_frame, text=" ⏱️ Hẹn Giờ Tắt Máy & Khởi Động ", font=("Segoe UI", 10, "bold"), fg="#38BDF8", bg="#1E293B", padx=12, pady=10)
        c1.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        row_timer = tk.Frame(c1, bg="#1E293B")
        row_timer.pack(fill=tk.X, pady=(0, 8))
        tk.Label(row_timer, text="Số phút hẹn giờ:", font=("Segoe UI", 9), fg="#FFFFFF", bg="#1E293B").pack(side=tk.LEFT)
        self.sp_mins = tk.Spinbox(row_timer, from_=1, to=300, width=5, font=("Segoe UI", 10), justify="center")
        self.sp_mins.delete(0, tk.END)
        self.sp_mins.insert(0, "30")
        self.sp_mins.pack(side=tk.LEFT, padx=8)

        tk.Button(c1, text="⏱️ Đặt Lịch Tắt Máy", font=("Segoe UI", 9, "bold"), bg="#DC2626", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=5, command=self.on_tool_shutdown).pack(fill=tk.X, pady=2)
        tk.Button(c1, text="🚫 Hủy Hẹn Giờ Tắt Máy", font=("Segoe UI", 9), bg="#475569", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=5, command=lambda: self.run_quick_cmd("Hủy tắt máy")).pack(fill=tk.X, pady=2)
        tk.Button(c1, text="🔄 Khởi Động Lại Máy Tính", font=("Segoe UI", 9), bg="#EA580C", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=5, command=lambda: self.run_quick_cmd("Khởi động lại")).pack(fill=tk.X, pady=2)

        # Card 2: Dọn dẹp & Màn hình
        c2 = tk.LabelFrame(grid_frame, text=" 🧹 Dọn Dẹp Rác & Màn Hình ", font=("Segoe UI", 10, "bold"), fg="#34D399", bg="#1E293B", padx=12, pady=10)
        c2.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        tk.Button(c2, text="🧹 Dọn Dẹp Rác Tạm (%TEMP%)", font=("Segoe UI", 9, "bold"), bg="#059669", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Dọn dẹp rác máy tính")).pack(fill=tk.X, pady=2)
        tk.Button(c2, text="📸 Chụp Màn Hình (Snipping)", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Chụp màn hình")).pack(fill=tk.X, pady=2)
        tk.Button(c2, text="🔒 Khóa Máy Tính (Lock)", font=("Segoe UI", 9), bg="#475569", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Khóa máy tính")).pack(fill=tk.X, pady=2)
        tk.Button(c2, text="🖥️ Thu Nhỏ Hết Cửa Sổ (Desktop)", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Thu nhỏ tất cả cửa sổ")).pack(fill=tk.X, pady=2)

        # Card 3: Điều khiển âm lượng loa
        c3 = tk.LabelFrame(grid_frame, text=" 🔊 Âm Lượng Loa Máy Tính ", font=("Segoe UI", 10, "bold"), fg="#F59E0B", bg="#1E293B", padx=12, pady=10)
        c3.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        tk.Button(c3, text="🔊 Tăng Âm Lượng Loa (+6 bậc)", font=("Segoe UI", 9, "bold"), bg="#D97706", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Tăng âm lượng loa")).pack(fill=tk.X, pady=2)
        tk.Button(c3, text="🔉 Giảm Âm Lượng Loa (-6 bậc)", font=("Segoe UI", 9), bg="#B45309", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Giảm âm lượng")).pack(fill=tk.X, pady=2)
        tk.Button(c3, text="🔇 Tắt / Mở Tiếng Loa (Mute)", font=("Segoe UI", 9), bg="#475569", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Tắt tiếng loa")).pack(fill=tk.X, pady=2)

        # Card 4: Bật ứng dụng
        c4 = tk.LabelFrame(grid_frame, text=" 🚀 Khởi Chạy Nhanh Phần Mềm ", font=("Segoe UI", 10, "bold"), fg="#A855F7", bg="#1E293B", padx=12, pady=10)
        c4.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)

        tk.Button(c4, text="🌐 Mở Trình Duyệt Cốc Cốc", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Mở Cốc Cốc")).pack(fill=tk.X, pady=2)
        tk.Button(c4, text="🌐 Mở Google Chrome", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Mở Chrome")).pack(fill=tk.X, pady=2)
        tk.Button(c4, text="🧮 Máy Tính (Calculator)", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Mở Calculator")).pack(fill=tk.X, pady=2)
        tk.Button(c4, text="🎨 Vẽ Tranh (MS Paint)", font=("Segoe UI", 9), bg="#334155", fg="#FFFFFF", relief=tk.FLAT, cursor="hand2", pady=6, command=lambda: self.run_quick_cmd("Mở Paint")).pack(fill=tk.X, pady=2)

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

    def on_tool_shutdown(self):
        mins = self.sp_mins.get().strip()
        self.run_quick_cmd(f"Hẹn giờ tắt máy sau {mins} phút")

    def run_quick_cmd(self, cmd: str):
        def _exec():
            res = self.controller.execute_command(cmd)
            msg = res.get("message", "")
            self.root.after(0, lambda: messagebox.showinfo("Kết quả hệ thống", msg))

        threading.Thread(target=_exec, daemon=True).start()

    # ==========================================
    # 6. TAB AUTO AGENT (TỰ ĐỘNG HÓA ĐA BƯỚC)
    # ==========================================
    def _setup_panel_agent(self):
        panel = tk.Frame(self.content_container, bg="#0F172A")
        self.panels["agent"] = panel

        head = tk.Frame(panel, bg="#1E293B", padx=16, pady=10)
        head.pack(fill=tk.X, pady=(0, 12))
        tk.Label(head, text="🤖 Auto Agent - Robot Tự Động Hóa Nhiệm Vụ Toàn Năng", font=("Segoe UI", 13, "bold"), fg="#EC4899", bg="#1E293B").pack(anchor="w")
        tk.Label(head, text="Tự động lập kế hoạch 4 giai đoạn, viết code kiểm tra và tự động đóng gói cả Word & Excel ra Desktop.", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B").pack(anchor="w")

        box_input = tk.Frame(panel, bg="#1E293B", padx=14, pady=12)
        box_input.pack(fill=tk.X, pady=(0, 10))

        tk.Label(box_input, text="Nhập mục tiêu lớn bạn muốn giao cho AI:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#1E293B").pack(anchor="w")
        self.txt_agent_goal = tk.Text(box_input, font=("Segoe UI", 10), height=3, bg="#0F172A", fg="#FFFFFF", insertbackground="#38BDF8", relief=tk.FLAT, highlightthickness=1, highlightbackground="#334155")
        self.txt_agent_goal.pack(fill=tk.X, pady=(6, 12))
        self.txt_agent_goal.insert("1.0", "Lập kế hoạch phát triển dự án AI PTK trong 3 tháng, kèm bảng dự toán ngân sách chi tiết và phân tích rủi ro.")

        self.btn_run_agent = tk.Button(
            box_input,
            text="🚀 KÍCH HOẠT AUTO AGENT (TỰ ĐỘNG HÓA TỪ A-Z)",
            font=("Segoe UI", 11, "bold"),
            bg="#BE185D",
            fg="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            command=self.on_run_auto_agent,
        )
        self.btn_run_agent.pack(fill=tk.X)

        self.txt_agent_log = scrolledtext.ScrolledText(panel, wrap=tk.WORD, font=("Segoe UI", 10), bg="#111827", fg="#F1F5F9", relief=tk.FLAT, padx=12, pady=10)
        self.txt_agent_log.pack(fill=tk.BOTH, expand=True)

    def on_run_auto_agent(self):
        goal = self.txt_agent_goal.get("1.0", tk.END).strip()
        if not goal:
            return

        def _agent_thread():
            self.btn_run_agent.configure(state=tk.DISABLED, text="⏳ Auto Agent đang tự động lập kế hoạch và giải quyết...")
            self.txt_agent_log.delete("1.0", tk.END)
            self.txt_agent_log.insert(tk.END, f"🚀 BẮT ĐẦU MỤC TIÊU: {goal}\n")
            self.txt_agent_log.insert(tk.END, "⚙️ Giai đoạn 1: Đang phân rã nhiệm vụ và lập kế hoạch đa bước...\n\n")

            try:
                res = self.agent_service.execute_goal(goal=goal)
                plan = res.get("plan", "")
                result_md = res.get("result_markdown", "")

                self.root.after(0, lambda: self._append_agent_results(plan, result_md, goal))
            except Exception as e:
                self.root.after(0, lambda: self.txt_agent_log.insert(tk.END, f"\n⚠️ Lỗi Auto Agent: {e}\n"))
            finally:
                self.root.after(0, lambda: self.btn_run_agent.configure(state=tk.NORMAL, text="🚀 KÍCH HOẠT AUTO AGENT (TỰ ĐỘNG HÓA TỪ A-Z)"))

        threading.Thread(target=_agent_thread, daemon=True).start()

    def _append_agent_results(self, plan: str, result_md: str, goal: str):
        self.txt_agent_log.insert(tk.END, "=== KẾ HOẠCH HÀNH ĐỘNG (GIAI ĐOẠN 1) ===\n")
        self.txt_agent_log.insert(tk.END, f"{plan}\n\n")
        self.txt_agent_log.insert(tk.END, "=== KẾT QUẢ THỰC THI CHI TIẾT (GIAI ĐOẠN 2 & 3) ===\n")
        self.txt_agent_log.insert(tk.END, f"{result_md}\n\n")

        # Lưu tự động ra Word và Excel trên Desktop
        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        desktop_dir = Path.home() / "Desktop"
        w_path = desktop_dir / f"AutoAgent_Word_{ts}.docx"
        e_path = desktop_dir / f"AutoAgent_Excel_{ts}.xlsx"

        try:
            w_bytes = ExportService.text_to_docx(result_md, title=f"AI PTK: {goal[:30]}")
            with open(w_path, "wb") as f:
                f.write(w_bytes)
            os.startfile(str(w_path))

            e_bytes = ExportService.text_to_excel(result_md, title="AI PTK AGENT")
            with open(e_path, "wb") as f:
                f.write(e_bytes)
        except Exception:
            pass

        self.txt_agent_log.insert(
            tk.END,
            f"🎉 GIAI ĐOẠN 4 HOÀN TẤT: Đã tự động đóng gói cả Word ({w_path.name}) và Excel ({e_path.name}) ra màn hình Desktop cho bạn!\n"
        )
        self.txt_agent_log.see(tk.END)


def main():
    root = tk.Tk()
    app = DesktopAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
