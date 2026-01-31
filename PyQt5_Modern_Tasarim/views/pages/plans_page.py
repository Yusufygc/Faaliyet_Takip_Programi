# views/pages/plans_page.py
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QScrollArea, QFrame, 
                             QDialog, QLineEdit, QTextEdit, QProgressBar, 
                             QSlider, QMessageBox, QGraphicsDropShadowEffect,
                             QGridLayout, QSizePolicy, QCheckBox, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QCursor
from datetime import datetime
from models import Plan
from views.styles import COLORS as GLOBAL_COLORS

# ═══════════════════════════════════════════════════════════════════════════════
# MODERN DESIGN SYSTEM & COLORS
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'bg_main': '#F4F7F6',      # Çok hafif gri-mavi arka plan
    'bg_card': '#FFFFFF',      # Kartlar için saf beyaz
    'text_main': '#2C3E50',    # Ana metin rengi
    'text_sub': '#7F8C8D',     # Alt metin rengi
    'primary': GLOBAL_COLORS['primary'],
    'primary_gradient': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {GLOBAL_COLORS['primary']}, stop:1 #3498DB)",
    'success_gradient': "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27AE60, stop:1 #2ECC71)",
    'danger': '#E74C3C',
    'border': '#E0E6ED'
}

# Öncelik Renkleri ve İkonları
PRIORITY_CFG = {
    'low': {'bg': '#E8F6F3', 'fg': '#1ABC9C', 'label': 'Düşük', 'dot': '🟢'},
    'medium': {'bg': '#FEF9E7', 'fg': '#F1C40F', 'label': 'Orta', 'dot': '🟡'},
    'high': {'bg': '#FDEDEC', 'fg': '#E74C3C', 'label': 'Yüksek', 'dot': '🔴'}
}

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class ModernCard(QFrame):
    """Hover animasyonlu temel kart sınıfı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)
        
        # Gölge Efekti
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 15)) # %15 Opaklık
        self.setGraphicsEffect(self.shadow)

        # Animasyon Değişkenleri
        self.default_y = 4
        self.hover_y = 8
        self.default_blur = 20
        self.hover_blur = 30

    def enterEvent(self, event):
        # Hover durumunda gölgeyi ve pozisyon hissini değiştir
        self.shadow.setYOffset(self.hover_y)
        self.shadow.setBlurRadius(self.hover_blur)
        self.shadow.setColor(QColor(0, 0, 0, 25)) # Biraz daha koyu gölge
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Normal duruma dön
        self.shadow.setYOffset(self.default_y)
        self.shadow.setBlurRadius(self.default_blur)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        super().leaveEvent(event)

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

        # ─── 1. Header (Öncelik - Tarih) ───
        header = QHBoxLayout()
        
        # Öncelik Badge (Hap şeklinde)
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
        
        # Tarih
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

        # ─── 2. İçerik (Başlık - Açıklama) ───
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

        # ─── 3. Progress Bar ───
        progress_container = QVBoxLayout()
        progress_container.setSpacing(4)
        
        # Label Row
        pl_row = QHBoxLayout()
        pl_lbl = QLabel("İlerleme")
        pl_lbl.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 11px; font-weight: 600;")
        pl_val = QLabel(f"%{self.plan.progress}")
        pl_val.setStyleSheet(f"color: {COLORS['primary']}; font-size: 12px; font-weight: 800;")
        pl_row.addWidget(pl_lbl)
        pl_row.addStretch()
        pl_row.addWidget(pl_val)
        
        # Bar
        pbar = QProgressBar()
        pbar.setRange(0, 100)
        pbar.setValue(self.plan.progress)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(8)
        
        # Duruma göre renk (Degrade)
        bar_color = COLORS['success_gradient'] if self.plan.progress == 100 else COLORS['primary_gradient']
        if self.plan.progress < 30: bar_color = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E74C3C, stop:1 #C0392B)"
        
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

        # ─── 4. Footer (Durum - Butonlar) ───
        footer = QHBoxLayout()
        footer.setSpacing(10)
        
        # Status Text
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

        # Action Buttons (Circle)
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
                    background-color: {color}1A; /* %10 Opacity */
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


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN DIALOG (MODERN FORM)
# ═══════════════════════════════════════════════════════════════════════════════

class PlanDialog(QDialog):
    def __init__(self, parent=None, plan: Plan = None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle("Plan Oluştur" if not plan else "Planı Düzenle")
        self.setFixedWidth(480)
        self.setStyleSheet(f"background-color: {COLORS['bg_card']};")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık Alanı
        title_lbl = QLabel("✨ Yeni Plan" if not self.plan else "✏️ Planı Düzenle")
        title_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {COLORS['text_main']}; margin-bottom: 10px;")
        layout.addWidget(title_lbl)

        # ─── Inputs ───
        
        # 1. Başlık
        layout.addWidget(self._make_label("BAŞLIK"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Hedefinizi buraya yazın...")
        self.inp_title.setStyleSheet(self._input_style())
        if self.plan: self.inp_title.setText(self.plan.title)
        layout.addWidget(self.inp_title)

        # 2. Açıklama
        layout.addWidget(self._make_label("AÇIKLAMA"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Detaylar (opsiyonel)...")
        self.inp_desc.setMinimumHeight(80)
        self.inp_desc.setMaximumHeight(100)
        self.inp_desc.setStyleSheet(self._input_style())
        if self.plan: self.inp_desc.setText(self.plan.description)
        layout.addWidget(self.inp_desc)

        # 3. Öncelik (Custom Combobox)
        layout.addWidget(self._make_label("ÖNCELİK"))
        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["🔵 Düşük Öncelik", "🟡 Orta Öncelik", "🔴 Yüksek Öncelik"])
        self.cmb_priority.setStyleSheet(self._combo_style())
        
        priority_map = {'low': 0, 'medium': 1, 'high': 2}
        idx = priority_map.get(self.plan.priority, 1) if self.plan else 1
        self.cmb_priority.setCurrentIndex(idx)
        layout.addWidget(self.cmb_priority)

        # 4. Durum & İlerleme (Sadece Düzenlerken)
        if self.plan:
            layout.addWidget(self._make_label("DURUM"))
            self.cmb_status = QComboBox()
            self.cmb_status.addItems(["📋 Planlandı", "⚙️ Sürüyor", "✅ Tamamlandı", "📦 Arşiv"])
            self.cmb_status.setStyleSheet(self._combo_style())
            
            st_map = {'planned': 0, 'in_progress': 1, 'completed': 2, 'archived': 3}
            self.cmb_status.setCurrentIndex(st_map.get(self.plan.status, 0))
            layout.addWidget(self.cmb_status)
            
            # Slider Area
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
            
            # box-shadow kaldırıldı
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

        # ─── Butonlar ───
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
        # Transform (rotate) kaldırıldı, yerine border-triangle eklendi
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
            'priority': priority_map.get(self.cmb_priority.currentIndex(), 'medium')
        }
        if self.plan:
            st_map = {0: 'planned', 1: 'in_progress', 2: 'completed', 3: 'archived'}
            data['status'] = st_map.get(self.cmb_status.currentIndex(), 'planned')
            data['progress'] = self.slider.value()
            if data['progress'] == 100: data['status'] = 'completed'
            elif data['status'] == 'completed' and data['progress'] < 100: data['progress'] = 100
        return data


# ═══════════════════════════════════════════════════════════════════════════════
# STATS WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class StatCard(ModernCard):
    def __init__(self, title, icon, color):
        super().__init__()
        self.setFixedHeight(100)
        self.setFixedWidth(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Üst Satır (Icon + Sayı)
        row = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")
        
        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {color}; background: transparent;")
        
        row.addWidget(lbl_icon)
        row.addStretch()
        row.addWidget(self.lbl_count)
        
        # Alt Satır (Başlık)
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


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
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
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # ─── 1. Header & Filters ───
        header = QHBoxLayout()
        
        title = QLabel("Planlama & Hedefler")
        title.setStyleSheet(f"font-size: 28px; font-weight: 900; color: {COLORS['text_main']};")
        header.addWidget(title)
        header.addStretch()

        # Filtre Kapsayıcısı (Beyaz Hap Şeklinde)
        filter_box = QFrame()
        filter_box.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 25px;
                padding: 4px;
            }}
        """)
        # Filtre kutusuna hafif gölge
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setColor(QColor(0,0,0,10)); shadow.setOffset(0,2)
        filter_box.setGraphicsEffect(shadow)

        fb_layout = QHBoxLayout(filter_box)
        fb_layout.setContentsMargins(10, 4, 10, 4)
        fb_layout.setSpacing(8)

        # Toggle Buttons
        self.btn_m = self._make_toggle("Aylık", True)
        self.btn_y = self._make_toggle("Yıllık", False)
        self.btn_m.clicked.connect(lambda: self.set_scope('monthly'))
        self.btn_y.clicked.connect(lambda: self.set_scope('yearly'))
        fb_layout.addWidget(self.btn_m)
        fb_layout.addWidget(self.btn_y)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #E0E0E0; margin: 5px;")
        line.setFixedWidth(1)
        fb_layout.addWidget(line)

        # Comboboxes
        self.cmb_year = self._make_header_combo([str(y) for y in range(self.current_year, self.current_year + 3)])
        self.cmb_year.currentIndexChanged.connect(self.refresh_data)
        fb_layout.addWidget(self.cmb_year)
        
        self.cmb_month = self._make_header_combo(['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'])
        self.cmb_month.setCurrentIndex(self.current_month - 1)
        self.cmb_month.currentIndexChanged.connect(self.refresh_data)
        fb_layout.addWidget(self.cmb_month)
        
        header.addWidget(filter_box)

        # Yeni Plan Butonu
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

        # ─── 2. İstatistikler ───
        self.stats = PlanStatsWidget()
        layout.addWidget(self.stats)

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
        self.card_layout = QVBoxLayout(container)
        self.card_layout.setSpacing(20)
        self.card_layout.setContentsMargins(0, 10, 10, 10)
        self.card_layout.addStretch()
        
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
        # Oku ve butonu tamamen gizliyoruz, sadece text kalıyor
        c.setStyleSheet(f"""
            QComboBox {{
                background: transparent; 
                border: none; 
                color: {COLORS['text_main']}; 
                font-weight: bold; 
                padding: 4px 10px; 
                min-width: 50px;
            }}
            /* Dropdown buton alanını gizle */
            QComboBox::drop-down {{
                border: none;
                width: 0px; 
            }}
            /* Oku gizle */
            QComboBox::down-arrow {{
                image: none;
            }}
            
            /* Tıklanabilir hissi için hover */
            QComboBox:hover {{
                background-color: #F5F7FA;
                border-radius: 12px;
                color: {COLORS['primary']};
            }}
            
            /* Popup Listesi */
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

    def on_loaded(self, plans):
        # Temizle
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not plans:
            lbl = QLabel("📭 Bu dönem için henüz bir plan yok.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {COLORS['text_sub']}; font-size: 16px; margin-top: 40px;")
            self.card_layout.addWidget(lbl)
        
        for p in plans:
            card = PlanCard(p)
            card.edited.connect(self.edit_plan)
            card.deleted.connect(self.delete_plan)
            card.status_changed.connect(self.update_status)
            self.card_layout.addWidget(card)
        
        self.card_layout.addStretch()
        self.stats.update_stats(plans)

    def add_plan_dialog(self):
        d = PlanDialog(self)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            y = int(self.cmb_year.currentText())
            m = self.cmb_month.currentIndex() + 1 if self.scope == 'monthly' else None
            self.controller.add_plan(data['title'], data['description'], self.scope, y, m, data['priority'], self.on_finished)

    def edit_plan(self, plan):
        d = PlanDialog(self, plan)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            self.controller.update_plan(plan.id, data['title'], data['description'], data['status'], data['progress'], data['priority'], self.on_finished)

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