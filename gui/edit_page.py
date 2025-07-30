# edit_page.py
import customtkinter as ctk
from tkinter import messagebox
from models import Activity
from database import get_connection
from utils import extract_year_month, is_valid_yyyymm
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from datetime import datetime

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class EditPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_activity = None
        self.original_activity_data = {}

        self.grid_rowconfigure(0, weight=1) # content_frame'in dikeyde ortalanması için
        self.grid_columnconfigure(0, weight=1) # content_frame'in yatayda ortalanması için

        # İçerik kapsayıcı çerçeve (add_page.py'deki gibi)
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="n", pady=40)
        content_frame.grid_columnconfigure(1, weight=1) # İkinci sütunun genişlemesi için

        ctk.CTkLabel(content_frame, text="Faaliyeti Düzenle", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ctk.CTkLabel(content_frame, text="Tür:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.type_var = ctk.StringVar()
        self.type_menu = ctk.CTkOptionMenu(content_frame, variable=self.type_var, values=FAALIYET_TURLERI)
        self.type_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5) # sticky="ew" yerine "w"

        ctk.CTkLabel(content_frame, text="Adı:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(content_frame, textvariable=self.name_var, width=300) # width eklendi
        self.name_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5) # sticky="ew" yerine "w"

        ctk.CTkLabel(content_frame, text="Tarih (Yıl-Ay):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.date_picker = build_month_year_picker(content_frame)
        self.date_picker.grid(row=3, column=1, sticky="w", padx=10, pady=5) # pady eklendi

        ctk.CTkLabel(content_frame, text="Yorum:").grid(row=4, column=0, sticky="ne", padx=10, pady=5)
        self.comment_entry = ctk.CTkTextbox(content_frame, height=80, width=300) # height ve width add_page.py ile uyumlu hale getirildi
        self.comment_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5) # sticky="ew" yerine "w"

        ctk.CTkLabel(content_frame, text="Puan:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.rating_var = ctk.StringVar(value="Seçiniz") 
        self.rating_menu = ctk.CTkOptionMenu(content_frame, variable=self.rating_var, values=["Seçiniz"] + [str(i) for i in range(1, 11)])
        self.rating_menu.grid(row=5, column=1, sticky="w", padx=10, pady=5) # pady eklendi

        self.message_label = ctk.CTkLabel(content_frame, text="") # Mesaj etiketi content_frame içine taşındı
        self.message_label.grid(row=6, column=0, columnspan=2, pady=5) # row 6

        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent") # Buton çerçevesi content_frame içine taşındı
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15) # row 7
        ctk.CTkButton(btn_frame, text="Kaydet", command=self.save_changes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Geri Dön", command=lambda: controller.show_list_page()).pack(side="left", padx=10)

    def load_activity(self, activity: Activity):
        """Düzenlenecek faaliyeti yükler ve form alanlarını doldurur."""
        self.current_activity = activity
        
        # Orijinal veriyi sakla
        self.original_activity_data = {
            "type": activity.type,
            "name": activity.name,
            "date": activity.date,
            "comment": activity.comment,
            "rating": activity.rating
        }

        self.type_var.set(activity.type)
        self.name_var.set(activity.name)
        
        year, month = extract_year_month(activity.date)
        if year:
            self.date_picker.year_var.set(str(year))
        if month:
            self.date_picker.month_var.set(f"{month:02d}")
        else: # Eğer sadece yıl varsa, ay kısmını temizle
            self.date_picker.month_var.set("")

        self.comment_entry.delete("1.0", "end")
        self.comment_entry.insert("1.0", activity.comment or "")
        
        # Puanı yüklerken "Seçiniz" durumu kontrolü
        if activity.rating == 0:
            self.rating_var.set("Seçiniz")
        else:
            self.rating_var.set(str(activity.rating))
        
        self.message_label.configure(text="") # Yüklemede mesajı temizle

    def save_changes(self):
        if not self.current_activity:
            messagebox.showwarning("Uyarı", "Düzenlenecek bir faaliyet seçilmedi.")
            return

        activity_name = self.name_var.get().strip()
        formatted_date = get_formatted_date_from_picker(self.date_picker)
        activity_type = self.type_var.get()
        comment = self.comment_entry.get("1.0", "end").strip()
        rating_str = self.rating_var.get()
        
        # self.controller.refresh_list_page() # BU SATIR BURADAN KALDIRILDI

        # Giriş Doğrulamaları
        if not activity_name:
            messagebox.showwarning("Uyarı", "Faaliyet adı boş bırakılamaz.")
            return

        if not formatted_date:
            messagebox.showwarning("Uyarı", "Tarih seçimi zorunludur.")
            return
        
        if not is_valid_yyyymm(formatted_date):
            messagebox.showwarning("Uyarı", "Geçersiz tarih formatı. Lütfen YYYY-MM formatında seçiniz.")
            return

        # Gelecek tarih kontrolü
        try:
            selected_year, selected_month = map(int, formatted_date.split('-'))
            current_date = datetime.now()
            selected_date = datetime(selected_year, selected_month, 1) 

            if selected_date > current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0):
                messagebox.showwarning("Uyarı", "Gelecekteki bir tarihi seçemezsiniz.")
                return
        except ValueError:
            messagebox.showwarning("Hata", "Tarih formatı hatası. Lütfen YYYY-MM formatında seçiniz.")
            return

        if rating_str == "Seçiniz" or not rating_str:
            rating = 0
            messagebox.showinfo("Bilgi", "Puan seçilmedi, 0 olarak kaydedildi.")
        else:
            try:
                rating = int(rating_str)
            except ValueError:
                messagebox.showwarning("Uyarı", "Geçersiz puan değeri.")
                return

        # Değişiklik kontrolü
        current_data = {
            "type": activity_type,
            "name": activity_name,
            "date": formatted_date,
            "comment": comment,
            "rating": rating
        }

        if all(current_data[key] == self.original_activity_data[key] for key in current_data):
            messagebox.showinfo("Bilgi", "Herhangi bir değişiklik yapılmadı.")
            self.controller.show_list_page()
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE activities
                SET type = ?, name = ?, date = ?, comment = ?, rating = ?
                WHERE id = ?
            """, (
                current_data["type"],
                current_data["name"],
                current_data["date"],
                current_data["comment"],
                current_data["rating"],
                self.current_activity.id
            ))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt başarıyla güncellendi.")
            self.controller.show_list_page()
            # Listeyi otomatik yenilemek için controller üzerinden çağrı yap
            self.controller.refresh_list_page() # BU SATIR BURAYA TAŞINDI
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt güncellenirken bir hata oluştu: {e}")
        finally:
            if conn:
                conn.close()
