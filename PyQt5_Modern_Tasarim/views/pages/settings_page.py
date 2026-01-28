# views/pages/settings_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QLineEdit, QMessageBox, 
                             QInputDialog, QFrame)
from PyQt5.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        title = QLabel("⚙️ Ayarlar")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        main_layout.addWidget(title)

        # --- Faaliyet Türleri Yönetimi Kartı ---
        card = QFrame()
        card.setObjectName("Card") # styles.py
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Alt Başlık
        sub_title = QLabel("Faaliyet Türleri Yönetimi")
        sub_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495E;")
        card_layout.addWidget(sub_title)

        # Açıklama
        desc = QLabel("Buradan yeni faaliyet türleri ekleyebilir, mevcutları düzenleyebilir veya silebilirsiniz.\n"
                      "Dikkat: Bir türün adını değiştirdiğinizde, o türe ait tüm geçmiş kayıtlar da güncellenir.")
        desc.setStyleSheet("color: #7F8C8D; font-size: 13px;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        # İçerik Alanı (Liste ve Butonlar)
        content_layout = QHBoxLayout()
        
        # 1. Liste
        self.type_list = QListWidget()
        self.type_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        content_layout.addWidget(self.type_list)

        # 2. İşlem Butonları (Sağ Taraf)
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignTop)
        
        self.btn_add = self.create_btn("➕ Yeni Ekle", "#2ECC71", self.add_type)
        self.btn_edit = self.create_btn("✏️ Düzenle", "#F39C12", self.edit_type)
        self.btn_delete = self.create_btn("🗑️ Sil", "#E74C3C", self.delete_type)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        content_layout.addLayout(btn_layout)
        card_layout.addLayout(content_layout)
        
        main_layout.addWidget(card)
        main_layout.addStretch()

        # İlk veri yükleme
        self.refresh_types()

    def create_btn(self, text, color, func):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(func)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
        """)
        return btn

    def refresh_types(self):
        """Türleri veritabanından çeker ve listeyi yeniler."""
        self.type_list.clear() # Temizle ama asenkron çağrıdan önce değil, callback'te yapılmalı? 
                               # Hayır, clear() senkron. Ama dolana kadar boş görünür.
                               # Loading ekleyebiliriz ama basit tutalım.
        self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        self.type_list.clear()
        if types:
            self.type_list.addItems(types)

    def add_type(self):
        text, ok = QInputDialog.getText(self, "Yeni Tür", "Faaliyet Türü Adı:")
        if ok and text:
            # Asenkron Ekleme
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
