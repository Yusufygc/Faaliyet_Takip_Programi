# list_page.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=False)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=5)
        self.filter_type_var = ctk.StringVar() #value=FAALIYET_TURLERI[0]
        filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_type_var, values=FAALIYET_TURLERI)
        filter_type_dropdown.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=2, padx=5)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=3, padx=5)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=4, padx=5)

        ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=5, padx=5)
        self.filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
        self.filter_name_entry.grid(row=0, column=6, padx=5)

        ctk.CTkButton(filter_frame, text="Filtrele", command=self.list_filtered_activities).grid(row=0, column=7, padx=10)

        self.tree = ttk.Treeview(self, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=20)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, pady=10)

        ctk.CTkButton(button_frame, text="Seçili Kaydı Sil", command=self.delete_selected).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Düzenle", command=self.edit_selected).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Yenile", command=self.refresh_all).pack(side="left", padx=10)

        # Minimum pencere boyutu
        self.controller.wm_minsize(800, 600)

        self.refresh_all()

    def refresh_all(self):
        self.list_filtered_activities(ignore_filters=True)

    def list_filtered_activities(self, ignore_filters=False):
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM activities WHERE 1=1"
        params = []

        if not ignore_filters:
            if self.filter_type_var.get():
                query += " AND type = ?"
                params.append(self.filter_type_var.get())

            date = get_formatted_date_from_picker(self.date_picker)
            if self.selected_year_only.get():
                query += " AND date LIKE ?"
                params.append(date[:4] + "%")
            else:
                query += " AND date = ?"
                params.append(date)

            name = self.filter_name_entry.get().strip()
            if name:
                query += " AND name LIKE ?"
                params.append(f"%{name}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            activity = Activity.from_row(row)
            self.tree.insert("", "end", values=(activity.type, activity.name, activity.date, activity.comment, activity.rating), tags=(activity.id,))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return

        item = self.tree.item(selected[0])
        name = item["values"][1]
        date = item["values"][2]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE name = ? AND date = ?", (name, date))
        conn.commit()
        conn.close()

        self.tree.delete(selected[0])
        messagebox.showinfo("Başarılı", "Kayıt silindi.")
        self.refresh_all()

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        item_id = self.tree.item(selected[0], "tags")[0]
        activity = Activity(item_id, *values)
        self.controller.show_edit_page(activity)
