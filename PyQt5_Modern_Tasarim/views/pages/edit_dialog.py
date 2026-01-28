# views/pages/edit_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QFormLayout, QDateEdit)
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
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("yyyy-MM")
        form_layout.addRow("Tarih:", self.input_date)

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
        
        # Tarihi ayarla (String -> QDate çevrimi)
        try:
            # activity.date formatı: "YYYY-MM"
            qdate = QDate.fromString(self.activity.date, "yyyy-MM")
            self.input_date.setDate(qdate)
        except:
            self.input_date.setDate(QDate.currentDate())

        # Yorumu yaz
        self.input_comment.setText(self.activity.comment)

        # Puanı seç
        if self.activity.rating and self.activity.rating > 0:
            self.combo_rating.setCurrentText(str(self.activity.rating))
        else:
            self.combo_rating.setCurrentIndex(0)

    def handle_update(self):
        """Güncelleme işlemini tetikler."""
        type_val = self.combo_type.currentText()
        name_val = self.input_name.text()
        date_val = self.input_date.date().toString("yyyy-MM")
        comment_val = self.input_comment.toPlainText()
        rating_val = self.combo_rating.currentText()

        # Butonu deaktif et
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Kaydediliyor...")

        # Controller'a güncelleme isteği gönder
        # self.activity parametresi, değişiklik kontrolü için gönderiliyor
        self.controller.update_activity(
            self.activity.id, 
            type_val, name_val, date_val, comment_val, rating_val,
            self.on_update_finished,
            original_activity=self.activity 
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