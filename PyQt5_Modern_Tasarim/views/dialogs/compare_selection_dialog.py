# views/dialogs/compare_selection_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from views.widgets import MonthYearWidget

class CompareSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Karşılaştırma Dönemlerini Seç")
        self.setFixedSize(500, 350)
        self.selected_dates = (None, None) # (Tarih1, Tarih2)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        title = QLabel("Hangi Dönemleri Karşılaştırmak İstersiniz?")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Seçim Alanları
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(30)

        # Sol Taraf (1. Dönem)
        self.date1_widget = self.create_date_group("1. Dönem (Eski)")
        selection_layout.addWidget(self.date1_widget['frame'])

        # Sağ Taraf (2. Dönem)
        self.date2_widget = self.create_date_group("2. Dönem (Yeni)")
        selection_layout.addWidget(self.date2_widget['frame'])

        layout.addLayout(selection_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedSize(100, 40)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_compare = QPushButton("Karşılaştır")
        btn_compare.setObjectName("PrimaryBtn") # styles.py'daki stil
        btn_compare.setStyleSheet("background-color: #2980B9; color: white; font-weight: bold; border-radius: 5px;")
        btn_compare.setFixedSize(120, 40)
        btn_compare.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_compare)

        layout.addLayout(btn_layout)

    def create_date_group(self, title):
        """Tarih seçim grubu oluşturur."""
        frame = QFrame()
        frame.setStyleSheet("background-color: #ECF0F1; border-radius: 8px;")
        layout = QVBoxLayout(frame)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: bold; color: #7F8C8D; margin-bottom: 5px;")
        lbl.setAlignment(Qt.AlignCenter)
        
        picker = MonthYearWidget()
        
        layout.addWidget(lbl)
        layout.addWidget(picker)
        
        return {'frame': frame, 'picker': picker}

    def validate_and_accept(self):
        date1 = self.date1_widget['picker'].get_date_str()
        date2 = self.date2_widget['picker'].get_date_str()

        if not date1 or not date2:
            QMessageBox.warning(self, "Eksik Seçim", "Lütfen her iki dönemi de seçiniz.")
            return

        if date1 == date2:
            QMessageBox.warning(self, "Aynı Tarih", "Karşılaştırma yapmak için farklı tarihler seçmelisiniz.")
            return

        # Tarihleri (Küçük, Büyük) şeklinde sırala ki mantıklı olsun
        # Ancak kullanıcı özel bir sıra istiyorsa dokunmayadabiliriz.
        # Biz kullanıcının seçtiği sırayı koruyalım (Sol vs Sağ).
        
        self.selected_dates = (date1, date2)
        self.accept()

    def get_dates(self):
        return self.selected_dates