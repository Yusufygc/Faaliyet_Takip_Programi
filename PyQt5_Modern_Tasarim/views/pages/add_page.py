# views/pages/add_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QDateEdit, QFormLayout, QFrame, QShortcut, QCompleter, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import QDate, Qt, QLocale, QTimer
from PyQt5.QtGui import QKeySequence


class AddPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
        # Klavye Kısayolu: Ctrl+S
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.handle_save)

    def init_ui(self):
        # Ana Layout (Sayfayı ortalamak için)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter) # İçeriği dikeyde ve yatayda ortala

        # --- Form Kartı (Card) ---
        card = QFrame()
        card.setObjectName("Card") # styles.py içindeki #Card stilini kullanır
        
        # Kart boyutu sabit (500x580 px - Mesaj alanı için biraz yükseklik artırıldı)
        card.setFixedSize(500, 580) 
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 20, 30, 30) # Üst boşluk biraz azaltıldı
        card_layout.setSpacing(10)

        # --- YENİ: Başarı Mesajı Alanı (Gizli) ---
        self.lbl_success = QLabel("")
        self.lbl_success.setAlignment(Qt.AlignCenter)
        self.lbl_success.setStyleSheet("""
            background-color: #D1E7DD; 
            color: #0F5132; 
            border: 1px solid #BADBCC; 
            border-radius: 8px;
            font-size: 16px; 
            font-weight: bold;
            padding: 10px;
        """)
        self.lbl_success.hide() # Başlangıçta gizli
        card_layout.addWidget(self.lbl_success)

        # Başlık
        title = QLabel("Yeni Faaliyet Ekle")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50; border: none; margin-top: 5px;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        # Form Elemanları
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        # Etiketleri sağa yasla, dikeyde ortala
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 1. Tür
        self.combo_type = QComboBox()
        self.combo_type.setMinimumHeight(35)
        # Türleri yükle
        self.load_types() 
        form_layout.addRow("<b>Tür:</b>", self.combo_type)

        # 2. Ad
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Örn: Inception")
        self.input_name.setMinimumHeight(35)
        form_layout.addRow("<b>Ad:</b>", self.input_name)
        
        # Otomatik Tamamlamayı Başlat
        self.setup_autocomplete()

        # 3. Tarih (TÜRKÇE AYARLANDI) - Aralık Seçeneği ile
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setLocale(QLocale(QLocale.Turkish, QLocale.Turkey))
        self.input_date.setDisplayFormat("d MMMM yyyy") 
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setMinimumHeight(35)
        
        self.chk_range = QCheckBox("Bitiş Tarihi")
        self.chk_range.toggled.connect(self.on_range_toggled)
        
        date_layout.addWidget(self.input_date)
        date_layout.addWidget(self.chk_range)
        
        form_layout.addRow("<b>Tarih:</b>", date_layout)
        
        # 3.1 Bitiş Tarihi (Başlangıçta Gizli)
        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setLocale(QLocale(QLocale.Turkish, QLocale.Turkey))
        self.input_end_date.setDisplayFormat("d MMMM yyyy") 
        self.input_end_date.setDate(QDate.currentDate().addDays(1))
        self.input_end_date.setMinimumHeight(35)
        
        # Label ve widget'ı saklamak için referansları tutuyoruz
        self.lbl_end_date = QLabel("<b>Bitiş:</b>")
        self.lbl_end_date.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Form layout'a ekle ama gizle
        form_layout.addRow(self.lbl_end_date, self.input_end_date)
        
        # İlk başta gizle
        self.lbl_end_date.hide()
        self.input_end_date.hide()

        # 4. Yorum
        self.input_comment = QTextEdit()
        self.input_comment.setMaximumHeight(80)
        self.input_comment.setPlaceholderText("Düşünceleriniz...")
        form_layout.addRow("<b>Yorum:</b>", self.input_comment)

        # 5. Puan
        self.combo_rating = QComboBox()
        self.combo_rating.addItem("Seçiniz")
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        self.combo_rating.setMinimumHeight(35)
        form_layout.addRow("<b>Puan:</b>", self.combo_rating)

        card_layout.addLayout(form_layout)

        # Kaydet Butonu
        card_layout.addSpacing(45)

        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setObjectName("SuccessBtn") # Yeşil buton stili
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setFixedWidth(220)
        self.btn_save.clicked.connect(self.handle_save)
        card_layout.addWidget(self.btn_save, 0, Qt.AlignCenter)
        
        # Kartın içinde altta boşluk kalırsa doldur
        card_layout.addStretch()

        main_layout.addWidget(card)

    def setup_autocomplete(self):
        """Veritabanından isimleri çekip otomatik tamamlayıcıya yükler."""
        if hasattr(self.controller, 'get_all_activity_names'):
            self.controller.get_all_activity_names(self.on_names_loaded)

    def on_names_loaded(self, names_list):
        if names_list:
            self.completer = QCompleter(names_list)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)
            self.input_name.setCompleter(self.completer)

    def on_range_toggled(self, checked):
        """Bitiş tarihi alanını göster/gizle."""
        if checked:
            self.lbl_end_date.show()
            self.input_end_date.show()
            # Bitiş tarihini başlangıçtan sonraya ayarla (eğer gerideyse)
            if self.input_end_date.date() <= self.input_date.date():
                self.input_end_date.setDate(self.input_date.date().addDays(1))
        else:
            self.lbl_end_date.hide()
            self.input_end_date.hide()

    def handle_save(self):
        """Kaydetme işlemi."""
        type_val = self.combo_type.currentText()
        name_val = self.input_name.text()
        date_val = self.input_date.date().toString("yyyy-MM-dd") # YYYY-MM-DD formatında tam tarih
        
        end_date_val = None
        if self.chk_range.isChecked():
            end_date_val = self.input_end_date.date().toString("yyyy-MM-dd")
            
        comment_val = self.input_comment.toPlainText()
        rating_val = self.combo_rating.currentText()

        # Butonu deaktif et
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Kaydediliyor...")

        self.controller.add_activity(
            type_val, name_val, date_val, comment_val, rating_val,
            self.on_save_finished,
            end_date=end_date_val
        )

    def on_save_finished(self, result):
        self.btn_save.setEnabled(True)
        self.btn_save.setText("💾 Kaydet (Ctrl+S)")
        
        # Validasyon hatası veya başarılı işlem
        success, message = result

        if success:
            # 1. Başarı Mesajını Göster
            self.show_success_message(f"✔ {message}")
            
            # 2. Status Bar'a da yaz (İsteğe bağlı)
            # 2. Status Bar'a da yaz (İsteğe bağlı)
            window = self.window()
            if window and hasattr(window, 'statusBar') and window.statusBar():
                window.statusBar().showMessage(f"✅ {message}", 3000)
                
            self.clear_inputs()
            self.setup_autocomplete() 
        else:
            QMessageBox.warning(self, "Hata", message)

    def show_success_message(self, message):
        """Başarı mesajını kartın tepesinde gösterir ve sonra gizler."""
        self.lbl_success.setText(message)
        self.lbl_success.show()
        
        # 2.5 saniye (2500 ms) sonra mesajı gizle
        QTimer.singleShot(2500, self.lbl_success.hide)

    def clear_inputs(self):
        """Formu temizler."""
        self.input_name.clear()
        self.input_comment.clear()
        self.combo_rating.setCurrentIndex(0)
        self.combo_type.setCurrentIndex(0)
    def clear_inputs(self):
        """Formu temizler."""
        self.input_name.clear()
        self.input_comment.clear()
        self.combo_rating.setCurrentIndex(0)
        self.combo_type.setCurrentIndex(0)
        self.input_date.setDate(QDate.currentDate())
        self.chk_range.setChecked(False)
        self.input_end_date.setDate(QDate.currentDate().addDays(1))

    def load_types(self):
        """Veritabanından türleri çeker."""
        if hasattr(self.controller, 'get_all_activity_types'):
            self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        current_text = self.combo_type.currentText()
        self.combo_type.clear()
        if types:
            self.combo_type.addItems(types)
        
        # Eğer eski seçili metin hala varsa onu seç
        index = self.combo_type.findText(current_text)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)
        elif self.combo_type.count() > 0:
            self.combo_type.setCurrentIndex(0)

    def refresh_data(self):
        """Sayfa her görüntülendiğinde verileri (özellikle türleri) yenile"""
        self.load_types()
        self.setup_autocomplete()