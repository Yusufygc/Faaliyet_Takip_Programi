from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QGridLayout,
                             QScrollArea, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QCursor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime

# Modern Cart Stilini burada tekrar tanımlıyoruz (stats_page.py'den bağımsız olsun)
class AnalysisCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        # Gölge
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class TrendAnalysisWidget(AnalysisCard):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_year = datetime.now().year
        self.peak_month_data = None  # En aktif aydaki aktivite detayları
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- Header (Başlık + Filtreler) ---
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        lbl_title = QLabel("📈 Zaman Serisi ve Trend Analizi")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B; border: none;")
        lbl_desc = QLabel("Faaliyetlerinizin aylık dağılımı ve değişim trendi.")
        lbl_desc.setStyleSheet("font-size: 12px; color: #64748B; border: none;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header_layout.addLayout(title_box)
        
        header_layout.addStretch()

        # Filtreler Container
        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: #F8FAFC; border-radius: 8px; border: 1px solid #F1F5F9;")
        fw_layout = QHBoxLayout(filter_widget)
        fw_layout.setContentsMargins(5, 5, 5, 5)
        
        # Yıl Seçimi
        self.cmb_year = QComboBox()
        self.cmb_year.addItems([str(y) for y in range(self.current_year - 2, self.current_year + 3)])
        self.cmb_year.setCurrentText(str(self.current_year))
        self.cmb_year.currentIndexChanged.connect(self.load_data)
        
        # Kategori Seçimi
        self.cmb_category = QComboBox()
        self.cmb_category.addItem("Hepsi")
        # Kategoriler sonradan yüklenecek
        self.cmb_category.currentIndexChanged.connect(self.load_data)

        # Combo Stili
        combo_style = """
            QComboBox {
                background: white; border: 1px solid #E2E8F0; border-radius: 6px;
                padding: 4px 10px; font-size: 12px; color: #475569; min-width: 80px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: url(icons/down_arrow.svg);
                width: 12px;
                height: 12px;
            }
        """
        self.cmb_year.setStyleSheet(combo_style)
        self.cmb_category.setStyleSheet(combo_style)

        fw_layout.addWidget(QLabel("Yıl: ", parent=filter_widget))
        fw_layout.addWidget(self.cmb_year)
        fw_layout.addWidget(QLabel(" Kategori: ", parent=filter_widget))
        fw_layout.addWidget(self.cmb_category)
        
        header_layout.addWidget(filter_widget)
        layout.addLayout(header_layout)

        # --- Chart ---
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setStyleSheet("background: transparent; border: none;")
        
        layout.addWidget(self.canvas)
        
        # --- İstatistik Kartları ---
        self.stats_container = QFrame()
        self.stats_container.setStyleSheet("background: transparent; border: none;")
        stats_layout = QGridLayout(self.stats_container)
        stats_layout.setContentsMargins(0, 15, 0, 0)
        stats_layout.setSpacing(15)
        
        # Kartlar
        self.card_total_activities = self.create_stat_card("📊 Toplam Aktivite", "0", "#3B82F6")
        self.card_avg_per_month = self.create_stat_card("📈 Aylık Ortalama", "0", "#8B5CF6")
        self.card_peak_month = self.create_stat_card("🏆 En Aktif Ay", "-", "#F59E0B", clickable=True)
        
        stats_layout.addWidget(self.card_total_activities, 0, 0)
        stats_layout.addWidget(self.card_avg_per_month, 0, 1)
        stats_layout.addWidget(self.card_peak_month, 0, 2)
        
        layout.addWidget(self.stats_container)
        
        # --- Aktivite Detayları Listesi ---
        self.details_container = QFrame()
        self.details_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        self.details_container.hide()  # Başlangıçta gizli
        
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(20, 15, 20, 15)
        details_layout.setSpacing(10)
        
        # Başlık
        self.details_title = QLabel("Aktivite Detayları")
        self.details_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B; border: none; background: transparent;")
        details_layout.addWidget(self.details_title)
        
        # Liste
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #E2E8F0;
                padding: 8px;
                color: #334155;
            }
            QListWidget::item:hover {
                background-color: #EFF6FF;
            }
        """)
        self.activity_list.setMaximumHeight(200)
        details_layout.addWidget(self.activity_list)
        
        layout.addWidget(self.details_container)

        # Başlangıç Yüklemesi
        self.load_categories()
        self.load_data()
    
    def create_stat_card(self, title, value, color, clickable=False):
        """Dinamik istatistik kartı oluşturur"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                border: 2px solid {color if clickable else '#E2E8F0'};
                border-left: 4px solid {color};
            }}
        """)
        
        if clickable:
            card.setCursor(QCursor(Qt.PointingHandCursor))
            card.mousePressEvent = self.on_peak_month_clicked
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(5)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        
        # Value labelini dışarıdan erişilebilir yap
        card.value_label = lbl_value
        return card

    def load_categories(self):
        def on_loaded(categories):
            current = self.cmb_category.currentText()
            self.cmb_category.blockSignals(True)
            self.cmb_category.clear()
            self.cmb_category.addItem("Hepsi")
            self.cmb_category.addItems(categories)
            if current in categories:
                self.cmb_category.setCurrentText(current)
            self.cmb_category.blockSignals(False)
        
        # Kategorileri (türleri) yükle
        self.controller.get_all_activity_types(on_loaded)

    def load_data(self):
        year = self.cmb_year.currentText()
        category = self.cmb_category.currentText()
        
        def on_data_ready(data):
            # data: [(month, count), ...]
            self.plot_chart(data)
            self.update_stats_cards(data, year, category)
            
        self.controller.get_trend_data(on_data_ready, year, category)

    def plot_chart(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Veriyi Hazırla (12 Ay için 0 doldur)
        monthly_counts = {m: 0 for m in range(1, 13)}
        if data:
            for row in data:
                # Veri doğrulama
                if not row or len(row) < 2: continue
                m, count = row
                
                # Ay ve sayı değerlerini güvenli hale getir
                try:
                    if m is None: continue
                    m_int = int(m)
                    count_int = int(count) if count is not None else 0
                    
                    if 1 <= m_int <= 12:
                        monthly_counts[m_int] = count_int
                except (ValueError, TypeError):
                    continue
            
        months = list(monthly_counts.keys())
        counts = list(monthly_counts.values())
        month_labels = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']

        # Çizim - Line Chart
        # Stil: Modern Mavi Çizgi, Altı hafif dolu
        line_color = '#3B82F6'
        fill_color = '#EFF6FF'
        
        ax.plot(months, counts, color=line_color, linewidth=2.5, marker='o', markersize=6, markerfacecolor='white', markeredgewidth=2)
        ax.fill_between(months, counts, color=fill_color, alpha=0.5)

        # Eksen Ayarları
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels, fontsize=9, color='#64748B')
        ax.tick_params(axis='y', colors='#64748B', labelsize=9)
        
        # Çerçeve ve Grid
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='#94A3B8')

        # Annotation (Değerleri nokta üzerine yaz)
        for i, txt in enumerate(counts):
            if txt > 0: # Sadece 0'dan büyükleri yazalım kalabalık olmasın
                ax.annotate(str(txt), (months[i], counts[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color=line_color, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_stats_cards(self, data, year, category):
        """İstatistik kartlarını güncelle"""
        if not data:
            self.card_total_activities.value_label.setText("0")
            self.card_avg_per_month.value_label.setText("0")
            self.card_peak_month.value_label.setText("-")
            self.peak_month_data = None
            self.details_container.hide()
            return
        
        # Toplam aktivite
        total = sum(count for _, count in data)
        self.card_total_activities.value_label.setText(str(total))
        
        # Aylık ortalama
        avg = total / 12  # Tüm aylar için ortalama
        self.card_avg_per_month.value_label.setText(f"{avg:.1f}")
        
        # En aktif ay
        if data:
            month_names_full = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                               'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            peak_month, peak_count = max(data, key=lambda x: x[1])
            if peak_count > 0:
                month_name = month_names_full[peak_month-1]
                self.card_peak_month.value_label.setText(f"{month_name} ({peak_count})")
                # En aktif ayın verilerini sakla
                self.peak_month_data = (year, peak_month, month_name, category)
            else:
                self.card_peak_month.value_label.setText("-")
                self.peak_month_data = None
    
    def on_peak_month_clicked(self, event):
        """En aktif ay kartına tıklandığında aktiviteleri göster"""
        if not self.peak_month_data:
            return
        
        year, month, month_name, category = self.peak_month_data
        
        # Başlığı güncelle
        category_text = f" - {category}" if category and category != "Hepsi" else ""
        self.details_title.setText(f"{month_name} {year} Aktiviteleri{category_text}")
        
        # Aktiviteleri yükle
        def on_activities_loaded(activities):
            self.activity_list.clear()
            if activities:
                for activity_name, activity_date in activities:
                    item = QListWidgetItem(f"📌 {activity_name} - {activity_date}")
                    self.activity_list.addItem(item)
                self.details_container.show()
            else:
                item = QListWidgetItem("Aktivite bulunamadı.")
                self.activity_list.addItem(item)
                self.details_container.show()
        
        # Veritabanından aktiviteleri çek
        date_str = f"{year}-{month:02d}"
        self.controller.get_activity_details_by_month(on_activities_loaded, date_str, category)
