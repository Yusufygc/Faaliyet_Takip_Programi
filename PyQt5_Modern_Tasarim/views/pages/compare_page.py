# views/pages/compare_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout, 
                             QComboBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from constants import COMPARE_PAGE_DATA_ORDER

class ComparePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Başlık
        title = QLabel("Karşılaştırma Sayfası")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Butonlar Alanı ---
        btn_layout = QHBoxLayout()
        
        btn_prev_month = QPushButton("Bir Önceki Ay ile Karşılaştır")
        btn_prev_month.clicked.connect(self.compare_previous_month)
        btn_layout.addWidget(btn_prev_month)

        btn_prev_year = QPushButton("Bir Önceki Yıl ile Karşılaştır")
        btn_prev_year.clicked.connect(self.compare_previous_year)
        btn_layout.addWidget(btn_prev_year)

        btn_custom = QPushButton("Tarihe Göre Karşılaştır")
        btn_custom.clicked.connect(self.open_date_selector)
        btn_layout.addWidget(btn_custom)

        layout.addLayout(btn_layout)

        # --- Karşılaştırma Alanı (Sol ve Sağ Panel) ---
        self.comparison_area = QHBoxLayout()
        
        # Sol Panel (Eski Tarih)
        self.left_panel = self.create_comparison_panel("1. Dönem")
        self.comparison_area.addLayout(self.left_panel["layout"])
        
        # Sağ Panel (Yeni Tarih)
        self.right_panel = self.create_comparison_panel("2. Dönem")
        self.comparison_area.addLayout(self.right_panel["layout"])

        layout.addLayout(self.comparison_area)

    def create_comparison_panel(self, title_text):
        """Karşılaştırma için tek bir sütun oluşturur."""
        layout = QVBoxLayout()
        
        # Başlık Etiketi
        lbl_title = QLabel(title_text)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1f538d;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # İçerik Alanı (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        return {"layout": layout, "title": lbl_title, "content": content_layout, "widget": content_widget}

    def display_comparison(self, title1, title2, data1, data2):
        """Gelen verileri panellere doldurur."""
        # Başlıkları Güncelle
        self.left_panel["title"].setText(title1)
        self.right_panel["title"].setText(title2)

        # İçerikleri Temizle ve Doldur
        self.fill_panel(self.left_panel["content"], data1)
        self.fill_panel(self.right_panel["content"], data2)

    def fill_panel(self, layout, data_rows):
        """Veritabanından gelen satırları (type, name) panele ekler."""
        # Önce temizle
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not data_rows:
            layout.addWidget(QLabel("Veri yok."))
            return

        # Verileri Türe Göre Grupla
        grouped_data = {}
        for dtype, dname in data_rows:
            dtype = dtype.upper()
            if dtype not in grouped_data:
                grouped_data[dtype] = []
            grouped_data[dtype].append(dname)

        # Sabit sıraya göre ekrana bas
        total_count = 0
        for dtype in COMPARE_PAGE_DATA_ORDER:
            if dtype in grouped_data:
                items = grouped_data[dtype]
                total_count += len(items)
                
                # Kategori Başlığı
                cat_label = QLabel(f"--- {dtype} ---")
                cat_label.setStyleSheet("font-weight: bold; color: #2c6cb0; margin-top: 10px;")
                layout.addWidget(cat_label)
                
                # Öğeler
                for item in sorted(items):
                    lbl = QLabel(f"• {item}")
                    lbl.setWordWrap(True)
                    layout.addWidget(lbl)

        # Toplam Sayı
        total_lbl = QLabel(f"\nToplam: {total_count} öğe")
        total_lbl.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(total_lbl)

    def compare_previous_month(self):
        today = datetime.today()
        current_str = today.strftime("%Y-%m")
        
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        prev_str = last_month.strftime("%Y-%m")

        data_current = self.controller.get_comparison_data(current_str)
        data_prev = self.controller.get_comparison_data(prev_str)

        self.display_comparison(f"Geçen Ay ({prev_str})", f"Bu Ay ({current_str})", data_prev, data_current)

    def compare_previous_year(self):
        this_year = datetime.today().year
        last_year = this_year - 1

        data_current = self.controller.get_comparison_data(str(this_year))
        data_prev = self.controller.get_comparison_data(str(last_year))

        self.display_comparison(f"Geçen Yıl ({last_year})", f"Bu Yıl ({this_year})", data_prev, data_current)

    def open_date_selector(self):
        """Basit bir tarih seçim dialogu (Geliştirilebilir)."""
        QMessageBox.information(self, "Bilgi", "Bu özellik şu an için 'Ay' ve 'Yıl' butonlarıyla sınırlandırılmıştır.")