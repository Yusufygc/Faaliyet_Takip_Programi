# stats_page.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
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
        ctk.CTkButton(filter_frame, text="PDF Oluştur", command=self.open_pdf_options).grid(row=0, column=5, padx=10)

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

    def open_pdf_options(self):
        """PDF oluşturma seçenekleri için diyalog penceresi açar"""
        dialog = PDFOptionsDialog(self)
        self.wait_window(dialog)
        
        if hasattr(dialog, 'result') and dialog.result:
            options = dialog.result
            self.create_pdf_with_options(options)

    def create_pdf_with_options(self, options):
        """Seçilen seçeneklere göre PDF oluşturur"""
        try:
            # PDF kaydetme konumu seç
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF dosyaları", "*.pdf")],
                title="PDF'i Kaydet"
            )
            
            if not file_path:
                return
            
            # PDF oluşturma parametrelerini hazırla
            date = get_formatted_date_from_picker(self.date_picker)
            year_mode = self.selected_year_only.get()
            
            pdf_params = {
                'file_path': file_path,
                'date': date,
                'year_mode': year_mode,
                'include_monthly_chart': options['monthly_chart'],
                'include_yearly_chart': options['yearly_chart'],
                'current_data': self.get_current_statistics_data()
            }
            
            # pdfcreate_page.py'deki PDF oluşturma fonksiyonunu çağır
            from gui.pdfcreate_page import create_statistics_pdf
            create_statistics_pdf(pdf_params)
            
            # Başarı mesajı
            result = messagebox.askyesno(
                "PDF Oluşturuldu", 
                f"PDF başarıyla oluşturuldu!\n\nDosya konumu: {file_path}\n\nPDF'i şimdi açmak ister misiniz?"
            )
            
            if result:
                os.startfile(file_path)  # Windows için
                # Linux/Mac için: os.system(f'xdg-open "{file_path}"') veya os.system(f'open "{file_path}"')
                
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def get_current_statistics_data(self):
        """Mevcut istatistik verilerini döndürür"""
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
        
        return rows


class PDFOptionsDialog(ctk.CTkToplevel):
    """PDF seçenekleri için diyalog penceresi"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("PDF Seçenekleri")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Ana pencereye göre merkeze konumlandır
        self.transient(parent)
        self.grab_set()
        
        # Seçenek değişkenleri
        self.monthly_chart_var = ctk.BooleanVar(value=True)
        self.yearly_chart_var = ctk.BooleanVar(value=True)
        
        self.setup_ui()
        
        # Pencereyi merkeze konumlandır
        self.center_window()

    def setup_ui(self):
        """UI bileşenlerini oluşturur"""
        # Başlık
        title_label = ctk.CTkLabel(
            self, 
            text="PDF Oluşturma Seçenekleri", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Seçenekler frame'i
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Açıklama metni
        info_label = ctk.CTkLabel(
            options_frame,
            text="PDF'e eklemek istediğiniz grafikleri seçin:",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=15)
        
        # Aylık grafik seçeneği
        monthly_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Seçilen ayın verisine göre grafik ekle",
            variable=self.monthly_chart_var,
            font=ctk.CTkFont(size=12)
        )
        monthly_checkbox.pack(pady=10, padx=20, anchor="w")
        
        # Yıllık grafik seçeneği
        yearly_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Yılın toplam verisine göre grafik ekle", 
            variable=self.yearly_chart_var,
            font=ctk.CTkFont(size=12)
        )
        yearly_checkbox.pack(pady=10, padx=20, anchor="w")
        
        # Butonlar frame'i
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(pady=20, padx=20, fill="x")
        
        # İptal butonu
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="İptal",
            command=self.cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_button.pack(side="left", padx=10)
        
        # Oluştur butonu
        create_button = ctk.CTkButton(
            buttons_frame,
            text="PDF Oluştur",
            command=self.create_pdf
        )
        create_button.pack(side="right", padx=10)

    def center_window(self):
        """Pencereyi ekranın merkezine konumlandırır"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_pdf(self):
        """PDF oluşturma seçeneklerini onaylar"""
        # En az bir seçenek seçilmeli
        if not self.monthly_chart_var.get() and not self.yearly_chart_var.get():
            messagebox.showwarning(
                "Uyarı", 
                "Lütfen en az bir grafik seçeneği işaretleyin!"
            )
            return
        
        # Sonuçları kaydet
        self.result = {
            'monthly_chart': self.monthly_chart_var.get(),
            'yearly_chart': self.yearly_chart_var.get()
        }
        
        self.destroy()

    def cancel(self):
        """Diyalogu iptal eder"""
        self.destroy()