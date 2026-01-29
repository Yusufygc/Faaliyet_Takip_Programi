# database/connection.py
import sqlite3
import os
import sys
from constants import DB_FILENAME, DATA_DIR_NAME
from logger_setup import logger

def get_db_path():
    """İşletim sistemine uyumlu veritabanı yolunu döndürür."""
    # 2. Standart Kullanıcı Yolu (AppData veya Home)
    if sys.platform == "win32":
        app_data_path = os.environ.get('LOCALAPPDATA')
        if app_data_path:
            db_dir = os.path.join(app_data_path, DATA_DIR_NAME)
        else:
            # Alternatif bir yol (eğer LOCALAPPDATA yoksa)
            home_path = os.path.expanduser("~")
            db_dir = os.path.join(home_path, DATA_DIR_NAME)
    else:
        # macOS ve Linux için
        home_path = os.path.expanduser("~")
        db_dir = os.path.join(home_path, ".config", DATA_DIR_NAME)

    # Klasörün var olduğundan emin ol
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    return os.path.join(db_dir, DB_FILENAME)

DB_PATH = get_db_path()

def init_db():
    """Veritabanını ve 'activities' tablosunu oluşturur (eğer yoksa)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,         -- dizi, film, kitap, vs.
            name TEXT NOT NULL,
            date TEXT NOT NULL,         -- YYYY-MM formatında
            comment TEXT,
            rating INTEGER             -- 1-10 arasında
        )
        ''')
        conn.commit()
    except Exception as e:
        logger.critical(f"Veritabanı başlatılırken kritik hata: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_connection():
    """Veritabanına yeni bir bağlantı döndürür."""
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        logger.error(f"Veritabanı bağlantısı alınırken hata oluştu: {e}")
        return None