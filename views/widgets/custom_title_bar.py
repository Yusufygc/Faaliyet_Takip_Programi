# views/widgets/custom_title_bar.py
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

from services.icon_service import IconService


class CustomTitleBar(QFrame):
    """Sürüklenebilir, özel pencere başlık çubuğu.

    Ana pencereye eklendiğinde standart OS başlık çubuğunun yerini alır.
    Pencereyi sürüklemek, küçültmek, büyütmek ve kapatmak için kontroller içerir.
    """

    HEIGHT = 42

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CustomTitleBar")
        self.setFixedHeight(self.HEIGHT)
        self._drag_pos: QPoint | None = None
        self._is_maximized = False
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("""
            QFrame#CustomTitleBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3D566E, stop:1 #2C3E50);
                border: none;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(10)

        # App icon + title
        icon_lbl = QLabel()
        icon_lbl.setPixmap(IconService.pixmap("app_logo", size=18, color_override="#60A5FA"))
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel("Faaliyet Takip Sistemi")
        title_lbl.setStyleSheet("color: #E2E8F0; background: transparent; font-size: 13px; font-weight: 600; letter-spacing: 0.4px;")
        layout.addWidget(title_lbl)

        layout.addStretch()

        # Window controls
        self._btn_min  = self._make_ctrl("–", "#F59E0B", "#D97706", self._minimize)
        self._btn_max  = self._make_ctrl("□", "#27AE60", "#1E8449", self._toggle_maximize)
        self._btn_close = self._make_ctrl("✕", "#E74C3C", "#C0392B", self._close)

        for btn in (self._btn_min, self._btn_max, self._btn_close):
            layout.addWidget(btn)

    @staticmethod
    def _make_ctrl(label: str, color: str, hover: str, slot) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedSize(28, 28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """)
        btn.clicked.connect(slot)
        return btn

    # ── Window actions ────────────────────────────────────────────────────────

    def _close(self):
        win = self.window()
        if win:
            win.close()

    def _minimize(self):
        win = self.window()
        if win:
            win.showMinimized()

    def _toggle_maximize(self):
        win = self.window()
        if not win:
            return
        if self._is_maximized:
            win.showNormal()
            self._btn_max.setText("□")
            self._is_maximized = False
        else:
            win.showMaximized()
            self._btn_max.setText("❐")
            self._is_maximized = True

    # ── Drag ──────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            win = self.window()
            if win and not self._is_maximized:
                win.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_maximize()
