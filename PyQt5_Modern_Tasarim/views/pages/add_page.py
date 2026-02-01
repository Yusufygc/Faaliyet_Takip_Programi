# views/pages/add_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QDateEdit, QFormLayout, QFrame, QShortcut, QCompleter, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import QDate, Qt, QLocale, QTimer
from PyQt5.QtCore import QDate, Qt, QLocale, QTimer
from PyQt5.QtGui import QKeySequence, QFont
from utils import get_resource_path
import os
from ..styles import arrow_url



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
        card.setObjectName("AddCard") # Özel stil için ID
        card.setFixedSize(520, 620) # Biraz daha geniş
        card.setStyleSheet("""
            QFrame#AddCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 16px;
                border: 3px solid #E2E8F0;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 25, 35, 30)
        card_layout.setSpacing(15)

        # --- Başarı Mesajı Alanı ---
        self.lbl_success = QLabel("")
        self.lbl_success.setAlignment(Qt.AlignCenter)
        self.lbl_success.setStyleSheet("""
            QLabel {
                background: linear-gradient(90deg, #D1FAE5, #A7F3D0);
                color: #065F46;
                border: 1px solid #6EE7B7;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px;
                margin-bottom: 10px;
            }
        """)
        self.lbl_success.hide()
        card_layout.addWidget(self.lbl_success)

        # Başlık
        title = QLabel("YENİ FAALİYET EKLE")
        title_font = QFont()
        title_font.setFamily("Segoe UI")
        title_font.setPointSize(100)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1E293B; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Açıklama metni
        desc = QLabel("Faaliyet bilgilerini aşağıdaki formu doldurarak ekleyebilirsiniz")
        desc.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 13px;
                background: transparent;
                border: none;
                margin-bottom: 5px;
            }
        """)
        desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)

        # Form Elemanları
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Form elemanları için genel stil
        input_style = f"""
            QComboBox, QLineEdit, QDateEdit, QTextEdit {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
                selection-background-color: #3B82F6;
                selection-color: white;
            }}
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {{
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }}
            QComboBox:hover, QLineEdit:hover, QDateEdit:hover {{
                border: 2px solid #CBD5E1;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox::down-arrow {{
                image: url('{arrow_url}');
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 15px;
                border-radius: 5px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #F1F5F9;
            }}
        """



        # 1. Tür - Modern Combobox
        self.combo_type = QComboBox()
        self.combo_type.setMinimumHeight(42)
        self.combo_type.setStyleSheet(f"""
            QComboBox {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }}
            QComboBox:focus {{
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }}
            QComboBox:hover {{
                border: 2px solid #CBD5E1;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
                border-left: 1px solid #E2E8F0;
                border-radius: 0 8px 8px 0;
                background-color: #F8FAFC;
            }}
            QComboBox::down-arrow {{
                image: url('{arrow_url}');
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 8px;
                font-size: 14px;
                margin-top: 5px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 12px 15px;
                border-radius: 5px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #F1F5F9;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: #3B82F6;
                color: white;
            }}
        """)

        # Türleri yükle
        self.load_types() 
        form_layout.addRow(self.create_label("Tür:"), self.combo_type)

        # 2. Ad
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Örn: Inception, Breaking Bad, Kitap Adı...")
        self.input_name.setMinimumHeight(42)
        self.input_name.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }
            QLineEdit:hover {
                border: 2px solid #CBD5E1;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
                font-style: italic;
            }
        """)
        form_layout.addRow(self.create_label("Ad:"), self.input_name)
        
        # Otomatik Tamamlamayı Başlat
        self.setup_autocomplete()

        # 3. Tarih - Modern DatePicker
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(10)
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setLocale(QLocale(QLocale.Turkish, QLocale.Turkey))
        self.input_date.setDisplayFormat("d MMMM yyyy") 
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setMinimumHeight(42)
        self.input_date.setStyleSheet(f"""
            QDateEdit {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }}
            QDateEdit:focus {{
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }}
            QDateEdit:hover {{
                border: 2px solid #CBD5E1;
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 40px;
                border-left: 1px solid #E2E8F0;
                border-radius: 0 8px 8px 0;
                background-color: #F8FAFC;
            }}
            QDateEdit::down-arrow {{
                image: url('{arrow_url}');
                width: 16px;
                height: 16px;
            }}
        """)

        
        # Bitiş Tarihi Checkbox - Modern toggle
        self.chk_range = QCheckBox("Bitiş Tarihi")
        # Checkbox Stili
        check_url = get_resource_path("icons/check.svg").replace("\\", "/")
        self.chk_range.setStyleSheet(f"""
            QCheckBox {{
                color: #475569;
                font-weight: 500;
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid #CBD5E1;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: #3B82F6;
                border-color: #3B82F6;
                image: url({check_url});
            }}
            QCheckBox::indicator:hover {{
                border-color: #94A3B8;
            }}
        """)

        self.chk_range.toggled.connect(self.on_range_toggled)
        
        date_layout.addWidget(self.input_date, 70)
        date_layout.addWidget(self.chk_range, 30)
        
        form_layout.addRow(self.create_label("Tarih:"), date_layout)
        
        # 3.1 Bitiş Tarihi
        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setLocale(QLocale(QLocale.Turkish, QLocale.Turkey))
        self.input_end_date.setDisplayFormat("d MMMM yyyy") 
        self.input_end_date.setDate(QDate.currentDate().addDays(1))
        self.input_end_date.setMinimumHeight(42)
        self.input_end_date.setStyleSheet(f"""
            QDateEdit {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }}
            QDateEdit:focus {{
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }}
            QDateEdit:hover {{
                border: 2px solid #CBD5E1;
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 40px;
                border-left: 1px solid #E2E8F0;
                border-radius: 0 8px 8px 0;
                background-color: #F8FAFC;
            }}
            QDateEdit::down-arrow {{
                image: url('{arrow_url}');
                width: 16px;
                height: 16px;
            }}
        """)

        
        # Label ve widget'ı saklamak için referansları tutuyoruz
        self.lbl_end_date = self.create_label("Bitiş:")
        
        # Form layout'a ekle ama gizle
        form_layout.addRow(self.lbl_end_date, self.input_end_date)
        
        # İlk başta gizle
        self.lbl_end_date.hide()
        self.input_end_date.hide()

        # 4. Yorum - Modern TextEdit
        self.input_comment = QTextEdit()
        self.input_comment.setMaximumHeight(100)
        self.input_comment.setPlaceholderText("Düşünceleriniz, notlarınız, izlenimleriniz...")
        self.input_comment.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }
            QTextEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }
            QTextEdit:hover {
                border: 2px solid #CBD5E1;
            }
            QTextEdit::placeholder {
                color: #94A3B8;
                font-style: italic;
            }
        """)
        form_layout.addRow(self.create_label("Yorum:"), self.input_comment)

        # 5. Puan - Star Rating gibi combobox
        self.combo_rating = QComboBox()
        self.combo_rating.addItem("Seçiniz")
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        self.combo_rating.setMinimumHeight(42)
        self.combo_rating.setStyleSheet(f"""
            QComboBox {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #334155;
            }}
            QComboBox:focus {{
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }}
            QComboBox:hover {{
                border: 2px solid #CBD5E1;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
                border-left: 1px solid #E2E8F0;
                border-radius: 0 8px 8px 0;
                background-color: #F8FAFC;
            }}
            QComboBox::down-arrow {{
                image: url('{arrow_url}');
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 15px;
                border-radius: 5px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #FEF3C7;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: linear-gradient(to right, #FBBF24, #F59E0B);
                color: #92400E;
            }}
        """)

        form_layout.addRow(self.create_label("Puan:"), self.combo_rating)

        card_layout.addLayout(form_layout)

        # Kaydet Butonu - Modern gradient button
        card_layout.addSpacing(20)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Temizle butonu
        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setMinimumHeight(48)
        self.btn_clear.setFixedWidth(150)
        self.btn_clear.clicked.connect(self.clear_inputs)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #F1F5F9, stop:1 #E2E8F0);
                color: #475569;
                border-radius: 12px;
                font-weight: 600;
                font-size: 15px;
                border: 2px solid #CBD5E1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #E2E8F0, stop:1 #CBD5E1);
                border: 2px solid #94A3B8;
            }
            QPushButton:pressed {
                background: #CBD5E1;
            }
        """)
        
        # Kaydet butonu
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setMinimumHeight(48)
        self.btn_save.setFixedWidth(200)
        self.btn_save.clicked.connect(self.handle_save)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:pressed {
                background: #1D4ED8;
                padding-top: 2px;
                padding-left: 2px;
            }
            QPushButton:disabled {
                background: #94A3B8;
                color: #CBD5E1;
            }
        """)
        
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_save)
        button_layout.setAlignment(Qt.AlignCenter)
        
        card_layout.addLayout(button_layout)
        
        # Alt bilgi
        footer = QLabel("📌 Tüm alanları doldurup kaydedebilirsiniz")
        footer.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 12px;
                background: transparent;
                border: none;
                margin-top: 15px;
            }
        """)
        footer.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

    def create_label(self, text):
        """Modern form etiketi oluşturur"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #475569;
                font-weight: 600;
                font-size: 14px;
                background: transparent;
                border: none;
                padding-right: 10px;
            }
        """)
        return label

    def setup_autocomplete(self):
        """Veritabanından isimleri çekip otomatik tamamlayıcıya yükler."""
        if hasattr(self.controller, 'get_all_activity_names'):
            self.controller.get_all_activity_names(self.on_names_loaded)

    def on_names_loaded(self, names_list):
        if names_list:
            self.completer = QCompleter(names_list)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)
            self.completer.setMaxVisibleItems(8)
            self.completer.popup().setStyleSheet("""
                QListView {
                    background-color: white;
                    border: 2px solid #E2E8F0;
                    border-radius: 8px;
                    font-size: 14px;
                    padding: 5px;
                }
                QListView::item {
                    padding: 10px 15px;
                    border-radius: 5px;
                }
                QListView::item:hover {
                    background-color: #F1F5F9;
                }
                QListView::item:selected {
                    background-color: #3B82F6;
                    color: white;
                }
            """)
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
        
        # Puan değeri direkt alındı

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
        self.btn_save.setText("Kaydet")
        
        # Validasyon hatası veya başarılı işlem
        success, message = result

        if success:
            # 1. Başarı Mesajını Göster
            self.show_success_message(f"✅ {message}")
            
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
        self.input_date.setDate(QDate.currentDate())
        self.chk_range.setChecked(False)
        self.input_end_date.setDate(QDate.currentDate().addDays(1))
        
        # Focus'u ilk alana getir
        self.input_name.setFocus()

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