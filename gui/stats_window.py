# stats_window.py
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from database import get_connection
from utils import sayim_yap_kategorilere_gore


def open_stats_window():
    stats_win = ctk.CTkToplevel()
    stats_win.title("Aylık / Yıllık Özet ve Grafik")
    stats_win.geometry("400x280")

    ctk.CTkLabel(stats_win, text="Tarih Seçimi").pack(pady=(10, 5))
    date_picker = build_month_year_picker(stats_win)
    date_picker.pack(pady=5)

    year_only_var = ctk.BooleanVar(value=False)
    year_only_checkbox = ctk.CTkCheckBox(stats_win, text="Sadece yıla göre filtrele", variable=year_only_var)
    year_only_checkbox.pack(pady=5)

    def show_stats():
        date_str = get_formatted_date_from_picker(date_picker)

        if year_only_var.get():
            date_str = date_str[:4]  # sadece yıl

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activities WHERE date LIKE ?", (date_str + "%",))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Veri yok", "Bu tarih için herhangi bir kayıt bulunamadı.")
            return

        sayim = sayim_yap_kategorilere_gore(rows)

        plt.figure(figsize=(6, 4))
        plt.bar(sayim.keys(), sayim.values())
        plt.title(f"{date_str} için Faaliyet Dağılımı")
        plt.xlabel("Faaliyet Türü")
        plt.ylabel("Adet")
        plt.tight_layout()
        plt.show()

    ctk.CTkButton(stats_win, text="İstatistikleri Göster", command=show_stats).pack(pady=15)
