from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QGraphicsDropShadowEffect, QComboBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont
from controllers.recommendation_controller import RecommendationController
import requests
from controllers.workers import DbWorker

class AsyncImage(QLabel):
    """
    URL'den resim yükleyen QLabel sınıfı.
    """
    def __init__(self, url, width=100, height=150):
        super().__init__()
        self.setFixedSize(width, height)
        self.setStyleSheet("background-color: #333; border-radius: 8px;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("...")
        self.url = url
        if url:
            self.load_image()
            
    def load_image(self):
        worker = DbWorker(self.fetch_image)
        worker.finished.connect(self.set_image)
        worker.start()
        self._worker = worker 

    def fetch_image(self):
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code == 200:
                img = QImage()
                img.loadFromData(response.content)
                return img
        except:
            return None
        return None

    def set_image(self, image):
        if image and not image.isNull():
            self.setPixmap(QPixmap.fromImage(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))
            self.setText("")
        else:
            self.setText("No Image")


class SuggestionCard(QFrame):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(200, 320)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: #333;
                border: 1px solid #555;
            }
            QLabel { background-color: transparent; border: none; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Image
        img_url = self.data.get('image')
        self.img_lbl = AsyncImage(img_url, 180, 240)
        layout.addWidget(self.img_lbl, alignment=Qt.AlignCenter)
        
        # Title
        title = self.data.get('title', 'Başlık Yok')
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_lbl.setWordWrap(True)
        title_lbl.setFixedHeight(40)
        layout.addWidget(title_lbl)
        
        # Rating & Date
        meta_layout = QHBoxLayout()
        rating = self.data.get('rating', 0) or 0
        rating_lbl = QLabel(f"⭐ {rating:.1f}")
        rating_lbl.setStyleSheet("color: #FFC107; font-size: 11px;")
        
        date_str = self.data.get('date', '')[:4] if self.data.get('date') else ''
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("color: #888; font-size: 11px;")
        
        meta_layout.addWidget(rating_lbl)
        meta_layout.addStretch()
        meta_layout.addWidget(date_lbl)
        layout.addLayout(meta_layout)


class SuggestionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RecommendationController()
        self.current_period = 'this_month'
        self.current_category = 'Film'
        self.current_genre = None
        self.init_ui()
        self.update_genre_combo()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 1. Header
        header_layout = QHBoxLayout()
        title = QLabel("🚀 Keşfet & Öneriler")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        
        # Period Toggle
        self.btn_this_month = QPushButton("Bu Ayın Trendleri")
        self.btn_last_year = QPushButton("Geçen Yılın Efsaneleri")
        
        for btn in [self.btn_this_month, self.btn_last_year]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(self.on_period_changed)
            
        self.btn_this_month.setChecked(True)
        self.update_toggle_styles_period()
        
        toggle_period_layout = QHBoxLayout()
        toggle_period_layout.setSpacing(10)
        toggle_period_layout.addWidget(self.btn_this_month)
        toggle_period_layout.addWidget(self.btn_last_year)
        
        header_layout.addStretch()
        header_layout.addLayout(toggle_period_layout)
        layout.addLayout(header_layout)

        # 2. Categories and Genre
        filter_layout = QHBoxLayout()
        
        # Category Buttons
        self.cat_btns = {}
        categories = ["Film", "Dizi", "Oyun", "Kitap"]
        
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(100, 35)
            btn.clicked.connect(lambda checked, c=cat: self.on_category_changed(c))
            filter_layout.addWidget(btn)
            self.cat_btns[cat] = btn
            
        self.cat_btns["Film"].setChecked(True)
        self.update_cat_styles()
        
        # Genre ComboBox
        filter_layout.addSpacing(20)
        genre_label = QLabel("Tür:")
        genre_label.setStyleSheet("color: black; font-weight: bold;")
        filter_layout.addWidget(genre_label)
        
        self.genre_combo = QComboBox()
        self.genre_combo.setMinimumWidth(120)
        self.genre_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #2196F3;
            }
        """)
        self.genre_combo.currentIndexChanged.connect(self.on_genre_changed)
        filter_layout.addWidget(self.genre_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 3. Content Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.content_widget)
        self.grid.setSpacing(20)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)
        
    def update_toggle_styles_period(self):
        base_style = """
            QPushButton {
                background-color: #1e1e1e; color: #aaa; border: 1px solid #444;
                padding: 6px 15px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:hover { border: 1px solid #666; color: #fff; }
        """
        active_style = """
            QPushButton {
                background-color: #2196F3; color: white; border: 1px solid #2196F3;
                padding: 6px 15px; border-radius: 15px; font-weight: bold;
            }
        """
        
        if self.btn_this_month.isChecked():
            self.btn_this_month.setStyleSheet(active_style)
            self.btn_last_year.setStyleSheet(base_style)
        else:
            self.btn_this_month.setStyleSheet(base_style)
            self.btn_last_year.setStyleSheet(active_style)

    def update_cat_styles(self):
        for cat, btn in self.cat_btns.items():
            if btn.isChecked():
                btn.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #2b2b2b; color: #aaa; border: 1px solid #444; border-radius: 5px;")

    def update_genre_combo(self):
        """Kategori değişince tür combobox'ını günceller."""
        self.genre_combo.blockSignals(True)
        self.genre_combo.clear()
        
        genres = self.controller.get_genres_for_category(self.current_category)
        self.genre_combo.addItems(genres)
        
        self.genre_combo.blockSignals(False)
        self.current_genre = self.controller.get_genre_value(self.current_category, "Tümü")

    def on_genre_changed(self, index):
        """Tür combobox değişince çağrılır."""
        genre_name = self.genre_combo.currentText()
        self.current_genre = self.controller.get_genre_value(self.current_category, genre_name)
        self.load_data()

    def on_period_changed(self):
        sender = self.sender()
        if sender == self.btn_this_month:
            self.current_period = 'this_month'
            self.btn_last_year.setChecked(False)
            self.btn_this_month.setChecked(True)
        else:
            self.current_period = 'last_year'
            self.btn_this_month.setChecked(False)
            self.btn_last_year.setChecked(True)
            
        self.update_toggle_styles_period()
        self.load_data()

    def on_category_changed(self, category):
        if not self.cat_btns[category].isChecked():
            self.cat_btns[category].setChecked(True)
            return

        self.current_category = category
        for cat, btn in self.cat_btns.items():
             if cat != category:
                 btn.setChecked(False)
        
        self.update_cat_styles()
        self.update_genre_combo()
        self.load_data()

    def load_data(self):
        # Clear Grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show Loading
        loading = QLabel("Veriler Çekiliyor...")
        loading.setStyleSheet("color: white; font-size: 16px;")
        loading.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(loading, 0, 0)
        
        # Call API with genre
        self.controller.get_recommendations(
            self.on_data_loaded, 
            self.current_category, 
            self.current_period,
            self.current_genre
        )

    def on_data_loaded(self, results):
        # Clear Loading
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not results:
            lbl = QLabel("Veri bulunamadı veya hata oluştu.")
            lbl.setStyleSheet("color: #f44336;")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        cols_per_row = 4
        
        for item in results:
            card = SuggestionCard(item)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1
