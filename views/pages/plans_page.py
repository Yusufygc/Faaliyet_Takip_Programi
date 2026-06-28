# views/pages/plans_page.py
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QScrollArea, QFrame,
                             QDialog, QMessageBox, QGraphicsDropShadowEffect,
                             QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from datetime import datetime
from views.widgets.plan_colors import COLORS, PRIORITY_CFG
from views.widgets.folder_widget import FolderWidget
from views.widgets.plan_card import PlanCard
from views.widgets.plan_dialog import PlanDialog
from views.widgets.plan_stats_widget import StatCard, PlanStatsWidget


class PlansPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scope = 'monthly'
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.folders = []
        self.current_folder_id = None
        self.init_ui()
        self.load_folders()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # ─── 1. Header & Filters ───
        header = QHBoxLayout()

        title = QLabel("Planlama & Hedefler")
        title.setStyleSheet(f"font-size: 28px; font-weight: 900; color: {COLORS['text_main']};")
        header.addWidget(title)
        header.addStretch()

        filter_box = QFrame()
        filter_box.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 25px;
                padding: 4px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        filter_box.setGraphicsEffect(shadow)

        fb_layout = QHBoxLayout(filter_box)
        fb_layout.setContentsMargins(10, 4, 10, 4)
        fb_layout.setSpacing(8)

        self.btn_m = self._make_toggle("Aylık", True)
        self.btn_y = self._make_toggle("Yıllık", False)
        self.btn_m.clicked.connect(lambda: self.set_scope('monthly'))
        self.btn_y.clicked.connect(lambda: self.set_scope('yearly'))
        fb_layout.addWidget(self.btn_m)
        fb_layout.addWidget(self.btn_y)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #E0E0E0; margin: 5px;")
        line.setFixedWidth(1)
        fb_layout.addWidget(line)

        self.cmb_year = self._make_header_combo([str(y) for y in range(self.current_year, self.current_year + 3)])
        self.cmb_year.currentIndexChanged.connect(self.refresh_data)
        fb_layout.addWidget(self.cmb_year)

        self.cmb_month = self._make_header_combo(['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                                                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'])
        self.cmb_month.setCurrentIndex(self.current_month - 1)
        self.cmb_month.currentIndexChanged.connect(self.refresh_data)
        fb_layout.addWidget(self.cmb_month)

        header.addWidget(filter_box)

        btn_new = QPushButton("+ Yeni Plan")
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setFixedSize(140, 50)
        btn_new.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary_gradient']};
                color: white; border-radius: 25px; font-weight: bold; font-size: 14px;
                padding-left: 10px; padding-right: 10px;
            }}
            QPushButton:hover {{ background: {COLORS['primary']}; }}
        """)
        btn_new.clicked.connect(self.add_plan_dialog)
        header.addWidget(btn_new)

        layout.addLayout(header)

        # ─── 2. Content Row (Folders + Stats) ───
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        self.folder_widget = FolderWidget()
        self.folder_widget.folder_selected.connect(self.on_folder_selected)
        self.folder_widget.folder_added.connect(self.on_add_folder)
        self.folder_widget.folder_renamed.connect(self.on_rename_folder)
        self.folder_widget.folder_deleted.connect(self.on_delete_folder)
        content_row.addWidget(self.folder_widget, 1, Qt.AlignVCenter)

        self.stats = PlanStatsWidget()
        content_row.addWidget(self.stats, 0)

        layout.addLayout(content_row)

        # ─── 3. Scroll Area ───
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDC3C7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95A5A6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.card_layout = QGridLayout(container)
        self.card_layout.setSpacing(20)
        self.card_layout.setContentsMargins(0, 10, 10, 10)
        self.card_layout.setAlignment(Qt.AlignTop)
        self.card_layout.setColumnStretch(0, 1)
        self.card_layout.setColumnStretch(1, 1)
        self.card_layout.setColumnStretch(2, 1)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _make_toggle(self, text, active):
        b = QPushButton(text)
        b.setCheckable(True)
        b.setChecked(active)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(36)
        self._style_toggle(b)
        return b

    def _style_toggle(self, b):
        if b.isChecked():
            b.setStyleSheet(f"background-color: {COLORS['bg_main']}; color: {COLORS['primary']}; font-weight: bold; border: none; border-radius: 18px; padding: 0 15px;")
        else:
            b.setStyleSheet(f"background: transparent; color: {COLORS['text_sub']}; font-weight: 500; border: none; padding: 0 15px;")

    def _make_header_combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setCursor(Qt.PointingHandCursor)
        c.setStyleSheet(f"""
            QComboBox {{
                background: transparent;
                border: none;
                color: {COLORS['text_main']};
                font-weight: bold;
                padding: 4px 10px;
                min-width: 50px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox:hover {{
                background-color: #F5F7FA;
                border-radius: 12px;
                color: {COLORS['primary']};
            }}
            QComboBox QAbstractItemView {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 5px;
                outline: none;
                min-width: 120px;
            }}
            QComboBox QAbstractItemView::item {{
                height: 32px;
                padding-left: 10px;
                color: {COLORS['text_main']};
                border-radius: 6px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']}1A;
                color: {COLORS['primary']};
            }}
        """)
        return c

    def set_scope(self, scope):
        self.scope = scope
        self.btn_m.setChecked(scope == 'monthly')
        self.btn_y.setChecked(scope == 'yearly')
        self._style_toggle(self.btn_m)
        self._style_toggle(self.btn_y)
        self.cmb_month.setVisible(scope == 'monthly')
        self.refresh_data()

    def refresh_data(self):
        y = int(self.cmb_year.currentText())
        m = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
        self.controller.get_plans(self.scope, y, m, self.on_loaded)

    def load_folders(self):
        self.controller.get_folders(self.on_folders_loaded)

    def on_folders_loaded(self, folders):
        self.folders = folders
        self.folder_widget.set_folders(folders)

    def on_folder_selected(self, folder_id):
        self.current_folder_id = folder_id
        self.refresh_data()

    def on_add_folder(self, name):
        self.controller.add_folder(name, lambda res: self.load_folders())

    def on_rename_folder(self, folder_id, name):
        self.controller.update_folder(folder_id, name, lambda res: self.load_folders())

    def on_delete_folder(self, folder_id):
        self.controller.delete_folder(folder_id, lambda res: self.load_folders())

    def on_loaded(self, plans):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered_plans = []
        if self.current_folder_id is None:
            filtered_plans = [p for p in plans if p.folder_id is None]
        else:
            filtered_plans = [p for p in plans if p.folder_id == self.current_folder_id]

        if not filtered_plans:
            lbl = QLabel("📭 Bu klasörde/dönemde henüz bir plan yok.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 16px; margin-top: 40px;")
            self.card_layout.addWidget(lbl, 0, 0, 1, 3)
            self.stats.update_stats([])
            return

        for i, p in enumerate(filtered_plans):
            row = i // 3
            col = i % 3

            card = PlanCard(p)
            card.edited.connect(self.edit_plan)
            card.deleted.connect(self.delete_plan)
            card.status_changed.connect(self.update_status)
            self.card_layout.addWidget(card, row, col)

        self.stats.update_stats(filtered_plans)

    def add_plan_dialog(self):
        d = PlanDialog(self, folders=self.folders)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            y = int(self.cmb_year.currentText())
            m = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
            selected_folder = data.get('folder_id')
            if selected_folder is None and self.current_folder_id is not None:
                selected_folder = self.current_folder_id

            self.controller.add_plan(data['title'], data['description'], self.scope, y, m,
                                     data['priority'], selected_folder, self.on_finished)

    def edit_plan(self, plan):
        d = PlanDialog(self, plan, folders=self.folders)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            self.controller.update_plan(plan.id, data['title'], data['description'],
                                        data['status'], data['progress'], data['priority'],
                                        data.get('folder_id'), self.on_finished)

    def delete_plan(self, pid):
        self.controller.delete_plan(pid, self.on_finished)

    def update_status(self, pid, prog, stat):
        self.controller.update_plan_progress(pid, prog, stat, lambda x: self.refresh_data())

    def on_finished(self, res):
        if (isinstance(res, tuple) and res[0]) or res is True:
            self.refresh_data()
        else:
            msg = res[1] if isinstance(res, tuple) else "Hata oluştu"
            QMessageBox.critical(self, "Hata", msg)
