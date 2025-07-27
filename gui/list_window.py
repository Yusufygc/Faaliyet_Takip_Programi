# list_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from gui.edit_window import open_edit_window
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from utils import is_valid_yyyymm, is_valid_yyyy

FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

def open_list_window():
    list_window = ctk.CTkToplevel()
    list_window.title("Kayıtları Listele ve Filtrele")
    list_window.geometry("950x600")

    filter_frame = ctk.CTkFrame(list_window)
    filter_frame.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=5)
    filter_type_var = ctk.StringVar()
    from gui.main_window import FAALIYET_TURLERI
    filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=filter_type_var, values=[""].__add__(FAALIYET_TURLERI))
    filter_type_dropdown.grid(row=0, column=1, padx=5)

    ctk.CTkLabel(filter_frame, text="Tarih (YYYY-MM):").grid(row=0, column=2, padx=5)
    filter_date_entry = ctk.CTkEntry(filter_frame, width=120)
    filter_date_entry.grid(row=0, column=3, padx=5)

    ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=4, padx=5)
    filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
    filter_name_entry.grid(row=0, column=5, padx=5)

    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
    style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"))
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    style.configure("Treeview", borderwidth=0, relief="flat")
    style.map("Treeview", background=[('selected', '#1f6aa5')])
    style.configure("Treeview", fieldbackground="#f0f0f0")

    tree = ttk.Treeview(list_window, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=20)
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")
    tree.pack(padx=10, pady=10, fill="both", expand=True)

    def list_filtered_activities():
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM activities WHERE 1=1"
        params = []

        if filter_type_var.get():
            query += " AND type = ?"
            params.append(filter_type_var.get())

        tarih_input = filter_date_entry.get().strip()
        if tarih_input:
            if is_valid_yyyymm(tarih_input):
                query += " AND date = ?"
                params.append(tarih_input)
            elif is_valid_yyyy(tarih_input):
                query += " AND date LIKE ?"
                params.append(tarih_input + "%")
            else:
                messagebox.showerror("Hatalı tarih", "Tarih formatı YYYY veya YYYY-MM olmalı.")
                return

        if filter_name_entry.get():
            query += " AND name LIKE ?"
            params.append(f"%{filter_name_entry.get()}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        tree.delete(*tree.get_children())
        for row in rows:
            activity = Activity.from_row(row)
            tree.insert("", "end", values=(activity.type, activity.name, activity.date, activity.comment, activity.rating))

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return
        item = tree.item(selected[0])
        name, = item["values"][1:2]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE name = ?", (name,))
        conn.commit()
        conn.close()

        tree.delete(selected[0])
        messagebox.showinfo("Başarılı", "Kayıt silindi.")

    def edit_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return
        item = tree.item(selected[0])
        row = item["values"]
        activity = Activity(None, *row)  # ID yok, varsayalım ki güncellemeye gerek yok
        from gui.edit_window import open_edit_window
        open_edit_window(activity, list_filtered_activities)

    button_frame = ctk.CTkFrame(list_window)
    button_frame.pack(pady=10)

    ctk.CTkButton(filter_frame, text="Filtrele", command=list_filtered_activities).grid(row=0, column=6, padx=10)
    ctk.CTkButton(button_frame, text="Seçili Kaydı Sil", command=delete_selected).pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Seçili Kaydı Düzenle", command=edit_selected).pack(side="left", padx=10)

    list_filtered_activities()