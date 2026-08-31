# views/widgets/empty_state.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from services.icon_service import IconService


class EmptyStateWidget(QWidget):
    """Veri yokken ekrana ortalanmış boş durum gösterici."""

    def __init__(
        self,
        icon_name: str = "inbox",
        title: str = "Henüz buralar çok ıssız...",
        description: str = "İlk faaliyetini eklemeye ne dersin?",
        action_text: str = "Yeni Kayıt Ekle",
        action_page_index: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self._action_page = action_page_index
        self._build_ui(icon_name, title, description, action_text)

    def _build_ui(self, icon_name, title, description, action_text):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 60, 40, 60)

        # Icon
        icon_lbl = QLabel()
        pix = IconService.pixmap(icon_name, size=72, color_override="#CBD5E1")
        icon_lbl.setPixmap(pix)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color: #334155; background: transparent;")
        layout.addWidget(title_lbl)

        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 14px; background: transparent;")
        layout.addWidget(desc_lbl)

        layout.addSpacing(8)

        # Action button
        btn = QPushButton(action_text)
        btn.setObjectName("btn_primary")
        btn.setFixedWidth(200)
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._navigate)
        layout.addWidget(btn, 0, Qt.AlignCenter)

    def _navigate(self):
        win = self.window()
        if hasattr(win, "switch_page"):
            win.switch_page(self._action_page)
