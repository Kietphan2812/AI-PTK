"""
AI PTK - Trợ Lý Robot Điều Khiển Máy Tính Cá Nhân (Desktop Controller)
Phần mềm Windows độc lập 1-Click: Tự động mở Word, gõ chữ, lưu file, mở Excel, PowerPoint, Cốc Cốc, Chrome,
Điều khiển chuột & bàn phím cấp sâu (RPA), Hẹn giờ tắt máy, Tăng giảm âm lượng, Dọn rác hệ thống,
và Ra lệnh bằng Giọng nói tiếng Việt (Voice Control).
Sáng lập và phát triển bởi Phan Tấn Kiệt.
"""

import os
import sys
import time
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
from tkinter import ttk, messagebox, scrolledtext
from services.desktop_controller import DesktopController
from services.voice_service import VoiceService


class DesktopAgentGUI:
    """Giao diện đồ họa hiện đại của trợ lý điều khiển máy tính AI PTK."""

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 AI PTK - Trợ Lý Điều Khiển Máy Tính Toàn Năng (Phan Tấn Kiệt)")
        self.root.geometry("820x700")
        self.root.minsize(750, 600)
        self.root.configure(bg="#0F172A")  # Giao diện Dark Mode sang trọng

        self.controller = DesktopController()

        self._setup_ui()

    def _setup_ui(self):
        # 1. HEADER BANNER
        header_frame = tk.Frame(self.root, bg="#1E293B", padx=20, pady=14)
        header_frame.pack(fill=tk.X, padx=16, pady=(14, 8))

        title_lbl = tk.Label(
            header_frame,
            text="🤖 AI PTK DESKTOP CONTROLLER (ROBOT WINDOWS)",
            font=("Segoe UI", 16, "bold"),
            fg="#38BDF8",
            bg="#1E293B",
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header_frame,
            text="Hệ thống điều khiển máy tính tự động bằng tiếng Việt & Giọng nói: Word, Excel, PowerPoint, Chuột, Bàn phím, Tắt máy, Dọn rác...",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#1E293B",
        )
        sub_lbl.pack(anchor="w", pady=(3, 0))

        # 2. KHU VỰC NHẬP LỆNH
        input_frame = tk.Frame(self.root, bg="#0F172A", padx=16)
        input_frame.pack(fill=tk.X, pady=6)

        lbl_prompt = tk.Label(
            input_frame,
            text="👉 Nhập mệnh lệnh hoặc bấm Micro để nói:",
            font=("Segoe UI", 11, "bold"),
            fg="#F8FAFC",
            bg="#0F172A",
        )
        lbl_prompt.pack(anchor="w", pady=(0, 6))

        self.entry_cmd = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg="#1E293B",
            fg="#FFFFFF",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground="#334155",
            highlightcolor="#38BDF8",
        )
        self.entry_cmd.pack(fill=tk.X, ipady=8)
        self.entry_cmd.insert(0, "Mở Word ghi Chào Kiệt nhé rồi lưu lại")
        self.entry_cmd.bind("<Return>", lambda e: self.on_execute_click())

        # KHUNG 2 NÚT THỰC THI CHÍNH: NÚT RA LỆNH VÀ NÚT MICRO GIỌNG NÓI
        btn_frame = tk.Frame(input_frame, bg="#0F172A")
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_run = tk.Button(
            btn_frame,
            text="🚀 RA LỆNH NGAY (ENTER)",
            font=("Segoe UI", 11, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            command=self.on_execute_click,
        )
        self.btn_run.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.btn_voice = tk.Button(
            btn_frame,
            text="🎤 NÓI VÀO MICRO (VOICE CONTROL)",
            font=("Segoe UI", 11, "bold"),
            bg="#059669",
            fg="#FFFFFF",
            activebackground="#047857",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            command=self.on_voice_click,
        )
        self.btn_voice.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

        # 3. CÁC NÚT TÁC VỤ 1-CLICK MẪU
        preset_frame = tk.LabelFrame(
            self.root,
            text=" ⚡ Tác vụ Mẫu 1-Click (Văn Phòng & Hệ Thống) ",
            font=("Segoe UI", 10, "bold"),
            fg="#38BDF8",
            bg="#0F172A",
            padx=12,
            pady=8,
        )
        preset_frame.pack(fill=tk.X, padx=16, pady=8)

        grid_presets = [
            ("🎵 Mở YouTube PHÁT NHẠC REMIX", "Mở YouTube tìm bài nhạc remix bấm phát luôn"),
            ("📊 Mở PPT tạo 20 Slide Đỏ Size 30pt", "vô ppt tao 20 slie thuyết trình về công nghệ ai ptk đi màu đỏ , tất cả chữ sie 30pt"),
            ("📝 Mở Word ghi tên Kiệt 100 lần", "vô word rồi ghi tên Kiệt 100 lần trong word đi"),
            ("💰 Mở Excel tạo Bảng Thu Chi", "Mở Excel tạo bảng quản lý thu chi cá nhân 1 tháng"),
            ("⏱️ Hẹn Giờ Tắt Máy (30 phút)", "Hẹn giờ tắt máy sau 30 phút"),
            ("🚫 Hủy Hẹn Giờ Tắt Máy", "Hủy tắt máy"),
            ("🧹 Dọn Dẹp Rác Máy Tính (%TEMP%)", "Dọn dẹp rác máy tính"),
            ("🔊 Tăng Âm Lượng Loa (+6 bậc)", "Tăng âm lượng loa"),
            ("📸 Chụp Ảnh Màn Hình (Snipping)", "Chụp ảnh màn hình"),
            ("🌐 Mở Cốc Cốc Lướt Web", "Mở trình duyệt Cốc Cốc tìm kiếm tin tức công nghệ"),
        ]

        for idx, (label, cmd_text) in enumerate(grid_presets):
            r = idx // 2
            c = idx % 2
            btn = tk.Button(
                preset_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#1E293B",
                fg="#E2E8F0",
                activebackground="#334155",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                padx=10,
                pady=5,
                command=lambda t=cmd_text: self.set_and_run(t),
            )
            btn.grid(row=r, column=c, sticky="ew", padx=5, pady=3)
            preset_frame.columnconfigure(c, weight=1)

        # 4. NHẬT KÝ HOẠT ĐỘNG (ACTION LOG)
        log_frame = tk.Frame(self.root, bg="#0F172A", padx=16)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

        lbl_log = tk.Label(
            log_frame,
            text="📋 Nhật ký hành động của AI trên máy tính:",
            font=("Segoe UI", 10, "bold"),
            fg="#94A3B8",
            bg="#0F172A",
        )
        lbl_log.pack(anchor="w", pady=(0, 4))

        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            bg="#030712",
            fg="#34D399",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            height=8,
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)
        self.log("Sẵn sàng! Nhập lệnh, bấm nút Micro để nói, hoặc click các nút mẫu để điều khiển máy tính.")

    def log(self, text: str):
        """Ghi nhật ký lên màn hình."""
        self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.log_box.see(tk.END)

    def set_and_run(self, cmd_text: str):
        self.entry_cmd.delete(0, tk.END)
        self.entry_cmd.insert(0, cmd_text)
        self.on_execute_click()

    def on_voice_click(self):
        """Kích hoạt thu âm và nhận diện giọng nói tiếng Việt."""
        self.btn_voice.config(state=tk.DISABLED, text="🔴 ĐANG LẮNG NGHE (NÓI TRONG 4 GIÂY)...", bg="#DC2626")
        self.log("🎤 Đang mở Micro... Hãy nói câu lệnh của bạn (ví dụ: 'Mở YouTube phát nhạc remix', 'Hẹn giờ tắt máy 30 phút')...")

        def voice_worker():
            try:
                res = VoiceService.record_and_recognize(duration_seconds=4, language="vi-VN")
                if res.get("success") and res.get("text"):
                    speech_text = res.get("text").strip()
                    self.log(f"🎤 Đã nghe thấy bạn nói: \"{speech_text}\"")
                    # Tự động điền vào ô lệnh và thực thi
                    self.root.after(0, lambda: self.set_and_run(speech_text))
                else:
                    err = res.get("error", "Không nhận diện được giọng nói.")
                    self.log(f"⚠️ {err}")
            except Exception as e:
                self.log(f"⚠️ Lỗi giọng nói: {str(e)}")
            finally:
                self.root.after(0, lambda: self.btn_voice.config(
                    state=tk.NORMAL, text="🎤 NÓI VÀO MICRO (VOICE CONTROL)", bg="#059669"
                ))

        threading.Thread(target=voice_worker, daemon=True).start()

    def on_execute_click(self):
        cmd = self.entry_cmd.get().strip()
        if not cmd:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập câu lệnh để AI thực hiện!")
            return

        self.btn_run.config(state=tk.DISABLED, text="⏳ AI ĐANG ĐIỀU KHIỂN...")
        self.log(f"Đang nhận lệnh: '{cmd}'...")

        def worker():
            try:
                res = self.controller.execute_command(cmd)
                msg = res.get("message", "Đã thực hiện xong lệnh.")
                self.log(f"Thành công: {msg}")
                if res.get("file_path"):
                    self.log(f"📁 Vị trí tệp tin: {res.get('file_path')}")
            except Exception as e:
                self.log(f"⚠️ Lỗi: {str(e)}")
            finally:
                self.root.after(0, lambda: self.btn_run.config(
                    state=tk.NORMAL, text="🚀 RA LỆNH NGAY (ENTER)"
                ))

        threading.Thread(target=worker, daemon=True).start()


def main():
    root = tk.Tk()
    app = DesktopAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
