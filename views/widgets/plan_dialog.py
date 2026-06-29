# views/widgets/plan_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QSlider, QPushButton)
from PyQt5.QtCore import Qt
from models import Plan
from views.widgets.styled_combo import StyledComboBox


class PlanDialog(QDialog):
    def __init__(self, parent=None, plan: Plan = None, folders=None):
        super().__init__(parent)
        self.plan = plan
        self.folders = folders or []
        self.setWindowTitle("Plan Oluştur" if not plan else "Planı Düzenle")
        self.setFixedWidth(480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title_lbl = QLabel("Yeni Plan" if not self.plan else "Planı Düzenle")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(title_lbl)

        if self.folders:
            layout.addWidget(self._make_label("KLASÖR / PROJE"))
            self.cmb_folder = StyledComboBox()
            self.cmb_folder.addItem("Genel (Klasörsüz)", None)

            selected_idx = 0
            for i, f in enumerate(self.folders):
                self.cmb_folder.addItem(f.name, f.id)
                if self.plan and self.plan.folder_id == f.id:
                    selected_idx = i + 1

            self.cmb_folder.setCurrentIndex(selected_idx)
            layout.addWidget(self.cmb_folder)

        layout.addWidget(self._make_label("BAŞLIK"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Hedefinizi buraya yazın...")
        if self.plan:
            self.inp_title.setText(self.plan.title)
        layout.addWidget(self.inp_title)

        layout.addWidget(self._make_label("AÇIKLAMA"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Detaylar (opsiyonel)...")
        self.inp_desc.setMinimumHeight(80)
        self.inp_desc.setMaximumHeight(100)
        if self.plan:
            self.inp_desc.setText(self.plan.description)
        layout.addWidget(self.inp_desc)

        layout.addWidget(self._make_label("ÖNCELİK"))
        self.cmb_priority = StyledComboBox()
        self.cmb_priority.addItems(["Düşük Öncelik", "Orta Öncelik", "Yüksek Öncelik"])

        priority_map = {'low': 0, 'medium': 1, 'high': 2}
        idx = priority_map.get(self.plan.priority, 1) if self.plan else 1
        self.cmb_priority.setCurrentIndex(idx)
        layout.addWidget(self.cmb_priority)

        if self.plan:
            layout.addWidget(self._make_label("DURUM"))
            self.cmb_status = StyledComboBox()
            self.cmb_status.addItems(["Planlandı", "Sürüyor", "Tamamlandı", "Arşiv"])

            st_map = {'planned': 0, 'in_progress': 1, 'completed': 2, 'archived': 3}
            self.cmb_status.setCurrentIndex(st_map.get(self.plan.status, 0))
            layout.addWidget(self.cmb_status)

            layout.addSpacing(10)
            sl_layout = QHBoxLayout()
            sl_layout.addWidget(self._make_label("İLERLEME"))
            self.lbl_val = QLabel(f"%{self.plan.progress}")
            self.lbl_val.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 15px;")
            sl_layout.addStretch()
            sl_layout.addWidget(self.lbl_val)
            layout.addLayout(sl_layout)

            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0, 100)
            self.slider.setValue(self.plan.progress)
            self.slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #F0F3F4; border-radius: 4px; }
                QSlider::handle:horizontal {
                    background: #3B82F6; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px;
                    border: 2px solid white;
                }
                QSlider::sub-page:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #3498DB);
                    border-radius: 4px;
                }
            """)
            self.slider.valueChanged.connect(lambda v: self.lbl_val.setText(f"%{v}"))
            layout.addWidget(self.slider)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Kaydet")
        btn_save.setObjectName("btn_primary")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(45)
        btn_save.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def _make_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 11px; font-weight: 700; color: #7F8C8D; letter-spacing: 0.5px;")
        return l

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
