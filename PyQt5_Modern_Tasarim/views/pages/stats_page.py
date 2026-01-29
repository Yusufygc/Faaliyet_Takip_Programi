# views/pages/stats_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QSplitter, QDialog, QListWidget, QSizePolicy)
from PyQt5.QtCore import Qt
import sys, os
# Debug: Matplotlib importlarını logla
try:
    log_f = "stats_import_debug.txt"
    if getattr(sys, 'frozen', False):
        log_f = os.path.join(os.path.dirname(sys.executable), log_f)
    with open(log_f, "a", encoding="utf-8") as f: f.write("Importing matplotlib modules...\n")
    
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.patches import Circle
    
    with open(log_f, "a", encoding="utf-8") as f: f.write("Matplotlib imported OK.\n")
except Exception as e:
    with open("stats_import_err.txt", "w", encoding="utf-8") as f: f.write(str(e))
    raise e

from views.widgets import MonthYearWidget

class DetailDialog(QDialog):
    def __init__(self, title, details_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        list_widget = QListWidget()
        if details_list:
            for item in details_list:
                list_widget.addItem(f"• {item[0]} ({item[1]})")
        else:
            list_widget.addItem("Kayıt bulunamadı.")
        layout.addWidget(list_widget)

class StatsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Başlık
        title = QLabel("İstatistik Paneli")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50; margin: 5px 0;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- Filtreleme Alanı ---
        filter_frame = QFrame()
        filter_frame.setObjectName("Card") # styles.py'daki #Card stilini kullanır
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)

        self.lbl_date = QLabel("Rapor Dönemi:")
        self.lbl_date.setStyleSheet("font-weight: bold; color: #555;")
        filter_layout.addWidget(self.lbl_date)
        
        self.date_picker = MonthYearWidget()
        self.date_picker.dateChanged.connect(self.refresh_statistics)
        filter_layout.addWidget(self.date_picker)
        
        filter_layout.addStretch()
        main_layout.addWidget(filter_frame)

        # --- Özet Kartları (KPIs) ---
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_total = self.create_kpi_card("Toplam Faaliyet", "0", "#3498DB") # Mavi
        self.card_avg = self.create_kpi_card("Genel Ort. Puan", "0.0", "#9B59B6") # Mor
        self.card_top = self.create_kpi_card("En Aktif Kategori", "-", "#E67E22") # Turuncu

        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_avg)
        kpi_layout.addWidget(self.card_top)
        
        main_layout.addLayout(kpi_layout)

        # --- Veri Yok Uyarısı ---
        self.lbl_no_data = QLabel("⚠️ Seçilen kriterlere uygun veri bulunamadı.")
        self.lbl_no_data.setAlignment(Qt.AlignCenter)
        self.lbl_no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-top: 30px;")
        self.lbl_no_data.hide()
        main_layout.addWidget(self.lbl_no_data)

        # --- İçerik Alanı (Splitter) ---
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(10) # Tutamaç genişliği (Rahat tutuş için)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; }")
        
        # 1. Tablo Alanı
        self.table_container = QWidget()
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Kategori", "Toplam Sayı", "Ort. Puan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #E0E0E0; background-color: white; border-radius: 8px; } 
            QHeaderView::section { background-color: #EAEDED; border: none; padding: 8px; font-weight: bold; color: #2C3E50; }
        """)
        self.table.doubleClicked.connect(self.open_details)
        
        # Tabloya minimum yükseklik vererek sıkışmasını önlüyoruz
        self.table.setMinimumHeight(250)
        table_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.table_container)

        # 2. Grafik Alanı
        self.graph_container = QWidget()
        graph_layout = QVBoxLayout(self.graph_container)
        graph_layout.setContentsMargins(0, 10, 0, 0) # Üstten biraz boşluk
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#F4F7F6') 
        self.canvas = FigureCanvas(self.figure)
        # Grafiğe de minimum yükseklik verelim
        self.canvas.setMinimumHeight(300)
        
        graph_layout.addWidget(self.canvas)
        self.splitter.addWidget(self.graph_container)

        # Başlangıçta oranları ayarla (Tablo biraz daha küçük, Grafik büyük)
        self.splitter.setSizes([300, 400])

        main_layout.addWidget(self.splitter)

        # İlk yükleme
        self.refresh_statistics()

    def create_kpi_card(self, title, value, color):
        """Şık bir özet kartı oluşturur."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 5px;
                border-top: 1px solid #E0E0E0;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7F8C8D; font-size: 12px; font-weight: bold; border: none;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; border: none;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        frame.value_label = lbl_value 
        return frame

    def refresh_statistics(self):
        date_str = self.date_picker.get_date_str()
        ignore_dates = (date_str == "")
        year_only = (len(date_str) == 4) 

        # Loading durumu
        # Loading durumu
        window = self.window()
        if window and hasattr(window, 'statusBar') and window.statusBar():
            window.statusBar().showMessage("İstatistikler hesaplanıyor...", 1000)

        self.controller.get_dashboard_stats(
            self.on_stats_loaded,
            date_str, year_only, ignore_dates
        )

    def on_stats_loaded(self, raw_data):
        if raw_data is None: return

        processed_dict = {}
        for category, count, avg_rating in raw_data:
            clean_cat = category.title() if category else "Diğer"
            current_avg = avg_rating if avg_rating else 0
            
            if clean_cat not in processed_dict:
                processed_dict[clean_cat] = {"count": 0, "total_score": 0, "scored_items": 0}
            
            processed_dict[clean_cat]["count"] += count
            if current_avg > 0:
                processed_dict[clean_cat]["total_score"] += (current_avg * count)
                processed_dict[clean_cat]["scored_items"] += count

        final_data = []
        total_activities = 0
        global_score_sum = 0
        global_scored_count = 0
        most_active_cat = ("-", 0)

        for cat, data in processed_dict.items():
            count = data["count"]
            avg = data["total_score"] / data["scored_items"] if data["scored_items"] > 0 else 0
            final_data.append((cat, count, avg))
            
            total_activities += count
            global_score_sum += data["total_score"]
            global_scored_count += data["scored_items"]
            
            if count > most_active_cat[1]:
                most_active_cat = (cat, count)

        final_data.sort(key=lambda x: x[1], reverse=True)

        self.card_total.value_label.setText(str(total_activities))
        global_avg = global_score_sum / global_scored_count if global_scored_count > 0 else 0
        self.card_avg.value_label.setText(f"{global_avg:.1f}")
        self.card_top.value_label.setText(f"{most_active_cat[0]}")

        if not final_data:
            self.splitter.hide()
            self.lbl_no_data.show()
        else:
            self.splitter.show()
            self.lbl_no_data.hide()
            self.update_table(final_data)
            self.update_graphs(final_data)
        
        window = self.window()
        if window and hasattr(window, 'statusBar') and window.statusBar():
            window.statusBar().showMessage("İstatistikler güncellendi.", 2000)

    def update_table(self, data):
        self.table.setRowCount(0)
        for row_idx, (cat, count, avg) in enumerate(data):
            self.table.insertRow(row_idx)
            
            item_cat = QTableWidgetItem(cat)
            item_cat.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item_cat)
            
            item_count = QTableWidgetItem(str(count))
            item_count.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_count)
            
            avg_str = f"{avg:.1f}" if avg > 0 else "-"
            item_avg = QTableWidgetItem(avg_str)
            item_avg.setTextAlignment(Qt.AlignCenter)
            
            if avg >= 8.0:
                item_avg.setForeground(Qt.darkGreen)
                item_avg.setFont(self.table.font()) 
            elif avg > 0 and avg < 5.0:
                item_avg.setForeground(Qt.red)
                
            self.table.setItem(row_idx, 2, item_avg)

    def update_graphs(self, data):
        self.figure.clear()
        
        types = [row[0] for row in data]
        counts = [row[1] for row in data]
        colors = ['#3498DB', '#E74C3C', '#F1C40F', '#2ECC71', '#9B59B6', '#34495E']

        ax1 = self.figure.add_subplot(121)
        bars = ax1.bar(types, counts, color=colors[:len(types)])
        ax1.set_title("Sayısal Dağılım", fontsize=9, fontweight='bold', color='#2C3E50')
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)

        ax2 = self.figure.add_subplot(122)
        ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, 
                colors=colors[:len(types)], pctdistance=0.75, textprops={'fontsize': 8})
        centre_circle = Circle((0,0),0.60,fc='#F4F7F6')
        ax2.add_artist(centre_circle)
        ax2.set_title("Oransal Dağılım", fontsize=9, fontweight='bold', color='#2C3E50')

        self.figure.tight_layout()
        self.canvas.draw()

    def open_details(self):
        selected_items = self.table.selectedItems()
        if not selected_items: return
            
        activity_type_display = self.table.item(selected_items[0].row(), 0).text()
        
        date_str = self.date_picker.get_date_str()
        ignore_dates = (date_str == "")
        year_only = (len(date_str) == 4) 
        
        # Repository artık büyük/küçük harf ayrımını kendi içinde hallediyor.
        self.activity_type_display = activity_type_display
        self.controller.get_activity_details_by_type(
            self.on_details_loaded,
            activity_type_display, date_str, year_only, ignore_dates
        )

    def on_details_loaded(self, details):
        if details is not None:
             dialog = DetailDialog(f"{self.activity_type_display} Detayları", details, self)
             dialog.exec_()