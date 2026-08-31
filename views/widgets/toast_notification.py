# views/widgets/toast_notification.py
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtGui import QFont

from services.icon_service import IconService

_COLORS = {
    "success": ("#10B981", "check"),
    "error":   ("#EF4444", "error"),
    "warning": ("#F59E0B", "warning"),
    "info":    ("#3B82F6", "edit"),
}


class ToastNotification(QFrame):
    """Sağ alt köşeden kayan, otomatik kapanan bildirim."""

    WIDTH = 340
    MIN_HEIGHT = 60
    MARGIN = 20
    SHOW_MS = 3000
    ANIM_MS = 300

    def __init__(self, parent_window, message: str, level: str = "success"):
        super().__init__(parent_window, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self._parent_win = parent_window
        self._level = level
        self._message = message
        self._slide_anim: QPropertyAnimation | None = None
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._build_ui()
        self.setFixedWidth(self.WIDTH)
        self.adjustSize()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        bg_color, icon_name = _COLORS.get(self._level, _COLORS["info"])

        self.setObjectName("toast_frame")
        self.setStyleSheet(f"""
            QFrame#toast_frame {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(IconService.pixmap(icon_name, size=20, color_override="#FFFFFF"))
        icon_lbl.setFixedSize(20, 20)
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel(self._message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: white; background: transparent; font-size: 13px;")
        font = QFont("Segoe UI", 10)
        msg_lbl.setFont(font)
        layout.addWidget(msg_lbl, 1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet("""
            QPushButton {
                color: rgba(255,255,255,180);
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { color: white; }
        """)
        close_btn.clicked.connect(self._dismiss)
        layout.addWidget(close_btn)

    # ── Animation ─────────────────────────────────────────────────────────────

    def show_toast(self):
        self.adjustSize()
        target = self._target_pos()
        start = QPoint(target.x(), self._parent_win.geometry().bottom())

        self.move(start)
        self.show()
        self.raise_()

        self._slide_anim = QPropertyAnimation(self, b"pos", self)
        self._slide_anim.setDuration(self.ANIM_MS)
        self._slide_anim.setStartValue(start)
        self._slide_anim.setEndValue(target)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.start()

        QTimer.singleShot(self.SHOW_MS, self._fade_out)

    def _target_pos(self) -> QPoint:
        pw = self._parent_win
        pg = pw.geometry()
        x = pg.right() - self.WIDTH - self.MARGIN
        y = pg.bottom() - self.height() - self.MARGIN
        return QPoint(x, y)

    def _fade_out(self):
        anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim.setDuration(self.ANIM_MS)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(self.close)
        anim.start()

    def _dismiss(self):
        if self._slide_anim:
            self._slide_anim.stop()
        self._fade_out()


# ── Module-level helper ────────────────────────────────────────────────────────

def show_toast(message: str, level: str = "success") -> None:
    """Show a toast notification anchored to the active main window."""
    win = QApplication.activeWindow()
    if win is None:
        return
    # Traverse up to top-level window
    while win.parent():
        win = win.parent()
    toast = ToastNotification(win, message, level)
    toast.show_toast()
