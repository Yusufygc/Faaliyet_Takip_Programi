# views/pages/edit_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QComboBox, QPushButton, QMessageBox, 
                             QFormLayout, QDateEdit, QCheckBox, QHBoxLayout, QFrame)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont

class EditDialog(QDialog):
    def __init__(self, controller, activity, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.activity = activity 
        self.setWindowTitle(f"Düzenle: {activity.name}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # İçerik genişlediği için boyutu artırdık
        self.setFixedSize(500, 650)
        
        # Modern Arka Plan
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)
        
        self.init_ui()
        self.load_types()

    def load_types(self):
        if hasattr(self.controller, 'get_all_activity_types'):
            self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        self.combo_type.clear()
        if types:
            self.combo_type.addItems(types)
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # --- Başlık ---
        title = QLabel("Faaliyet Düzenle")
        title.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 24px;
            font-weight: bold;
            color: #1E293B;
            margin-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # --- Form Container (Beyaz Kart Görünümü) ---
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        form_layout_container = QVBoxLayout(form_frame)
        form_layout_container.setContentsMargins(20, 25, 20, 25)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Ortak Input Stili
        self.input_style = """
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #334155;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #F8FAFC;
            }
            QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QTextEdit:hover {
                border: 2px solid #CBD5E1;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 30px;
                background-color: transparent;
            }
            QComboBox::down-arrow, QDateEdit::down-arrow {
                image: url(icons/down_arrow.svg);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 4px;
            }
        """

        # Label Stili Helper
        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #475569;")
            return lbl

        # 1. Tür
        self.combo_type = QComboBox()
        self.combo_type.setMinimumHeight(40)
        self.combo_type.setStyleSheet(self.input_style)
        form_layout.addRow(create_label("Tür:"), self.combo_type)

        # 2. Ad
        self.input_name = QLineEdit()
        self.input_name.setMinimumHeight(40)
        self.input_name.setStyleSheet(self.input_style)
        form_layout.addRow(create_label("Ad:"), self.input_name)

        # 3. Tarih
        date_container = QHBoxLayout()
        date_container.setSpacing(10)
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("d MMMM yyyy")
        self.input_date.setMinimumHeight(40)
        self.input_date.setStyleSheet(self.input_style)
        
        self.chk_range = QCheckBox("Bitiş Tarihi")
        self.chk_range.setStyleSheet("""
            QCheckBox {
                color: #475569;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #CBD5E1;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3B82F6;
                border-color: #3B82F6;
                image: url(icons/check.svg);
            }
        """)
        self.chk_range.toggled.connect(self.on_range_toggled)
        
        date_container.addWidget(self.input_date, 60)
        date_container.addWidget(self.chk_range, 40)
        form_layout.addRow(create_label("Tarih:"), date_container)
        
        # 4. Bitiş Tarihi (Başta gizli)
        self.lbl_end_date = create_label("Bitiş:")
        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setDisplayFormat("d MMMM yyyy")
        self.input_end_date.setMinimumHeight(40)
        self.input_end_date.setStyleSheet(self.input_style)
        
        form_layout.addRow(self.lbl_end_date, self.input_end_date)
        self.lbl_end_date.hide()
        self.input_end_date.hide()

        # 5. Yorum
        self.input_comment = QTextEdit()
        self.input_comment.setMinimumHeight(80)
        self.input_comment.setStyleSheet(self.input_style)
        form_layout.addRow(create_label("Yorum:"), self.input_comment)

        # 6. Puan
        self.combo_rating = QComboBox()
        self.combo_rating.setMinimumHeight(40)
        self.combo_rating.addItem("Seçiniz")
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        self.combo_rating.setStyleSheet(self.input_style)
        form_layout.addRow(create_label("Puan:"), self.combo_rating)

        form_layout_container.addLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Alt Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #64748B;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #475569;
            }
        """)
        
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.handle_update)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
                padding-top: 2px;
            }
        """)
        
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(self.btn_save)
        main_layout.addLayout(button_layout)

    def load_data(self):
        index = self.combo_type.findText(self.activity.type)
        if index >= 0: self.combo_type.setCurrentIndex(index)
        
        self.input_name.setText(self.activity.name)
        
        try:
            date_str = self.activity.date
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            if not qdate.isValid():
                qdate = QDate.fromString(date_str, "yyyy-MM")
            self.input_date.setDate(qdate if qdate.isValid() else QDate.currentDate())
        except:
            self.input_date.setDate(QDate.currentDate())
            
        if hasattr(self.activity, 'end_date') and self.activity.end_date:
            self.chk_range.setChecked(True)
            qend = QDate.fromString(self.activity.end_date, "yyyy-MM-dd")
            if qend.isValid(): self.input_end_date.setDate(qend)
        else:
            self.chk_range.setChecked(False)

        self.input_comment.setText(self.activity.comment)
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
        type_val = self.combo_type.currentText()
        name_val = self.input_name.text()
        date_val = self.input_date.date().toString("yyyy-MM-dd")
        
        end_date_val = None
        if self.chk_range.isChecked():
            end_date_val = self.input_end_date.date().toString("yyyy-MM-dd")
            
        comment_val = self.input_comment.toPlainText()
        rating_val = self.combo_rating.currentText()

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Kaydediliyor...")

        self.controller.update_activity(
            self.activity.id, 
            type_val, name_val, date_val, comment_val, rating_val,
            self.on_update_finished,
            original_activity=self.activity,
            end_date=end_date_val
        )

    def on_update_finished(self, result):
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Kaydet")
        success, message = result
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", message)