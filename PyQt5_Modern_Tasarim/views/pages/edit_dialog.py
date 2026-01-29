# views/pages/edit_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QFormLayout, QDateEdit, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import QDate, Qt

class EditDialog(QDialog):
    def __init__(self, controller, activity, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.activity = activity # Düzenlenecek aktivite nesnesi
        self.setWindowTitle(f"Düzenle: {activity.name}")
        self.setFixedSize(400, 500)
        self.init_ui()
        self.load_types() # Türleri yükle
        # self.load_data() # Bunu load_types bittikten sonra çağırmalıyız ki combo dolu olsun

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

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Başlık
        title = QLabel("Faaliyet Düzenle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        
        # Tür
        self.combo_type = QComboBox()
        # self.combo_type.addItems(FAALIYET_TURLERI) # Artık dinamik
        form_layout.addRow("Tür:", self.combo_type)

        # Ad
        self.input_name = QLineEdit()
        form_layout.addRow("Ad:", self.input_name)

        # Tarih
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("yyyy-MM-dd") # Formatı güncelledik
        self.input_date.setMinimumHeight(35)
        
        self.chk_range = QCheckBox("Bitiş Tarihi")
        self.chk_range.toggled.connect(self.on_range_toggled)
        
        date_layout.addWidget(self.input_date)
        date_layout.addWidget(self.chk_range)
        
        form_layout.addRow("Tarih:", date_layout)
        
        # Bitiş Tarihi (Gizli)
        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setDisplayFormat("yyyy-MM-dd")
        self.input_end_date.setMinimumHeight(35)
        
        self.lbl_end_date = QLabel("Bitiş:")
        
        form_layout.addRow(self.lbl_end_date, self.input_end_date)
        
        # Gizle
        self.lbl_end_date.hide()
        self.input_end_date.hide()

        # Yorum
        self.input_comment = QTextEdit()
        self.input_comment.setMaximumHeight(80)
        form_layout.addRow("Yorum:", self.input_comment)

        # Puan
        self.combo_rating = QComboBox()
        self.combo_rating.addItem("Seçiniz")
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        form_layout.addRow("Puan:", self.combo_rating)

        layout.addLayout(form_layout)

        # Butonlar
        self.btn_save = QPushButton("Değişiklikleri Kaydet")
        self.btn_save.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        self.btn_save.clicked.connect(self.handle_update)
        layout.addWidget(self.btn_save)

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject) # Pencereyi kapatır
        layout.addWidget(btn_cancel)

    def load_data(self):
        """Mevcut aktivite verilerini form alanlarına doldurur."""
        # Türü seç
        index = self.combo_type.findText(self.activity.type)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)
        
        # Adı yaz
        self.input_name.setText(self.activity.name)
        
        # Tarihi ayarla
        try:
            # Önce tam tarih denemesi
            if len(self.activity.date.split('-')) == 3:
                 qdate = QDate.fromString(self.activity.date, "yyyy-MM-dd")
            else:
                 qdate = QDate.fromString(self.activity.date, "yyyy-MM")
            
            if qdate.isValid():
                self.input_date.setDate(qdate)
            else:
                self.input_date.setDate(QDate.currentDate())
        except:
            self.input_date.setDate(QDate.currentDate())
            
        # Bitiş tarihi varsa ayarla
        if hasattr(self.activity, 'end_date') and self.activity.end_date:
            self.chk_range.setChecked(True)
            try:
                qend = QDate.fromString(self.activity.end_date, "yyyy-MM-dd")
                if qend.isValid():
                    self.input_end_date.setDate(qend)
            except:
                pass
        else:
            self.chk_range.setChecked(False)

        # Yorumu yaz
        self.input_comment.setText(self.activity.comment)

        # Puanı seç
        if self.activity.rating and self.activity.rating > 0:
            self.combo_rating.setCurrentText(str(self.activity.rating))
        else:
            self.combo_rating.setCurrentIndex(0)

    def on_range_toggled(self, checked):
        if checked:
            self.lbl_end_date.show()
            self.input_end_date.show()
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
        
        success, message = result

        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.accept() # Dialogu onayla ve kapat
        else:
            QMessageBox.warning(self, "Hata", message)