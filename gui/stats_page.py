# stats_page.py
import customtkinter as ctk
from tkinter import messagebox
from utils import sayim_yap_kategorilere_gore, is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from database import get_connection

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="İstatistikler", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        # Tarih seçici
        picker_frame = ctk.CTkFrame(self)
        picker_frame.pack(pady=5)

        self.date_picker = build_month_year_picker(picker_frame)
        self.date_picker.pack(side="left", padx=5)

        self.only_year_var = ctk.BooleanVar(value=False)
        year_only_checkbox = ctk.CTkCheckBox(picker_frame, text="Sadece Yıla Göre Filtrele", variable=self.only_year_var)
        year_only_checkbox.pack(side="left", padx=10)

        ctk.CTkButton(self, text="Göster", command=self.plot_stats).pack(pady=10)

        # Grafik alanı
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def plot_stats(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        cursor = conn.cursor()

        selected_date = get_formatted_date_from_picker(self.date_picker)
        if self.only_year_var.get():
            query = "SELECT * FROM activities WHERE date LIKE ?"
            param = (selected_date[:4] + "%",)
        else:
            query = "SELECT * FROM activities WHERE date = ?"
            param = (selected_date,)

        cursor.execute(query, param)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Bilgi", "Seçilen tarihte kayıt bulunamadı.")
            return

        sayim = sayim_yap_kategorilere_gore(rows)

        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.bar(sayim.keys(), sayim.values(), color="#5588cc")
        ax.set_title("Türlere Göre Faaliyet Sayısı")
        ax.set_ylabel("Adet")
        ax.set_xlabel("Tür")

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
