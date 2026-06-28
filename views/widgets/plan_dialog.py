# views/widgets/plan_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QComboBox, QSlider, QPushButton)
from PyQt5.QtCore import Qt
from models import Plan
from views.widgets.plan_colors import COLORS


class PlanDialog(QDialog):
    def __init__(self, parent=None, plan: Plan = None, folders=None):
        super().__init__(parent)
        self.plan = plan
        self.folders = folders or []
        self.setWindowTitle("Plan Oluştur" if not plan else "Planı Düzenle")
        self.setFixedWidth(480)
        self.setStyleSheet(f"background-color: {COLORS['bg_card']};")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title_lbl = QLabel("✨ Yeni Plan" if not self.plan else "✏️ Planı Düzenle")
        title_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {COLORS['text_main']}; margin-bottom: 10px;")
        layout.addWidget(title_lbl)

        if self.folders:
            layout.addWidget(self._make_label("KLASÖR / PROJE"))
            self.cmb_folder = QComboBox()
            self.cmb_folder.addItem("📁 Genel (Klasörsüz)", None)

            selected_idx = 0
            for i, f in enumerate(self.folders):
                self.cmb_folder.addItem(f"📁 {f.name}", f.id)
                if self.plan and self.plan.folder_id == f.id:
                    selected_idx = i + 1

            self.cmb_folder.setStyleSheet(self._combo_style())
            self.cmb_folder.setCurrentIndex(selected_idx)
            layout.addWidget(self.cmb_folder)

        layout.addWidget(self._make_label("BAŞLIK"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Hedefinizi buraya yazın...")
        self.inp_title.setStyleSheet(self._input_style())
        if self.plan:
            self.inp_title.setText(self.plan.title)
        layout.addWidget(self.inp_title)

        layout.addWidget(self._make_label("AÇIKLAMA"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Detaylar (opsiyonel)...")
        self.inp_desc.setMinimumHeight(80)
        self.inp_desc.setMaximumHeight(100)
        self.inp_desc.setStyleSheet(self._input_style())
        if self.plan:
            self.inp_desc.setText(self.plan.description)
        layout.addWidget(self.inp_desc)

        layout.addWidget(self._make_label("ÖNCELİK"))
        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["🔵 Düşük Öncelik", "🟡 Orta Öncelik", "🔴 Yüksek Öncelik"])
        self.cmb_priority.setStyleSheet(self._combo_style())

        priority_map = {'low': 0, 'medium': 1, 'high': 2}
        idx = priority_map.get(self.plan.priority, 1) if self.plan else 1
        self.cmb_priority.setCurrentIndex(idx)
        layout.addWidget(self.cmb_priority)

        if self.plan:
            layout.addWidget(self._make_label("DURUM"))
            self.cmb_status = QComboBox()
            self.cmb_status.addItems(["📋 Planlandı", "⚙️ Sürüyor", "✅ Tamamlandı", "📦 Arşiv"])
            self.cmb_status.setStyleSheet(self._combo_style())

            st_map = {'planned': 0, 'in_progress': 1, 'completed': 2, 'archived': 3}
            self.cmb_status.setCurrentIndex(st_map.get(self.plan.status, 0))
            layout.addWidget(self.cmb_status)

            layout.addSpacing(10)
            sl_layout = QHBoxLayout()
            sl_layout.addWidget(self._make_label("İLERLEME"))
            self.lbl_val = QLabel(f"%{self.plan.progress}")
            self.lbl_val.setStyleSheet(f"font-weight: bold; color: {COLORS['primary']}; font-size: 15px;")
            sl_layout.addStretch()
            sl_layout.addWidget(self.lbl_val)
            layout.addLayout(sl_layout)

            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0, 100)
            self.slider.setValue(self.plan.progress)
            self.slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{ height: 8px; background: #F0F3F4; border-radius: 4px; }}
                QSlider::handle:horizontal {{
                    background: {COLORS['primary']}; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px;
                    border: 2px solid white;
                }}
                QSlider::sub-page:horizontal {{ background: {COLORS['primary_gradient']}; border-radius: 4px; }}
            """)
            self.slider.valueChanged.connect(lambda v: self.lbl_val.setText(f"%{v}"))
            layout.addWidget(self.slider)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ color: {COLORS['text_sub']}; background: transparent; border: none; font-weight: 600; font-size: 14px; }}
            QPushButton:hover {{ color: {COLORS['text_main']}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Kaydet")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(45)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary_gradient']};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 25px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
            }}
        """)
        btn_save.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def _make_label(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS['text_sub']}; letter-spacing: 0.5px;")
        return l

    def _input_style(self):
        return f"""
            QLineEdit, QTextEdit {{
                background-color: #FAFAFA;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: {COLORS['text_main']};
                selection-background-color: {COLORS['primary']}40;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                background-color: white;
                border: 1px solid {COLORS['primary']};
            }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: #FAFAFA;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                color: {COLORS['text_main']};
            }}
            QComboBox:hover {{ background-color: white; border-color: {COLORS['text_sub']}; }}
            QComboBox:focus {{ border-color: {COLORS['primary']}; background-color: white; }}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 30px; border-left-width: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text_sub']};
                margin-top: 2px;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white; border: 1px solid {COLORS['border']};
                border-radius: 8px; padding: 5px; outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                height: 40px; padding-left: 10px; color: {COLORS['text_main']}; border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']}1A; color: {COLORS['primary']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #F5F5F5;
            }}
        """

    def get_data(self):
        priority_map = {0: 'low', 1: 'medium', 2: 'high'}
        data = {
            'title': self.inp_title.text().strip(),
            'description': self.inp_desc.toPlainText().strip(),
            'priority': priority_map.get(self.cmb_priority.currentIndex(), 'medium'),
            'folder_id': self.cmb_folder.currentData() if hasattr(self, 'cmb_folder') else None
        }
        if self.plan:
            st_map = {0: 'planned', 1: 'in_progress', 2: 'completed', 3: 'archived'}
            data['status'] = st_map.get(self.cmb_status.currentIndex(), 'planned')
            data['progress'] = self.slider.value()
            if data['progress'] == 100:
                data['status'] = 'completed'
            elif data['status'] == 'completed' and data['progress'] < 100:
                data['progress'] = 100
        return data
