# -*- coding: utf-8 -*-
"""
Keşfet & Öneriler sayfası.
Film, Dizi, Oyun ve Kitap önerileri sunar.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from controllers.recommendation_controller import RecommendationController
import requests
from controllers.workers import DbWorker


class AsyncImage(QLabel):
    """URL'den resim yükleyen QLabel sınıfı."""
    
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
            response = requests.get(self.url, stream=True, timeout=10)
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
            self.setText("📷")


class SuggestionCard(QFrame):
    """Öneri kartı widget'ı."""
    
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
        self.img_lbl = AsyncImage(img_url, 180, 220)
        layout.addWidget(self.img_lbl, alignment=Qt.AlignCenter)
        
        # Title
        title = self.data.get('title', 'Başlık Yok')
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        title_lbl.setWordWrap(True)
        title_lbl.setFixedHeight(35)
        layout.addWidget(title_lbl)
        
        # Rating & Date
        meta_layout = QHBoxLayout()
        rating = self.data.get('rating', 0) or 0
        rating_lbl = QLabel(f"⭐ {rating:.1f}")
        rating_lbl.setStyleSheet("color: #FFC107; font-size: 11px;")
        
        date_str = str(self.data.get('date', ''))[:4] if self.data.get('date') else ''
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("color: #888; font-size: 11px;")
        
        meta_layout.addWidget(rating_lbl)
        meta_layout.addStretch()
        meta_layout.addWidget(date_lbl)
        layout.addLayout(meta_layout)


class SuggestionPage(QWidget):
    """Keşfet & Öneriler ana sayfası."""
    
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
        layout.setContentsMargins(20, 20, 20, 20)
        
        # =====================================================================
        # 1. HEADER
        # =====================================================================
        header_layout = QHBoxLayout()
        
        title = QLabel("🚀 Keşfet & Öneriler")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # =====================================================================
        # 2. FİLTRELER - Periyot, Kategori, Tür
        # =====================================================================
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)
        
        # -- Periyot Seçimi --
        period_label = QLabel("📅 Dönem:")
        period_label.setStyleSheet("font-weight: bold; color: #333;")
        filter_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.setMinimumWidth(220)
        self._style_combobox(self.period_combo)
        
        # Periyotları ekle
        for key, name in self.controller.get_all_period_names():
            self.period_combo.addItem(name, key)
        
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addSpacing(20)
        
        # -- Kategori Butonları --
        self.cat_btns = {}
        categories = ["Film", "Dizi", "Oyun", "Kitap"]
        
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(80, 32)
            btn.clicked.connect(lambda checked, c=cat: self.on_category_changed(c))
            filter_layout.addWidget(btn)
            self.cat_btns[cat] = btn
            
        self.cat_btns["Film"].setChecked(True)
        self.update_cat_styles()
        
        filter_layout.addSpacing(20)
        
        # -- Tür Seçimi --
        genre_label = QLabel("🎭 Tür:")
        genre_label.setStyleSheet("font-weight: bold; color: #333;")
        filter_layout.addWidget(genre_label)
        
        self.genre_combo = QComboBox()
        self.genre_combo.setMinimumWidth(130)
        self._style_combobox(self.genre_combo)
        self.genre_combo.currentIndexChanged.connect(self.on_genre_changed)
        filter_layout.addWidget(self.genre_combo)
        
        filter_layout.addStretch()
        layout.addWidget(filter_frame)
        
        # =====================================================================
        # 3. İÇERİK ALANI
        # =====================================================================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background: #e0e0e0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 5px;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.content_widget)
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

    def _style_combobox(self, combo):
        """ComboBox stilini uygular."""
        combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #2196F3;
            }
            QComboBox::drop-down { 
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333;
                selection-background-color: #2196F3;
                selection-color: white;
                border: 1px solid #ccc;
            }
        """)

    def update_cat_styles(self):
        """Kategori butonlarının stilini günceller."""
        for cat, btn in self.cat_btns.items():
            if btn.isChecked():
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #555;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                        border: 1px solid #2196F3;
                    }
                """)

    def update_genre_combo(self):
        """Kategori değişince tür combobox'ını günceller."""
        self.genre_combo.blockSignals(True)
        self.genre_combo.clear()
        
        genres = self.controller.get_genres_for_category(self.current_category)
        self.genre_combo.addItems(genres)
        
        self.genre_combo.blockSignals(False)
        self.current_genre = self.controller.get_genre_value(self.current_category, "Tümü")

    def on_period_changed(self, index):
        """Periyot combobox değişince çağrılır."""
        self.current_period = self.period_combo.currentData()
        self.load_data()

    def on_genre_changed(self, index):
        """Tür combobox değişince çağrılır."""
        genre_name = self.genre_combo.currentText()
        self.current_genre = self.controller.get_genre_value(self.current_category, genre_name)
        self.load_data()

    def on_category_changed(self, category):
        """Kategori butonu değişince çağrılır."""
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
        """Verileri API'den çeker."""
        # Grid'i temizle
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Yükleniyor göster
        loading = QLabel("⏳ Veriler Çekiliyor...")
        loading.setStyleSheet("color: #666; font-size: 16px; padding: 50px;")
        loading.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(loading, 0, 0)
        
        # API çağrısı
        self.controller.get_recommendations(
            self.on_data_loaded, 
            self.current_category, 
            self.current_period,
            self.current_genre
        )

    def on_data_loaded(self, results):
        """Veriler yüklenince çağrılır."""
        # Grid'i temizle
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not results:
            lbl = QLabel("❌ Veri bulunamadı veya bir hata oluştu.\n\nAPI anahtarlarınızı kontrol edin.")
            lbl.setStyleSheet("color: #f44336; font-size: 14px; padding: 50px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        cols_per_row = 5
        
        for item in results:
            card = SuggestionCard(item)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1
