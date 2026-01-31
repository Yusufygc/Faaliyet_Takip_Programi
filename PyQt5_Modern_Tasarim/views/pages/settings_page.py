# views/pages/settings_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QLineEdit, QMessageBox, 
                             QInputDialog, QFrame, QGraphicsDropShadowEffect,
                             QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class SettingsPage(QWidget):
    # Sayfalama sabitleri
    ITEMS_PER_PAGE = 10
    MIN_LIST_HEIGHT = 120
    MAX_LIST_HEIGHT = 500  # Liste yüksekliği arttırıldı
    ITEM_HEIGHT = 40  # Öğe yüksekliği arttırıldı
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.all_types = []  # Tüm türleri saklar
        self.filtered_types = []  # Filtrelenmiş türler
        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Başlık
        title = QLabel("⚙️ Ayarlar")
        title.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            color: #2C3E50;
            padding-bottom: 5px;
        """)
        main_layout.addWidget(title)

        # --- Faaliyet Türleri Yönetimi Kartı ---
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setMaximumWidth(650) # Kart genişletildi
        self.card.setStyleSheet("""
            QFrame#Card {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
        """)
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 15, 18, 15)
        card_layout.setSpacing(10)

        # Alt Başlık
        sub_title = QLabel("📋 Faaliyet Türleri")
        sub_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #34495E;
            border: none;
        """)
        card_layout.addWidget(sub_title)

        # Açıklama
        desc = QLabel("Türleri ekleyin, düzenleyin veya silin.")
        desc.setStyleSheet("color: #95A5A6; font-size: 14px; border: none;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        # --- Arama Kutusu ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 16px;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tür ara...")
        self.search_input.textChanged.connect(self.filter_types)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                background-color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
                background-color: #FFFFFF;
            }
        """)
        search_layout.addWidget(self.search_input)
        card_layout.addLayout(search_layout)

        # İçerik Alanı (Liste ve Butonlar)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        # Liste Alanı (Liste + Sayfalama)
        list_container = QVBoxLayout()
        list_container.setSpacing(6)
        
        # Liste
        self.type_list = QListWidget()
        self.type_list.setMinimumHeight(self.MIN_LIST_HEIGHT)
        self.type_list.setMaximumHeight(self.MAX_LIST_HEIGHT)
        self.type_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 6px;
                font-size: 15px;
                background-color: #FAFAFA;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #EBF5FB;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        list_container.addWidget(self.type_list)
        
        # Sayfalama Kontrolleri
        self.pagination_frame = QFrame()
        self.pagination_frame.setStyleSheet("border: none;")
        pagination_layout = QHBoxLayout(self.pagination_frame)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(5)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(36, 36)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #ECF0F1;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                color: #2C3E50;
            }
            QPushButton:hover { background-color: #BDC3C7; }
            QPushButton:disabled { color: #BDC3C7; background-color: #F5F5F5; }
        """)
        pagination_layout.addWidget(self.btn_prev)
        
        self.page_label = QLabel("1/1")
        self.page_label.setStyleSheet("font-size: 13px; color: #7F8C8D; border: none;")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(50)
        pagination_layout.addWidget(self.page_label)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(36, 36)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: #ECF0F1;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                color: #2C3E50;
            }
            QPushButton:hover { background-color: #BDC3C7; }
            QPushButton:disabled { color: #BDC3C7; background-color: #F5F5F5; }
        """)
        pagination_layout.addWidget(self.btn_next)
        
        pagination_layout.addStretch()
        
        # Toplam sayı etiketi
        self.total_label = QLabel("0 tür")
        self.total_label.setStyleSheet("font-size: 13px; color: #95A5A6; border: none;")
        pagination_layout.addWidget(self.total_label)
        
        list_container.addWidget(self.pagination_frame)
        content_layout.addLayout(list_container, 1)

        # İşlem Butonları
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignTop)
        btn_layout.setSpacing(8)
        
        self.btn_add = self.create_btn("➕ Ekle", "#27AE60", "#219A52", self.add_type)
        self.btn_edit = self.create_btn("✏️ Düzenle", "#E67E22", "#D35400", self.edit_type)
        self.btn_delete = self.create_btn("🗑️ Sil", "#E74C3C", "#C0392B", self.delete_type)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        content_layout.addLayout(btn_layout)
        card_layout.addLayout(content_layout)
        
        main_layout.addWidget(self.card, 0, Qt.AlignLeft | Qt.AlignTop)
        main_layout.addStretch()

        # İlk veri yükleme
        self.refresh_types()

    def create_btn(self, text, color, hover_color, func):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(func)
        btn.setFixedWidth(120)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                padding-top: 9px;
                padding-bottom: 7px;
            }}
        """)
        return btn

    def filter_types(self, search_text):
        """Arama metnine göre türleri filtreler."""
        search_text = search_text.lower().strip()
        if search_text:
            self.filtered_types = [t for t in self.all_types if search_text in t.lower()]
        else:
            self.filtered_types = self.all_types.copy()
        
        self.current_page = 0
        self.update_list_display()

    def update_list_display(self):
        """Listeyi gösterir ve sayfalama kontrollerini günceller."""
        self.type_list.clear()
        
        total_items = len(self.filtered_types)
        total_pages = max(1, (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        
        # Sayfa sınırlarını kontrol et
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        if self.current_page < 0:
            self.current_page = 0
        
        # Bu sayfadaki öğeleri göster
        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = min(start_idx + self.ITEMS_PER_PAGE, total_items)
        
        page_items = self.filtered_types[start_idx:end_idx]
        for item_text in page_items:
            self.type_list.addItem(item_text)
        
        # Sayfalama kontrollerini güncelle
        self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < total_pages - 1)
        
        # Toplam sayı
        self.total_label.setText(f"{total_items} tür")
        
        # Sayfalama görünürlüğü
        self.pagination_frame.setVisible(total_items > self.ITEMS_PER_PAGE)
        
        # Dinamik liste yüksekliği
        self.adjust_list_height(len(page_items))

    def adjust_list_height(self, item_count):
        """Öğe sayısına göre liste yüksekliğini dinamik ayarlar."""
        if item_count == 0:
            new_height = self.MIN_LIST_HEIGHT
        else:
            calculated_height = item_count * self.ITEM_HEIGHT + 20  # Padding için ekstra
            new_height = max(self.MIN_LIST_HEIGHT, min(calculated_height, self.MAX_LIST_HEIGHT))
        
        self.type_list.setMinimumHeight(new_height)
        self.type_list.setMaximumHeight(new_height)

    def prev_page(self):
        """Önceki sayfaya git."""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_list_display()

    def next_page(self):
        """Sonraki sayfaya git."""
        total_pages = max(1, (len(self.filtered_types) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_list_display()

    def refresh_types(self):
        """Türleri veritabanından çeker ve listeyi yeniler."""
        self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        self.all_types = types if types else []
        self.filtered_types = self.all_types.copy()
        self.search_input.clear()
        self.current_page = 0
        self.update_list_display()

    def add_type(self):
        text, ok = QInputDialog.getText(self, "Yeni Tür", "Faaliyet Türü Adı:")
        if ok and text:
            self.btn_add.setEnabled(False)
            self.controller.add_activity_type(text, self.on_add_finished)

    def on_add_finished(self, result):
        self.btn_add.setEnabled(True)
        success, msg = result
        if success:
            self.refresh_types()
            if self.window().statusBar():
                self.window().statusBar().showMessage(f"✅ {msg}", 3000)
        else:
            QMessageBox.warning(self, "Hata", msg)

    def edit_type(self):
        current_item = self.type_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir tür seçin.")
            return
            
        old_name = current_item.text()
        new_name, ok = QInputDialog.getText(self, "Türü Düzenle", "Yeni Ad:", text=old_name)
        
        if ok and new_name:
            if old_name == new_name: return
            
            confirm = QMessageBox.question(self, "Onay", 
                f"'{old_name}' türünü '{new_name}' olarak değiştirmek istediğinize emin misiniz?\n"
                "Bu işlem, bu türe sahip tüm geçmiş kayıtları da güncelleyecektir.",
                QMessageBox.Yes | QMessageBox.No)
                
            if confirm == QMessageBox.Yes:
                self.btn_edit.setEnabled(False)
                self.controller.update_activity_type(old_name, new_name, self.on_edit_finished)

    def on_edit_finished(self, result):
        self.btn_edit.setEnabled(True)
        success, msg = result
        if success:
            self.refresh_types()
            if self.window().statusBar():
                 self.window().statusBar().showMessage(f"✅ {msg}", 3000)
        else:
            QMessageBox.warning(self, "Hata", msg)

    def delete_type(self):
        current_item = self.type_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir tür seçin.")
            return

        name = current_item.text()
        confirm = QMessageBox.question(self, "Onay", 
            f"'{name}' türünü listeden silmek istediğinize emin misiniz?\n"
            "Not: Bu türe ait geçmiş kayıtlar silinmez, sadece yeni ekleme listesinden kalkar.",
            QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.btn_delete.setEnabled(False)
            self.controller.delete_activity_type(name, self.on_delete_finished)

    def on_delete_finished(self, result):
        self.btn_delete.setEnabled(True)
        success, msg = result
        if success:
            self.refresh_types()
            if self.window().statusBar():
                 self.window().statusBar().showMessage(f"🗑️ {msg}", 3000)
        else:
            QMessageBox.warning(self, "Hata", msg)
