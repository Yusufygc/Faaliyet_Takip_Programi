# add_page.py
import customtkinter as ctk
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class AddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Yeni Faaliyet Ekle", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

        # Tür
        ctk.CTkLabel(self, text="Tür:").pack()
        self.type_var = ctk.StringVar(value=FAALIYET_TURLERI[0])  # Varsayılan: "dizi"
        self.type_menu = ctk.CTkOptionMenu(self, variable=self.type_var, values=FAALIYET_TURLERI)
        self.type_menu.pack(pady=5)

        # Ad
        ctk.CTkLabel(self, text="Ad:").pack()
        self.name_entry = ctk.CTkEntry(self, width=400)
        self.name_entry.pack(pady=5)

        # Tarih (Yıl-Ay)
        ctk.CTkLabel(self, text="Tarih (Yıl-Ay):").pack()
        self.date_picker = build_month_year_picker(self)
        self.date_picker.pack(pady=5)

        # Yorum
        ctk.CTkLabel(self, text="Yorum:").pack()
        self.comment_text = ctk.CTkTextbox(self, width=400, height=80)
        self.comment_text.pack(pady=5)

        # Puan (1-10)
        ctk.CTkLabel(self, text="Puan:").pack()
        self.rating_var = ctk.StringVar(value="")
        self.rating_menu = ctk.CTkOptionMenu(self, variable=self.rating_var, values=[str(i) for i in range(1, 11)])
        self.rating_menu.pack(pady=5)

        # Eklendi yazısı için alan
        self.success_label = ctk.CTkLabel(self, text="", text_color="green")
        self.success_label.pack()

        # Ekle Butonu
        ctk.CTkButton(self, text="Ekle", command=self.add_activity).pack(pady=10)

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
            self.success_label.configure(text="✅ Eklendi!")

            # 3 saniye sonra mesajı temizle
            self.after(3000, lambda: self.success_label.configure(text=""))
        except Exception as e:
            self.success_label.configure(text=f"Hata: {e}", text_color="red")
        finally:
            conn.close()