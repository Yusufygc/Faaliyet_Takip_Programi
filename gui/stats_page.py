# stats_page.py
import customtkinter as ctk
from tkinter import ttk
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

class StatsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):  # ← controller parametresi eklendi
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=True)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Filtre
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=0, padx=5)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=1, padx=5)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=2, padx=5)

        ctk.CTkButton(filter_frame, text="Göster", command=self.show_statistics).grid(row=0, column=3, padx=10)

        # Tablo
        self.tree = ttk.Treeview(self, columns=("Tür", "Toplam"), show="headings", height=15)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)

        self.tree.heading("Tür", text="Tür")
        self.tree.heading("Toplam", text="Toplam")
        self.tree.column("Tür", anchor="center")
        self.tree.column("Toplam", anchor="center")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def show_statistics(self):
        date = get_formatted_date_from_picker(self.date_picker)
        year_mode = self.selected_year_only.get()

        query = "SELECT type, COUNT(*) FROM activities"
        params = []

        if year_mode:
            query += " WHERE date LIKE ?"
            params.append(date[:4] + "%")
        else:
            query += " WHERE date = ?"
            params.append(date)

        query += " GROUP BY type"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)
