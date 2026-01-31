# views/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame, QStatusBar, 
                             QShortcut, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon, QColor

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
from views.styles import STYLESHEET 

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Faaliyet Takip Sistemi")
        self.setGeometry(100, 100, 1150, 750)
        
        icon_path = os.path.join(os.getcwd(), "icons", "icon.ico")
        if not os.path.exists(icon_path):
             icon_path = os.path.join(os.getcwd(), "icons", "icon.png")
        
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet(STYLESHEET)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #F8FAFC; color: #64748B; border-top: 1px solid #E2E8F0;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistem Hazır", 3000)

        self.controller = MainController()

        # Ana Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Modern Sidebar
        self.setup_sidebar()

        # 2. İçerik Alanı
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(25, 25, 25, 25) 
        
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
        
        lbl_icon = QLabel("📊") # Placeholder icon
        lbl_icon.setStyleSheet("font-size: 40px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        
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
        
        # (Label, Icon, Index)
        menu_items = [
            ("Ekle", "➕", 0),
            ("Listele", "📋", 1),
            ("İstatistik", "📊", 2),
            ("Karşılaştır", "🆚", 3),
            ("PDF Rapor", "📄", 4),
            ("Hedefler", "🎯", 5),
            ("Keşfet", "🚀", 6),
            ("Ayarlar", "⚙️", 7),
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

    def add_sidebar_btn(self, text, icon, index, layout):
        btn = QPushButton(f"  {icon}   {text}")
        btn.setObjectName(f"SidebarBtn_{index}")
        btn.setCursor(Qt.PointingHandCursor)
        
        # Normal Stil
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

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.update_active_button(index)
        
        if index != 3 and not self.sidebar.isVisible():
            self.sidebar.show()
        
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
        elif hasattr(current_widget, 'refresh_statistics'):
            current_widget.refresh_statistics()

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
    
    def open_trend_analysis(self):
        """İstatistik sayfasından trend analizi sayfasına geç"""
        self.stacked_widget.setCurrentWidget(self.trend_analysis_page)
        # Sidebar'ı gizle (daha geniş alan için)
        # self.sidebar.hide()  # İsterseniz bunu açabilirsiniz
    
    def close_trend_analysis(self):
        """Trend analizi sayfasından istatistik sayfasına geri dön"""
        self.stacked_widget.setCurrentWidget(self.stats_page)
        self.update_active_button(2)  # İstatistik butonu index 2
        # Sidebar'ı göster
        if not self.sidebar.isVisible():
            self.sidebar.show()