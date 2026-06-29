# views/dialogs/edit_dialog.py
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
        self.setFixedSize(500, 650)
        self.init_ui()
        self.load_types()

    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #475569;")
        return lbl

    def load_types(self):
        if hasattr(self.controller, 'get_all_activity_types'):
            self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        self.combo_type.clear()
        if types:
            self.combo_type.addItems(types)
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        self._build_title(layout)
        self._build_form(layout)
        self._build_buttons(layout)

    def _build_title(self, layout):
        title = QLabel("Faaliyet Düzenle")
        title.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 24px; font-weight: bold;
            color: #1E293B; margin-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

    def _build_form(self, layout):
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        container = QVBoxLayout(form_frame)
        container.setContentsMargins(20, 25, 20, 25)

        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.combo_type = QComboBox()
        self.combo_type.setMinimumHeight(40)
        form.addRow(self._create_label("Tür:"), self.combo_type)

        self.input_name = QLineEdit()
        self.input_name.setMinimumHeight(40)
        form.addRow(self._create_label("Ad:"), self.input_name)

        # Tarih + bitiş tarihi checkbox
        date_row = QHBoxLayout()
        date_row.setSpacing(10)

        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("d MMMM yyyy")
        self.input_date.setMinimumHeight(40)

        self.chk_range = QCheckBox("Bitiş Tarihi")
        self.chk_range.setStyleSheet("""
            QCheckBox { color: #475569; font-size: 14px; spacing: 8px; }
            QCheckBox::indicator {
                width: 18px; height: 18px; border-radius: 4px;
                border: 2px solid #CBD5E1; background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3B82F6; border-color: #3B82F6; image: url(icons/check.svg);
            }
        """)
        self.chk_range.toggled.connect(self.on_range_toggled)
        date_row.addWidget(self.input_date, 60)
        date_row.addWidget(self.chk_range, 40)
        form.addRow(self._create_label("Tarih:"), date_row)

        self.lbl_end_date = self._create_label("Bitiş:")
        self.input_end_date = QDateEdit()
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setDisplayFormat("d MMMM yyyy")
        self.input_end_date.setMinimumHeight(40)
        form.addRow(self.lbl_end_date, self.input_end_date)
        self.lbl_end_date.hide()
        self.input_end_date.hide()

        self.input_comment = QTextEdit()
        self.input_comment.setMinimumHeight(80)
        form.addRow(self._create_label("Yorum:"), self.input_comment)

        self.combo_rating = QComboBox()
        self.combo_rating.setMinimumHeight(40)
        self.combo_rating.addItem("Seçiniz")
        self.combo_rating.addItems([str(i) for i in range(1, 11)])
        form.addRow(self._create_label("Puan:"), self.combo_rating)

        container.addLayout(form)
        layout.addWidget(form_frame)

    def _build_buttons(self, layout):
        button_row = QHBoxLayout()
        button_row.setSpacing(15)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.handle_update)

        button_row.addWidget(btn_cancel)
        button_row.addWidget(self.btn_save)
        layout.addLayout(button_row)

    def load_data(self):
        index = self.combo_type.findText(self.activity.type)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)

        self.input_name.setText(self.activity.name)

        try:
            date_str = self.activity.date
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            if not qdate.isValid():
                qdate = QDate.fromString(date_str, "yyyy-MM")
            self.input_date.setDate(qdate if qdate.isValid() else QDate.currentDate())
        except Exception:
            self.input_date.setDate(QDate.currentDate())

        if hasattr(self.activity, 'end_date') and self.activity.end_date:
            self.chk_range.setChecked(True)
            qend = QDate.fromString(self.activity.end_date, "yyyy-MM-dd")
            if qend.isValid():
                self.input_end_date.setDate(qend)
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
        end_date_val = self.input_end_date.date().toString("yyyy-MM-dd") if self.chk_range.isChecked() else None
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
