
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QScrollArea, QFrame, 
                             QDialog, QLineEdit, QTextEdit, QProgressBar, 
                             QSlider, QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QFont, QIcon
from datetime import datetime
from models import Plan

# --- Plan Card Widget ---
class PlanCard(QFrame):
    edited = pyqtSignal(Plan)
    deleted = pyqtSignal(int)
    status_changed = pyqtSignal(int, int, str) # id, progress, status

    def __init__(self, plan: Plan):
        super().__init__()
        self.plan = plan
        self.init_ui()

    def init_ui(self):
        self.setObjectName("PlanCard")
        self.setStyleSheet("""
            #PlanCard {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
            }
            #PlanCard:hover {
                border: 1px solid #555;
            }
        """)
        
        # Gölge Efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header: Title + Priority + Dates
        header_layout = QHBoxLayout()
        
        # Priority Indicator
        priority_colors = {'low': '#4CAF50', 'medium': '#FFC107', 'high': '#F44336'}
        priority_indicator = QLabel()
        priority_indicator.setFixedSize(12, 12)
        priority_indicator.setStyleSheet(f"background-color: {priority_colors.get(self.plan.priority, '#999')}; border-radius: 6px;")
        
        title_lbl = QLabel(self.plan.title)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #eee;")
        
        date_lbl = QLabel(f"{self.plan.year}" + (f"-{self.plan.month:02d}" if self.plan.month else ""))
        date_lbl.setStyleSheet("color: #888; font-size: 12px;")
        
        header_layout.addWidget(priority_indicator)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(date_lbl)
        
        layout.addLayout(header_layout)
        
        # Description
        if self.plan.description:
            desc_lbl = QLabel(self.plan.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #ccc; font-size: 13px; margin-bottom: 5px;")
            layout.addWidget(desc_lbl)
            
        # Progress Bar section
        progress_layout = QHBoxLayout()
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(self.plan.progress)
        self.pbar.setTextVisible(True)
        self.pbar.setFixedHeight(15)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444;
                border-radius: 7px;
                background-color: #222;
                text-align: center;
                color: white;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {self.get_progress_color(self.plan.progress)};
                border-radius: 7px;
            }}
        """)
        progress_layout.addWidget(self.pbar)
        layout.addLayout(progress_layout)

        # Status & Actions Footer
        footer_layout = QHBoxLayout()
        
        # Status Badge
        status_colors = {
            'planned': '#2196F3', 'in_progress': '#FF9800', 
            'completed': '#4CAF50', 'archived': '#9E9E9E'
        }
        status_tr = {
            'planned': 'Planlandı', 'in_progress': 'Devam Ediyor', 
            'completed': 'Tamamlandı', 'archived': 'Arşiv'
        }
        
        status_lbl = QLabel(status_tr.get(self.plan.status, self.plan.status))
        status_lbl.setStyleSheet(f"""
            background-color: {status_colors.get(self.plan.status, '#555')}33;
            color: {status_colors.get(self.plan.status, '#eee')};
            padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;
        """)
        footer_layout.addWidget(status_lbl)
        footer_layout.addStretch()
        
        # Action Buttons
        btn_style = """
            QPushButton {
                background-color: transparent; border: none; color: #888;
                font-weight: bold; padding: 4px;
            }
            QPushButton:hover { color: #eee; background-color: #444; border-radius: 4px;}
        """
        
        btn_edit = QPushButton("Düzenle")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(lambda: self.edited.emit(self.plan))
        
        btn_del = QPushButton("Sil")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet(btn_style.replace("#888", "#d32f2f"))
        btn_del.clicked.connect(self.on_delete)

        # Hızlı tamamla butonu
        if self.plan.status != 'completed':
            btn_check = QPushButton("✔")
            btn_check.setCursor(Qt.PointingHandCursor)
            btn_check.setToolTip("Hızlıca Tamamla")
            btn_check.setStyleSheet("QPushButton { color: #4CAF50; font-weight: bold; border: 1px solid #4CAF50; border-radius: 4px; padding: 2px 8px; } QPushButton:hover { background-color: #4CAF50; color: white; }")
            btn_check.clicked.connect(self.on_quick_complete)
            footer_layout.addWidget(btn_check)

        footer_layout.addWidget(btn_edit)
        footer_layout.addWidget(btn_del)
        
        layout.addLayout(footer_layout)

    def get_progress_color(self, value):
        if value < 30: return "#F44336"
        if value < 70: return "#FFC107"
        return "#4CAF50"

    def on_delete(self):
        msg = QMessageBox()
        msg.setWindowTitle("Plan Sil")
        msg.setText(f"'{self.plan.title}' planını silmek istediğinize emin misiniz?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            self.deleted.emit(self.plan.id)

    def on_quick_complete(self):
        self.status_changed.emit(self.plan.id, 100, 'completed')


# --- Add/Edit Dialog ---
class PlanDialog(QDialog):
    def __init__(self, parent=None, plan: Plan = None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle("Plan Ekle" if not plan else "Plan Düzenle")
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: #ccc; font-size: 14px; }
            QLineEdit, QTextEdit, QComboBox { 
                background-color: #1e1e1e; color: white; border: 1px solid #444; 
                padding: 8px; border-radius: 4px; 
            }
            QPushButton { 
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        layout.addWidget(QLabel("Başlık:"))
        self.inp_title = QLineEdit()
        if self.plan: self.inp_title.setText(self.plan.title)
        layout.addWidget(self.inp_title)

        # Description
        layout.addWidget(QLabel("Açıklama:"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setFixedHeight(80)
        if self.plan: self.inp_desc.setText(self.plan.description)
        layout.addWidget(self.inp_desc)

        # Priority
        layout.addWidget(QLabel("Öncelik:"))
        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["Düşük", "Orta", "Yüksek"])
        priority_map = {'low': 0, 'medium': 1, 'high': 2}
        if self.plan: self.cmb_priority.setCurrentIndex(priority_map.get(self.plan.priority, 1))
        else: self.cmb_priority.setCurrentIndex(1) # Default Medium
        layout.addWidget(self.cmb_priority)

        # Status & Progress (Only if Editing)
        if self.plan:
            layout.addWidget(QLabel("Durum:"))
            self.cmb_status = QComboBox()
            self.cmb_status.addItems(["Planlandı", "Devam Ediyor", "Tamamlandı", "Arşiv"])
            status_map = {'planned': 0, 'in_progress': 1, 'completed': 2, 'archived': 3}
            self.cmb_status.setCurrentIndex(status_map.get(self.plan.status, 0))
            layout.addWidget(self.cmb_status)
            
            layout.addWidget(QLabel(f"İlerleme: %{self.plan.progress}"))
            self.slider_progress = QSlider(Qt.Horizontal)
            self.slider_progress.setRange(0, 100)
            self.slider_progress.setValue(self.plan.progress)
            layout.addWidget(self.slider_progress)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Kaydet")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setStyleSheet("background-color: #d32f2f; color: white;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def get_data(self):
        priority_map = {0: 'low', 1: 'medium', 2: 'high'}
        data = {
            'title': self.inp_title.text().strip(),
            'description': self.inp_desc.toPlainText().strip(),
            'priority': priority_map.get(self.cmb_priority.currentIndex(), 'medium')
        }
        
        if self.plan:
            status_map = {0: 'planned', 1: 'in_progress', 2: 'completed', 3: 'archived'}
            data['status'] = status_map.get(self.cmb_status.currentIndex(), 'planned')
            data['progress'] = self.slider_progress.value()
            
            # Logic: If progress 100, set completed. If completed, set progress 100.
            if data['progress'] == 100 and data['status'] != 'completed':
                data['status'] = 'completed'
            elif data['status'] == 'completed' and data['progress'] < 100:
                data['progress'] = 100
                
        return data


# --- Statistics Widget ---
class PlanStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 15)
        layout.setSpacing(20)
        
        self.lbl_total = self.create_stat_label("Toplam: 0", "#2196F3")
        self.lbl_completed = self.create_stat_label("Tamamlanan: 0", "#4CAF50")
        self.lbl_pending = self.create_stat_label("Bekleyen: 0", "#FFC107")
        
        layout.addWidget(self.lbl_total)
        layout.addWidget(self.lbl_completed)
        layout.addWidget(self.lbl_pending)
        layout.addStretch()

    def create_stat_label(self, text, color):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px; border: 1px solid {color}; padding: 5px 10px; border-radius: 15px;")
        return lbl

    def update_stats(self, plans):
        total = len(plans)
        completed = sum(1 for p in plans if p.status == 'completed')
        pending = total - completed
        
        self.lbl_total.setText(f"Toplam: {total}")
        self.lbl_completed.setText(f"Tamamlanan: {completed}")
        self.lbl_pending.setText(f"Bekleyen: {pending}")


# --- Main Page ---
class PlansPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scope = 'monthly' # Default
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. Header Area
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2b2b2b; border-radius: 10px; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        
        # Title of Section
        lbl_head = QLabel("📅 Planlama & Hedefler")
        lbl_head.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(lbl_head)
        header_layout.addStretch()

        # Scope Toggles (Buttons)
        self.btn_monthly = QPushButton("Aylık")
        self.btn_monthly.setCheckable(True)
        self.btn_monthly.setChecked(True)
        self.btn_yearly = QPushButton("Yıllık")
        self.btn_yearly.setCheckable(True)
        
        # Toggle Logic
        self.btn_monthly.clicked.connect(lambda: self.set_scope('monthly'))
        self.btn_yearly.clicked.connect(lambda: self.set_scope('yearly'))
        
        toggle_style = """
            QPushButton {
                background-color: #1e1e1e; color: #888; border: 1px solid #444;
                padding: 6px 15px; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #2196F3; color: white; border: 1px solid #2196F3;
            }
            QPushButton:first-child { border-top-left-radius: 5px; border-bottom-left-radius: 5px; }
            QPushButton:last-child { border-top-right-radius: 5px; border-bottom-right-radius: 5px; }
        """
        
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0,0,0,0)
        toggle_layout.setSpacing(0)
        self.btn_monthly.setStyleSheet(toggle_style)
        self.btn_yearly.setStyleSheet(toggle_style)
        toggle_layout.addWidget(self.btn_monthly)
        toggle_layout.addWidget(self.btn_yearly)
        header_layout.addWidget(toggle_container)
        
        # Filters
        # Combo Box Style
        cmb_style = """
            QComboBox {
                padding: 5px;
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 2px solid black;
                border-bottom: 2px solid black;
                width: 8px;
                height: 8px;
                margin-right: 5px;
                transform: rotate(-45deg);
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #ddd;
                selection-color: black;
            }
        """

        self.cmb_year = QComboBox()
        self.cmb_year.addItems([str(y) for y in range(self.current_year, self.current_year + 3)])
        self.cmb_year.setCurrentText(str(self.current_year))
        self.cmb_year.currentIndexChanged.connect(self.refresh_data)
        self.cmb_year.setStyleSheet(cmb_style)
        header_layout.addWidget(self.cmb_year)

        self.cmb_month = QComboBox()
        self.cmb_month.addItems([f"{m:02d}" for m in range(1, 13)])
        self.cmb_month.setCurrentIndex(self.current_month - 1)
        self.cmb_month.currentIndexChanged.connect(self.refresh_data)
        self.cmb_month.setStyleSheet(cmb_style)
        header_layout.addWidget(self.cmb_month)

        # New Plan Button
        btn_add = QPushButton(" + Yeni Plan ")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 5px; 
                padding: 6px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_plan_dialog)
        header_layout.addWidget(btn_add)
        
        layout.addWidget(header_frame)
        
        # 2. Stats Area
        self.stats_widget = PlanStatsWidget()
        layout.addWidget(self.stats_widget)

        # 3. Content Area (Scrollable Card List)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.content_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.addStretch()
        
        self.scroll.setWidget(self.content_container)
        layout.addWidget(self.scroll)
        
        # Initial Load
        # self.refresh_data() -> Main Window will call this

    def set_scope(self, scope):
        self.scope = scope
        if scope == 'monthly':
            self.btn_monthly.setChecked(True)
            self.btn_yearly.setChecked(False)
            self.cmb_month.setVisible(True)
        else:
            self.btn_monthly.setChecked(False)
            self.btn_yearly.setChecked(True)
            self.cmb_month.setVisible(False)
        self.refresh_data()

    def refresh_data(self):
        year = int(self.cmb_year.currentText())
        month = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
        
        self.controller.get_plans(self.scope, year, month, self.on_data_loaded)

    def on_data_loaded(self, plans):
        # Clear existing items
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # layout silmek biraz daha karışıktır ama burada addStretch kullanıyoruz
                pass

        if not plans:
            lbl_empty = QLabel("Bu dönem için henüz bir plan oluşturulmamış.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("color: #666; font-size: 16px; margin-top: 50px;")
            self.cards_layout.addWidget(lbl_empty)
        
        for plan in plans:
            card = PlanCard(plan)
            card.edited.connect(self.edit_plan_dialog)
            card.deleted.connect(self.delete_plan)
            card.status_changed.connect(self.update_status)
            self.cards_layout.addWidget(card)
            
        self.cards_layout.addStretch()
        self.stats_widget.update_stats(plans)

    def add_plan_dialog(self):
        dialog = PlanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            year = int(self.cmb_year.currentText())
            month = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
            
            self.controller.add_plan(
                data['title'], data['description'], self.scope, year, month, data['priority'],
                self.on_operation_finished
            )

    def edit_plan_dialog(self, plan):
        dialog = PlanDialog(self, plan)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.controller.update_plan(
                plan.id, data['title'], data['description'], data['status'], 
                data['progress'], data['priority'], self.on_operation_finished
            )

    def delete_plan(self, plan_id):
        self.controller.delete_plan(plan_id, self.on_operation_finished)

    def update_status(self, plan_id, progress, status):
        self.controller.update_plan_progress(plan_id, progress, status, lambda res: self.refresh_data())

    def on_operation_finished(self, result):
        if isinstance(result, tuple):
            success, msg = result
        else:
            success = result
            msg = ""
            
        if success:
            self.refresh_data()
            if msg:
                # Parent status bar'a ulaşmak zor olabilir, msgbox opsiyonel
                pass
        else:
            QMessageBox.critical(self, "Hata", msg)
