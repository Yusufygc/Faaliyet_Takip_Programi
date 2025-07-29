# compare_page.py
import customtkinter as ctk
from datetime import datetime, timedelta
from database import get_connection

class ComparePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Sabit veri türleri sırası - her iki yılda da aynı sıralama
        self.data_types_order = ["DIZI", "FILM", "KITAP", "KURS", "OYUN", "ŞEHIR"]
        
        # Türkçe ay isimleri
        self.turkish_months = {
            "January": "Ocak", "February": "Şubat", "March": "Mart",
            "April": "Nisan", "May": "Mayıs", "June": "Haziran",
            "July": "Temmuz", "August": "Ağustos", "September": "Eylül",
            "October": "Ekim", "November": "Kasım", "December": "Aralık"
        }

        ctk.CTkLabel(self, text="Karşılaştırma Sayfası", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=20)

        # Butonlar
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=1, column=0, pady=10)

        ctk.CTkButton(btn_frame, text="Bir Önceki Ay ile Karşılaştır", command=self.compare_previous_month).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Bir Önceki Yıl ile Karşılaştır", command=self.compare_previous_year).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Tarihe Göre Karşılaştır", command=self.open_date_selector).pack(side="left", padx=5)

        # Ana karşılaştırma container'ı - responsive tasarım için
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Tarih seçim modal'ı için değişkenler
        self.date_modal = None
        self.comparison_type = "month"  # "month" veya "year"
        self.selected_dates = {"first": None, "second": None}

    def fetch_data_by_date(self, date_prefix):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT type, name FROM activities WHERE date LIKE ?", (f"{date_prefix}%",))
        rows = cursor.fetchall()
        conn.close()

        data = {}
        for t, name in rows:
            # Veri türünü büyük harfe çevir
            t_upper = t.upper()
            if t_upper not in data:
                data[t_upper] = []
            data[t_upper].append(name)
        return data

    def setup_responsive_layout(self):
        """Pencere boyutuna göre layout'u ayarla"""
        # Responsive kontrol için pencere genişliğini kontrol et
        self.update_idletasks()
        window_width = self.winfo_width()
        
        # 800px altında alt alta, üstünde yan yana
        if window_width < 800:
            self.main_container.grid_columnconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(1, weight=0)
            return "vertical"
        else:
            self.main_container.grid_columnconfigure((0, 1), weight=1)
            return "horizontal"

    def create_period_section(self, parent, title, data, row, column, sticky="nsew"):
        """Belirli bir dönem için veri bölümü oluşturur"""
        # Ana section frame
        section_frame = ctk.CTkFrame(parent, corner_radius=10)
        section_frame.grid(row=row, column=column, padx=8, pady=8, sticky=sticky)
        
        # Başlık - tarih formatı
        title_frame = ctk.CTkFrame(section_frame, fg_color="#1f538d", corner_radius=8)
        title_frame.grid(row=0, column=0, columnspan=len(self.data_types_order), sticky="ew", padx=10, pady=(10, 15))
        
        title_label = ctk.CTkLabel(title_frame, text=f"📅 {title}", 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 text_color="white")
        title_label.pack(pady=8)

        # Veri türü başlıkları - sabit sıralı
        headers_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        headers_frame.grid(row=1, column=0, columnspan=len(self.data_types_order), sticky="ew", padx=10, pady=(0, 5))
        
        # Her veri türü için eşit kolon genişliği
        for i in range(len(self.data_types_order)):
            headers_frame.grid_columnconfigure(i, weight=1, uniform="headers")
            section_frame.grid_columnconfigure(i, weight=1, uniform="columns")

        # Veri türü başlıklarını oluştur
        for col_idx, data_type in enumerate(self.data_types_order):
            header_btn = ctk.CTkButton(headers_frame, 
                                     text=data_type,
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     fg_color="#2c6cb0",
                                     hover_color="#1e4a7a",
                                     height=30,
                                     corner_radius=6)
            header_btn.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")

        # Veri içeriği scrollable frame
        content_frame = ctk.CTkScrollableFrame(section_frame, height=350)
        content_frame.grid(row=2, column=0, columnspan=len(self.data_types_order), 
                          sticky="nsew", padx=10, pady=(5, 10))
        
        # İçerik için kolon ayarları
        for i in range(len(self.data_types_order)):
            content_frame.grid_columnconfigure(i, weight=1, uniform="content")

        # Her veri türü için veri kolonları
        max_items = 0
        for col_idx, data_type in enumerate(self.data_types_order):
            items = data.get(data_type, [])
            sorted_items = sorted(items) if items else []
            max_items = max(max_items, len(sorted_items))
            
            # Veri kolonu frame
            column_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            column_frame.grid(row=0, column=col_idx, padx=3, pady=5, sticky="nsew")
            
            if sorted_items:
                for item_idx, item in enumerate(sorted_items):
                    item_label = ctk.CTkLabel(column_frame, 
                                            text=f"• {item}",
                                            font=ctk.CTkFont(size=11),
                                            anchor="w",
                                            wraplength=120)  # Metin sarma
                    item_label.grid(row=item_idx, column=0, sticky="ew", padx=5, pady=1)
            else:
                # Boş veri durumu
                empty_label = ctk.CTkLabel(column_frame, 
                                         text="—",
                                         font=ctk.CTkFont(size=12),
                                         text_color="gray60")
                empty_label.grid(row=0, column=0, padx=5, pady=10)

        # Toplam sayı - daha belirgin
        total_count = sum(len(items) for items in data.values())
        total_frame = ctk.CTkFrame(section_frame, fg_color="#2c6cb0", corner_radius=8)
        total_frame.grid(row=3, column=0, columnspan=len(self.data_types_order), 
                        pady=(10, 15), padx=40, sticky="ew")
        
        total_label = ctk.CTkLabel(total_frame, 
                                 text=f"Toplam: {total_count} öğe",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 text_color="white")
        total_label.pack(pady=8)
        
        # Grid weight ayarları
        section_frame.grid_rowconfigure(2, weight=1)
        
        return section_frame

    def display_comparison(self, current_label, previous_label, current_data, previous_data):
        # Önceki widget'ları temizle
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Layout tipini belirle
        layout_type = self.setup_responsive_layout()

        # Veri yoksa mesaj göster
        if not current_data and not previous_data:
            no_data_label = ctk.CTkLabel(self.main_container, 
                                       text="❌ Karşılaştırma yapılacak veri bulunamadı.",
                                       font=ctk.CTkFont(size=16))
            no_data_label.grid(row=0, column=0, columnspan=2, pady=50)
            return

        if layout_type == "horizontal":
            # Yan yana düzen (geniş ekran)
            self.create_period_section(self.main_container, previous_label, previous_data, 0, 0)
            self.create_period_section(self.main_container, current_label, current_data, 0, 1)
        else:
            # Alt alta düzen (dar ekran)
            self.create_period_section(self.main_container, previous_label, previous_data, 0, 0, sticky="ew")
            self.create_period_section(self.main_container, current_label, current_data, 1, 0, sticky="ew")
            self.main_container.grid_rowconfigure((0, 1), weight=1)

    def compare_previous_month(self):
        today = datetime.today()
        current = today.strftime("%Y-%m")
        first_of_month = today.replace(day=1)
        last_month = (first_of_month - timedelta(days=1)).strftime("%Y-%m")

        current_data = self.fetch_data_by_date(current)
        previous_data = self.fetch_data_by_date(last_month)

        # Ay isimlerini Türkçe formatla
        current_english = today.strftime("%B %Y")
        previous_english = (first_of_month - timedelta(days=1)).strftime("%B %Y")
        
        # İngilizce ay isimlerini Türkçe'ye çevir
        for eng, tr in self.turkish_months.items():
            current_english = current_english.replace(eng, tr)
            previous_english = previous_english.replace(eng, tr)

        self.display_comparison(current_english, previous_english, current_data, previous_data)

    def compare_previous_year(self):
        this_year = datetime.today().year
        last_year = this_year - 1

        current_data = self.fetch_data_by_date(str(this_year))
        previous_data = self.fetch_data_by_date(str(last_year))

        self.display_comparison(f"{this_year}", f"{last_year}", current_data, previous_data)

    def get_available_periods(self, period_type="month"):
        """Veritabanında mevcut olan dönemleri getirir"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if period_type == "month":
            # Ay bazlı: YYYY-MM formatında
            cursor.execute("SELECT DISTINCT substr(date, 1, 7) as period FROM activities ORDER BY period DESC")
        else:
            # Yıl bazlı: YYYY formatında
            cursor.execute("SELECT DISTINCT substr(date, 1, 4) as period FROM activities ORDER BY period DESC")
        
        periods = [row[0] for row in cursor.fetchall()]
        conn.close()
        return periods

    def format_period_display(self, period, period_type="month"):
        """Dönem string'ini kullanıcı dostu formata çevirir"""
        if period_type == "month":
            # "2025-07" -> "Temmuz 2025"
            year, month = period.split("-")
            month_names = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            return f"{month_names[int(month)]} {year}"
        else:
            # "2025" -> "2025"
            return period

    def open_date_selector(self):
        """Tarih seçim modal penceresini açar"""
        self.date_modal = ctk.CTkToplevel(self)
        self.date_modal.title("Tarihe Göre Karşılaştırma")
        self.date_modal.geometry("500x600")
        self.date_modal.resizable(False, False)
        
        # Modal'ı ana pencereye merkezle
        self.date_modal.transient(self.master)
        self.date_modal.grab_set()
        
        # Ana frame
        main_frame = ctk.CTkFrame(self.date_modal)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(main_frame, text="📅 Tarih Karşılaştırması", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        # Karşılaştırma tipi seçimi
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(type_frame, text="Karşılaştırma Tipi:", 
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.type_var = ctk.StringVar(value="month")
        type_radio_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        type_radio_frame.pack(pady=(0, 10))
        
        month_radio = ctk.CTkRadioButton(type_radio_frame, text="Ay Bazlı", 
                                       variable=self.type_var, value="month",
                                       command=self.on_type_change)
        month_radio.pack(side="left", padx=20)
        
        year_radio = ctk.CTkRadioButton(type_radio_frame, text="Yıl Bazlı", 
                                      variable=self.type_var, value="year",
                                      command=self.on_type_change)
        year_radio.pack(side="left", padx=20)
        
        # Tarih seçim alanları
        self.selection_frame = ctk.CTkFrame(main_frame)
        self.selection_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # İlk tarih seçimi
        first_date_frame = ctk.CTkFrame(self.selection_frame)
        first_date_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(first_date_frame, text="1. Tarih:", 
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.first_date_var = ctk.StringVar()
        self.first_date_menu = ctk.CTkOptionMenu(first_date_frame, variable=self.first_date_var,
                                               values=["Tarih seçin..."],
                                               command=self.on_date_selection_change)
        self.first_date_menu.pack(pady=(0, 10), padx=20, fill="x")
        
        # İkinci tarih seçimi
        second_date_frame = ctk.CTkFrame(self.selection_frame)
        second_date_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(second_date_frame, text="2. Tarih:", 
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.second_date_var = ctk.StringVar()
        self.second_date_menu = ctk.CTkOptionMenu(second_date_frame, variable=self.second_date_var,
                                                values=["Tarih seçin..."],
                                                command=self.on_date_selection_change)
        self.second_date_menu.pack(pady=(0, 10), padx=20, fill="x")
        
        # Uyarı mesajı alanı
        self.warning_label = ctk.CTkLabel(self.selection_frame, text="", 
                                        text_color="orange", font=ctk.CTkFont(size=12))
        self.warning_label.pack(pady=5)
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="İptal", 
                                 command=self.close_date_modal,
                                 fg_color="gray", hover_color="gray30")
        cancel_btn.pack(side="left", padx=10)
        
        compare_btn = ctk.CTkButton(button_frame, text="Karşılaştır", 
                                  command=self.execute_custom_comparison,
                                  fg_color="#2c6cb0", hover_color="#1e4a7a")
        compare_btn.pack(side="right", padx=10)
        
        # İlk yükleme
        self.update_date_options()

    def on_date_selection_change(self, selected_value):
        """Tarih seçimi değiştiğinde uyarıları temizle"""
        self.warning_label.configure(text="")

    def on_type_change(self):
        """Karşılaştırma tipi değiştiğinde çağrılır"""
        self.comparison_type = self.type_var.get()
        self.update_date_options()
        self.warning_label.configure(text="")

    def update_date_options(self):
        """Seçilen tipe göre tarih seçeneklerini günceller"""
        periods = self.get_available_periods(self.comparison_type)
        
        if not periods:
            display_options = ["Veri bulunamadı"]
            self.warning_label.configure(text="⚠️ Bu tip için kayıt bulunmamaktadır.")
        else:
            display_options = [self.format_period_display(p, self.comparison_type) for p in periods]
            self.warning_label.configure(text="")
        
        # Dropdown'ları güncelle
        self.first_date_menu.configure(values=display_options)
        self.second_date_menu.configure(values=display_options)
        
        # Seçimleri sıfırla - farklı değerler ata
        if display_options and display_options[0] != "Veri bulunamadı":
            # İlk dropdown için ilk seçeneği ata
            self.first_date_var.set(display_options[0])
            
            # İkinci dropdown için farklı bir seçenek ata
            if len(display_options) > 1:
                self.second_date_var.set(display_options[1])
            else:
                # Tek seçenek varsa, kullanıcının manuel seçim yapmasını bekle
                self.second_date_var.set("Tarih seçin...")
        else:
            self.first_date_var.set("Veri bulunamadı")
            self.second_date_var.set("Veri bulunamadı")
        
        # Periods'ı sakla (display -> raw mapping için)
        self.available_periods = periods

    def get_raw_period_from_display(self, display_text):
        """Display text'ten raw period değerini getirir"""
        periods = self.get_available_periods(self.comparison_type)
        display_options = [self.format_period_display(p, self.comparison_type) for p in periods]
        
        try:
            index = display_options.index(display_text)
            return periods[index]
        except (ValueError, IndexError):
            return None

    def execute_custom_comparison(self):
        """Seçilen tarihleri karşılaştırır"""
        first_display = self.first_date_var.get()
        second_display = self.second_date_var.get()
        
        # Geçerli seçim kontrolü
        if first_display in ["Tarih seçin...", "Veri bulunamadı"] or \
           second_display in ["Tarih seçin...", "Veri bulunamadı"]:
            self.warning_label.configure(text="⚠️ Lütfen geçerli tarihler seçin.")
            return
        
        if first_display == second_display:
            self.warning_label.configure(text="⚠️ Farklı tarihler seçin.")
            return
        
        # Raw period değerlerini al
        first_period = self.get_raw_period_from_display(first_display)
        second_period = self.get_raw_period_from_display(second_display)
        
        if not first_period or not second_period:
            self.warning_label.configure(text="⚠️ Tarih seçiminde hata oluştu.")
            return
        
        # Kronolojik sıralama yap (küçük tarih solda, büyük tarih sağda)
        if self.comparison_type == "month":
            # Ay karşılaştırması: YYYY-MM formatında karşılaştır
            if first_period < second_period:
                left_period, left_display = first_period, first_display
                right_period, right_display = second_period, second_display
            else:
                left_period, left_display = second_period, second_display
                right_period, right_display = first_period, first_display
        else:
            # Yıl karşılaştırması: YYYY formatında karşılaştır
            if int(first_period) < int(second_period):
                left_period, left_display = first_period, first_display
                right_period, right_display = second_period, second_display
            else:
                left_period, left_display = second_period, second_display
                right_period, right_display = first_period, first_display
        
        # Verileri çek
        left_data = self.fetch_data_by_date(left_period)
        right_data = self.fetch_data_by_date(right_period)
        
        # Karşılaştırmayı doğru sırayla göster (sol = eski/küçük, sağ = yeni/büyük)
        self.display_comparison(right_display, left_display, right_data, left_data)
        
        # Modal'ı kapat
        self.close_date_modal()

    def close_date_modal(self):
        """Modal penceresini kapatır"""
        if self.date_modal:
            self.date_modal.grab_release()
            self.date_modal.destroy()
            self.date_modal = None