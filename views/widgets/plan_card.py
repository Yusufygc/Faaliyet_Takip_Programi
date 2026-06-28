# views/widgets/plan_card.py
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from models import Plan
from views.widgets.modern_card import ModernCard
from views.widgets.plan_colors import COLORS, PRIORITY_CFG


class PlanCard(ModernCard):
    edited = pyqtSignal(Plan)
    deleted = pyqtSignal(int)
    status_changed = pyqtSignal(int, int, str)

    def __init__(self, plan: Plan):
        super().__init__()
        self.plan = plan
        self.init_ui()

    def init_ui(self):
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ─── Header (Öncelik - Tarih) ───
        header = QHBoxLayout()

        p_data = PRIORITY_CFG.get(self.plan.priority, PRIORITY_CFG['medium'])
        lbl_priority = QLabel(f"{p_data['dot']} {p_data['label']}")
        lbl_priority.setStyleSheet(f"""
            background-color: {p_data['bg']};
            color: {p_data['fg']};
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 12px;
        """)

        date_str = f"{self.plan.year}"
        if self.plan.month:
            months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                      'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            date_str = f"{months[self.plan.month-1]} {self.plan.year}"

        lbl_date = QLabel(f"📅 {date_str}")
        lbl_date.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 12px; font-weight: 600;")

        header.addWidget(lbl_priority)
        header.addStretch()
        header.addWidget(lbl_date)
        layout.addLayout(header)

        # ─── İçerik (Başlık - Açıklama) ───
        content = QVBoxLayout()
        content.setSpacing(6)

        lbl_title = QLabel(self.plan.title)
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {COLORS['text_main']};
            background: transparent;
        """)

        if self.plan.description:
            lbl_desc = QLabel(self.plan.description)
            lbl_desc.setWordWrap(True)
            lbl_desc.setMaximumHeight(40)
            lbl_desc.setStyleSheet(f"""
                font-size: 13px;
                color: {COLORS['text_sub']};
                line-height: 1.4;
                background: transparent;
            """)
            content.addWidget(lbl_title)
            content.addWidget(lbl_desc)
        else:
            content.addWidget(lbl_title)

        layout.addLayout(content)

        # ─── Progress Bar ───
        progress_container = QVBoxLayout()
        progress_container.setSpacing(4)

        pl_row = QHBoxLayout()
        pl_lbl = QLabel("İlerleme")
        pl_lbl.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 11px; font-weight: 600;")
        pl_val = QLabel(f"%{self.plan.progress}")
        pl_val.setStyleSheet(f"color: {COLORS['primary']}; font-size: 12px; font-weight: 800;")
        pl_row.addWidget(pl_lbl)
        pl_row.addStretch()
        pl_row.addWidget(pl_val)

        pbar = QProgressBar()
        pbar.setRange(0, 100)
        pbar.setValue(self.plan.progress)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(8)

        bar_color = COLORS['success_gradient'] if self.plan.progress == 100 else COLORS['primary_gradient']
        if self.plan.progress < 30:
            bar_color = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E74C3C, stop:1 #C0392B)"

        pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #F0F3F4;
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {bar_color};
                border-radius: 4px;
            }}
        """)

        progress_container.addLayout(pl_row)
        progress_container.addWidget(pbar)
        layout.addLayout(progress_container)

        # ─── Footer (Durum - Butonlar) ───
        footer = QHBoxLayout()
        footer.setSpacing(10)

        status_map = {
            'planned': ('📋 Planlandı', '#7F8C8D'),
            'in_progress': ('⚙️ Sürüyor', '#F39C12'),
            'completed': ('✅ Tamamlandı', '#27AE60'),
            'archived': ('📦 Arşiv', '#95A5A6')
        }
        st_text, st_color = status_map.get(self.plan.status, status_map['planned'])
        lbl_status = QLabel(st_text)
        lbl_status.setStyleSheet(f"color: {st_color}; font-weight: bold; font-size: 12px; background: transparent;")

        footer.addWidget(lbl_status)
        footer.addStretch()

        def create_circle_btn(icon, color, tooltip, callback):
            btn = QPushButton(icon)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {COLORS['border']};
                    border-radius: 16px;
                    color: {COLORS['text_sub']};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color}1A;
                    border: 1px solid {color};
                    color: {color};
                }}
            """)
            btn.clicked.connect(callback)
            return btn

        if self.plan.status != 'completed':
            btn_ok = create_circle_btn("✓", "#27AE60", "Tamamla", self.on_quick_complete)
            footer.addWidget(btn_ok)

        btn_edit = create_circle_btn("✏️", "#2980B9", "Düzenle", lambda: self.edited.emit(self.plan))
        footer.addWidget(btn_edit)

        btn_del = create_circle_btn("🗑️", "#E74C3C", "Sil", self.on_delete)
        footer.addWidget(btn_del)

        layout.addLayout(footer)

    def on_delete(self):
        msg = QMessageBox()
        msg.setWindowTitle("Planı Sil")
        msg.setText(f"'{self.plan.title}' silinecek. Onaylıyor musunuz?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(f"background-color: white; color: {COLORS['text_main']}; font-size: 13px;")
        if msg.exec_() == QMessageBox.Yes:
            self.deleted.emit(self.plan.id)

    def on_quick_complete(self):
        self.status_changed.emit(self.plan.id, 100, 'completed')
