# views/pages/compare_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
from views.dialogs.compare_selection_dialog import CompareSelectionDialog
from constants import FAALIYET_TURLERI

class ComparePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # ÜST ALAN: Başlık + Butonlar + Filtreler
        top_section = self.create_top_section()
        layout.addWidget(top_section)

        # ORTA ALAN: Karşılaştırma Tabloları
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(3)
        self.splitter.setStyleSheet("""
            QSplitter::handle { 
                background-color: #E0E0E0; 
                border-radius: 2px;
                margin: 2px 0;
            }
            QSplitter::handle:hover { 
                background-color: #2980B9; 
            }
        """)

        # Sol Panel
        self.left_panel = self.create_modern_table_panel("1. Dönem", "left")
        self.splitter.addWidget(self.left_panel['widget'])

        # Sağ Panel
        self.right_panel = self.create_modern_table_panel("2. Dönem", "right")
        self.splitter.addWidget(self.right_panel['widget'])

        # Senkronize Kaydırma
        scroll1 = self.left_panel['table'].verticalScrollBar()
        scroll2 = self.right_panel['table'].verticalScrollBar()
        scroll1.valueChanged.connect(scroll2.setValue)
        scroll2.valueChanged.connect(scroll1.setValue)

        layout.addWidget(self.splitter, 1)

    def create_top_section(self):
        """Üst bölüm: Başlık, Butonlar ve Filtreler"""
        container = QWidget()
        container.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Başlık
        title = QLabel("📊 Dönemsel Karşılaştırma")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1A1A1A;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Butonlar - Üst Sıra
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(12)
        
        # Üst sıra: Ay ve Yıl karşılaştırma
        top_btn_layout = QHBoxLayout()
        top_btn_layout.setSpacing(15)
        top_btn_layout.addStretch()
        self.create_modern_btn("⏪ Geçen Ay", self.compare_previous_month, top_btn_layout, "#3498DB")
        self.create_modern_btn("📅 Geçen Yıl", self.compare_previous_year, top_btn_layout, "#9B59B6")
        top_btn_layout.addStretch()
        btn_layout.addLayout(top_btn_layout)
        
        # Alt sıra: Özel karşılaştırma
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        self.create_modern_btn("🔍 Özel Karşılaştırma", self.open_date_selector, bottom_btn_layout, "#E74C3C", True)
        bottom_btn_layout.addStretch()
        btn_layout.addLayout(bottom_btn_layout)
        
        layout.addLayout(btn_layout)

        return container

    def create_modern_btn(self, text, func, layout, color, is_primary=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(func)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        if is_primary:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {color}, stop:1 #C0392B);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 14px 50px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6B6B, stop:1 {color});
                }}
                QPushButton:pressed {{ padding-top: 16px; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 14px 40px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {color}DD;
                }}
                QPushButton:pressed {{ padding-top: 16px; }}
            """)
        
        layout.addWidget(btn)

    def create_modern_table_panel(self, default_title, side):
        """Modern tablo paneli"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Başlık Kartı
        header_card = QWidget()
        header_card.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            border-radius: 10px;
            padding: 5px;
        """)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_period = QLabel(default_title)
        lbl_period.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_period.setStyleSheet("color: white;")
        lbl_period.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(lbl_period)
        
        layout.addWidget(header_card)

        # Tablo
        table = QTableWidget()
        table.setColumnCount(len(FAALIYET_TURLERI))
        table.setHorizontalHeaderLabels([t.title() for t in FAALIYET_TURLERI])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectItems)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FAFAFA;
                border: none;
                border-radius: 10px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #E9ECEF);
                padding: 12px 8px;
                border: none;
                border-bottom: 3px solid #667EEA;
                font-weight: bold;
                color: #2C3E50;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 10px;
                margin: 4px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E8E8E8;
                color: #2C3E50;
            }
            QTableWidget::item:hover {
                background-color: #EBF5FB;
                border: 2px solid #3498DB;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D6EAF8, stop:1 #AED6F1);
                border: 2px solid #2980B9;
                color: #154360;
                font-weight: bold;
                outline: none;
            }
            QTableWidget:focus {
                outline: none;
            }
        """)
        
        layout.addWidget(table, 1)

        # Özet Kartı (Alt)
        summary_card = QWidget()
        summary_card.setStyleSheet("""
            background-color: #ECF0F1;
            border-radius: 8px;
            padding: 5px;
        """)
        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(15, 8, 15, 8)
        
        # İkon ve Metin
        icon_label = QLabel("📈" if side == "right" else "📊")
        icon_label.setFont(QFont("Segoe UI", 16))
        summary_layout.addWidget(icon_label)
        
        lbl_summary = QLabel("Toplam: 0 Kayıt")
        lbl_summary.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_summary.setStyleSheet("color: #2C3E50;")
        summary_layout.addWidget(lbl_summary)
        
        summary_layout.addStretch()
        
        # Kazanma Rozeti
        badge = QLabel("")
        badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
        badge.setStyleSheet("""
            background-color: #BDC3C7;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
        """)
        badge.setVisible(False)
        summary_layout.addWidget(badge)
        
        layout.addWidget(summary_card)
        
        return {
            'widget': container, 
            'label': lbl_period, 
            'summary': lbl_summary,
            'badge': badge,
            'table': table
        }

    def update_summary_style(self, panel, status):
        """Özet kartını ve rozetini güncelle"""
        badge = panel['badge']
        
        if status == "win":
            badge.setText("🏆 KAZANAN")
            badge.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #52C234, stop:1 #27AE60);
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: bold;
            """)
            badge.setVisible(True)
        elif status == "lose":
            badge.setText("📉 KAYIP")
            badge.setStyleSheet("""
                background-color: #95A5A6;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
            """)
            badge.setVisible(True)
        else:
            badge.setVisible(False)

    def display_comparison(self, title1, title2, data1, data2):
        count1 = self.update_panel(self.left_panel, title1, data1)
        count2 = self.update_panel(self.right_panel, title2, data2)

        # Kazananı Vurgula
        if count1 > count2:
            self.update_summary_style(self.left_panel, "win")
            self.update_summary_style(self.right_panel, "lose")
        elif count2 > count1:
            self.update_summary_style(self.left_panel, "lose")
            self.update_summary_style(self.right_panel, "win")
        else:
            self.update_summary_style(self.left_panel, "neutral")
            self.update_summary_style(self.right_panel, "neutral")

    def update_panel(self, panel, title, data):
        """Paneli günceller"""
        panel['label'].setText(f"📅 {title}")
        
        item_count = len(data) if data else 0
        panel['summary'].setText(f"Toplam: {item_count} Kayıt")
        
        table = panel['table']
        table.setRowCount(0)
        
        grouped_data = {t: [] for t in FAALIYET_TURLERI}
        if data:
            for cat, name in data:
                cat_clean = cat.lower() if cat else ""
                for main_cat in FAALIYET_TURLERI:
                    if main_cat.lower() == cat_clean:
                        grouped_data[main_cat].append(name)
                        break
        
        max_rows = max(len(items) for items in grouped_data.values()) if grouped_data and item_count > 0 else 0
        table.setRowCount(max_rows)

        # Dinamik Başlıklar
        headers = []
        for col_idx, main_cat in enumerate(FAALIYET_TURLERI):
            items = grouped_data[main_cat]
            count = len(items)
            headers.append(f"{main_cat.title()} ({count})")
            
            for row_idx, name in enumerate(items):
                item = QTableWidgetItem(name)
                # Tooltip: Fare ile üzerine gelindiğinde tam adı göster
                item.setToolTip(f"📌 {name}\n🏷️ Kategori: {main_cat.title()}")
                # Uzun metinleri kısalt
                display_name = name if len(name) <= 20 else name[:17] + "..."
                item.setText(display_name)
                # Orijinal veriyi sakla
                item.setData(Qt.UserRole, name)
                table.setItem(row_idx, col_idx, item)
        
        table.setHorizontalHeaderLabels(headers)
        
        return item_count

    def compare_previous_month(self):
        today = datetime.today()
        current_str = today.strftime("%Y-%m")
        
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        prev_str = last_month.strftime("%Y-%m")

        self.fetch_and_compare(prev_str, current_str)

    def compare_previous_year(self):
        this_year = datetime.today().year
        last_year = this_year - 1
        
        self.fetch_and_compare(str(last_year), str(this_year), 
                              f"{last_year} Yılı", f"{this_year} Yılı")

    def open_date_selector(self):
        dialog = CompareSelectionDialog(self)
        if dialog.exec_():
            date1, date2 = dialog.get_dates()
            self.fetch_and_compare(date1, date2)

    def fetch_and_compare(self, date1, date2, title1=None, title2=None):
        """İki tarih için veriyi sırayla çeker ve karşılaştırır."""
        
        # Loading
        # Loading
        window = self.window()
        if window and hasattr(window, 'statusBar') and window.statusBar():
            window.statusBar().showMessage("Karşılaştırma verileri yükleniyor...", 1000)

        # İç içe callback (Callback Hell'den kaçınmak için ayrı metod kullanılabilir ama basitlik için böyle)
        def on_data1_loaded(data1):
            def on_data2_loaded(data2):
                 self.display_comparison(
                     title1 if title1 else date1, 
                     title2 if title2 else date2, 
                     data1, data2
                 )
                 window = self.window()
                 if window and hasattr(window, 'statusBar') and window.statusBar():
                    window.statusBar().showMessage("Karşılaştırma tamamlandı.", 2000)

            self.controller.get_comparison_data(on_data2_loaded, date2)
        
        self.controller.get_comparison_data(on_data1_loaded, date1)