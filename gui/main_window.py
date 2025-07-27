# main_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from gui.list_window import open_list_window
from gui.stats_window import open_stats_window
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from database import get_connection
from models import Activity
from tkinter import messagebox

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

def add_activity(type_var, name_entry, date_picker_frame, comment_entry, rating_entry):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        formatted_date = get_formatted_date_from_picker(date_picker_frame)

        cursor.execute('''
            INSERT INTO activities (type, name, date, comment, rating)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            type_var.get(),
            name_entry.get(),
            formatted_date,
            comment_entry.get(),
            int(rating_entry.get() or 0)
        ))
        conn.commit()
        messagebox.showinfo("Başarılı", "Faaliyet eklendi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")
    finally:
        conn.close()

def run_gui():
    window = ctk.CTk()
    window.title("Faaliyet Takip Uygulaması")
    window.geometry("500x600")

    def ekle_callback():
        try:
            date = get_formatted_date_from_picker(date_picker)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activities (type, name, date, comment, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (
                type_var.get(),
                name_entry.get(),
                date,
                comment_textbox.get("0.0", "end").strip(),
                int(rating_var.get())
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Faaliyet eklendi!")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    ctk.CTkLabel(window, text="Tür").pack(pady=(10, 2))
    type_var = ctk.StringVar(value="dizi")
    type_menu = ctk.CTkOptionMenu(window, variable=type_var, values=["dizi", "film", "kitap", "oyun", "kurs", "şehir"])
    type_menu.pack(pady=2)

    ctk.CTkLabel(window, text="Adı").pack(pady=2)
    name_entry = ctk.CTkEntry(window, width=300)
    name_entry.pack(pady=2)

    ctk.CTkLabel(window, text="Tarih (YYYY-MM)").pack(pady=2)
    date_picker = build_month_year_picker(window)
    date_picker.pack(pady=2)

    ctk.CTkLabel(window, text="Yorum").pack(pady=2)
    comment_textbox = ctk.CTkTextbox(window, width=300, height=100)
    comment_textbox.pack(pady=2)

    ctk.CTkLabel(window, text="Puan (1-10)").pack(pady=2)
    rating_var = ctk.StringVar(value="10")
    rating_menu = ctk.CTkOptionMenu(window, variable=rating_var, values=[str(i) for i in range(1, 11)])
    rating_menu.pack(pady=2)

    ctk.CTkButton(window, text="Ekle", command=ekle_callback).pack(pady=10)
    ctk.CTkButton(window, text="Kayıtları Listele", command=open_list_window).pack(pady=5)
    ctk.CTkButton(window, text="İstatistikler", command=open_stats_window).pack(pady=5)

    window.mainloop()
