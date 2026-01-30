# views/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame, QStatusBar, 
                             QShortcut, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon

from controllers.main_controller import MainController
from views.pages.add_page import AddPage
from views.pages.list_page import ListPage
from views.pages.stats_page import StatsPage
from views.pages.compare_page import ComparePage
from views.pages.pdf_page import PdfPage
from views.pages.settings_page import SettingsPage
from views.pages.pdf_page import PdfPage
from views.pages.settings_page import SettingsPage
from views.pages.plans_page import PlansPage
from views.pages.suggestion_page import SuggestionPage
from views.styles import STYLESHEET # Stilleri import et

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Faaliyet Takip Sistemi")
        self.setGeometry(100, 100, 1100, 700) # Biraz daha geniş başlatalım
        
        # Icon Yolu Ayarlama (Robust Path)
        # Nuitka/PyInstaller çalışma dizinini main.py içinde ayarlıyor, 
        # ancak garantiye almak için mutlak yol kullanalım.
        icon_path = os.path.join(os.getcwd(), "icons", "icon.ico")
        if not os.path.exists(icon_path):
             # Yedek olarak PNG deneyelim
             icon_path = os.path.join(os.getcwd(), "icons", "icon.png")
        
        self.setWindowIcon(QIcon(icon_path))
        # Stilleri Uygula
        self.setStyleSheet(STYLESHEET)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistem Hazır", 3000)

        self.controller = MainController()

        # Ana Widget ve Yatay Layout (Sol: Menü, Sağ: İçerik)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sol Yan Menü (Sidebar)
        self.setup_sidebar()

        # 2. Sağ İçerik Alanı
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20) # İçerik kenarlardan nefes alsın
        
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        self.main_layout.addWidget(self.content_area)

        # Sayfaları Başlat
        self.init_pages()
        self.setup_shortcuts()

    def setup_sidebar(self):
        """Sol taraftaki modern menüyü oluşturur."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar") # Stil dosyasındaki ID ile eşleşir
        self.sidebar.setFixedWidth(220) # Sabit genişlik
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)

        # Logo / Başlık Alanı
        lbl_logo = QLabel("FAALİYET\nTAKİP")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 30px 0;")
        sidebar_layout.addWidget(lbl_logo)

        # Menü Butonları
        self.buttons = [] # Butonları listede tutalım ki stil değiştirebilelim
        
        self.add_sidebar_btn("➕  Ekle", 0, sidebar_layout)
        self.add_sidebar_btn("📋  Listele", 1, sidebar_layout)
        self.add_sidebar_btn("📊  İstatistik", 2, sidebar_layout)
        self.add_sidebar_btn("🆚  Karşılaştır", 3, sidebar_layout)
        self.add_sidebar_btn("📄  PDF Rapor", 4, sidebar_layout)
        self.add_sidebar_btn("📅  Planlama", 5, sidebar_layout)
        self.add_sidebar_btn("🚀  Keşfet", 6, sidebar_layout)
        self.add_sidebar_btn("⚙️  Ayarlar", 7, sidebar_layout)

        sidebar_layout.addStretch() # Butonları yukarı it

        # Çıkış Butonu (En altta)
        btn_exit = QPushButton("❌  Çıkış")
        btn_exit.setObjectName("SidebarBtn")
        btn_exit.clicked.connect(self.close)
        sidebar_layout.addWidget(btn_exit)

        self.main_layout.addWidget(self.sidebar)

    def add_sidebar_btn(self, text, index, layout):
        btn = QPushButton(text)
        btn.setObjectName("SidebarBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(index))
        layout.addWidget(btn)
        self.buttons.append(btn)

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

        self.suggestion_page = SuggestionPage() # Controller kendi içinde
        self.stacked_widget.addWidget(self.suggestion_page)

        self.settings_page = SettingsPage(self.controller)
        self.stacked_widget.addWidget(self.settings_page)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Karşılaştırma sayfasından çıkınca sidebar'ı göster
        if index != 3 and not self.sidebar.isVisible():
            self.sidebar.show()
        
        # Aktif sayfa ise listeyi yenile
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
        elif hasattr(current_widget, 'refresh_statistics'):
            current_widget.refresh_statistics()

    def toggle_sidebar(self):
        """Sidebar'ı göster/gizle (hamburger menü için)."""
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