# views/widgets/styled_combo.py
from PyQt5.QtWidgets import QComboBox, QListView, QStyledItemDelegate, QApplication
from PyQt5.QtCore import Qt


class StyledComboBox(QComboBox):
    """Yuvarlak köşeli, QSS ile stillenebilir popup'a sahip QComboBox.

    Windows native popup ::item QSS'ini (hover, height, border-radius) yok
    sayar ve köşeli bir pencere çerçevesi içinde çizer. QListView view'a
    geçmek ::item kurallarını aktif eder; popup container'ı frameless +
    translucent yapmak border-radius'u görünür kılar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))
        self.setItemDelegate(QStyledItemDelegate(self))
        self._popup_flags_set = False

    def showPopup(self):
        super().showPopup()
        container = self.view().window()
        if not self._popup_flags_set:
            container.setWindowFlags(
                Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
            )
            container.setAttribute(Qt.WA_TranslucentBackground)
            container.setObjectName("ComboPopupContainer")
            container.setStyleSheet("#ComboPopupContainer { background-color: transparent; border: none; }")
            self._popup_flags_set = True

        # flag değişimi pencereyi gizler → ekrana sığacak şekilde yeniden konumla.
        # Qt'nin kendi ekran-sığdırma mantığı flag override'ı ile kayboluyor;
        # burada manuel olarak: alta sığmazsa üste çevir, yine sığmazsa
        # yüksekliği ekrana kıp (QAbstractItemView scrollbar devreye girer).
        screen = QApplication.desktop().availableGeometry(self)
        below = self.mapToGlobal(self.rect().bottomLeft())
        above = self.mapToGlobal(self.rect().topLeft())

        w = container.width()
        max_h = screen.height() - 16
        h = container.height()
        if h > max_h:
            container.setMaximumHeight(max_h)
            h = max_h

        x = below.x()
        y = below.y() + 4
        if y + h > screen.bottom():           # alta taşıyor
            y_above = above.y() - 4 - h
            y = y_above if y_above >= screen.top() else screen.bottom() - h
        x = max(screen.left(), min(x, screen.right() - w))

        container.move(x, y)
        container.show()
