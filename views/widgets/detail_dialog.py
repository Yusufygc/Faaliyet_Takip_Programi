# views/widgets/detail_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt


class DetailDialog(QDialog):
    def __init__(self, title, details_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #F1F5F9;
                padding: 0px;
                margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_head = QLabel(title)
        lbl_head.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(lbl_head)

        list_widget = QListWidget()
        layout.addWidget(list_widget)

        if details_list:
            for item in details_list:
                widget = QWidget()
                widget_layout = QVBoxLayout(widget)
                widget_layout.setContentsMargins(10, 10, 10, 10)
                widget_layout.setSpacing(5)

                lbl_name = QLabel(f"📌 {item[0]}")
                lbl_name.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155; background: transparent;")
                lbl_name.setWordWrap(True)

                lbl_date = QLabel(f"📅 {item[1]}")
                lbl_date.setStyleSheet("font-size: 12px; color: #64748B; background: transparent;")

                widget_layout.addWidget(lbl_name)
                widget_layout.addWidget(lbl_date)

                list_item = QListWidgetItem(list_widget)
                list_item.setSizeHint(widget.sizeHint())
                list_widget.addItem(list_item)
                list_widget.setItemWidget(list_item, widget)
        else:
            item = QListWidgetItem("Kayıt bulunamadı.")
            item.setTextAlignment(Qt.AlignCenter)
            list_widget.addItem(item)
