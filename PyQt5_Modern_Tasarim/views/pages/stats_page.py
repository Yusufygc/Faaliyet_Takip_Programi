# views/pages/stats_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QCheckBox, QFrame, QSplitter, QDialog, QListWidget)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from views.widgets import MonthYearWidget

# --- Detay Dialog (Aynı kalıyor) ---
class DetailDialog(QDialog):
    def __init__(self, title, details_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        list_widget = QListWidget()
        if details_list:
            for item in details_list:
                list_widget.addItem(f"• {item[0]} ({item[1]})")
        else:
            list_widget.addItem("Kayıt bulunamadı.")
        layout.addWidget(list_widget)
        btn = QListWidget() # Hata olmasın diye dummy, aslında gerek yok
        
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
            QCheckBox { font-weight: bold; color: #555; spacing: 8px; }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)

        # 1. Tüm Zamanlar
        self.chk_all_time = QCheckBox("Tüm Zamanlar")
        self.chk_all_time.toggled.connect(self.on_all_time_toggled)
        filter_layout.addWidget(self.chk_all_time)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        filter_layout.addWidget(line)

        # 2. Tarih Seçici (Artık Checkbox YOK)
        self.lbl_date = QLabel("Tarih:")
        filter_layout.addWidget(self.lbl_date)
        
        self.date_picker = MonthYearWidget()
        self.date_picker.dateChanged.connect(self.refresh_statistics)
        filter_layout.addWidget(self.date_picker)
        
        filter_layout.addStretch()
        main_layout.addWidget(filter_frame)

        # --- Veri Yok Uyarısı (YENİ) ---
        self.lbl_no_data = QLabel("⚠️ Seçilen kriterlere uygun veri bulunamadı.")
        self.lbl_no_data.setAlignment(Qt.AlignCenter)
        self.lbl_no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-top: 50px;")
        self.lbl_no_data.hide() # Başlangıçta gizli
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
        self.table.setStyleSheet("QTableWidget { border: none; } QHeaderView::section { background-color: #f0f0f0; border: none; padding: 5px; }")
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

    def on_all_time_toggled(self, checked):
        """'Tüm Zamanlar' seçildiğinde tarih seçimini devre dışı bırak."""
        self.date_picker.set_enabled(not checked)
        self.lbl_date.setEnabled(not checked)
        self.refresh_statistics()

    def refresh_statistics(self):
        """Verileri çeker ve ekranı günceller."""
        ignore_dates = self.chk_all_time.isChecked()
        date_str = self.date_picker.get_date_str()
        
        # OTOMATİK MOD ALGILAMA:
        # Eğer string uzunluğu 4 ise (örn: "2024") -> Yıl modudur.
        # Eğer string uzunluğu 7 ise (örn: "2024-05") -> Ay modudur.
        year_only = (len(date_str) == 4) 

        # Controller'dan veriyi al
        data = self.controller.get_dashboard_stats(date_str, year_only, ignore_dates)
        
        # VERİ YOK KONTROLÜ
        if not data:
            self.splitter.hide()      # Tablo ve grafiği gizle
            self.lbl_no_data.show()   # Uyarıyı göster
        else:
            self.splitter.show()      # Tablo ve grafiği göster
            self.lbl_no_data.hide()   # Uyarıyı gizle
            
            # Güncelle
            self.update_table(data)
            self.update_graphs(data)

    def update_table(self, data):
        self.table.setRowCount(0)
        for row_idx, (activity_type, count) in enumerate(data):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(activity_type))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(count)))

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
        """Detayları açarken de aynı otomatik mantığı kullanıyoruz."""
        selected_items = self.table.selectedItems()
        if not selected_items: return
            
        activity_type = self.table.item(selected_items[0].row(), 0).text()
        
        ignore_dates = self.chk_all_time.isChecked()
        date_str = self.date_picker.get_date_str()
        year_only = (len(date_str) == 4) 
        
        details = self.controller.get_activity_details_by_type(
            activity_type, date_str, year_only, ignore_dates
        )
        
        dialog = DetailDialog(f"{activity_type} Detayları", details, self)
        dialog.exec_()