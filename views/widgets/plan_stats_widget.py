# views/widgets/plan_stats_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from views.widgets.modern_card import ModernCard
from views.widgets.plan_colors import COLORS


class StatCard(ModernCard):
    def __init__(self, title, icon, color):
        super().__init__()
        self.setFixedHeight(100)
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        row = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")

        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {color}; background: transparent;")

        row.addWidget(lbl_icon)
        row.addStretch()
        row.addWidget(self.lbl_count)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 13px; font-weight: 600; background: transparent;")

        layout.addLayout(row)
        layout.addWidget(lbl_title)


class PlanStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 20)
        layout.setSpacing(20)

        self.card_total = StatCard("Toplam Plan", "📊", COLORS['primary'])
        self.card_done = StatCard("Tamamlanan", "✅", "#27AE60")
        self.card_wait = StatCard("Bekleyen", "⏳", "#F39C12")

        layout.addWidget(self.card_total)
        layout.addWidget(self.card_done)
        layout.addWidget(self.card_wait)
        layout.addStretch()

    def update_stats(self, plans):
        total = len(plans)
        completed = sum(1 for p in plans if p.status == 'completed')
        self.card_total.lbl_count.setText(str(total))
        self.card_done.lbl_count.setText(str(completed))
        self.card_wait.lbl_count.setText(str(total - completed))
