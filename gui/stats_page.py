# stats_page.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import get_connection
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from gui.pdfcreate_page import PDFCreatePage 
from utils import is_valid_yyyymm, is_valid_yyyy,resource_path
from datetime import datetime
import matplotlib.font_manager as fm # Matplotlib için Türkçe karakter desteği
import os
# Matplotlib için Türkçe karakter desteği
# Eğer matplotlib fontun yolunu doğrudan belirtmek istiyorsanız:
font_path_regular = resource_path('fonts/DejaVuSans.ttf')
font_path_bold = resource_path('fonts/DejaVuSans-Bold.ttf')

if os.path.exists(font_path_regular):
    fm.fontManager.addfont(font_path_regular)
    plt.rcParams['font.family'] = 'DejaVu Sans' # Bu isim ReportLab'e kaydettiğiniz isimle aynı olmalı

if os.path.exists(font_path_bold):
    fm.fontManager.addfont(font_path_bold)
    # Eğer Matplotlib'de kalın fontu ayrıca kullanıyorsanız, buraya ek ayar yapabilirsiniz.
    # Genellikle tek bir font ailesi belirtmek yeterlidir ve Matplotlib kalın versiyonu kendi bulur.
    # plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'DejaVu Sans Bold'] # Örnek
    # plt.rcParams['font.weight'] = 'bold' # Matplotlib'e kalın font kullanmasını söylemek için

plt.rcParams['axes.unicode_minus'] = False # Negatif işaretlerin düzgün görünmesi için

class TypeDetailsDialog(ctk.CTkToplevel):
    """
    Belirli bir faaliyet türüne ait detaylı listeyi gösteren diyalog penceresi.
    """
    def __init__(self, parent, title, details_list):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x400")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main_frame, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 15))

        # Kaydırılabilir çerçeve içine detayları yerleştir
        scrollable_frame = ctk.CTkScrollableFrame(main_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if details_list:
            for idx, detail in enumerate(details_list):
                ctk.CTkLabel(scrollable_frame, text=f"• {detail}", wraplength=300, justify="left").pack(anchor="w", padx=5, pady=2)
        else:
            ctk.CTkLabel(scrollable_frame, text="Detay bulunamadı.").pack(pady=20)

        ctk.CTkButton(main_frame, text="Kapat", command=self.destroy).pack(pady=10)


class StatsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=True)
        self.current_filter_mode_is_all = False # Yeni bayrak eklendi

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Başlık
        ctk.CTkLabel(self, text="İstatistikler", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=15)

        # Filtre
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        # Filtre çerçevesindeki sütunları duyarlı hale getir
        # Tarih etiketi ve checkbox sabit, diğerleri eşit ağırlıkla genişlesin
        filter_frame.grid_columnconfigure(0, weight=0) # "Tarih:" etiketi sabit
        filter_frame.grid_columnconfigure(1, weight=1) # Tarih seçici genişlesin
        filter_frame.grid_columnconfigure(2, weight=0) # Checkbox sabit
        filter_frame.grid_columnconfigure(3, weight=1) # "Göster" butonu genişlesin
        filter_frame.grid_columnconfigure(4, weight=1) # "Tümünü Göster" butonu genişlesin
        filter_frame.grid_columnconfigure(5, weight=1) # "Karşılaştır" butonu genişlesin
        filter_frame.grid_columnconfigure(6, weight=1) # "PDF Oluştur" butonu genişlesin


        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=0, padx=5)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=1, padx=5, sticky="ew") # sticky="ew" eklendi

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=2, padx=5)

        ctk.CTkButton(filter_frame, text="Göster", command=self.show_statistics).grid(row=0, column=3, padx=10, sticky="ew") # sticky="ew" eklendi
        ctk.CTkButton(filter_frame, text="Tümünü Göster", command=self.show_all_statistics).grid(row=0, column=4, padx=10, sticky="ew") # sticky="ew" eklendi
        ctk.CTkButton(filter_frame, text="Karşılaştır", command=self.open_compare_page).grid(row=0, column=5, padx=10, sticky="ew") # sticky="ew" eklendi
        ctk.CTkButton(filter_frame, text="PDF Oluştur", command=self.open_pdf_options).grid(row=0, column=6, padx=10, sticky="ew") # sticky="ew" eklendi

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

        # İyileştirilmiş "Veri Yok" etiketi - Tam ortalanmış ve sade görünüm
        self.no_data_label = ctk.CTkLabel(
            table_frame,
            text="İstatistik verisi bulunamadı.\nLütfen önce 'Ekle' sayfasından yeni faaliyetler ekleyin.",
            font=ctk.CTkFont(size=18, slant="italic"),  # Daha küçük font ve italik
            text_color="#999999",  # Sade gri ton
            wraplength=500,  # Uygun genişlik
            justify="center"  # Metin ortalanmış
        )
        
        # Etiketi table_frame'in tam ortasına yerleştir
        # place() kullanarak tam ortalama sağlayalım
        self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")
        self.no_data_label.place_forget()  # Başlangıçta gizli tut

        self.tree.bind("<Double-1>", self.show_details_for_type)

        # Grafik Alanı
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # Program başlangıcında varsayılan olarak mevcut yılın istatistiklerini göster
        self.date_picker.year_var.set(str(datetime.now().year))
        self.selected_year_only.set(True) # Varsayılan olarak yıla göre
        self.show_statistics()

    def show_statistics(self, ignore_date_filters=False):
        self.current_filter_mode_is_all = ignore_date_filters # Bayrağı güncelle

        date_prefix = get_formatted_date_from_picker(self.date_picker)
        year_mode = self.selected_year_only.get()

        query = "SELECT type, COUNT(*) FROM activities"
        params = []

        if not ignore_date_filters:
            # Tarih doğrulama
            if year_mode:
                if not date_prefix or not is_valid_yyyy(date_prefix):
                    messagebox.showwarning("Uyarı", "Lütfen istatistikleri göstermek için geçerli bir yıl seçiniz.")
                    self.clear_statistics_display()
                    return
                query += " WHERE date LIKE ?"
                params.append(date_prefix + "%")
            else:
                if not date_prefix or not is_valid_yyyymm(date_prefix):
                    messagebox.showwarning("Uyarı", "Lütfen istatistikleri göstermek için geçerli bir ay ve yıl seçiniz.")
                    self.clear_statistics_display()
                    return
                query += " WHERE date = ?"
                params.append(date_prefix)
        # Eğer ignore_date_filters True ise, WHERE koşulu eklenmez.

        query += " GROUP BY type"

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            self.tree.delete(*self.tree.get_children())
            if not rows:
                self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")  # Etiketi tam ortada göster
                self.clear_graphs() # Grafik alanını temizle
                return
            else:
                self.no_data_label.place_forget()  # Veri varsa etiketi gizle

            for row in rows:
                self.tree.insert("", "end", values=row)

            self.plot_graphs(rows)
        except Exception as e:
            messagebox.showerror("Veritabanı Hatası", f"İstatistikler çekilirken bir hata oluştu: {e}")
            self.clear_statistics_display() # Hata durumunda ekranı temizle
        finally:
            if conn:
                conn.close()

    def show_all_statistics(self):
        """Tüm faaliyetlerin istatistiklerini gösterir (tarih filtresi olmadan)."""
        # Tarih seçiciyi ve yıl seçeneğini temizle/sıfırla
        self.date_picker.year_var.set("")
        self.date_picker.month_var.set("")
        self.selected_year_only.set(False) # Yıl bazlı filtrelemeyi kapat

        self.show_statistics(ignore_date_filters=True) # Tüm filtreleri yok sayarak çağır

    def clear_statistics_display(self):
        """İstatistik tablosunu ve grafik alanını temizler."""
        self.tree.delete(*self.tree.get_children())
        self.clear_graphs()
        self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")  # Etiketi tam ortada göster

    def plot_graphs(self, data):
        self.clear_graphs() # Önceki grafikleri temizle

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

    def clear_graphs(self):
        """Grafik alanını temizler."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        plt.close('all') # Tüm açık Matplotlib figürlerini kapat

    def show_details_for_type(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        selected_type = values[0]

        query = "SELECT name, date FROM activities WHERE type = ?"
        params = [selected_type]

        # Eğer "Tümünü Göster" modundaysak, tarih filtresini uygulamayız
        if not self.current_filter_mode_is_all:
            date_prefix = get_formatted_date_from_picker(self.date_picker)
            year_mode = self.selected_year_only.get()

            # Tarih doğrulama (sadece filtreleme modunda)
            if year_mode:
                if not date_prefix or not is_valid_yyyy(date_prefix):
                    messagebox.showwarning("Uyarı", "Detayları görmek için lütfen geçerli bir yıl seçiniz.")
                    return
                query += " AND date LIKE ?"
                params.append(date_prefix + "%")
            else:
                if not date_prefix or not is_valid_yyyymm(date_prefix):
                    messagebox.showwarning("Uyarı", "Detayları görmek için lütfen geçerli bir ay ve yıl seçiniz.")
                    return
                query += " AND date = ?"
                params.append(date_prefix)

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            details_list = [f"{name} ({date})" for name, date in rows]
            
            # Yeni detay diyalogunu aç
            TypeDetailsDialog(self, f"'{selected_type}' Kategorisi Detayları", details_list)

        except Exception as e:
            messagebox.showerror("Veritabanı Hatası", f"Detaylar çekilirken bir hata oluştu: {e}")
        finally:
            if conn:
                conn.close()

    # Bu kısımlara dokunulmayacak
    def open_compare_page(self):
        self.controller.show_compare_page()

    def open_pdf_options(self):
        """PDF oluşturma seçenekleri için yeni bir pencere açar."""
        # PDFCreatePage'i doğrudan CTkToplevel olarak aç
        pdf_dialog = ctk.CTkToplevel(self)
        pdf_dialog.title("PDF Raporu Oluştur")
        # Pencere boyutunu ve resizable özelliğini burada ayarla
        pdf_dialog.geometry("550x550") # Daha orantılı bir boyut
        pdf_dialog.resizable(False, False)
        
        pdf_dialog.transient(self.master) # Ana pencereye göre konumlandır
        pdf_dialog.grab_set() # Ana pencere etkileşimini engelle

        # PDFCreatePage örneğini oluştur ve yeni pencereye yerleştir
        pdf_page_instance = PDFCreatePage(pdf_dialog, self.controller)
        pdf_page_instance.pack(fill="both", expand=True, padx=20, pady=20)

        # Pencere kapatıldığında grab_release yap
        pdf_dialog.protocol("WM_DELETE_WINDOW", lambda: self.on_pdf_dialog_close(pdf_dialog))
        
        # PDFCreatePage içindeki tarih seçicilerin varsayılan değerlerini ayarla
        # stats_page'deki seçime göre pdf_page_instance'ı başlat
        if self.selected_year_only.get(): # Eğer istatistik sayfasında sadece yıl seçiliyse
            pdf_page_instance.pdf_option_var.set("year")
            pdf_page_instance.year_combobox.set(self.date_picker.year_var.get())
        else: # Ay ve yıl seçiliyse
            pdf_page_instance.pdf_option_var.set("month")
            pdf_page_instance.year_combobox.set(self.date_picker.year_var.get())
            pdf_page_instance.month_combobox.set(self.date_picker.month_var.get())
        
        pdf_page_instance.on_option_change() # UI'ı güncelle

        self.wait_window(pdf_dialog) # Diyalog kapanana kadar bekle

    def on_pdf_dialog_close(self, dialog):
        """PDF diyalog penceresi kapatıldığında çağrılır."""
        dialog.grab_release()
        dialog.destroy()