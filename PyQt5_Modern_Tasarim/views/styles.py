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
        border: 1px solid {COLORS["border"]};
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
    }}
    
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 1px solid {COLORS["primary"]};
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