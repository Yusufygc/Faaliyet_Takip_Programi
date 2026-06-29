# views/pages/analysis_page/trend_analysis_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from views.pages.analysis_page.trend_analysis_widget import TrendAnalysisWidget


class TrendAnalysisPage(QWidget):
    """Zaman Serisi ve Trend Analizi sayfası - Stack mantığıyla açılır"""
    
    back_clicked = pyqtSignal()  # Geri dönme sinyali
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Header Area (Başlık + Geri Butonu) ---
        header_frame = QFrame()
        header_frame.setObjectName("card_elevated")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(15)
        
        # Geri Butonu
        self.btn_back = QPushButton("← Geri")
        self.btn_back.setObjectName("btn_secondary")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.btn_back)
        
        # Başlık
        title = QLabel("📈 Zaman Serisi ve Trend Analizi")
        title.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 24px; 
            font-weight: bold; 
            color: #1E293B; 
            background: transparent;
            border: none;
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title, 1)  # Stretch factor 1 to center
        
        # Sağ tarafta boş alan (geri butonu ile simetri için)
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # --- Trend Analysis Widget ---
        self.trend_widget = TrendAnalysisWidget(self.controller)
        main_layout.addWidget(self.trend_widget)
        
        # Alt boşluk
        main_layout.addStretch()
    
    def refresh_data(self):
        """Sayfa her açıldığında verileri yenile"""
        if hasattr(self.trend_widget, 'load_data'):
            self.trend_widget.load_data()
