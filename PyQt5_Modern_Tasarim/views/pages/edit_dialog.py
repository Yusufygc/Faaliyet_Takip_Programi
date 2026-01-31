# views/pages/edit_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QDateEdit, QCheckBox, QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QCursor
from views.styles import COLORS

class EditDialog(QDialog):
    def __init__(self, controller, activity, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.activity = activity # Düzenlenecek aktivite nesnesi
        
        self.setWindowTitle(f"Düzenle: {activity.name}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(450, 650) # Boyutu biraz artırdık ferahlık için
        
        # Arka plan rengi
        self.setStyleSheet(f"background-color: #FFFFFF;")
        
        self.init_ui()
        self.load_types() # Türleri yükle

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # ─── Başlık ───
        lbl_head = QLabel("Faaliyet Düzenle")
        lbl_head.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {COLORS['text']}; margin-bottom: 10px;")
        layout.addWidget(lbl_head)

        # ─── 1. Tür Seçimi ───
        layout.addWidget(self._create_label("TÜR"))
        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet(self._get_combo_style())
        layout.addWidget(self.combo_type)

        # ─── 2. Ad (Başlık) ───
        layout.addWidget(self._create_label("BAŞLIK / AD"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Faaliyet adını girin...")
        self.input_name.setStyleSheet(self._get_input_style())
        layout.addWidget(self.input_name)

        # ─── 3. Tarih Alanı ───
        layout.addWidget(self._create_label("TARİH"))
        
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("yyyy-MM-dd")
        self.input_date.setStyleSheet(self._get_date_style())
        self.input_date.setFixedHeight(40)
        date_layout.addWidget(self.input_date)
        
        # Bitiş Tarihi Checkbox
        self.chk_range = QCheckBox("Bitiş Tarihi")
        self.chk_range.setCursor(Qt.PointingHandCursor)
        self.chk_range.setStyleSheet(f"""
            QCheckBox {{ spacing: 8px; font-size: 14px; color: {COLORS['text']}; font-weight: 600; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid #BDC3C7; }}
            QCheckBox::indicator:checked {{ background-color: {COLORS['primary']}; border-color: {COLORS['primary']}; }}
        """)
        self.chk_range.toggled.connect(self.toggle_end_date)
        date_layout.addWidget(self.chk_range)
        
        layout.addLayout(date_layout)

        # ─── 4. Bitiş Tarihi (Gizli) ───
        self.lbl_end_date = self._create_label("BİTİŞ TARİHİ")
        self.lbl_end_date.hide()
        layout.addWidget(self.lbl_end_date)

        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setDisplayFormat("yyyy-MM-dd")
        self.input_end_date.setStyleSheet(self._get_date_style())
        self.input_end_date.setFixedHeight(40)
        self.input_end_date.hide()
        layout.addWidget(self.input_end_date)

        # ─── 5. Yorum ───
        layout.addWidget(self._create_label("YORUM / AÇIKLAMA"))
        self.input_comment = QTextEdit()
        self.input_comment.setPlaceholderText("Detayları buraya yazabilirsiniz...")
        self.input_comment.setStyleSheet(self._get_input_style())
        self.input_comment.setMinimumHeight(80)
        layout.addWidget(self.input_comment)

        # ─── 6. Puan ───
        layout.addWidget(self._create_label("PUAN (1-10)"))
        self.combo_rating = QComboBox()
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        self.combo_rating.setStyleSheet(self._get_combo_style())
        layout.addWidget(self.combo_rating)

        layout.addStretch()

        # ─── Butonlar ───
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setFixedHeight(45)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #7F8C8D;
                border: 2px solid #E0E6ED;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #F8F9F9;
                color: {COLORS['text']};
                border-color: #BDC3C7;
            }}
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Değişiklikleri Kaydet")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: #BDC3C7;
            }}
        """)
        self.btn_save.clicked.connect(self.handle_update)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    # ─── Yardımcı Stil Metodları ───
    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 12px; 
            font-weight: 800; 
            color: #95A5A6; 
            margin-top: 5px;
            letter-spacing: 0.5px;
        """)
        return lbl

    def _get_input_style(self):
        return f"""
            QLineEdit, QTextEdit {{
                background-color: #FAFAFA;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
                padding: 10px 12px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                background-color: #FFFFFF;
                border: 2px solid {COLORS['primary']};
            }}
        """

    def _get_combo_style(self):
        return f"""
            QComboBox {{
                background-color: #FAFAFA;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QComboBox:hover {{ background-color: #FFFFFF; border-color: #BDC3C7; }}
            QComboBox:focus {{ border: 2px solid {COLORS['primary']}; }}
            QComboBox::drop-down {{ width: 25px; border: none; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #95A5A6;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white; border: 1px solid #E0E6ED; border-radius: 8px; padding: 5px;
            }}
            QComboBox QAbstractItemView::item {{ height: 35px; padding-left: 10px; }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']}1A; color: {COLORS['primary']};
            }}
        """

    def _get_date_style(self):
        return f"""
            QDateEdit {{
                background-color: #FAFAFA;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QDateEdit::drop-down {{ width: 25px; border: none; }}
            QDateEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #95A5A6;
                margin-right: 10px;
            }}
            QDateEdit:focus {{ border: 2px solid {COLORS['primary']}; background-color: white; }}
        """

    # ─── Mantıksal Fonksiyonlar (Aynen Korundu) ───
    def load_types(self):
        """Veritabanından türleri çeker."""
        if hasattr(self.controller, 'get_all_activity_types'):
            self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        self.combo_type.clear()
        if types:
            self.combo_type.addItems(types)
        
        # Türler yüklendikten sonra veriyi doldur
        self.load_data()

    def load_data(self):
        """Aktivite verilerini alanlara doldurur."""
        # 1. Tür
        index = self.combo_type.findText(self.activity.type)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)
        
        # 2. Ad
        self.input_name.setText(self.activity.name)
        
        # 3. Tarih
        try:
            date_obj = QDate.fromString(self.activity.date, "yyyy-MM-dd")
            self.input_date.setDate(date_obj)
        except:
            self.input_date.setDate(QDate.currentDate())

        # 4. Bitiş Tarihi
        if self.activity.end_date:
            self.chk_range.setChecked(True)
            try:
                end_date_obj = QDate.fromString(self.activity.end_date, "yyyy-MM-dd")
                self.input_end_date.setDate(end_date_obj)
            except:
                pass
        else:
            self.chk_range.setChecked(False)
            self.lbl_end_date.hide()
            self.input_end_date.hide()

        # 5. Yorum
        self.input_comment.setText(self.activity.comment)
        
        # 6. Puan
        rating_index = self.combo_rating.findText(str(self.activity.rating))
        if rating_index >= 0:
            self.combo_rating.setCurrentIndex(rating_index)

    def toggle_end_date(self, checked):
        if checked:
            self.lbl_end_date.show()
            self.input_end_date.show()
            # Varsayılan olarak başlangıç tarihinden 1 gün sonrasını ayarla
            if self.input_end_date.date() <= self.input_date.date():
                self.input_end_date.setDate(self.input_date.date().addDays(1))
        else:
            self.lbl_end_date.hide()
            self.input_end_date.hide()

    def handle_update(self):
        """Güncelleme işlemini tetikler."""
        type_val = self.combo_type.currentText()
        name_val = self.input_name.text()
        date_val = self.input_date.date().toString("yyyy-MM-dd")
        
        end_date_val = None
        if self.chk_range.isChecked():
            end_date_val = self.input_end_date.date().toString("yyyy-MM-dd")
            
        comment_val = self.input_comment.toPlainText()
        rating_val = self.combo_rating.currentText()

        # Butonu deaktif et
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Kaydediliyor...")

        # Controller'a güncelleme isteği gönder
        self.controller.update_activity(
            self.activity.id, 
            type_val, name_val, date_val, comment_val, rating_val,
            self.on_update_finished,
            original_activity=self.activity,
            end_date=end_date_val
        )

    def on_update_finished(self, result):
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Değişiklikleri Kaydet")
        
        success, msg = result
        if success:
            self.accept() # Pencereyi kapat ve 'Accepted' dön
        else:
            QMessageBox.warning(self, "Hata", f"Güncelleme başarısız: {msg}")