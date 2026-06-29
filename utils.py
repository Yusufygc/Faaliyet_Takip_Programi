import sys
import os
from datetime import datetime

def get_resource_path(relative_path):
    """
    Uygulamanın kaynak dosyalarına (ikonlar, fontlar vb.) erişim sağlar.
    PyInstaller ve Nuitka (onefile) modlarında çalışır.
    """
    try:
        # PyInstaller temp folder
        base_path = sys._MEIPASS
    except Exception:
        # Nuitka onefile mode or Dev environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)



def is_valid_yyyymm(date_str):
    """YYYY-MM veya YYYY-MM-DD formatını doğrular."""
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

def is_valid_yyyy(date_str):
    """YYYY formatını doğrular."""
    try:
        datetime.strptime(date_str, "%Y")
        return True
    except ValueError:
        return False

def extract_year_month(date_str):
    """Tarih stringinden yıl ve ayı ayırır. YYYY-MM-DD ve YYYY-MM destekler."""
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.year, dt.month
        except ValueError:
            continue
    if is_valid_yyyy(date_str):
        return int(date_str), None
    return None, None