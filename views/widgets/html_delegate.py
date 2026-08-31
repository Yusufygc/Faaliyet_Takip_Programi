# views/widgets/html_delegate.py
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QTextDocument, QTextOption, QPalette, QColor


class HtmlDelegate(QStyledItemDelegate):
    """QStyledItemDelegate that renders HTML/rich text in table cells."""

    def __init__(self, parent=None, elide_lines: int = 2):
        super().__init__(parent)
        self._elide_lines = elide_lines

    def _make_doc(self, html: str, width: float) -> QTextDocument:
        doc = QTextDocument()
        doc.setHtml(html)
        doc.setTextWidth(width)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(option)
        default_font = QApplication.font()
        doc.setDefaultFont(default_font)
        return doc

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        painter.save()

        style = option.widget.style() if option.widget else QApplication.style()

        # Draw background (handles selection highlight)
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, option.widget)

        html = index.data(Qt.DisplayRole) or ""
        rect = option.rect.adjusted(8, 4, -8, -4)

        painter.translate(rect.topLeft())
        doc = self._make_doc(html, rect.width())

        # Clip to cell height
        painter.setClipRect(QRectF(0, 0, rect.width(), rect.height()))

        # Text color: use selection color when selected, else default
        if option.state & QStyle.State_Selected:
            painter.setPen(option.palette.color(QPalette.HighlightedText))
            color = option.palette.color(QPalette.HighlightedText)
            # Override doc default color for selected state
            doc.setHtml(
                f"<span style='color:{color.name()};'>{html}</span>"
            )

        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        html = index.data(Qt.DisplayRole) or ""
        doc = self._make_doc(html, option.rect.width() if option.rect.isValid() else 200)
        return QSize(int(doc.idealWidth()) + 16, max(52, int(doc.size().height()) + 8))
