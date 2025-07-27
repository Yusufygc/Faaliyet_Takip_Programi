import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection
from models import Activity
from utils import extract_year_month, is_valid_yyyymm, is_valid_yyyy ,sayim_yap_kategorilere_gore
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkcalendar import DateEntry
import datetime 
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

current_theme = "System"

def build_month_year_picker(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    now = datetime.datetime.now()
    years = [str(y) for y in range(now.year - 10, now.year + 1)]
    months = [f"{m:02d}" for m in range(1, 13)]

    year_var = tk.StringVar(value=str(now.year))
    month_var = tk.StringVar(value=f"{now.month:02d}")

    year_menu = ctk.CTkOptionMenu(frame, variable=year_var, values=years)
    month_menu = ctk.CTkOptionMenu(frame, variable=month_var, values=months)

    year_menu.grid(row=0, column=0, padx=5)
    month_menu.grid(row=0, column=1, padx=5)

    frame.year_var = year_var
    frame.month_var = month_var
    return frame

def get_formatted_date_from_picker(picker_frame):
    year = picker_frame.year_var.get()
    month = picker_frame.month_var.get()
    return f"{year}-{month}"

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

def open_edit_window(activity: Activity):
    edit_win = ctk.CTkToplevel()
    edit_win.title("Kaydı Düzenle")
    edit_win.geometry("400x400")

    ctk.CTkLabel(edit_win, text="Tür").pack(pady=5)
    type_var = ctk.StringVar(value=activity.type)
    type_menu = ctk.CTkOptionMenu(edit_win, variable=type_var, values=FAALIYET_TURLERI)
    type_menu.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Ad").pack(pady=5)
    name_entry = ctk.CTkEntry(edit_win)
    name_entry.insert(0, activity.name)
    name_entry.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Tarih (YYYY-MM)").pack(pady=5)
    date_picker = build_month_year_picker(edit_win)
    year, month = extract_year_month(activity.date)
    date_picker.year_var.set(str(year))
    date_picker.month_var.set(f"{month:02d}")
    date_picker.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Yorum").pack(pady=5)
    comment_entry = ctk.CTkEntry(edit_win)
    comment_entry.insert(0, activity.comment)
    comment_entry.pack(pady=2)

    ctk.CTkLabel(edit_win, text="Puan (1-10)").pack(pady=5)
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

    ctk.CTkButton(edit_win, text="Güncelle", command=update_activity).pack(pady=15)


def open_list_window():
    list_win = ctk.CTkToplevel()
    list_win.title("Kayıtları Listele ve Filtrele")
    list_win.geometry("950x600")

    filter_frame = ctk.CTkFrame(list_win)
    filter_frame.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=5)
    filter_type_var = tk.StringVar()
    filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=filter_type_var, values=[""].__add__(FAALIYET_TURLERI))
    filter_type_dropdown.grid(row=0, column=1, padx=5)

    ctk.CTkLabel(filter_frame, text="Tarih (YYYY-MM):").grid(row=0, column=2, padx=5)
    filter_date_entry = ctk.CTkEntry(filter_frame, width=120)
    filter_date_entry.grid(row=0, column=3, padx=5)

    ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=4, padx=5)
    filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
    filter_name_entry.grid(row=0, column=5, padx=5)

    tree = ttk.Treeview(list_win, columns=("ID", "Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=20)
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=130)
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
            tree.insert("", "end", values=(activity.id, activity.type, activity.name, activity.date, activity.comment, activity.rating))

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return
        item = tree.item(selected[0])
        activity_id = item["values"][0]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
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
        activity = Activity.from_row(row)
        open_edit_window(activity)

    button_frame = ctk.CTkFrame(list_win)
    button_frame.pack(pady=10)

    ctk.CTkButton(filter_frame, text="Filtrele", command=list_filtered_activities).grid(row=0, column=6, padx=10)
    ctk.CTkButton(button_frame, text="Seçili Kaydı Sil", command=delete_selected).pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Seçili Kaydı Düzenle", command=edit_selected).pack(side="left", padx=10)

    list_filtered_activities()

def open_stats_window():
    stats_win = ctk.CTkToplevel()
    stats_win.title("Aylık / Yıllık Özet ve Grafik")
    stats_win.geometry("400x200")

    ctk.CTkLabel(stats_win, text="Tarih (YYYY veya YYYY-MM)").pack()
    date_entry = ctk.CTkEntry(stats_win)
    date_entry.pack()

    def show_stats():
        tarih = date_entry.get().strip()
        if not (is_valid_yyyy(tarih) or is_valid_yyyymm(tarih)):
            messagebox.showerror("Hatalı giriş", "Tarih formatı YYYY veya YYYY-MM olmalı.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        if is_valid_yyyymm(tarih):
            cursor.execute("SELECT * FROM activities WHERE date = ?", (tarih,))
        elif is_valid_yyyy(tarih):
            cursor.execute("SELECT * FROM activities WHERE date LIKE ?", (tarih + "%",))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Veri yok", "Bu tarih için herhangi bir kayıt bulunamadı.")
            return

        sayim = sayim_yap_kategorilere_gore(rows)

        plt.figure(figsize=(6, 4))
        plt.bar(sayim.keys(), sayim.values())
        plt.title(f"{tarih} için Faaliyet Dağılımı")
        plt.xlabel("Faaliyet Türü")
        plt.ylabel("Adet")
        plt.tight_layout()
        plt.show()

    ctk.CTkButton(stats_win, text="İstatistikleri Göster", command=show_stats).pack(pady=10)

def run_gui():
    window = ctk.CTk()
    window.title("Faaliyet Takip Uygulaması")
    window.geometry("500x650")

    def tema_degistir(secilen):
        ctk.set_appearance_mode(secilen)

    title = ctk.CTkLabel(window, text="Faaliyet Takip", font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=10)

    entries = {}

    ctk.CTkLabel(window, text="Tür").pack(pady=(10, 2))
    type_var = ctk.StringVar(value=FAALIYET_TURLERI[0])
    type_menu = ctk.CTkOptionMenu(window, variable=type_var, values=FAALIYET_TURLERI)
    type_menu.pack(pady=2)

    ctk.CTkLabel(window, text="Adı").pack(pady=2)
    name_entry = ctk.CTkEntry(window, width=300)
    name_entry.pack(pady=2)

    ctk.CTkLabel(window, text="Tarih").pack(pady=2)
    date_picker = build_month_year_picker(window)
    date_picker.pack(pady=2)

    ctk.CTkLabel(window, text="Yorum").pack(pady=2)
    comment_entry = ctk.CTkEntry(window, width=300)
    comment_entry.pack(pady=2)

    ctk.CTkLabel(window, text="Puan (1-10)").pack(pady=2)
    rating_entry = ctk.CTkEntry(window, width=300)
    rating_entry.pack(pady=2)

    def ekle_callback():
        add_activity(type_var, name_entry, date_picker, comment_entry, rating_entry)

    ctk.CTkButton(window, text="Ekle", command=ekle_callback).pack(pady=10)
    ctk.CTkButton(window, text="Kayıtları Listele", command=open_list_window).pack(pady=5)
    ctk.CTkButton(window, text="İstatistikler", command=open_stats_window).pack(pady=5)

    ctk.CTkLabel(window, text="Tema").pack(pady=(20, 2))
    theme_menu = ctk.CTkOptionMenu(window, values=["System", "Light", "Dark"], command=tema_degistir)
    theme_menu.set("System")
    theme_menu.pack(pady=5)

    window.mainloop()
