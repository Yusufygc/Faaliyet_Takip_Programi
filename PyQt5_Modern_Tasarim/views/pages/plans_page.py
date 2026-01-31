# views/pages/plans_page.py
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QScrollArea, QFrame, 
                             QDialog, QLineEdit, QTextEdit, QProgressBar, 
                             QSlider, QMessageBox, QGraphicsDropShadowEffect,
                             QGridLayout, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QIcon
from datetime import datetime
from models import Plan

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Color Palette (WCAG 2.1 AA Compliant - Minimum 4.5:1 Contrast)
COLORS = {
    'bg_main': '#1a1a1a',
    'bg_card': '#2d2d2d',
    'bg_hover': '#3d3d3d',
    'bg_input': '#252525',
    'primary': '#2196F3',
    'primary_hover': '#1976D2',
    'success': '#4CAF50',
    'success_hover': '#43A047',
    'warning': '#FF9800',
    'danger': '#F44336',
    'danger_hover': '#D32F2F',
    'text_primary': '#ffffff',
    'text_secondary': '#e0e0e0',
    'text_muted': '#9e9e9e',
    'border': '#3d3d3d',
    'border_light': '#555555'
}

# Spacing System (8px Grid)
SPACING = {'xs': 8, 'sm': 16, 'md': 24, 'lg': 32, 'xl': 48}

# Typography
FONTS = {'h1': 24, 'h2': 18, 'body': 14, 'caption': 12, 'small': 11}

# Priority Colors & Configuration
PRIORITY_CONFIG = {
    'low': {'color': '#2196F3', 'label': 'Düşük', 'icon': '🔵'},
    'medium': {'color': '#FF9800', 'label': 'Orta', 'icon': '🟡'},
    'high': {'color': '#F44336', 'label': 'Yüksek', 'icon': '🔴'}
}

# Status Configuration
STATUS_CONFIG = {
    'planned': {'color': '#2196F3', 'label': 'Planlandı', 'icon': '📋'},
    'in_progress': {'color': '#FF9800', 'label': 'Devam Ediyor', 'icon': '⚙️'},
    'completed': {'color': '#4CAF50', 'label': 'Tamamlandı', 'icon': '✅'},
    'archived': {'color': '#9E9E9E', 'label': 'Arşiv', 'icon': '📦'}
}


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN CARD WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class PlanCard(QFrame):
    edited = pyqtSignal(Plan)
    deleted = pyqtSignal(int)
    status_changed = pyqtSignal(int, int, str)

    def __init__(self, plan: Plan):
        super().__init__()
        self.plan = plan
        self.init_ui()

    def init_ui(self):
        self.setObjectName("PlanCard")
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Card Base Style
        self.setStyleSheet(f"""
            #PlanCard {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            #PlanCard:hover {{
                border: 1px solid {COLORS['border_light']};
                background-color: {COLORS['bg_hover']};
            }}
        """)
        
        # Drop Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        layout.setSpacing(SPACING['sm'])
        
        # ─── Header Section ───
        header_layout = QHBoxLayout()
        header_layout.setSpacing(SPACING['sm'])
        
        # Priority Indicator (Larger, More Visible)
        priority_cfg = PRIORITY_CONFIG.get(self.plan.priority, PRIORITY_CONFIG['medium'])
        priority_indicator = QLabel()
        priority_indicator.setFixedSize(14, 14)
        priority_indicator.setStyleSheet(f"""
            background-color: {priority_cfg['color']}; 
            border-radius: 7px;
            border: 2px solid {COLORS['bg_card']};
        """)
        priority_indicator.setToolTip(f"Öncelik: {priority_cfg['label']}")
        
        # Title (Bold and Prominent)
        title_lbl = QLabel(self.plan.title)
        title_lbl.setStyleSheet(f"""
            font-size: {FONTS['h2']}px; 
            font-weight: 600; 
            color: {COLORS['text_primary']};
            border: none;
        """)
        
        # Date Badge (Better Formatted)
        date_parts = []
        if self.plan.year:
            date_parts.append(str(self.plan.year))
        if self.plan.month:
            months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                     'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            date_parts.insert(0, months[self.plan.month - 1])
        
        date_text = ' '.join(date_parts) if date_parts else 'Tarihsiz'
        date_lbl = QLabel(f"📅 {date_text}")
        date_lbl.setStyleSheet(f"""
            color: {COLORS['text_muted']}; 
            font-size: {FONTS['caption']}px;
            background-color: {COLORS['bg_main']};
            padding: 6px 12px;
            border-radius: 6px;
            border: none;
        """)
        
        header_layout.addWidget(priority_indicator)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(date_lbl)
        layout.addLayout(header_layout)
        
        # ─── Description Section ───
        if self.plan.description:
            desc_lbl = QLabel(self.plan.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setMaximumHeight(45)  # ~2 lines with proper spacing
            desc_lbl.setStyleSheet(f"""
                color: {COLORS['text_secondary']}; 
                font-size: {FONTS['body']}px; 
                line-height: 1.5;
                border: none;
            """)
            layout.addWidget(desc_lbl)
        
        # Add spacing before progress bar
        layout.addSpacing(SPACING['xs'])
            
        # ─── Progress Bar Section ───
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(SPACING['xs'])
        
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(self.plan.progress)
        self.pbar.setTextVisible(True)
        self.pbar.setFixedHeight(14)
        self.pbar.setFormat(f"%p%")
        
        progress_color = self._get_progress_color(self.plan.progress)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 7px;
                background-color: {COLORS['bg_main']};
                text-align: center;
                color: {COLORS['text_primary']};
                font-size: {FONTS['small']}px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 7px;
            }}
        """)
        progress_layout.addWidget(self.pbar)
        layout.addLayout(progress_layout)

        # ─── Footer Section ───
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(SPACING['xs'])
        
        # Status Badge (Pill Style with Icon)
        status_cfg = STATUS_CONFIG.get(self.plan.status, STATUS_CONFIG['planned'])
        status_lbl = QLabel(f"{status_cfg['icon']} {status_cfg['label']}")
        status_lbl.setStyleSheet(f"""
            background-color: {status_cfg['color']}22;
            color: {status_cfg['color']};
            padding: 8px 14px; 
            border-radius: 14px; 
            font-size: {FONTS['caption']}px; 
            font-weight: 600;
            border: 1px solid {status_cfg['color']}40;
        """)
        footer_layout.addWidget(status_lbl)
        footer_layout.addStretch()
        
        # Quick Complete Button
        if self.plan.status != 'completed':
            btn_check = QPushButton("✓")
            btn_check.setFixedSize(38, 38)
            btn_check.setCursor(Qt.PointingHandCursor)
            btn_check.setToolTip("Hızlıca Tamamla")
            btn_check.setStyleSheet(f"""
                QPushButton {{ 
                    color: {COLORS['success']}; 
                    font-weight: bold; 
                    font-size: 18px;
                    border: 2px solid {COLORS['success']}; 
                    border-radius: 19px; 
                    background-color: transparent;
                }} 
                QPushButton:hover {{ 
                    background-color: {COLORS['success']}; 
                    color: white; 
                }}
            """)
            btn_check.clicked.connect(self.on_quick_complete)
            footer_layout.addWidget(btn_check)

        # Edit Button
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(38, 38)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Düzenle")
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; 
                border: none;
                border-radius: 19px;
                font-size: 17px;
            }}
            QPushButton:hover {{ 
                background-color: {COLORS['primary']}33;
            }}
        """)
        btn_edit.clicked.connect(lambda: self.edited.emit(self.plan))
        
        # Delete Button
        btn_del = QPushButton("🗑️")
        btn_del.setFixedSize(38, 38)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip("Sil")
        btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; 
                border: none;
                border-radius: 19px;
                font-size: 17px;
            }}
            QPushButton:hover {{ 
                background-color: {COLORS['danger']}33;
            }}
        """)
        btn_del.clicked.connect(self.on_delete)

        footer_layout.addWidget(btn_edit)
        footer_layout.addWidget(btn_del)
        layout.addLayout(footer_layout)

    def _get_progress_color(self, value):
        """Get progress color based on completion percentage."""
        if value < 30: return COLORS['danger']
        if value < 70: return COLORS['warning']
        return COLORS['success']

    def on_delete(self):
        """Show confirmation dialog before deleting."""
        msg = QMessageBox()
        msg.setWindowTitle("Plan Sil")
        msg.setText(f"'{self.plan.title}' planını silmek istediğinize emin misiniz?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(f"""
            QMessageBox {{ 
                background-color: {COLORS['bg_card']}; 
                color: {COLORS['text_primary']}; 
            }}
            QPushButton {{ 
                padding: 8px 16px; 
                border-radius: 6px; 
                min-width: 80px;
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        if msg.exec_() == QMessageBox.Yes:
            self.deleted.emit(self.plan.id)

    def on_quick_complete(self):
        """Quick complete action - set progress to 100% and status to completed."""
        self.status_changed.emit(self.plan.id, 100, 'completed')


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN ADD/EDIT DIALOG (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════════

class PlanDialog(QDialog):
    def __init__(self, parent=None, plan: Plan = None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle("✨ Plan Ekle" if not plan else "✏️ Plan Düzenle")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(540)
        self.setMinimumHeight(450)
        self.setMaximumHeight(750)
        
        # Dialog Base Stylesheet
        self.setStyleSheet(f"""
            QDialog {{ 
                background-color: {COLORS['bg_card']}; 
                color: {COLORS['text_primary']}; 
            }}
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(SPACING['lg'], SPACING['md'], SPACING['lg'], SPACING['lg'])

        # ─── Form: Title ───
        lbl_title = self._create_label("BAŞLIK *")
        layout.addWidget(lbl_title)
        
        self.inp_title = QLineEdit()
        self.inp_title.setFixedHeight(44)
        self.inp_title.setPlaceholderText("Plan başlığını girin...")
        self.inp_title.setStyleSheet(self._get_input_style())
        if self.plan: 
            self.inp_title.setText(self.plan.title)
        layout.addWidget(self.inp_title)

        layout.addSpacing(SPACING['xs'])

        # ─── Form: Description ───
        layout.addWidget(self._create_label("AÇIKLAMA"))
        
        self.inp_desc = QTextEdit()
        self.inp_desc.setMinimumHeight(120)
        self.inp_desc.setMaximumHeight(150)
        self.inp_desc.setPlaceholderText("Plan açıklaması (opsiyonel)...")
        self.inp_desc.setStyleSheet(self._get_input_style())
        if self.plan: 
            self.inp_desc.setText(self.plan.description)
        layout.addWidget(self.inp_desc)

        layout.addSpacing(SPACING['xs'])

        # ─── Form: Priority (Separate Dropdown with Icons) ───
        layout.addWidget(self._create_label("ÖNCELİK"))
        
        self.cmb_priority = QComboBox()
        self.cmb_priority.setFixedHeight(44)
        self.cmb_priority.addItems([
            "🔵 Düşük", 
            "🟡 Orta", 
            "🔴 Yüksek"
        ])
        self.cmb_priority.setStyleSheet(self._get_combo_style())
        self.cmb_priority.setCursor(Qt.PointingHandCursor)
        priority_map = {'low': 0, 'medium': 1, 'high': 2}
        if self.plan: 
            self.cmb_priority.setCurrentIndex(priority_map.get(self.plan.priority, 1))
        else: 
            self.cmb_priority.setCurrentIndex(1)
        layout.addWidget(self.cmb_priority)

        # ─── Form: Status (Edit Mode Only - Separate Dropdown) ───
        if self.plan:
            layout.addSpacing(SPACING['xs'])
            layout.addWidget(self._create_label("DURUM"))
            
            self.cmb_status = QComboBox()
            self.cmb_status.setFixedHeight(44)
            self.cmb_status.addItems([
                "📋 Planlandı", 
                "⚙️ Devam Ediyor", 
                "✅ Tamamlandı", 
                "📦 Arşiv"
            ])
            self.cmb_status.setStyleSheet(self._get_combo_style())
            self.cmb_status.setCursor(Qt.PointingHandCursor)
            status_map = {'planned': 0, 'in_progress': 1, 'completed': 2, 'archived': 3}
            self.cmb_status.setCurrentIndex(status_map.get(self.plan.status, 0))
            layout.addWidget(self.cmb_status)

            layout.addSpacing(SPACING['sm'])

            # ─── Form: Progress Slider ───
            progress_header = QHBoxLayout()
            progress_header.addWidget(self._create_label("İLERLEME"))
            
            # Large Progress Value Display
            self.lbl_progress_value = QLabel(f"%{self.plan.progress}")
            self.lbl_progress_value.setStyleSheet(f"""
                font-size: 26px;
                font-weight: bold;
                color: {self._get_progress_color_for_value(self.plan.progress)};
                border: none;
            """)
            progress_header.addStretch()
            progress_header.addWidget(self.lbl_progress_value)
            layout.addLayout(progress_header)
            
            self.slider_progress = QSlider(Qt.Horizontal)
            self.slider_progress.setRange(0, 100)
            self.slider_progress.setValue(self.plan.progress)
            self.slider_progress.setSingleStep(5)
            self.slider_progress.setPageStep(10)
            self.slider_progress.setFixedHeight(32)
            self.slider_progress.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 10px;
                    background: {COLORS['bg_main']};
                    border-radius: 5px;
                }}
                QSlider::handle:horizontal {{
                    background: {COLORS['primary']};
                    border: 3px solid {COLORS['bg_card']};
                    width: 24px;
                    height: 24px;
                    margin: -9px 0;
                    border-radius: 12px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {COLORS['primary_hover']};
                    border: 3px solid {COLORS['primary']}44;
                    width: 26px;
                    height: 26px;
                    margin: -10px 0;
                    border-radius: 13px;
                }}
                QSlider::sub-page:horizontal {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 {COLORS['danger']}, 
                        stop:0.5 {COLORS['warning']}, 
                        stop:1 {COLORS['success']});
                    border-radius: 5px;
                }}
            """)
            self.slider_progress.valueChanged.connect(self._on_progress_changed)
            layout.addWidget(self.slider_progress)

        layout.addSpacing(SPACING['md'])

        # ─── Action Buttons ───
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(44)
        btn_cancel.setMinimumWidth(100)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; 
                color: {COLORS['text_secondary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                font-weight: 600;
                font-size: {FONTS['body']}px;
                padding: 0 {SPACING['md']}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['border_light']};
                color: {COLORS['text_primary']};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("💾 Kaydet")
        btn_save.setFixedHeight(44)
        btn_save.setMinimumWidth(120)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']}; 
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: {FONTS['body']}px;
                padding: 0 {SPACING['md']}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_hover']};
            }}
        """)
        btn_save.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _create_label(self, text):
        """Create styled form label with uppercase text."""
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: {FONTS['caption']}px;
            font-weight: 700;
            color: {COLORS['text_secondary']};
            background-color: transparent;
            margin-bottom: 4px;
            border: none;
            letter-spacing: 0.5px;
        """)
        return lbl

    def _get_input_style(self):
        """Return consistent input styling with focus states."""
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {COLORS['bg_input']}; 
                color: {COLORS['text_primary']}; 
                border: 1px solid {COLORS['border']}; 
                padding: 12px 16px; 
                border-radius: 8px;
                font-size: {FONTS['body']}px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['bg_card']};
            }}
            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """

    def _get_combo_style(self):
        """Return consistent combobox styling with dropdown improvements."""
        return f"""
            QComboBox {{
                background-color: {COLORS['bg_input']}; 
                color: {COLORS['text_primary']}; 
                border: 1px solid {COLORS['border']}; 
                padding: 12px 16px; 
                border-radius: 8px;
                font-size: {FONTS['body']}px;
            }}
            QComboBox:hover {{
                border: 1px solid {COLORS['border_light']};
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 30px;
                border: none;
                background-color: transparent;
            }}
            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {COLORS['text_muted']};
            }}
            QComboBox::down-arrow:hover {{
                border-top: 8px solid {COLORS['text_primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                selection-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px 0;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 40px;
                padding: 10px 16px;
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: none;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """

    def _get_progress_color_for_value(self, value):
        """Get progress color based on value."""
        if value < 30: return COLORS['danger']
        if value < 70: return COLORS['warning']
        return COLORS['success']

    def _on_progress_changed(self, value):
        """Update progress value label with color animation."""
        self.lbl_progress_value.setText(f"%{value}")
        self.lbl_progress_value.setStyleSheet(f"""
            font-size: 26px;
            font-weight: bold;
            color: {self._get_progress_color_for_value(value)};
            border: none;
        """)

    def get_data(self):
        """Extract and return form data."""
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
            
            # Auto-sync: If progress is 100%, mark as completed
            if data['progress'] == 100 and data['status'] != 'completed':
                data['status'] = 'completed'
            # Auto-sync: If status is completed, set progress to 100%
            elif data['status'] == 'completed' and data['progress'] < 100:
                data['progress'] = 100
                
        return data


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS WIDGET (PILL BADGES)
# ═══════════════════════════════════════════════════════════════════════════════

class PlanStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, SPACING['xs'], 0, SPACING['md'])
        layout.setSpacing(SPACING['sm'])
        
        self.lbl_total = self._create_badge("📊", "0", "Toplam", COLORS['primary'])
        self.lbl_completed = self._create_badge("✅", "0", "Tamamlanan", COLORS['success'])
        self.lbl_pending = self._create_badge("⏳", "0", "Bekleyen", COLORS['warning'])
        
        layout.addWidget(self.lbl_total)
        layout.addWidget(self.lbl_completed)
        layout.addWidget(self.lbl_pending)
        layout.addStretch()

    def _create_badge(self, icon, count, label, color):
        """Create a modern pill-shaped statistics badge."""
        badge = QFrame()
        badge.setObjectName("statsBadge")
        badge.setStyleSheet(f"""
            #statsBadge {{
                background-color: {color}1a; 
                border: 1px solid {color}40;
                border-radius: 20px;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        h = QHBoxLayout(badge)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(12)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px;")
        
        count_lbl = QLabel(count)
        count_lbl.setObjectName("count")
        count_lbl.setStyleSheet(f"""
            font-size: 18px; 
            font-weight: bold; 
            color: {color};
        """)
        
        text_lbl = QLabel(label)
        text_lbl.setStyleSheet(f"""
            font-size: 13px; 
            color: {COLORS['text_secondary']};
            font-weight: 500;
        """)
        
        h.addWidget(icon_lbl)
        h.addWidget(count_lbl)
        h.addWidget(text_lbl)
        
        badge.count_label = count_lbl
        return badge

    def update_stats(self, plans):
        """Update badge counts based on plans list."""
        total = len(plans)
        completed = sum(1 for p in plans if p.status == 'completed')
        pending = total - completed
        
        self.lbl_total.count_label.setText(str(total))
        self.lbl_completed.count_label.setText(str(completed))
        self.lbl_pending.count_label.setText(str(pending))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PLANS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class PlansPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scope = 'monthly'
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['lg'], SPACING['md'], SPACING['lg'], SPACING['md'])

        # ═══════════════════════════════════════════════════════════════════════
        # HEADER SECTION
        # ═══════════════════════════════════════════════════════════════════════
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']}; 
                border-radius: 12px;
            }}
        """)
        
        # Header Shadow
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(15)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header_shadow.setOffset(0, 2)
        header_frame.setGraphicsEffect(header_shadow)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(SPACING['md'], SPACING['sm'], SPACING['md'], SPACING['sm'])
        header_layout.setSpacing(SPACING['md'])
        
        # Page Title (H1)
        lbl_head = QLabel("📅 Planlama & Hedefler")
        lbl_head.setStyleSheet(f"""
            color: {COLORS['text_primary']}; 
            font-size: {FONTS['h1']}px; 
            font-weight: bold;
            border: none;
        """)
        header_layout.addWidget(lbl_head)
        header_layout.addStretch()

        # ─── Scope Toggle (Segment Control) ───
        toggle_container = QFrame()
        toggle_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_main']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(4, 4, 4, 4)
        toggle_layout.setSpacing(4)
        
        self.btn_monthly = QPushButton("📆 Aylık")
        self.btn_monthly.setCheckable(True)
        self.btn_monthly.setChecked(True)
        self.btn_monthly.setFixedHeight(36)
        self.btn_monthly.setCursor(Qt.PointingHandCursor)
        self.btn_monthly.clicked.connect(lambda: self.set_scope('monthly'))
        
        self.btn_yearly = QPushButton("📊 Yıllık")
        self.btn_yearly.setCheckable(True)
        self.btn_yearly.setFixedHeight(36)
        self.btn_yearly.setCursor(Qt.PointingHandCursor)
        self.btn_yearly.clicked.connect(lambda: self.set_scope('yearly'))
        
        toggle_layout.addWidget(self.btn_monthly)
        toggle_layout.addWidget(self.btn_yearly)
        header_layout.addWidget(toggle_container)

        # ─── Date Selectors ───
        cmb_style = f"""
            QComboBox {{
                background-color: {COLORS['bg_main']}; 
                color: {COLORS['text_primary']}; 
                border: 1px solid {COLORS['border']}; 
                padding: 8px 16px; 
                border-radius: 6px;
                font-size: {FONTS['body']}px;
                font-weight: 500;
                min-width: 90px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['border_light']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text_muted']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 0;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 32px;
                padding: 6px 12px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """
        
        # Year Selector
        self.cmb_year = QComboBox()
        self.cmb_year.addItems([str(y) for y in range(self.current_year, self.current_year + 3)])
        self.cmb_year.setCurrentText(str(self.current_year))
        self.cmb_year.currentIndexChanged.connect(self.refresh_data)
        self.cmb_year.setStyleSheet(cmb_style)
        self.cmb_year.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.cmb_year)
        
        # Month Selector
        self.cmb_month = QComboBox()
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        self.cmb_month.addItems(months)
        self.cmb_month.setCurrentIndex(self.current_month - 1)
        self.cmb_month.currentIndexChanged.connect(self.refresh_data)
        self.cmb_month.setStyleSheet(cmb_style)
        self.cmb_month.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.cmb_month)

        # ─── New Plan Button ───
        btn_add = QPushButton("➕ Yeni Plan")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']}; 
                color: white; 
                border-radius: 8px; 
                padding: 0 {SPACING['md']}px; 
                font-weight: 600;
                font-size: {FONTS['body']}px;
            }}
            QPushButton:hover {{ 
                background-color: {COLORS['success_hover']}; 
            }}
        """)
        btn_add.clicked.connect(self.add_plan_dialog)
        header_layout.addWidget(btn_add)
        
        layout.addWidget(header_frame)
        
        # ═══════════════════════════════════════════════════════════════════════
        # STATS SECTION
        # ═══════════════════════════════════════════════════════════════════════
        self.stats_widget = PlanStatsWidget()
        layout.addWidget(self.stats_widget)

        # ═══════════════════════════════════════════════════════════════════════
        # CONTENT AREA (Scrollable Cards)
        # ═══════════════════════════════════════════════════════════════════════
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ 
                border: none; 
                background-color: transparent; 
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_main']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['border_light']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.content_container)
        self.cards_layout.setSpacing(SPACING['sm'])
        self.cards_layout.setContentsMargins(0, 0, SPACING['xs'], 0)
        self.cards_layout.addStretch()
        
        self.scroll.setWidget(self.content_container)
        layout.addWidget(self.scroll)

    def set_scope(self, scope):
        """Set the time scope (monthly/yearly) and update UI."""
        self.scope = scope
        
        toggle_style_checked = f"""
            QPushButton {{
                background-color: {COLORS['primary']}; 
                color: white;
                border: none;
                padding: 0 {SPACING['sm']}px;
                font-weight: 600;
                font-size: {FONTS['body']}px;
                border-radius: 6px;
            }}
        """
        toggle_style_unchecked = f"""
            QPushButton {{
                background-color: transparent; 
                color: {COLORS['text_muted']};
                border: none;
                padding: 0 {SPACING['sm']}px;
                font-weight: 500;
                font-size: {FONTS['body']}px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_secondary']};
                background-color: {COLORS['bg_hover']};
            }}
        """
        
        if scope == 'monthly':
            self.btn_monthly.setChecked(True)
            self.btn_yearly.setChecked(False)
            self.btn_monthly.setStyleSheet(toggle_style_checked)
            self.btn_yearly.setStyleSheet(toggle_style_unchecked)
            self.cmb_month.setVisible(True)
        else:
            self.btn_monthly.setChecked(False)
            self.btn_yearly.setChecked(True)
            self.btn_monthly.setStyleSheet(toggle_style_unchecked)
            self.btn_yearly.setStyleSheet(toggle_style_checked)
            self.cmb_month.setVisible(False)
        
        self.refresh_data()

    def refresh_data(self):
        """Fetch and display plans based on current filters."""
        year = int(self.cmb_year.currentText())
        month = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
        self.controller.get_plans(self.scope, year, month, self.on_data_loaded)

    def on_data_loaded(self, plans):
        """Handle loaded plans data and update UI."""
        # Clear existing items
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not plans:
            # Empty State
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setAlignment(Qt.AlignCenter)
            
            empty_icon = QLabel("📭")
            empty_icon.setStyleSheet(f"font-size: 64px; border: none;")
            empty_icon.setAlignment(Qt.AlignCenter)
            
            empty_lbl = QLabel("Bu dönem için henüz plan oluşturulmamış")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"""
                color: {COLORS['text_muted']}; 
                font-size: {FONTS['h2']}px;
                margin-top: {SPACING['sm']}px;
                border: none;
            """)
            
            empty_hint = QLabel("Yukarıdaki '+ Yeni Plan' butonunu kullanarak başlayın")
            empty_hint.setAlignment(Qt.AlignCenter)
            empty_hint.setStyleSheet(f"""
                color: {COLORS['text_muted']}; 
                font-size: {FONTS['body']}px;
                border: none;
            """)
            
            empty_layout.addStretch()
            empty_layout.addWidget(empty_icon)
            empty_layout.addSpacing(SPACING['sm'])
            empty_layout.addWidget(empty_lbl)
            empty_layout.addSpacing(SPACING['xs'])
            empty_layout.addWidget(empty_hint)
            empty_layout.addStretch()
            
            self.cards_layout.addWidget(empty_container)
        
        for plan in plans:
            card = PlanCard(plan)
            card.edited.connect(self.edit_plan_dialog)
            card.deleted.connect(self.delete_plan)
            card.status_changed.connect(self.update_status)
            self.cards_layout.addWidget(card)
            
        self.cards_layout.addStretch()
        self.stats_widget.update_stats(plans)

    def add_plan_dialog(self):
        """Show dialog to add a new plan."""
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
        """Show dialog to edit an existing plan."""
        dialog = PlanDialog(self, plan)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.controller.update_plan(
                plan.id, data['title'], data['description'], data['status'], 
                data['progress'], data['priority'], self.on_operation_finished
            )

    def delete_plan(self, plan_id):
        """Delete a plan by ID."""
        self.controller.delete_plan(plan_id, self.on_operation_finished)

    def update_status(self, plan_id, progress, status):
        """Update plan progress and status."""
        self.controller.update_plan_progress(plan_id, progress, status, lambda res: self.refresh_data())

    def on_operation_finished(self, result):
        """Handle the result of a plan operation."""
        if isinstance(result, tuple):
            success, msg = result
        else:
            success = result
            msg = ""
            
        if success:
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Hata", msg)