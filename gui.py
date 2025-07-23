# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection

FAALIYET_TURLERI = ["dizi", "film", "kitap", "oyun", "kurs", "şehir"]

def add_activity(type_var, name_entry, date_entry, comment_entry, rating_entry, tree=None):
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
        if tree:
            list_activities(tree)  # tabloyu güncelle
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")
    finally:
        conn.close()

def list_activities(tree):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activities")
    rows = cursor.fetchall()
    conn.close()

    # eski verileri temizle
    for i in tree.get_children():
        tree.delete(i)

    # yeni verileri ekle
    for row in rows:
        tree.insert("", "end", values=row)

def delete_selected_activity(tree):
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

def run_gui():
    window = tk.Tk()
    window.title("Faaliyet Takip Uygulaması")
    window.geometry("800x600")

    # Üst Form Alanı
    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    # Tür seçimi
    tk.Label(form_frame, text="Tür").grid(row=0, column=0)
    type_var = tk.StringVar()
    type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=FAALIYET_TURLERI, state="readonly", width=15)
    type_dropdown.current(0)
    type_dropdown.grid(row=0, column=1)

    # Diğer alanlar
    labels = ["Adı", "Tarih (YYYY-MM)", "Yorum", "Puan (1-10)"]
    entries = []
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label).grid(row=i+1, column=0)
        entry = tk.Entry(form_frame, width=20)
        entry.grid(row=i+1, column=1)
        entries.append(entry)

    name_entry, date_entry, comment_entry, rating_entry = entries

    # Kayıt ekle butonu
    tk.Button(form_frame, text="Ekle", command=lambda: add_activity(type_var, name_entry, date_entry, comment_entry, rating_entry, tree)).grid(row=5, column=0, columnspan=2, pady=10)

    # Listeleme ve Silme Tablosu
    tree = ttk.Treeview(window, columns=("ID", "Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill="both", expand=True)

    # Silme butonu
    tk.Button(window, text="Seçili Kaydı Sil", command=lambda: delete_selected_activity(tree)).pack(pady=5)

    # Başlangıçta listeyi doldur
    list_activities(tree)

    window.mainloop()
