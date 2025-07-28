# edit_page.py
import customtkinter as ctk
from tkinter import messagebox
from models import Activity
from database import get_connection
from utils import extract_year_month
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class EditPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_activity = None

        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Faaliyeti Düzenle", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ctk.CTkLabel(self, text="Tür:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.type_var = ctk.StringVar()
        self.type_menu = ctk.CTkOptionMenu(self, variable=self.type_var, values=FAALIYET_TURLERI)
        self.type_menu.grid(row=1, column=1, sticky="ew", padx=10)

        ctk.CTkLabel(self, text="Adı:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self, textvariable=self.name_var)
        self.name_entry.grid(row=2, column=1, sticky="ew", padx=10)

        ctk.CTkLabel(self, text="Tarih (Yıl-Ay):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.date_picker = build_month_year_picker(self)
        self.date_picker.grid(row=3, column=1, sticky="w", padx=10)

        ctk.CTkLabel(self, text="Yorum:").grid(row=4, column=0, sticky="ne", padx=10, pady=5)
        self.comment_entry = ctk.CTkTextbox(self, height=100, width=400)
        self.comment_entry.grid(row=4, column=1, sticky="ew", padx=10)

        ctk.CTkLabel(self, text="Puan:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.rating_var = ctk.StringVar()
        self.rating_menu = ctk.CTkOptionMenu(self, variable=self.rating_var, values=[str(i) for i in range(1, 11)])
        self.rating_menu.grid(row=5, column=1, sticky="w", padx=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ctk.CTkButton(btn_frame, text="Kaydet", command=self.save_changes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Geri Dön", command=lambda: controller.show_list_page()).pack(side="left", padx=10)

    def load_activity(self, activity: Activity):
        self.current_activity = activity
        self.type_var.set(activity.type)
        self.name_var.set(activity.name)
        year, month = extract_year_month(activity.date)
        if year:
            self.date_picker.year_var.set(str(year))
        if month:
            self.date_picker.month_var.set(f"{month:02d}")
        self.comment_entry.delete("1.0", "end")
        self.comment_entry.insert("1.0", activity.comment or "")
        self.rating_var.set(str(activity.rating))

    def save_changes(self):
        if not self.current_activity:
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            formatted_date = get_formatted_date_from_picker(self.date_picker)
            cursor.execute("""
                UPDATE activities
                SET type = ?, name = ?, date = ?, comment = ?, rating = ?
                WHERE id = ?
            """, (
                self.type_var.get(),
                self.name_var.get(),
                formatted_date,
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
