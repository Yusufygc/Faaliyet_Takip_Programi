# views/widgets/heatmap_widget.py
from __future__ import annotations

import math
from datetime import date, timedelta

from PyQt5.QtWidgets import QWidget, QToolTip
from PyQt5.QtCore import Qt, QRectF, QSize, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

_CELL = 14      # px per cell
_GAP  = 3       # px gap between cells
_STRIDE = _CELL + _GAP

_LEFT_PAD  = 30  # room for day labels (Mon/Wed/Fri)
_TOP_PAD   = 24  # room for month labels

_COLORS = [
    QColor("#E2E8F0"),  # 0 activities
    QColor("#BAE6FD"),  # 1-2
    QColor("#38BDF8"),  # 3-4
    QColor("#0284C7"),  # 5-9
    QColor("#0C4A6E"),  # 10+
]

_DAY_LABELS  = {1: "Pzt", 3: "Çar", 5: "Cum"}  # weekday index → label
_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
               "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _color_for(count: int) -> QColor:
    if count == 0:   return _COLORS[0]
    if count <= 2:   return _COLORS[1]
    if count <= 4:   return _COLORS[2]
    if count <= 9:   return _COLORS[3]
    return _COLORS[4]


class ContributionHeatmap(QWidget):
    """GitHub contribution grafiği benzeri 52×7 ısı haritası."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._daily: dict[str, int] = {}
        self._year = date.today().year
        self._cells: list[tuple[QRectF, str, int]] = []  # (rect, date_str, count)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        self._update_size()

    # ── Public ────────────────────────────────────────────────────────────────

    def set_data(self, daily_counts: dict[str, int], year: int):
        self._daily = daily_counts or {}
        self._year  = year
        self._build_cells()
        self.update()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _update_size(self):
        w = _LEFT_PAD + 53 * _STRIDE + _GAP
        h = _TOP_PAD  +  7 * _STRIDE + _GAP
        self.setFixedSize(w, h)

    def _build_cells(self):
        self._cells = []
        start = date(self._year, 1, 1)
        end   = date(self._year, 12, 31)
        # Align to Monday of the week containing Jan 1
        col_start = start - timedelta(days=start.weekday())

        current = col_start
        col = 0
        while current <= end or (col < 53 and current.year <= self._year):
            for row in range(7):
                d = current + timedelta(days=row)
                if d.year != self._year:
                    continue
                ds = d.isoformat()
                count = self._daily.get(ds, 0)
                x = _LEFT_PAD + col * _STRIDE
                y = _TOP_PAD  + row * _STRIDE
                rect = QRectF(x, y, _CELL, _CELL)
                self._cells.append((rect, ds, count))
            current += timedelta(weeks=1)
            col += 1
            if col > 53:
                break

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        if not self._cells:
            self._build_cells()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        label_font = QFont("Segoe UI", 9)
        painter.setFont(label_font)
        painter.setPen(QColor("#94A3B8"))

        # Day labels
        for row, label in _DAY_LABELS.items():
            y = _TOP_PAD + row * _STRIDE + _CELL / 2 + 4
            painter.drawText(0, int(y), label)

        # Month labels
        drawn_months: set[int] = set()
        for rect, ds, _ in self._cells:
            d = date.fromisoformat(ds)
            if d.month not in drawn_months:
                drawn_months.add(d.month)
                painter.drawText(int(rect.x()), _TOP_PAD - 6, _MONTHS_TR[d.month - 1])

        # Cells
        painter.setPen(Qt.NoPen)
        for rect, ds, count in self._cells:
            painter.setBrush(_color_for(count))
            painter.drawRoundedRect(rect, 3, 3)

        painter.end()

    # ── Tooltip ───────────────────────────────────────────────────────────────

    def mouseMoveEvent(self, event):
        pos = event.pos()
        for rect, ds, count in self._cells:
            if rect.contains(pos.x(), pos.y()):
                d = date.fromisoformat(ds)
                label = f"{d.strftime('%d %B %Y')} — {count} aktivite"
                QToolTip.showText(event.globalPos(), label, self)
                return
        QToolTip.hideText()

    def sizeHint(self) -> QSize:
        return self.minimumSizeHint()
