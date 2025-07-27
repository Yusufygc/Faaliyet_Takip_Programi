# edit_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from models import Activity
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

def open_edit_window(activity: Activity, on_update_callback=None):
    edit_win = ctk.CTkToplevel()
    edit_win.title("Kaydı Düzenle")
    edit_win.geometry("400x400")

    ctk.CTkLabel(edit_win, text="Tür").pack(pady=(10, 2))
    type_var = ctk.StringVar(value=activity.type)
    type_menu = ctk.CTkOptionMenu(edit_win, variable=type_var, values=["dizi", "film", "kitap", "oyun", "kurs", "şehir"])
    type_menu.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Adı").pack(pady=2)
    name_entry = ctk.CTkEntry(edit_win)
    name_entry.insert(0, activity.name)
    name_entry.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Tarih").pack(pady=2)
    date_picker = build_month_year_picker(edit_win)
    year, month = activity.date.split("-")
    date_picker.year_var.set(year)
    date_picker.month_var.set(month)
    date_picker.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Yorum").pack(pady=2)
    comment_entry = ctk.CTkEntry(edit_win)
    comment_entry.insert(0, activity.comment)
    comment_entry.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Puan (1-10)").pack(pady=2)
    rating_entry = ctk.CTkEntry(edit_win)
    rating_entry.insert(0, str(activity.rating))
    rating_entry.pack(pady=2)

    def update_activity():
        new_type = type_var.get()
        new_name = name_entry.get()
        new_date = get_formatted_date_from_picker(date_picker)
        new_comment = comment_entry.get()
        new_rating = int(rating_entry.get() or 0)

        if not new_type or not new_name or not new_date:
            messagebox.showwarning("Eksik bilgi", "Tür, Ad ve Tarih boş olamaz.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE activities
            SET type = ?, name = ?, date = ?, comment = ?, rating = ?
            WHERE id = ?
        ''', (new_type, new_name, new_date, new_comment, new_rating, activity.id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
        edit_win.destroy()

        if on_update_callback:
            on_update_callback()

    ctk.CTkButton(edit_win, text="Güncelle", command=update_activity).pack(pady=10)
