# views/pages/stats_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QSplitter, QDialog, QListWidget, QListWidgetItem, QSizePolicy, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
import sys, os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from views.widgets import MonthYearWidget

class DetailDialog(QDialog):
    def __init__(self, title, details_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QListWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #F1F5F9;
                padding: 0px;
                margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_head = QLabel(title)
        lbl_head.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(lbl_head)

        list_widget = QListWidget()
        layout.addWidget(list_widget)

        if details_list:
            for item in details_list:
                # item[0]: isim, item[1]: tarih
                
                # Container Widget
                widget = QWidget()
                widget_layout = QVBoxLayout(widget)
                widget_layout.setContentsMargins(10, 10, 10, 10)
                widget_layout.setSpacing(5)
                
                # Başlık Label
                lbl_name = QLabel(f"📌 {item[0]}")
                lbl_name.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155; background: transparent;")
                lbl_name.setWordWrap(True)
                
                # Tarih Label
                lbl_date = QLabel(f"📅 {item[1]}")
                lbl_date.setStyleSheet("font-size: 12px; color: #64748B; background: transparent;")
                
                widget_layout.addWidget(lbl_name)
                widget_layout.addWidget(lbl_date)
                
                # List Item
                list_item = QListWidgetItem(list_widget)
                list_item.setSizeHint(widget.sizeHint())
                list_widget.addItem(list_item)
                list_widget.setItemWidget(list_item, widget)
                
        else:
            item = QListWidgetItem("Kayıt bulunamadı.")
            item.setTextAlignment(Qt.AlignCenter)
            list_widget.addItem(item)

class StatsPage(QWidget):
    
    open_trend_analysis = pyqtSignal()  # Trend analizi sayfasını açma sinyali
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0) # Parent widget padding'i kullanır genelde

        # --- Başlık ---
        title = QLabel("İSTATİSTİK PANELİ")
        title.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 26px; 
            font-weight: bold; 
            color: #1E293B; 
            margin-bottom: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- Filtreleme Alanı (Card Stili) ---
        filter_frame = QFrame()
        filter_frame.setObjectName("FilterCard")
        filter_frame.setStyleSheet("""
            QFrame#FilterCard {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(15)

        self.lbl_date = QLabel("Rapor Dönemi:")
        self.lbl_date.setStyleSheet("font-size: 14px; font-weight: 600; color: #64748B;")
        filter_layout.addWidget(self.lbl_date)
        
        self.date_picker = MonthYearWidget()
        # Widget'ın kendi stili var ama burada hizalamasını sağlıyoruz
        self.date_picker.dateChanged.connect(self.refresh_statistics)
        filter_layout.addWidget(self.date_picker)
        
        filter_layout.addStretch()
        
        # Trend Analizi Butonu
        self.btn_trend = QPushButton("📈 Zaman Serisi ve Trend Analizi")
        self.btn_trend.setCursor(Qt.PointingHandCursor)
        self.btn_trend.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:pressed {
                background: #1E40AF;
            }
        """)
        self.btn_trend.clicked.connect(self.open_trend_analysis.emit)
        filter_layout.addWidget(self.btn_trend)
        
        main_layout.addWidget(filter_frame)

        # --- Özet Kartları (KPIs) ---
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)

        # Kart Renkleri
        self.card_total = self.create_kpi_card("TOPLAM FAALİYET", "0", "#3B82F6", "icons/activity.svg") 
        self.card_avg = self.create_kpi_card("GENEL ORT. PUAN", "0.0", "#8B5CF6", "icons/star.svg") 
        self.card_top = self.create_kpi_card("EN AKTİF KATEGORİ", "-", "#F59E0B", "icons/trophy.svg") 

        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_avg)
        kpi_layout.addWidget(self.card_top)
        
        main_layout.addLayout(kpi_layout)

        # --- Veri Yok Uyarısı ---
        self.lbl_no_data = QLabel("⚠️ Seçilen kriterlere uygun veri bulunamadı.")
        self.lbl_no_data.setAlignment(Qt.AlignCenter)
        self.lbl_no_data.setStyleSheet("""
            font-size: 16px; 
            color: #94A3B8; 
            background-color: white;
            border: 2px dashed #E2E8F0;
            border-radius: 12px;
            padding: 30px;
            margin-top: 10px;
        """)
        self.lbl_no_data.hide()
        main_layout.addWidget(self.lbl_no_data)

        # --- İçerik Alanı (Splitter) ---
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(2)
        self.splitter.setStyleSheet("""
            QSplitter::handle { 
                background-color: #E2E8F0; 
                margin: 10px 0px; 
            }
        """)
        
        # 1. Tablo Alanı
        self.table_container = QWidget()
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 5, 0, 5)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["KATEGORİ", "TOPLAM SAYI", "ORT. PUAN"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False) # Satır numaralarını gizle
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus) # Tıklayınca oluşan dotted border'ı kaldırır
        
        # Tablo Stili
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 2px solid #E2E8F0; 
                background-color: white; 
                border-radius: 12px; 
                padding: 0px;
                gridline-color: transparent;
            } 
            QHeaderView::section { 
                background-color: #F1F5F9; 
                border: none; 
                border-bottom: 2px solid #E2E8F0;
                padding: 12px; 
                font-weight: bold; 
                color: #475569; 
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F8FAFC;
                color: #334155;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        self.table.doubleClicked.connect(self.open_details)
        self.table.setMinimumHeight(250)
        table_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.table_container)

        # 2. Grafik Alanı
        self.graph_container = QWidget()
        graph_layout = QVBoxLayout(self.graph_container)
        graph_layout.setContentsMargins(0, 10, 0, 0)
        
        # Grafik için beyaz bir kart görünümü oluştur
        graph_card = QFrame()
        graph_card.setStyleSheet("""
            background-color: white;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
        """)
        card_inner_layout = QVBoxLayout(graph_card)
        card_inner_layout.setContentsMargins(15, 15, 15, 15)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#FFFFFF') # Grafik arka planı beyaz
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        
        self.canvas.setMinimumHeight(320)
        
        card_inner_layout.addWidget(self.canvas)
        graph_layout.addWidget(graph_card)
        
        self.splitter.addWidget(self.graph_container)

        self.splitter.setSizes([350, 450])

        main_layout.addWidget(self.splitter)

        self.refresh_statistics()

    def create_kpi_card(self, title, value, color, icon_path=None):
        """Modern, şık KPI kartı."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                border-left: 6px solid {color};
            }}
            QFrame:hover {{
                border: 2px solid {color};
                border-left: 6px solid {color};
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)
        
        # Üst Kısım: Başlık
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 700; letter-spacing: 0.5px; border: none; background: transparent;")
        
        # Alt Kısım: Değer
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 800; border: none; background: transparent;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        frame.value_label = lbl_value 
        return frame

    def refresh_statistics(self):
        date_str = self.date_picker.get_date_str()
        ignore_dates = (date_str == "")
        year_only = (len(date_str) == 4) 

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
                font = item_avg.font()
                font.setBold(True)
                item_avg.setFont(font)
            elif avg > 0 and avg < 5.0:
                item_avg.setForeground(Qt.red)
                
            self.table.setItem(row_idx, 2, item_avg)

    def update_graphs(self, data):
        self.figure.clear()
        
        types = [row[0] for row in data]
        counts = [row[1] for row in data]
        # Modern Pastel Renkler
        colors = ['#3B82F6', '#EF4444', '#F59E0B', '#10B981', '#8B5CF6', '#6366F1', '#EC4899']

        # 1. Bar Chart (Sayısal)
        ax1 = self.figure.add_subplot(121)
        bars = ax1.bar(types, counts, color=colors[:len(types)], zorder=3)
        ax1.set_title("Faaliyet Sayıları", fontsize=10, fontweight='bold', color='#334155', pad=15)
        ax1.tick_params(axis='x', rotation=45, labelsize=9, colors='#64748B')
        ax1.tick_params(axis='y', labelsize=9, colors='#64748B')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#CBD5E1')
        ax1.spines['bottom'].set_color('#CBD5E1')
        ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#475569')

        # 2. Pie Chart (Oransal)
        ax2 = self.figure.add_subplot(122)
        wedges, texts, autotexts = ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, 
                                          colors=colors[:len(types)], pctdistance=0.80, 
                                          textprops={'fontsize': 9, 'color': '#475569'},
                                          wedgeprops={'width': 0.5, 'edgecolor': 'white'}) # Donut chart görünümü
        
        # Donut Chart Merkezi Text
        total = sum(counts)
        ax2.text(0, 0, f"TOPLAM\n{total}", ha='center', va='center', fontsize=10, fontweight='bold', color='#334155')
        
        ax2.set_title("Oransal Dağılım", fontsize=10, fontweight='bold', color='#334155', pad=15)
        
        # Metin renklerini ayarla
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)

        self.figure.tight_layout()
        self.canvas.draw()

    def open_details(self):
        selected_items = self.table.selectedItems()
        if not selected_items: return
            
        activity_type_display = self.table.item(selected_items[0].row(), 0).text()
        
        date_str = self.date_picker.get_date_str()
        ignore_dates = (date_str == "")
        year_only = (len(date_str) == 4) 
        
        self.activity_type_display = activity_type_display
        self.controller.get_activity_details_by_type(
            self.on_details_loaded,
            activity_type_display, date_str, year_only, ignore_dates
        )

    def on_details_loaded(self, details):
        if details is not None:
             dialog = DetailDialog(f"{self.activity_type_display} Detayları", details, self)
             dialog.exec_()