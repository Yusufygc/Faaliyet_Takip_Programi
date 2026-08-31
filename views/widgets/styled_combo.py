# views/widgets/styled_combo.py
from PyQt5.QtWidgets import (QComboBox, QListView, QStyledItemDelegate,
                             QApplication, QStyle, QFrame)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QPen


class _RoundedItemDelegate(QStyledItemDelegate):
    """Dropdown elemanlarını yuvarlak "pill" olarak çizer.

    Neden gerekli: QListView, QSS `::item` üzerindeki margin ve border-radius
    değerlerini yok sayar; seçim/hover arka planını item'ın TAM dikdörtgenine
    doldurur. Bu da yuvarlak popup içinde kare bir vurgu barı ("kutu içinde
    kutu") oluşturur. Delegate, arka planı yatay/dikey inset ile yuvarlatılmış
    çizerek bu artefaktı tamamen giderir.
    """
    _HOVER_BG = QColor("#EFF6FF")   # blue-50
    _SEL_BG = QColor("#EFF6FF")
    _ACCENT = QColor("#3B82F6")     # C_PRIMARY
    _NORMAL = QColor("#475569")     # C_TEXT_MID

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(option.rect).adjusted(4, 2, -4, -2)
        selected = bool(option.state & QStyle.State_Selected)
        hover = bool(option.state & QStyle.State_MouseOver)

        if selected or hover:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._SEL_BG if selected else self._HOVER_BG)
            painter.drawRoundedRect(rect, 6, 6)

        painter.setPen(QPen(self._ACCENT if (selected or hover) else self._NORMAL))
        font = painter.font()
        font.setBold(selected)
        painter.setFont(font)
        text_rect = option.rect.adjusted(16, 0, -12, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft,
                         str(index.data(Qt.DisplayRole)))
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(38)
        return size


class StyledComboBox(QComboBox):
    """QComboBox subclass that bypasses Windows native popup rendering.

    The default QComboBox on Windows renders its dropdown via the native menu
    manager, which ignores QSS border-radius, item padding and hover effects.
    This class:
      - Switches to QListView so QSS ::item rules take effect.
      - Overrides showPopup() to make the popup container frameless and
        translucent, exposing border-radius without a native chrome box.
      - Recalculates popup position manually (Qt's built-in placement logic
        breaks after window-flag changes).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))
        # Yuvarlak pill çizen delegate (QSS ::item margin/radius yok sayıldığı için)
        self.view().setItemDelegate(_RoundedItemDelegate(self))
        # View'in kendi kare çerçevesini kaldır — yalnızca container'ın yuvarlak
        # kenarı görünsün (ekstra "kutu içinde kutu" kaynağını eler).
        self.view().setFrameShape(QFrame.NoFrame)

    def showPopup(self) -> None:
        view = self.view()
        # Before the first showPopup(), view.window() is the main window
        # (the view is parented to this combo which lives in the main window).
        # After super().showPopup() Qt creates the popup container and reparents
        # the view into it, so view.window() changes to the popup container.
        # We use this transition to detect "first open" without a boolean flag.
        is_first_open = view.window() is self.window()

        super().showPopup()
        container = view.window()

        if is_first_open:
            # setWindowFlags() hides the widget (Qt enforces hide/show on flag
            # change); container.show() at the end re-displays it with new flags.
            container.setWindowFlags(
                Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
            )
            container.setAttribute(Qt.WA_TranslucentBackground)

        # Popup must never be narrower than the combo itself.
        container.setMinimumWidth(self.width())
        self._reposition_popup(container)
        container.show()

    def _reposition_popup(self, container: "QWidget") -> None:
        """Place the popup below (or above) the combo, clamped to screen bounds.

        Qt's built-in placement logic is discarded when we change window flags,
        so we recalculate manually:
          - Try below the combo with a 4px gap.
          - If it overflows the bottom, try above.
          - If neither fits fully, prefer the direction with more room and let
            the scrollbar handle overflow (max-height clip).
        """
        screen = self.screen() or QApplication.primaryScreen()
        avail = screen.availableGeometry()

        combo_bottom = self.mapToGlobal(self.rect().bottomLeft())
        combo_top = self.mapToGlobal(self.rect().topLeft())

        w = container.width()
        h = container.height()

        max_h = avail.height() - 16
        if h > max_h:
            container.setMaximumHeight(max_h)
            h = max_h

        x = combo_bottom.x()
        y = combo_bottom.y() + 4

        if y + h > avail.bottom():
            y_above = combo_top.y() - 4 - h
            y = y_above if y_above >= avail.top() else avail.bottom() - h

        x = max(avail.left(), min(x, avail.right() - w))
        container.move(x, y)
