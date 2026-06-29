# views/widgets/styled_combo.py
from PyQt5.QtWidgets import QComboBox, QListView, QStyledItemDelegate, QApplication
from PyQt5.QtCore import Qt


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
        self.setItemDelegate(QStyledItemDelegate(self))

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
