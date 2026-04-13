import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import winsound
from database_manager import DatabaseManager
from audio_engine import AudioEngine

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Hệ Thống Cơ Sở Dữ Liệu Âm Thanh - Bài 8")
        self.geometry("1100x700")
        
        self.db = DatabaseManager()
        self.engine = AudioEngine()
        
        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar for filters
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BỘ LỌC TÌM KIẾM", font=ctk.CTkFont(size=22, weight="bold", family="Inter"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        # Filters (Loudness, Pitch, Brightness, Bandwidth)
        self.create_filter_slider("Độ lớn (Loudness)", 0, 1, 1)
        self.create_filter_slider("Cao độ (Pitch)", 0, 2000, 2)
        self.create_filter_slider("Độ sáng (Brightness)", 0, 8000, 3)
        self.create_filter_slider("Băng thông (Bandwidth)", 0, 5000, 4)
        
        self.search_button = ctk.CTkButton(self.sidebar_frame, text="Tìm kiếm", font=ctk.CTkFont(weight="bold"), 
                                          height=40, command=self.perform_search)
        self.search_button.grid(row=9, column=0, padx=20, pady=10)
        
        self.reset_button = ctk.CTkButton(self.sidebar_frame, text="Làm mới Danh sách", fg_color="transparent", 
                                         border_width=2, height=35, command=self.load_data)
        self.reset_button.grid(row=10, column=0, padx=20, pady=10, sticky="n")
        
        self.regen_button = ctk.CTkButton(self.sidebar_frame, text="Tạo lại 5 Âm thanh", fg_color="#E74C3C", 
                                         hover_color="#C0392B", command=self.auto_index)
        self.regen_button.grid(row=11, column=0, padx=20, pady=20)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self.main_title = ctk.CTkLabel(self.main_frame, text="CƠ SỞ DỮ LIỆU ÂM THANH", 
                                      font=ctk.CTkFont(size=28, weight="bold", family="Inter"))
        self.main_title.grid(row=0, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Table Frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Danh sách Âm thanh Đã Index", 
                                                       label_font=ctk.CTkFont(weight="bold"))
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        # Auto-index and load data at the VERY END
        if not self.db.get_all():
            self.auto_index()
        else:
            self.load_data()

    def auto_index(self):
        """Reset and index sounds."""
        self.engine.generate_sample_sounds()
        files = [f for f in os.listdir("sounds") if f.endswith(".wav")]
        for f in files:
            path = os.path.join("sounds", f)
            features = self.engine.extract_features(path)
            self.db.add_audio(f, features)
        self.load_data()

    def create_filter_slider(self, label_text, min_v, max_v, row_idx):
        frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        frame.grid(row=row_idx, column=0, padx=20, pady=5, sticky="ew")
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        lbl = ctk.CTkLabel(header_frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"))
        lbl.pack(side="left")
        
        val_lbl = ctk.CTkLabel(header_frame, text=str(max_v), font=ctk.CTkFont(size=12))
        val_lbl.pack(side="right")
        
        slider = ctk.CTkSlider(frame, from_=min_v, to=max_v, number_of_steps=100,
                               command=lambda v, l=val_lbl: l.configure(text=f"{v:.2f}"))
        slider.pack(fill="x", pady=(2, 10))
        slider.set(max_v) 
        
        if "độ lớn" in label_text.lower(): self.s_loud = slider
        elif "cao độ" in label_text.lower(): self.s_pitch = slider
        elif "độ sáng" in label_text.lower(): self.s_bright = slider
        elif "băng thông" in label_text.lower(): self.s_band = slider

    def load_data(self, data=None):
        if data is None:
            data = self.db.get_all()
            
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        
        # Headers
        headers = ["Tên file", "Độ lớn", "Cao độ", "Độ sáng", "Băng thông", "Tính nhạc", "Hành động"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.scrollable_frame, text=h, font=ctk.CTkFont(weight="bold", size=14))
            lbl.grid(row=0, column=i, padx=5, pady=10)
            
        # Rows
        for idx, row in enumerate(data):
            # Tên file
            ctk.CTkLabel(self.scrollable_frame, text=row[1], font=ctk.CTkFont(weight="bold"), text_color="#3498DB").grid(row=idx + 1, column=0, padx=5, pady=5)
            # Other features
            for i, val in enumerate(row[2:]): # skip id and filename
                ctk.CTkLabel(self.scrollable_frame, text=str(val)).grid(row=idx + 1, column=i+1, padx=5, pady=5)
            
            # Action button
            file_name = row[1]
            btn = ctk.CTkButton(self.scrollable_frame, text="▶ Phát Âm", width=90, height=30,
                               fg_color="#2ECC71", hover_color="#27AE60", font=ctk.CTkFont(weight="bold"),
                               command=lambda f=file_name: self.play_sound(f))
            btn.grid(row=idx + 1, column=6, padx=5, pady=5)

    def play_sound(self, filename):
        path = os.path.join("sounds", filename)
        if os.path.exists(path):
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể phát âm thanh: {e}")
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy file {filename}")

    def perform_search(self):
        all_data = self.db.get_all()
        filtered = []
        
        # We find sounds within a +/- 20% range of the slider value for a better experience
        # or just stick to the filter logic. Let's make it a "Tối đa" filter but more clear.
        max_loud = self.s_loud.get()
        max_pitch = self.s_pitch.get()
        max_bright = self.s_bright.get()
        max_band = self.s_band.get()
        
        for row in all_data:
            _, fname, loud, pitch, bright, band, harm = row
            # Filter condition: all properties must be BELOW or EQUAL to the slider value
            if loud <= max_loud and pitch <= max_pitch and bright <= max_bright and band <= max_band:
                filtered.append(row)
        
        self.load_data(filtered)
        if not filtered:
            messagebox.showwarning("Thông báo", "Không tìm thấy âm thanh nào thỏa mãn TẤT CẢ các giới hạn tối đa này!")

if __name__ == "__main__":
    app = AudioApp()
    app.mainloop()
