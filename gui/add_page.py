# add_page.py
import customtkinter as ctk
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from tkinter import messagebox
from utils import is_valid_yyyymm
from datetime import datetime

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
        self.rating_var = ctk.StringVar(value="Seçiniz")
        self.rating_menu = ctk.CTkOptionMenu(content_frame, variable=self.rating_var, values=["Seçiniz"] + [str(i) for i in range(1, 11)])
        self.rating_menu.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        self.message_label = ctk.CTkLabel(content_frame, text="")
        self.message_label.grid(row=6, column=0, columnspan=2, pady=5)

        ctk.CTkButton(content_frame, text="Ekle", command=self.add_activity).grid(row=7, column=0, columnspan=2, pady=15)


    def add_activity(self):
        activity_name = self.name_entry.get().strip()
        date_value = get_formatted_date_from_picker(self.date_picker)
        activity_type = self.type_var.get()
        comment = self.comment_text.get("1.0", "end").strip()
        rating_str = self.rating_var.get()

        # Hata ayıklama çıktıları
        #print(f"DEBUG: Faaliyet Adı: '{activity_name}'")
        #print(f"DEBUG: Tarih Değeri: '{date_value}'")
        #print(f"DEBUG: Puan String: '{rating_str}'")


        # Giriş Doğrulamaları
        if not activity_name:
            self.show_message("Faaliyet adı boş bırakılamaz.", "red")
            return

        if not date_value:
            self.show_message("Tarih seçimi zorunludur.", "red")
            return
        
        if not is_valid_yyyymm(date_value):
            self.show_message("Geçersiz tarih formatı. Lütfen YYYY-MM formatında seçiniz.", "red")
            return

        # Gelecek tarih kontrolü
        try:
            selected_year, selected_month = map(int, date_value.split('-'))
            current_date = datetime.now()
            # Ayın ilk günü olarak kabul et (gün ve saat bilgisi olmadan karşılaştırma için)
            selected_date = datetime(selected_year, selected_month, 1) 

            # Seçilen tarih, mevcut ayın ilk gününden daha ileride mi kontrol et
            if selected_date > current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0):
                self.show_message("Gelecekteki bir tarihi seçemezsiniz.", "red")
                return
        except ValueError:
            # is_valid_yyyymm bu hatayı yakalamalı, ancak bir güvenlik önlemi olarak tutuldu.
            self.show_message("Tarih formatı hatası. Lütfen YYYY-MM formatında seçiniz.", "red")
            return


        if rating_str == "Seçiniz" or not rating_str:
            rating = 0
            # show_message yerine messagebox.showinfo kullanıldı
            messagebox.showinfo("Bilgi", "Puan seçilmedi, 0 olarak kaydedildi.")
        else:
            try:
                rating = int(rating_str)
            except ValueError:
                self.show_message("Geçersiz puan değeri.", "red")
                return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO activities (type, name, date, comment, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                activity_type,
                activity_name,
                date_value,
                comment,
                rating
            ))
            conn.commit()
            self.show_message("✅ Faaliyet başarıyla eklendi!", "green")
            self.clear_inputs()
            # Faaliyet eklendikten sonra list_page'i yenile
            self.controller.refresh_list_page() 
        except Exception as e:
            self.show_message(f"Hata oluştu: {e}", "red")
        finally:
            conn.close()

    def show_message(self, message, color):
        """Kullanıcıya mesaj gösterir ve belirli bir süre sonra temizler."""
        self.message_label.configure(text=message, text_color=color)
        self.after(3000, lambda: self.message_label.configure(text=""))

    def clear_inputs(self):
        """Giriş alanlarını temizler ve varsayılan değerlere döndürür."""
        self.name_entry.delete(0, ctk.END)
        self.comment_text.delete("1.0", ctk.END)
        self.type_var.set(FAALIYET_TURLERI[0])
        self.rating_var.set("Seçiniz")
        self.date_picker.year_var.set("")
        self.date_picker.month_var.set("")
        self.name_entry.focus_set()
