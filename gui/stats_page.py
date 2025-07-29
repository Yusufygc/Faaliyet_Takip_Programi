# stats_page.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

class StatsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=True)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Başlık
        ctk.CTkLabel(self, text="İstatistikler", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=15)

        # Filtre
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=0, padx=5)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=1, padx=5)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=2, padx=5)

        ctk.CTkButton(filter_frame, text="Göster", command=self.show_statistics).grid(row=0, column=3, padx=10)
        ctk.CTkButton(filter_frame, text="Karşılaştır", command=self.open_compare_page).grid(row=0, column=4, padx=10)

        # Tablo
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=("Tür", "Toplam"), show="headings", height=10)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)

        self.tree.heading("Tür", text="Tür")
        self.tree.heading("Toplam", text="Toplam")
        self.tree.column("Tür", anchor="center")
        self.tree.column("Toplam", anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", self.show_details_for_type)

        # Grafik Alanı
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.show_statistics()

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

        self.plot_graphs(rows)

    def plot_graphs(self, data):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if not data:
            return

        types = [row[0] for row in data]
        counts = [row[1] for row in data]

        fig, axs = plt.subplots(1, 2, figsize=(10, 4))

        # Histogram
        axs[0].bar(types, counts, color="#1f77b4")
        axs[0].set_title("Faaliyet Dağılımı (Histogram)")
        axs[0].set_xlabel("Tür")
        axs[0].set_ylabel("Sayı")
        axs[0].tick_params(axis='x', rotation=45)

        # Pasta Grafik
        axs[1].pie(counts, labels=types, autopct='%1.1f%%', startangle=140)
        axs[1].set_title("Faaliyet Dağılımı (Pasta Dilimi)")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_details_for_type(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        selected_type = values[0]

        date = get_formatted_date_from_picker(self.date_picker)
        year_mode = self.selected_year_only.get()

        query = "SELECT name, date FROM activities WHERE type = ?"
        params = [selected_type]

        if year_mode:
            query += " AND date LIKE ?"
            params.append(date[:4] + "%")
        else:
            query += " AND date = ?"
            params.append(date)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if rows:
            detail_text = "\n".join(f"- {name} ({date})" for name, date in rows)
        else:
            detail_text = "Veri bulunamadı."

        messagebox.showinfo(f"'{selected_type}' Kategorisi Detayları", detail_text)

    def open_compare_page(self):
        self.controller.show_compare_page()



