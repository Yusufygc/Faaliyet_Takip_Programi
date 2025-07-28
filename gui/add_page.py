# add_page.py
import customtkinter as ctk
from datetime import datetime
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class AddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # İçerik kapsayıcı çerçeve
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="n", pady=40)
        content_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(content_frame, text="Yeni Faaliyet Ekle", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ctk.CTkLabel(content_frame, text="Tür:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.type_var = ctk.StringVar(value=FAALIYET_TURLERI[0])
        self.type_menu = ctk.CTkOptionMenu(content_frame, variable=self.type_var, values=FAALIYET_TURLERI)
        self.type_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(content_frame, text="Ad:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(content_frame, width=300)
        self.name_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(content_frame, text="Tarih (Yıl-Ay):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.date_picker = build_month_year_picker(content_frame)
        self.date_picker.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(content_frame, text="Yorum:").grid(row=4, column=0, sticky="ne", padx=10, pady=5)
        self.comment_text = ctk.CTkTextbox(content_frame, width=300, height=80)
        self.comment_text.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(content_frame, text="Puan:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.rating_var = ctk.StringVar(value="")
        self.rating_menu = ctk.CTkOptionMenu(content_frame, variable=self.rating_var, values=[str(i) for i in range(1, 11)])
        self.rating_menu.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        self.message_label = ctk.CTkLabel(content_frame, text="")
        self.message_label.grid(row=6, column=0, columnspan=2, pady=5)

        ctk.CTkButton(content_frame, text="Ekle", command=self.add_activity).grid(row=7, column=0, columnspan=2, pady=15)

        controller.wm_minsize(1000, 600)


    def add_activity(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            date_value = get_formatted_date_from_picker(self.date_picker)
            cursor.execute('''
                INSERT INTO activities (type, name, date, comment, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.type_var.get(),
                self.name_entry.get(),
                date_value,
                self.comment_text.get("1.0", "end").strip(),
                int(self.rating_var.get()) if self.rating_var.get() else 0
            ))
            conn.commit()
            self.message_label.configure(text="✅ Eklendi!", text_color="green")
            self.after(3000, lambda: self.message_label.configure(text=""))
        except Exception as e:
            self.message_label.configure(text=f"Hata: {e}", text_color="red")
        finally:
            conn.close()
