# views/widgets/folder_widget.py
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QScrollArea, QPushButton,
                             QMenu, QAction, QInputDialog, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from services.icon_service import IconService


class FolderWidget(QWidget):
    folder_selected = pyqtSignal(object)  # None for all, int for folder_id
    folder_added = pyqtSignal(str)
    folder_renamed = pyqtSignal(int, str)
    folder_deleted = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folders = []
        self.selected_folder_id = None
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.setSpacing(10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(60)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:horizontal { height: 0px; }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.chip_layout = QHBoxLayout(self.container)
        self.chip_layout.setContentsMargins(0, 5, 0, 5)
        self.chip_layout.setSpacing(10)
        self.chip_layout.setAlignment(Qt.AlignLeft)

        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def set_folders(self, folders):
        self.folders = folders
        self.refresh_chips()

    def refresh_chips(self):
        while self.chip_layout.count():
            item = self.chip_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        btn_all = self._create_chip("Genel", None, self.selected_folder_id is None, "folder_open")
        self.chip_layout.addWidget(btn_all)

        for folder in self.folders:
            is_selected = (self.selected_folder_id == folder.id)
            btn = self._create_chip(folder.name, folder.id, is_selected, "folder")
            self.chip_layout.addWidget(btn)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(36, 36)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setToolTip("Yeni Klasör Ekle")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #E8F6F3;
                color: #3B82F6;
                border: 1px dashed #3B82F6;
                border-radius: 18px;
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 3px;
            }
            QPushButton:hover {
                background-color: #3B82F620;
            }
        """)
        btn_add.clicked.connect(self._on_add_click)
        self.chip_layout.addWidget(btn_add)

        self.chip_layout.addStretch()

    def _create_chip(self, text, folder_id, is_active, icon_name=None):
        btn = QPushButton(f"  {text}")
        if icon_name:
            icon_color = "white" if is_active else "#F59E0B"
            btn.setIcon(IconService.get(icon_name, icon_color))
            btn.setIconSize(QSize(14, 14))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)

        bg = "#3B82F6" if is_active else "white"
        fg = "white" if is_active else "#2C3E50"
        border = "#3B82F6" if is_active else "#E0E6ED"
        weight = "bold" if is_active else "normal"

        hover_bg = "#3B82F6" if is_active else "#F4F6F7"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: 18px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: {weight};
            }}
            QPushButton:hover {{
                border-color: #3B82F6;
                background-color: {hover_bg};
            }}
        """)

        btn.clicked.connect(lambda: self._on_chip_click(folder_id))

        if folder_id is not None:
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos: self._show_context_menu(pos, folder_id, text))

        return btn

    def _on_chip_click(self, folder_id):
        self.selected_folder_id = folder_id
        self.refresh_chips()
        self.folder_selected.emit(folder_id)

    def _on_add_click(self):
        text, ok = QInputDialog.getText(self, "Yeni Klasör", "Klasör Adı:")
        if ok and text:
            self.folder_added.emit(text)

    def _show_context_menu(self, pos, folder_id, current_name):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #E0E6ED; }
            QMenu::item { padding: 8px 20px; }
            QMenu::item:selected { background-color: #F4F7F6; }
        """)

        action_rename = QAction("Yeniden Adlandır", self)
        action_rename.setIcon(IconService.get("edit", "#2980B9"))
        action_delete = QAction("Sil", self)
        action_delete.setIcon(IconService.get("delete"))

        action_rename.triggered.connect(lambda: self._rename_folder(folder_id, current_name))
        action_delete.triggered.connect(lambda: self._delete_folder(folder_id))

        menu.addAction(action_rename)
        menu.addAction(action_delete)

        sender = self.sender()
        menu.exec_(sender.mapToGlobal(pos))

    def _rename_folder(self, folder_id, current_name):
        clean_name = current_name.strip()
        text, ok = QInputDialog.getText(self, "Klasörü Yeniden Adlandır", "Yeni Ad:", QLineEdit.Normal, clean_name)
        if ok and text and text != clean_name:
            self.folder_renamed.emit(folder_id, text)

    def _delete_folder(self, folder_id):
        msg = QMessageBox()
        msg.setWindowTitle("Klasörü Sil")
        msg.setText("Bu klasörü silmek istediğinize emin misiniz?\nİçindeki planlar silinmez, sadece klasörsüz kalır.")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            self.folder_deleted.emit(folder_id)
