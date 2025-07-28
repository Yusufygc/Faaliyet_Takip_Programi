# edit_page.py
import customtkinter as ctk
from tkinter import messagebox
from models import Activity
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class EditPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_activity = None

        ctk.CTkLabel(self, text="Faaliyeti Düzenle", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        self.type_var = ctk.StringVar()
        self.name_var = ctk.StringVar()
        self.comment_var = ctk.StringVar()
        self.rating_var = ctk.StringVar()

        ctk.CTkLabel(self, text="Tür").pack()
        self.type_menu = ctk.CTkOptionMenu(self, variable=self.type_var, values=FAALIYET_TURLERI)
        self.type_menu.pack(pady=5)

        ctk.CTkLabel(self, text="Adı").pack()
        self.name_entry = ctk.CTkEntry(self, textvariable=self.name_var, width=300)
        self.name_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Tarih (Yıl-Ay)").pack()
        self.date_picker = build_month_year_picker(self)
        self.date_picker.pack(pady=5)

        ctk.CTkLabel(self, text="Yorum").pack()
        self.comment_entry = ctk.CTkTextbox(self, height=100, width=400)
        self.comment_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Puan").pack()
        self.rating_menu = ctk.CTkOptionMenu(self, variable=self.rating_var, values=[str(i) for i in range(1, 11)])
        self.rating_menu.pack(pady=5)

        ctk.CTkButton(self, text="Kaydet", command=self.save_changes).pack(pady=10)
        ctk.CTkButton(self, text="Geri Dön", command=lambda: controller.show_list_page()).pack(pady=5)

    def load_activity(self, activity: Activity):
        self.current_activity = activity
        self.type_var.set(activity.type)
        self.name_var.set(activity.name)
        year, month = activity.date.split("-")
        self.date_picker.year_var.set(year)
        self.date_picker.month_var.set(month)
        self.comment_entry.delete("1.0", "end")
        self.comment_entry.insert("1.0", activity.comment or "")
        self.rating_var.set(str(activity.rating))

    def save_changes(self):
        if not self.current_activity:
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            updated_date = get_formatted_date_from_picker(self.date_picker)
            cursor.execute("""
                UPDATE activities
                SET type = ?, name = ?, date = ?, comment = ?, rating = ?
                WHERE id = ?
            """, (
                self.type_var.get(),
                self.name_var.get(),
                updated_date,
                self.comment_entry.get("1.0", "end").strip(),
                int(self.rating_var.get()),
                self.current_activity.id
            ))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
            self.controller.show_list_page()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            conn.close()
