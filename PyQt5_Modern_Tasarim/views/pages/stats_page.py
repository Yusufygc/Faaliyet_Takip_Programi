# views/pages/stats_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QSplitter, QDialog, QListWidget) # QCheckBox kaldırıldı
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from views.widgets import MonthYearWidget

# --- Detay Dialog Penceresi ---
class DetailDialog(QDialog):
    def __init__(self, title, details_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        list_widget = QListWidget()
        if details_list:
            for item in details_list:
                # item: (name, date)
                list_widget.addItem(f"• {item[0]} ({item[1]})")
        else:
            list_widget.addItem("Kayıt bulunamadı.")
        layout.addWidget(list_widget)

# --- İstatistik Sayfası ---
class StatsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Başlık
        title = QLabel("İstatistik Paneli")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- Filtreleme Alanı ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; }
            QLabel { border: none; font-weight: bold; color: #555; }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)

        # GÜNCELLEME: "Tüm Zamanlar" Checkbox'ı ve ayırıcı çizgi kaldırıldı.
        
        # Tarih Seçici
        self.lbl_date = QLabel("Tarih Aralığı:")
        filter_layout.addWidget(self.lbl_date)
        
        self.date_picker = MonthYearWidget()
        self.date_picker.dateChanged.connect(self.refresh_statistics)
        filter_layout.addWidget(self.date_picker)
        
        # Sağa yasla (Tarih seçici sola dayalı, kalan boşluk sağda olsun)
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_frame)

        # --- Veri Yok Uyarısı ---
        self.lbl_no_data = QLabel("⚠️ Seçilen kriterlere uygun veri bulunamadı.")
        self.lbl_no_data.setAlignment(Qt.AlignCenter)
        self.lbl_no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-top: 50px;")
        self.lbl_no_data.hide()
        main_layout.addWidget(self.lbl_no_data)

        # --- İçerik Alanı (Splitter) ---
        self.splitter = QSplitter(Qt.Vertical)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Kategori", "Toplam Sayı"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { border: none; } 
            QHeaderView::section { background-color: #f0f0f0; border: none; padding: 5px; }
        """)
        self.table.doubleClicked.connect(self.open_details)
        self.splitter.addWidget(self.table)

        # Grafik
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#f0f0f0')
        self.canvas = FigureCanvas(self.figure)
        self.splitter.addWidget(self.canvas)

        main_layout.addWidget(self.splitter)

        # İlk yükleme
        self.refresh_statistics()

    def refresh_statistics(self):
        """Verileri çeker, BİRLEŞTİRİR ve ekranı günceller."""
        date_str = self.date_picker.get_date_str()
        
        # MANTIK GÜNCELLEMESİ:
        # Eğer date_str boşsa (""), "Tüm Yıllar" seçilidir -> ignore_dates = True
        # Eğer doluysa (örn "2025" veya "2025-05") -> ignore_dates = False
        ignore_dates = (date_str == "")
        
        # Yıl modu kontrolü: "2025" (4 karakter) -> True, "2025-05" (7 karakter) -> False
        year_only = (len(date_str) == 4) 

        # Controller'dan ham veriyi al
        raw_data = self.controller.get_dashboard_stats(date_str, year_only, ignore_dates)
        
        # --- VERİ BİRLEŞTİRME VE DÜZENLEME ---
        processed_dict = {}
        
        for category, count in raw_data:
            # Baş harfi büyüt (Örn: "dizi" -> "Dizi", "film" -> "Film")
            clean_cat = category.title() if category else "Diğer"
            
            if clean_cat in processed_dict:
                processed_dict[clean_cat] += count
            else:
                processed_dict[clean_cat] = count
                
        # Sayıya göre sırala (Çoktan aza)
        final_data = sorted(processed_dict.items(), key=lambda x: x[1], reverse=True)

        # VERİ YOK KONTROLÜ
        if not final_data:
            self.splitter.hide()
            self.lbl_no_data.show()
        else:
            self.splitter.show()
            self.lbl_no_data.hide()
            
            # Güncelle
            self.update_table(final_data)
            self.update_graphs(final_data)

    def update_table(self, data):
        """Tabloyu günceller ve verileri ortalar."""
        self.table.setRowCount(0)
        for row_idx, (activity_type, count) in enumerate(data):
            self.table.insertRow(row_idx)
            
            # 1. Kategori (Ortalı ve Baş harfi büyük)
            item_type = QTableWidgetItem(activity_type)
            item_type.setTextAlignment(Qt.AlignCenter) 
            self.table.setItem(row_idx, 0, item_type)
            
            # 2. Sayı (Ortalı)
            item_count = QTableWidgetItem(str(count))
            item_count.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_count)

    def update_graphs(self, data):
        self.figure.clear()
        
        types = [row[0] for row in data]
        counts = [row[1] for row in data]
        colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7']

        # 1. Bar Chart
        ax1 = self.figure.add_subplot(121)
        bars = ax1.bar(types, counts, color=colors[:len(types)])
        ax1.set_title("Sayısal Dağılım", fontsize=10, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)

        # 2. Donut Chart
        ax2 = self.figure.add_subplot(122)
        ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, 
                colors=colors[:len(types)], pctdistance=0.85)
        centre_circle = plt.Circle((0,0),0.70,fc='#f0f0f0')
        ax2.add_artist(centre_circle)
        ax2.set_title("Oransal Dağılım", fontsize=10, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()

    def open_details(self):
        """Detayları açar."""
        selected_items = self.table.selectedItems()
        if not selected_items: return
            
        activity_type_display = self.table.item(selected_items[0].row(), 0).text()
        
        # Filtre mantığını burada da tekrar kuruyoruz
        date_str = self.date_picker.get_date_str()
        ignore_dates = (date_str == "")
        year_only = (len(date_str) == 4) 
        
        # Önce tam eşleşme ara (Veritabanında "Dizi" olarak kayıtlıysa)
        details = self.controller.get_activity_details_by_type(
            activity_type_display, date_str, year_only, ignore_dates
        )
        # Bulamazsa küçük harfle ara ("dizi" olarak kayıtlıysa)
        if not details:
             details = self.controller.get_activity_details_by_type(
                activity_type_display.lower(), date_str, year_only, ignore_dates
            )
        
        dialog = DetailDialog(f"{activity_type_display} Detayları", details, self)
        dialog.exec_()