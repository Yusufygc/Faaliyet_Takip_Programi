# views/widgets/media_card.py
from __future__ import annotations

from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from views.widgets.modern_card import ModernCard
from views.widgets.async_image import AsyncImage
from models import Activity

_TYPE_COLORS: dict[str, str] = {
    "Film":  "#3B82F6",
    "Dizi":  "#8B5CF6",
    "Oyun":  "#10B981",
    "Kitap": "#F59E0B",
    "Kurs":  "#F97316",
    "Şehir": "#06B6D4",
}
_DEFAULT_COLOR = "#64748B"

CARD_WIDTH   = 200
COVER_HEIGHT = 140


def _darken(hex_color: str, factor: float = 0.7) -> str:
    c = QColor(hex_color)
    return QColor(
        round(c.red()   * factor),
        round(c.green() * factor),
        round(c.blue()  * factor),
    ).name()


class MediaCard(ModernCard):
    """Grid görünümü için aktivite kartı. Çift tıkla edit_requested yayar."""

    edit_requested = pyqtSignal(int)

    def __init__(self, activity: Activity, parent=None):
        super().__init__(parent, card_type="media_card")
        self._activity = activity
        self._color = _TYPE_COLORS.get(activity.type, _DEFAULT_COLOR)
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()
        self._fetch_cover()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_cover())
        root.addWidget(self._make_content())

    def _make_cover(self) -> QFrame:
        self._cover_frame = QFrame()
        self._cover_frame.setObjectName("media_card_cover")
        self._cover_frame.setFixedSize(CARD_WIDTH, COVER_HEIGHT)
        dark = _darken(self._color)
        self._cover_frame.setStyleSheet(f"""
            QFrame#media_card_cover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._color}, stop:1 {dark});
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)
        inner = QVBoxLayout(self._cover_frame)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setAlignment(Qt.AlignCenter)

        self._cover_label = QLabel(self._activity.type[0])
        self._cover_label.setAlignment(Qt.AlignCenter)
        self._cover_label.setStyleSheet("color: rgba(255,255,255,120); font-size: 48px; font-weight: bold; background: transparent;")
        inner.addWidget(self._cover_label)
        return self._cover_frame

    def _make_content(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("media_card_content")
        frame.setStyleSheet("""
            QFrame#media_card_content {
                background: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(4)

        # Type badge
        badge = QLabel(self._activity.type)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(18)
        badge.setMaximumWidth(60)
        badge.setStyleSheet(f"""
            color: white;
            background: {self._color};
            border-radius: 4px;
            padding: 0 6px;
            font-size: 10px;
            font-weight: bold;
        """)
        layout.addWidget(badge)

        # Name
        name_lbl = QLabel(self._activity.name)
        name_lbl.setWordWrap(True)
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color: #1E293B; background: transparent;")
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(name_lbl)

        # Date
        date_text = self._activity.date or ""
        if self._activity.end_date:
            date_text += f" → {self._activity.end_date}"
        if date_text:
            date_lbl = QLabel(date_text)
            date_lbl.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
            layout.addWidget(date_lbl)

        # Rating
        if self._activity.rating:
            rating_lbl = QLabel(f"★ {self._activity.rating}/10")
            rating_lbl.setStyleSheet(
                f"color: {self._color}; font-size: 12px; font-weight: bold; background: transparent;"
            )
            layout.addWidget(rating_lbl)

        layout.addStretch()
        return frame

    # ── Cover fetch ───────────────────────────────────────────────────────────

    def _fetch_cover(self):
        from services.cover_fetch_service import CoverFetchService
        CoverFetchService.get_cover_async(
            self._activity.name, self._activity.type, self._on_cover_url
        )

    def _on_cover_url(self, url: str | None):
        if not url or self._cover_frame is None:
            return
        # Swap placeholder label for AsyncImage
        inner = self._cover_frame.layout()
        while inner.count():
            item = inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        img = AsyncImage(url, CARD_WIDTH, COVER_HEIGHT)
        img.setStyleSheet("""
            background: transparent;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)
        inner.addWidget(img)

    # ── Interaction ───────────────────────────────────────────────────────────

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.edit_requested.emit(self._activity.id)
        super().mouseDoubleClickEvent(event)
