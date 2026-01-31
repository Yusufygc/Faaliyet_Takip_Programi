# views/styles.py
from utils import get_resource_path
import os
# views/styles.py

# Renk Paleti (Gözü yormayan modern tonlar)
COLORS = {
    "background": "#F4F7F6",       # Çok açık gri-mavi (Ana arka plan)
    "sidebar": "#2C3E50",          # Koyu Lacivert (Yan menü)
    "sidebar_text": "#ECF0F1",     # Açık gri (Menü yazıları)
    "primary": "#2980B9",          # Mavi (Ana butonlar)
    "primary_hover": "#3498DB",    # Açık Mavi (Hover)
    "secondary": "#95A5A6",        # Gri (İkincil butonlar)
    "danger": "#E74C3C",           # Kırmızı (Silme işlemleri)
    "success": "#27AE60",          # Yeşil (Kaydetme işlemleri)
    "card": "#FFFFFF",             # Beyaz (İçerik kutuları)
    "text": "#2C3E50",             # Koyu Gri (Genel metin)
    "border": "#BDC3C7"            # Kenarlık rengi
}

# QSS (Qt Style Sheets) - CSS benzeri stiller
# Fix for Qt Stylesheet URL
arrow_path = get_resource_path(os.path.join('icons', 'down_arrow.svg')).replace('\\', '/')
# Ensure proper URI scheme if needed, but standard paths usually work with forward slashes.
# Quote the URL in the stylesheet to handle spaces.
arrow_url = arrow_path

STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLORS["background"]};
    }}
    
    QWidget {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        color: {COLORS["text"]};
    }}

    /* --- Yan Menü (Sidebar) --- */
    QFrame#Sidebar {{
        background-color: {COLORS["sidebar"]};
        border: none;
    }}
    
    QPushButton#SidebarBtn {{
        background-color: transparent;
        color: {COLORS["sidebar_text"]};
        text-align: left;
        padding: 12px 20px;
        border: none;
        font-weight: bold;
        font-size: 15px;
    }}
    
    QPushButton#SidebarBtn:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        border-left: 4px solid {COLORS["primary_hover"]};
    }}

    /* --- Kartlar ve Kutular --- */
    QFrame#Card {{
        background-color: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
    }}

    /* --- Form Elemanları --- */
    QLineEdit, QComboBox, QDateEdit, QTextEdit {{
        background-color: {COLORS["card"]};
        border: 2px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        color: {COLORS["text"]};
    }}
    
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {{
        border: 2px solid {COLORS["primary"]};
        background-color: #F8FAFC;
    }}
    QLineEdit:hover, QComboBox:hover, QTextEdit:hover, QDateEdit:hover {{
        border: 2px solid #CBD5E1;
    }}

    /* --- ComboBox Özel Ok (SVG) --- */
    QComboBox {{
        padding-right: 25px;
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left-width: 0px;
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
    }}

    QComboBox::down-arrow {{
        image: url('{arrow_url}');
        width: 14px;
        height: 14px;
    }}

    /* --- Tablo --- */
    QTableWidget {{
        background-color: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 5px;
        gridline-color: #EEE;
    }}
    
    QHeaderView::section {{
        background-color: #EAEDED;
        padding: 8px;
        border: none;
        font-weight: bold;
        color: {COLORS["text"]};
    }}
    
    /* --- Butonlar --- */
    QPushButton#PrimaryBtn {{
        background-color: {COLORS["primary"]};
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton#PrimaryBtn:hover {{ background-color: {COLORS["primary_hover"]}; }}

    QPushButton#DangerBtn {{
        background-color: {COLORS["danger"]};
        color: white;
        border-radius: 5px;
        padding: 5px 10px;
    }}
    
    QPushButton#SuccessBtn {{
        background-color: {COLORS["success"]};
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
    }}
"""