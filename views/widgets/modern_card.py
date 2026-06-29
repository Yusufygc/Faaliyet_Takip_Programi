# views/widgets/modern_card.py
from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
class ModernCard(QFrame):
    """Hover animasyonlu temel kart sınıfı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border: 1px solid #E0E6ED;
                border-radius: 16px;
            }
        """)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(self.shadow)

        self.default_y = 4
        self.hover_y = 8
        self.default_blur = 20
        self.hover_blur = 30

    def enterEvent(self, event):
        self.shadow.setYOffset(self.hover_y)
        self.shadow.setBlurRadius(self.hover_blur)
        self.shadow.setColor(QColor(0, 0, 0, 25))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow.setYOffset(self.default_y)
        self.shadow.setBlurRadius(self.default_blur)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        super().leaveEvent(event)
