# -*- coding: utf-8 -*-
"""
Keşfet & Öneriler sayfası.
Film, Dizi, Oyun ve Kitap önerileri sunar.
Pagination, cache ve Türkçe içerik filtresi destekler.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QComboBox, QCheckBox, QSizePolicy)
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
        
        # State
        self.current_period = 'this_month'
        self.current_category = 'Film'
        self.current_genre = None
        self.current_page = 1
        self.is_turkish = False
        self.all_results = []  # Tüm yüklenen sonuçlar
        
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
        
        # Rastgele Öneri butonu
        self.btn_random = QPushButton("🎲 Rastgele Öneri")
        self.btn_random.setCursor(Qt.PointingHandCursor)
        self.btn_random.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7b1fa2; }
        """)
        self.btn_random.clicked.connect(self.on_random_clicked)
        header_layout.addWidget(self.btn_random)
        
        # Yenile butonu
        self.btn_refresh = QPushButton("🔄 Yenile")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f57c00; }
        """)
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)
        
        # =====================================================================
        # 2. FİLTRELER - Periyot, Kategori, Tür, Türkçe
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
        self.period_combo.setMinimumWidth(200)
        self._style_combobox(self.period_combo)
        
        for key, name in self.controller.get_all_period_names():
            self.period_combo.addItem(name, key)
        
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addSpacing(15)
        
        # -- Kategori Butonları --
        self.cat_btns = {}
        categories = ["Film", "Dizi", "Oyun", "Kitap"]
        
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(70, 30)
            btn.clicked.connect(lambda checked, c=cat: self.on_category_changed(c))
            filter_layout.addWidget(btn)
            self.cat_btns[cat] = btn
            
        self.cat_btns["Film"].setChecked(True)
        self.update_cat_styles()
        
        filter_layout.addSpacing(15)
        
        # -- Tür Seçimi --
        genre_label = QLabel("🎭 Tür:")
        genre_label.setStyleSheet("font-weight: bold; color: #333;")
        filter_layout.addWidget(genre_label)
        
        self.genre_combo = QComboBox()
        self.genre_combo.setMinimumWidth(120)
        self._style_combobox(self.genre_combo)
        self.genre_combo.currentIndexChanged.connect(self.on_genre_changed)
        filter_layout.addWidget(self.genre_combo)
        
        filter_layout.addSpacing(15)
        
        # -- Türkçe Yapımlar Checkbox --
        self.turkish_checkbox = QCheckBox("🇹🇷 Türkçe Yapımlar")
        self.turkish_checkbox.setStyleSheet("""
            QCheckBox {
                color: #333;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #e53935;
                border: 2px solid #c62828;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.turkish_checkbox.stateChanged.connect(self.on_turkish_filter_changed)
        filter_layout.addWidget(self.turkish_checkbox)
        
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
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        
        # Grid for cards
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content_layout.addWidget(self.grid_widget)
        
        # =====================================================================
        # 4. PAGINATION ALANI
        # =====================================================================
        self.pagination_widget = QWidget()
        self.pagination_widget.setStyleSheet("background: transparent;")
        pagination_layout = QHBoxLayout(self.pagination_widget)
        pagination_layout.setContentsMargins(0, 10, 0, 10)
        
        # Eski verileri göster butonu
        self.btn_show_cached = QPushButton("📂 Eski Verileri Göster")
        self.btn_show_cached.setCursor(Qt.PointingHandCursor)
        self.btn_show_cached.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #546e7a; }
            QPushButton:disabled { background-color: #ccc; color: #888; }
        """)
        self.btn_show_cached.clicked.connect(self.on_show_cached_clicked)
        pagination_layout.addWidget(self.btn_show_cached)
        
        pagination_layout.addStretch()
        
        # Sayfa bilgisi
        self.page_label = QLabel("Sayfa: 1")
        self.page_label.setStyleSheet("color: #666; font-size: 14px; font-weight: bold;")
        pagination_layout.addWidget(self.page_label)
        
        pagination_layout.addStretch()
        
        # Daha fazla göster butonu
        self.btn_load_more = QPushButton("➕ Daha Fazla Göster")
        self.btn_load_more.setCursor(Qt.PointingHandCursor)
        self.btn_load_more.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #43a047; }
            QPushButton:disabled { background-color: #ccc; color: #888; }
        """)
        self.btn_load_more.clicked.connect(self.on_load_more_clicked)
        pagination_layout.addWidget(self.btn_load_more)
        
        self.content_layout.addWidget(self.pagination_widget)
        self.content_layout.addStretch()
        
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
                font-size: 12px;
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
                        font-size: 12px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #555;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        font-size: 12px;
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

    def _reset_pagination(self):
        """Sayfa state'ini sıfırlar."""
        self.current_page = 1
        self.all_results = []
        self.update_page_label()

    def update_page_label(self):
        """Sayfa etiketini günceller."""
        self.page_label.setText(f"Sayfa: {self.current_page} | Toplam: {len(self.all_results)} içerik")

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def on_period_changed(self, index):
        """Periyot combobox değişince çağrılır."""
        self.current_period = self.period_combo.currentData()
        self._reset_pagination()
        self.load_data()

    def on_genre_changed(self, index):
        """Tür combobox değişince çağrılır."""
        genre_name = self.genre_combo.currentText()
        self.current_genre = self.controller.get_genre_value(self.current_category, genre_name)
        self._reset_pagination()
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
        self._reset_pagination()
        self.load_data()

    def on_turkish_filter_changed(self, state):
        """Türkçe yapımlar checkbox değişince çağrılır."""
        self.is_turkish = state == Qt.Checked
        self._reset_pagination()
        self.load_data()

    def on_refresh_clicked(self):
        """Yenile butonuna basılınca çağrılır."""
        self._reset_pagination()
        self.load_data(force_refresh=True)

    def on_random_clicked(self):
        """Rastgele öneri butonuna basılınca çağrılır. Seçili kategoriden rastgele içerik getirir."""
        self.btn_random.setEnabled(False)
        self.btn_random.setText("🎲 Yükleniyor...")
        # Seçili kategoriden rastgele öneri getir
        self.controller.get_random_recommendation(self.on_random_loaded, self.current_category)

    def on_random_loaded(self, result):
        """Rastgele öneri geldiğinde çağrılır."""
        self.btn_random.setEnabled(True)
        self.btn_random.setText("🎲 Rastgele Öneri")
        
        if result:
            self._show_random_modal(result)
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Hata", "Rastgele öneri bulunamadı. Lütfen tekrar deneyin.")

    def _show_random_modal(self, data):
        """Rastgele öneriyi modal pencerede gösterir."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Rastgele Öneri")
        dialog.setFixedSize(450, 550)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Kategori badge
        category = data.get('random_category', data.get('type', 'İçerik'))
        cat_label = QLabel(f"📌 {category}")
        cat_label.setStyleSheet("""
            background-color: #9c27b0;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 14px;
        """)
        cat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cat_label, alignment=Qt.AlignCenter)
        
        # Poster
        img_url = data.get('image')
        if img_url:
            img_label = AsyncImage(img_url, 200, 280)
            layout.addWidget(img_label, alignment=Qt.AlignCenter)
        
        # Başlık
        title = data.get('title', 'Bilinmiyor')
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #fff;
        """)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Rating & Date
        meta_layout = QHBoxLayout()
        
        rating = data.get('rating', 0) or 0
        rating_label = QLabel(f"⭐ {rating:.1f}/10")
        rating_label.setStyleSheet("color: #FFC107; font-size: 14px; font-weight: bold;")
        
        date_str = str(data.get('date', ''))[:4] if data.get('date') else ''
        date_label = QLabel(f"📅 {date_str}" if date_str else "")
        date_label.setStyleSheet("color: #aaa; font-size: 14px;")
        
        meta_layout.addStretch()
        meta_layout.addWidget(rating_label)
        meta_layout.addSpacing(20)
        meta_layout.addWidget(date_label)
        meta_layout.addStretch()
        layout.addLayout(meta_layout)
        
        # Açıklama
        desc = data.get('description', '')
        if desc:
            desc_label = QLabel(desc[:200])
            desc_label.setStyleSheet("color: #bbb; font-size: 12px;")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_another = QPushButton("🔄 Başka Öneri")
        btn_another.setCursor(Qt.PointingHandCursor)
        btn_another.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #546e7a; }
        """)
        btn_another.clicked.connect(lambda: self._refresh_random_modal(dialog))
        
        btn_close = QPushButton("✓ Tamam")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #43a047; }
        """)
        btn_close.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(btn_another)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def _refresh_random_modal(self, dialog):
        """Modal içinde yeni rastgele öneri getir."""
        dialog.close()
        self.on_random_clicked()

    def on_load_more_clicked(self):
        """Daha fazla göster butonuna basılınca çağrılır."""
        self.btn_load_more.setEnabled(False)
        self.btn_load_more.setText("⏳ Yükleniyor...")
        
        self.controller.get_next_page(
            self.on_more_data_loaded,
            self.current_category,
            self.current_period,
            self.current_genre,
            self.current_page,
            self.is_turkish
        )

    def on_show_cached_clicked(self):
        """Eski verileri göster butonuna basılınca çağrılır."""
        self.btn_show_cached.setEnabled(False)
        self.btn_show_cached.setText("⏳ Yükleniyor...")
        
        self.controller.get_previous_data(
            self.on_cached_data_loaded,
            self.current_category,
            self.current_period,
            self.current_genre,
            self.is_turkish
        )

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    def load_data(self, force_refresh=False):
        """Verileri API veya cache'den çeker."""
        self._clear_grid()
        
        # Yükleniyor göster
        loading = QLabel("⏳ Veriler Çekiliyor...")
        loading.setStyleSheet("color: #666; font-size: 16px; padding: 50px;")
        loading.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(loading, 0, 0)
        
        # Butonları devre dışı bırak
        self.btn_load_more.setEnabled(False)
        self.btn_show_cached.setEnabled(False)
        
        # API çağrısı
        self.controller.get_recommendations(
            self.on_data_loaded, 
            self.current_category, 
            self.current_period,
            self.current_genre,
            self.current_page,
            self.is_turkish,
            force_refresh
        )

    def _clear_grid(self):
        """Grid'i temizler."""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_results(self, results):
        """Sonuçları grid'e render eder."""
        self._clear_grid()
        
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

    def on_data_loaded(self, results):
        """İlk sayfa verisi yüklenince çağrılır."""
        self.all_results = results if results else []
        self._render_results(self.all_results)
        self.update_page_label()
        
        # Butonları etkinleştir
        self.btn_load_more.setEnabled(True)
        self.btn_load_more.setText("➕ Daha Fazla Göster")
        self.btn_show_cached.setEnabled(True)
        self.btn_show_cached.setText("📂 Eski Verileri Göster")

    def on_more_data_loaded(self, results):
        """Sonraki sayfa verisi yüklenince çağrılır."""
        if results:
            self.current_page += 1
            self.all_results.extend(results)
            self._render_results(self.all_results)
        
        self.update_page_label()
        self.btn_load_more.setEnabled(True)
        self.btn_load_more.setText("➕ Daha Fazla Göster")

    def on_cached_data_loaded(self, results):
        """Cache'den veri yüklenince çağrılır."""
        if results:
            self.all_results = results
            self._render_results(self.all_results)
            # Sayfa sayısını güncelle (yaklaşık)
            self.current_page = len(results) // 10 or 1
        
        self.update_page_label()
        self.btn_show_cached.setEnabled(True)
        self.btn_show_cached.setText("📂 Eski Verileri Göster")
