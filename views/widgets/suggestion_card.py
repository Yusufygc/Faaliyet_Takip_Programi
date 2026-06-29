# views/widgets/suggestion_card.py
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from views.widgets.async_image import AsyncImage


class SuggestionCard(QFrame):
    """Öneri kartı widget'ı."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(220, 360)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 12px;
            }
            QFrame:hover {
                background-color: #383838;
                border: 1px solid #666;
            }
            QLabel { background-color: transparent; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        img_url = self.data.get('image')
        self.img_lbl = AsyncImage(img_url, 200, 260)
        layout.addWidget(self.img_lbl, alignment=Qt.AlignCenter)

        title = self.data.get('title', 'Başlık Yok')
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_lbl.setWordWrap(True)
        title_lbl.setFixedHeight(35)
        layout.addWidget(title_lbl)

        meta_layout = QHBoxLayout()
        rating = self.data.get('rating', 0) or 0
        rating_lbl = QLabel(f"★ {rating:.1f}")
        rating_lbl.setStyleSheet("color: #FFC107; font-size: 11px;")

        date_str = str(self.data.get('date', ''))[:4] if self.data.get('date') else ''
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("color: #888; font-size: 11px;")

        meta_layout.addWidget(rating_lbl)
        meta_layout.addStretch()
        meta_layout.addWidget(date_lbl)
        layout.addLayout(meta_layout)
