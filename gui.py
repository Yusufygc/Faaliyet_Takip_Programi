import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection
from models import Activity
from utils import extract_year_month, is_valid_yyyymm, is_valid_yyyy


FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]  # "" = tüm türler

def add_activity(type_var, name_entry, date_entry, comment_entry, rating_entry):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO activities (type, name, date, comment, rating)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            type_var.get(),
            name_entry.get(),
            date_entry.get(),
            comment_entry.get(),
            int(rating_entry.get() or 0)
        ))
        conn.commit()
        messagebox.showinfo("Başarılı", "Faaliyet eklendi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")
    finally:
        conn.close()

def open_list_window():
    list_window = tk.Toplevel()
    list_window.title("Kayıtları Listele ve Filtrele")
    list_window.geometry("850x500")

    # Filtre çubuğu
    filter_frame = tk.Frame(list_window)
    filter_frame.pack(pady=5)

    # Tür filtresi
    tk.Label(filter_frame, text="Tür:").grid(row=0, column=0)
    filter_type_var = tk.StringVar()
    filter_type_dropdown = ttk.Combobox(filter_frame, textvariable=filter_type_var, values=FAALIYET_TURLERI, width=15, state="readonly")
    filter_type_dropdown.current(0)
    filter_type_dropdown.grid(row=0, column=1)

    # Tarih filtresi
    tk.Label(filter_frame, text="Tarih (YYYY-MM):").grid(row=0, column=2)
    filter_date_entry = tk.Entry(filter_frame, width=15)
    filter_date_entry.grid(row=0, column=3)

    # İsim filtresi
    tk.Label(filter_frame, text="İsim:").grid(row=0, column=4)
    filter_name_entry = tk.Entry(filter_frame, width=15)
    filter_name_entry.grid(row=0, column=5)

    # Treeview
    tree = ttk.Treeview(list_window, columns=("ID", "Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10, fill="both", expand=True)

    def list_filtered_activities():
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM activities WHERE 1=1"
        params = []

        # Tür filtresi
        if filter_type_var.get():
            query += " AND type = ?"
            params.append(filter_type_var.get())

        # Tarih filtresi (manual string karşılaştırma)
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

        # İsim filtresi
        if filter_name_entry.get():
            query += " AND name LIKE ?"
            params.append(f"%{filter_name_entry.get()}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Treeview güncelle
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

    # Filtrele Butonu
    tk.Button(filter_frame, text="Filtrele", command=list_filtered_activities).grid(row=0, column=6, padx=10)

    # Sil Butonu
    tk.Button(list_window, text="Seçili Kaydı Sil", command=delete_selected).pack(pady=5)

    list_filtered_activities()  # ilk açılışta tüm kayıtları getir

def run_gui():
    window = tk.Tk()
    window.title("Faaliyet Takip Uygulaması")
    window.geometry("400x400")

    # Form alanı
    labels = ["Adı", "Tarih (YYYY-MM)", "Yorum", "Puan (1-10)"]
    entries = []

    for label in labels:
        tk.Label(window, text=label).pack()
        entry = tk.Entry(window)
        entry.pack()
        entries.append(entry)

    name_entry, date_entry, comment_entry, rating_entry = entries

    # Tür seçimi
    tk.Label(window, text="Tür").pack()
    type_var = tk.StringVar()
    type_dropdown = ttk.Combobox(window, textvariable=type_var, values=FAALIYET_TURLERI[1:], state="readonly")
    type_dropdown.current(0)
    type_dropdown.pack()

    tk.Button(window, text="Ekle", command=lambda: add_activity(type_var, name_entry, date_entry, comment_entry, rating_entry)).pack(pady=10)

    # Listeleme Penceresini Aç Butonu
    tk.Button(window, text="Kayıtları Listele", command=open_list_window).pack(pady=10)

    window.mainloop()
