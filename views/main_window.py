# views/main_window.py
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame,
                             QShortcut, QSizePolicy, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QAbstractAnimation, QEasingCurve
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QPalette
from services.icon_service import IconService
from views.widgets.custom_title_bar import CustomTitleBar

from controllers.main_controller import MainController
from views.pages.add_page import AddPage
from views.pages.list_page import ListPage
from views.pages.stats_page import StatsPage
from views.pages.compare_page import ComparePage
from views.pages.pdf_page import PdfPage
from views.pages.settings_page import SettingsPage
from views.pages.plans_page import PlansPage
from views.pages.suggestion_page import SuggestionPage
from views.pages.analysis_page import TrendAnalysisPage

import os
from utils import get_resource_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Faaliyet Takip Sistemi")
        self.setGeometry(100, 100, 1150, 750)

        icon_path = get_resource_path(os.path.join("icons", "icon.ico"))
        if not os.path.exists(icon_path):
             icon_path = get_resource_path(os.path.join("icons", "icon.png"))

        self.setWindowIcon(QIcon(icon_path))

        self.controller = MainController()
        self._animating = False

        # Ana Widget — dikey: title_bar üstte, içerik altta
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        outer_layout = QVBoxLayout(self.central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Özel başlık çubuğu
        self.title_bar = CustomTitleBar(self)
        outer_layout.addWidget(self.title_bar)

        # Yatay: sidebar + içerik
        content_row = QWidget()
        self.main_layout = QHBoxLayout(content_row)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        outer_layout.addWidget(content_row, 1)

        # 1. Modern Sidebar
        self.setup_sidebar()

        # 2. İçerik Alanı
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(25, 25, 25, 0)

        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        self.main_layout.addWidget(self.content_area)

        # Sayfaları Başlat
        self.init_pages()
        self.setup_shortcuts()

        # İlk butonu aktif yap
        self.update_active_button(0)

    def setup_sidebar(self):
        """Sol taraftaki modern menüyü oluşturur."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar") 
        self.sidebar.setFixedWidth(240)
        
        # Sidebar Stili - Daha Açık Lacivert Gradient (#2C3E50 bazlı)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #34495E, stop:1 #2C3E50);
                border-right: 1px solid #334155;
            }
            QLabel { color: white; }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 10)
        sidebar_layout.setSpacing(8)

        # --- Logo Alanı ---
        logo_area = QWidget()
        logo_area.setFixedHeight(120)
        logo_layout = QVBoxLayout(logo_area)
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(5)
        
        lbl_icon = QLabel()
        lbl_icon.setPixmap(IconService.pixmap("app_logo", 48))
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent;")
        
        lbl_title = QLabel("FAALİYET\nTAKİP")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: white; font-size: 18px; font-weight: 800; font-family: 'Segoe UI'; letter-spacing: 1px; background: transparent;")
        
        logo_layout.addWidget(lbl_icon)
        logo_layout.addWidget(lbl_title)
        
        sidebar_layout.addWidget(logo_area)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #5D6D7E; margin: 0 20px;")
        line.setFixedHeight(1)
        sidebar_layout.addWidget(line)
        sidebar_layout.addSpacing(10)

        # --- Menü Butonları ---
        self.buttons = []
        
        # (Label, IconName, Index)
        menu_items = [
            ("Ekle",        "nav_add",      0),
            ("Listele",     "nav_list",     1),
            ("İstatistik",  "nav_stats",    2),
            ("Karşılaştır", "nav_compare",  3),
            ("PDF Rapor",   "nav_pdf",      4),
            ("Hedefler",    "nav_plans",    5),
            ("Keşfet",      "nav_discover", 6),
            ("Ayarlar",     "nav_settings", 7),
        ]
        
        for text, icon, idx in menu_items:
            self.add_sidebar_btn(text, icon, idx, sidebar_layout)

        sidebar_layout.addStretch() 
        
        # Geliştirici Label
        dev_label = QLabel("Geliştirici : MYY yazılım")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet("color: #909497; font-size: 11px; font-weight: 600; margin-bottom: 15px; letter-spacing: 0.5px;")
        sidebar_layout.addWidget(dev_label)
        
        # Çıkış butonu kaldırıldı

        self.main_layout.addWidget(self.sidebar)

    def add_sidebar_btn(self, text, icon_name, index, layout):
        btn = QPushButton(f"  {text}")
        btn.setObjectName(f"SidebarBtn_{index}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(IconService.get(icon_name))
        btn.setIconSize(QSize(20, 20))

        self.set_btn_style(btn, False)

        btn.clicked.connect(lambda: self.switch_page(index))
        layout.addWidget(btn)
        self.buttons.append(btn)

    def set_btn_style(self, btn, active):
        # Font boyutu 14px -> 17px yapıldı
        if active:
            # Aktif Buton Stili (Glow ve Gradient)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                    color: white;
                    text-align: left;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 17px;
                    margin: 2px 12px;
                }
            """)
        else:
            # Pasif Buton Stili
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #BDC3C7;
                    text-align: left;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 17px;
                    margin: 2px 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                }
            """)

    def update_active_button(self, index):
        for i, btn in enumerate(self.buttons):
            self.set_btn_style(btn, i == index)

    def init_pages(self):
        self.add_page = AddPage(self.controller)
        self.stacked_widget.addWidget(self.add_page)

        self.list_page = ListPage(self.controller)
        self.stacked_widget.addWidget(self.list_page)

        self.stats_page = StatsPage(self.controller)
        self.stacked_widget.addWidget(self.stats_page)

        self.compare_page = ComparePage(self.controller)
        self.stacked_widget.addWidget(self.compare_page)
        
        self.pdf_page = PdfPage(self.controller)
        self.stacked_widget.addWidget(self.pdf_page)

        self.plans_page = PlansPage(self.controller)
        self.stacked_widget.addWidget(self.plans_page)

        self.suggestion_page = SuggestionPage() 
        self.stacked_widget.addWidget(self.suggestion_page)

        self.settings_page = SettingsPage(self.controller)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Trend Analysis Page (Stacked navigation - not in sidebar)
        self.trend_analysis_page = TrendAnalysisPage(self.controller)
        self.stacked_widget.addWidget(self.trend_analysis_page)
        
        # Connect signals
        self.stats_page.open_trend_analysis.connect(self.open_trend_analysis)
        self.trend_analysis_page.back_clicked.connect(self.close_trend_analysis)

        # Observer: aktivite veya plan değişince aktif sayfayı yenile
        self.controller.activity_changed.connect(self._on_activity_changed)
        self.controller.plan_changed.connect(self._on_plan_changed)

    def switch_page(self, index):
        if self._animating or self.stacked_widget.currentIndex() == index:
            return
        self._animating = True

        if index != 3 and not self.sidebar.isVisible():
            self.sidebar.show()

        self.stacked_widget.setCurrentIndex(index)
        self.update_active_button(index)

        # Animate a child-less overlay on content_area — avoids QPainter conflicts
        # that arise when QGraphicsOpacityEffect is applied directly to page widgets
        # that have descendant widgets with their own QGraphicsDropShadowEffect.
        overlay = QWidget(self.content_area)
        overlay.setAutoFillBackground(True)
        pal = overlay.palette()
        pal.setColor(QPalette.Window, QColor("#FFFFFF"))
        overlay.setPalette(pal)
        overlay.resize(self.content_area.size())
        overlay.show()
        overlay.raise_()

        eff = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(eff)
        eff.setOpacity(0.85)

        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(200)
        anim.setStartValue(0.85)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def _done():
            overlay.deleteLater()
            self._animating = False
            new_widget = self.stacked_widget.currentWidget()
            if hasattr(new_widget, 'refresh_data'):
                new_widget.refresh_data()
            elif hasattr(new_widget, 'refresh_statistics'):
                new_widget.refresh_statistics()

        anim.finished.connect(_done)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(self.next_page)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(self.prev_page)

    def next_page(self):
        idx = (self.stacked_widget.currentIndex() + 1) % self.stacked_widget.count()
        self.switch_page(idx)

    def prev_page(self):
        idx = (self.stacked_widget.currentIndex() - 1 + self.stacked_widget.count()) % self.stacked_widget.count()
        self.switch_page(idx)
    
    def _refresh_current(self, page):
        """Sayfa şu an aktifse yeniler."""
        if self.stacked_widget.currentWidget() is page:
            if hasattr(page, 'refresh_data'):
                page.refresh_data()
            elif hasattr(page, 'refresh_statistics'):
                page.refresh_statistics()

    def _on_activity_changed(self):
        for page in (self.list_page, self.stats_page, self.compare_page, self.pdf_page):
            self._refresh_current(page)

    def _on_plan_changed(self):
        self._refresh_current(self.plans_page)

    def open_trend_analysis(self):
        idx = self.stacked_widget.indexOf(self.trend_analysis_page)
        self.switch_page(idx)

    def close_trend_analysis(self):
        self.switch_page(2)  # İstatistik index 2