# views/pages/settings_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QLineEdit, QMessageBox,
                             QInputDialog, QFrame, QGraphicsDropShadowEffect,
                             QListWidgetItem, QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from services.icon_service import IconService

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
        title = IconService.title_widget(
            "nav_settings", "Ayarlar",
            style="font-size: 26px; font-weight: bold; color: #2C3E50; padding-bottom: 5px; background: transparent;",
            icon_size=28
        )
        main_layout.addWidget(title)
        
        # --- Kartlar Alanı ---
        # Grid Layout Kullanımı
        cards_layout = QGridLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 3 sütun için esneklik ayarları (Eşit genişlik)
        cards_layout.setColumnStretch(0, 1)
        cards_layout.setColumnStretch(1, 1)        
        cards_layout.setColumnStretch(2, 1)

        # --- API Konfigürasyon Kartı (0,0) ---
        self.api_card = self._create_api_stats_card()
        cards_layout.addWidget(self.api_card, 0, 0)

        # --- Faaliyet Türleri Yönetimi Kartı (0,1) ---
        self.card = self._create_activity_types_card()
        cards_layout.addWidget(self.card, 0, 1)
        
        # (0,2) şu an boş kalacak
        
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        # İlk veri yükleme
        self.refresh_types()
        self.load_api_keys()

    def _create_activity_types_card(self):
        """Faaliyet türleri yönetimi için kart oluşturur."""
        card = QFrame()
        card.setObjectName("card")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 15, 18, 15)
        card_layout.setSpacing(10)

        sub_title = IconService.title_widget(
            "tasks", "Faaliyet Türleri",
            style="font-size: 18px; font-weight: bold; color: #34495E; border: none; background: transparent;",
            icon_size=20
        )
        card_layout.addWidget(sub_title)

        desc = QLabel("Türleri ekleyin, düzenleyin veya silin.")
        desc.setStyleSheet("color: #95A5A6; font-size: 14px; border: none;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        card_layout.addLayout(self._build_types_search())
        card_layout.addLayout(self._build_types_content())

        return card

    def _build_types_search(self):
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        search_icon = QLabel()
        search_icon.setPixmap(IconService.pixmap("search", 16))
        search_icon.setStyleSheet("border: none;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tür ara...")
        self.search_input.textChanged.connect(self.filter_types)
        search_layout.addWidget(self.search_input)
        return search_layout

    def _build_types_content(self):
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        content_layout.addLayout(self._build_types_list_area(), 1)
        content_layout.addLayout(self._build_types_action_buttons())
        return content_layout

    def _build_types_list_area(self):
        list_container = QVBoxLayout()
        list_container.setSpacing(6)

        self.type_list = QListWidget()
        self.type_list.setMinimumHeight(self.MIN_LIST_HEIGHT)
        self.type_list.setMaximumHeight(self.MAX_LIST_HEIGHT)
        list_container.addWidget(self.type_list)

        self.pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(self.pagination_frame)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(5)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setObjectName("btn_nav")
        self.btn_prev.setFixedSize(36, 36)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.btn_prev)

        self.page_label = QLabel("1/1")
        self.page_label.setStyleSheet("font-size: 13px; color: #7F8C8D; border: none;")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(50)
        pagination_layout.addWidget(self.page_label)

        self.btn_next = QPushButton("▶")
        self.btn_next.setObjectName("btn_nav")
        self.btn_next.setFixedSize(36, 36)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.btn_next)

        pagination_layout.addStretch()

        self.total_label = QLabel("0 tür")
        self.total_label.setStyleSheet("font-size: 13px; color: #95A5A6; border: none;")
        pagination_layout.addWidget(self.total_label)

        list_container.addWidget(self.pagination_frame)
        return list_container

    def _build_types_action_buttons(self):
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignTop)
        btn_layout.setSpacing(8)

        self.btn_add = self.create_btn("Ekle", "btn_success", self.add_type, "add")
        self.btn_edit = self.create_btn("Düzenle", "btn_warning", self.edit_type, "edit")
        self.btn_delete = self.create_btn("Sil", "btn_danger", self.delete_type, "delete")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        return btn_layout

    def _create_api_stats_card(self):
        """API Anahtarları yönetimi için kart oluşturur."""
        card = QFrame()
        card.setObjectName("card")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)
        
        # Başlık ve Açıklama
        header = IconService.title_widget(
            "key", "API Yapılandırması",
            style="font-size: 18px; font-weight: bold; color: #34495E; border: none; background: transparent;",
            icon_size=20
        )
        layout.addWidget(header)
        
        desc = QLabel("Keşfet sayfası ve öneri sistemi için gerekli API anahtarlarını buradan yönetebilirsiniz. (Değişikliklerin etkili olması için uygulamayı yeniden başlatmanız önerilir.)")
        desc.setStyleSheet("color: #95A5A6; font-size: 13px; border: none;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        
        # TMDB
        tmdb_lbl = QLabel("TMDB API Key (Film/Dizi):")
        tmdb_lbl.setStyleSheet("font-weight: bold; color: #555;")
        self.txt_tmdb = QLineEdit()
        self.txt_tmdb.setPlaceholderText("TMDB API Anahtarını giriniz...")
        self.txt_tmdb.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(tmdb_lbl)
        form_layout.addWidget(self.txt_tmdb)
        
        # RAWG
        rawg_lbl = QLabel("RAWG API Key (Oyun):")
        rawg_lbl.setStyleSheet("font-weight: bold; color: #555;")
        self.txt_rawg = QLineEdit()
        self.txt_rawg.setPlaceholderText("RAWG API Anahtarını giriniz...")
        self.txt_rawg.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(rawg_lbl)
        form_layout.addWidget(self.txt_rawg)
        
        # Kaydet Butonu
        btn_save = QPushButton("Kaydet")
        btn_save.setIcon(IconService.get("save"))
        btn_save.setIconSize(QSize(16, 16))
        btn_save.setObjectName("btn_primary")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedWidth(120)
        btn_save.clicked.connect(self.save_api_keys)
        
        layout.addLayout(form_layout)
        layout.addWidget(btn_save, 0, Qt.AlignRight)
        
        return card

    def load_api_keys(self):
        """API anahtarlarını yükler."""
        self.controller.get_api_keys(self.on_keys_loaded)

    def on_keys_loaded(self, keys):
        if keys:
            from constants import KEYRING_KEY_TMDB, KEYRING_KEY_RAWG
            self.txt_tmdb.setText(keys.get(KEYRING_KEY_TMDB, ""))
            self.txt_rawg.setText(keys.get(KEYRING_KEY_RAWG, ""))

    def save_api_keys(self):
        """API anahtarlarını kaydeder."""
        tmdb = self.txt_tmdb.text()
        rawg = self.txt_rawg.text()
        self.controller.save_api_keys(tmdb, rawg, self.on_save_keys_finished)

    def on_save_keys_finished(self, result):
        success, msg = result
        if success:
            if self.window().statusBar():
                self.window().statusBar().showMessage(msg, 3000)
            
            # Label'ları (Input alanlarını) temizle
            self.txt_tmdb.clear()
            self.txt_rawg.clear()
            
            QMessageBox.information(self, "Bilgi", "Ayarlar kaydedildi.\nDeğişikliklerin tam olarak yansıması için uygulamayı yeniden başlatmanız gerekebilir.")
        else:
            QMessageBox.warning(self, "Hata", msg)

    def create_btn(self, text, style_name, func, icon_name=None):
        btn = QPushButton(text)
        if icon_name:
            btn.setIcon(IconService.get(icon_name, "#FFFFFF"))
            btn.setIconSize(QSize(16, 16))
        btn.setObjectName(style_name)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(func)
        btn.setFixedWidth(120)
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
                self.window().statusBar().showMessage(msg, 3000)
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
                 self.window().statusBar().showMessage(msg, 3000)
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
                 self.window().statusBar().showMessage(msg, 3000)
        else:
            QMessageBox.warning(self, "Hata", msg)
