# list_page.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from datetime import datetime

FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        # Filtreleme Alanı
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=5)
        self.filter_type_var = ctk.StringVar()
        filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_type_var, values=FAALIYET_TURLERI)
        filter_type_dropdown.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=2, padx=5)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=3, padx=5)

        self.year_only_var = ctk.BooleanVar()
        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.year_only_var)
        self.year_only_checkbox.grid(row=0, column=4, padx=5)

        ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=5, padx=5)
        self.filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
        self.filter_name_entry.grid(row=0, column=6, padx=5)

        ctk.CTkButton(filter_frame, text="Filtrele", command=self.list_filtered_activities).grid(row=0, column=7, padx=10)

        # Tablo (TreeView)
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=("Arial", 12),
                        rowheight=30,
                        borderwidth=0)
        style.configure("Custom.Treeview.Heading", font=("Arial", 13, "bold"))
        style.layout("Custom.Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview", background="#f5f5f5", fieldbackground="#f5f5f5")
        style.map("Custom.Treeview", background=[("selected", "#a3c9f1")])

        self.tree = ttk.Treeview(self, columns=("ID", "Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=20, style="Custom.Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=0, stretch=False)  # Gizli kolon
        for col in ("Tür", "Ad", "Tarih", "Yorum", "Puan"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Dikey çizgiler (kolon ayrımı için)
        self.tree.tag_configure('striped', background='#ffffff')

        # Düğmeler
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Seçili Kaydı Sil", command=self.delete_selected).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Düzenle", command=self.edit_selected).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Yenile", command=self.refresh_all_data).pack(side="left", padx=10)

        self.list_all_activities()

    def list_filtered_activities(self):
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT id, type, name, date, comment, rating FROM activities WHERE 1=1"
        params = []

        if self.filter_type_var.get():
            query += " AND type = ?"
            params.append(self.filter_type_var.get())

        tarih_input = get_formatted_date_from_picker(self.date_picker)
        if tarih_input:
            if self.year_only_var.get():
                query += " AND date LIKE ?"
                params.append(tarih_input[:4] + "%")
            else:
                query += " AND date = ?"
                params.append(tarih_input)

        if self.filter_name_entry.get():
            query += " AND name LIKE ?"
            params.append(f"%{self.filter_name_entry.get()}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.populate_tree(rows)

    def list_all_activities(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, name, date, comment, rating FROM activities")
        rows = cursor.fetchall()
        conn.close()
        self.populate_tree(rows)

    def refresh_all_data(self):
        self.list_all_activities()
        self.reset_filters()

    def reset_filters(self):
        self.filter_type_var.set("")
        self.filter_name_entry.delete(0, "end")
        self.year_only_var.set(False)
        self.date_picker.year_var.set(str(datetime.now().year))
        self.date_picker.month_var.set("01")

    def populate_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            activity = Activity.from_row(row)
            self.tree.insert("", "end", values=(activity.id, activity.type, activity.name, activity.date, activity.comment, activity.rating))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]  # ID

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

        self.refresh_all_data()
        messagebox.showinfo("Başarılı", "Kayıt silindi.")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        activity = Activity(*values)
        self.controller.show_edit_page(activity)
        self.refresh_all_data()
