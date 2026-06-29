# database/connection.py
import sqlite3
import os
import sys
from contextlib import contextmanager
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

def _configure_conn(conn: sqlite3.Connection) -> None:
    """WAL modu ve performans pragmaları."""
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")


def init_db():
    """Veritabanını ve 'activities' tablosunu oluşturur (eğer yoksa)."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15.0)
        _configure_conn(conn)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            comment TEXT,
            rating INTEGER CHECK(rating IS NULL OR (rating >= 1 AND rating <= 10)),
            end_date TEXT
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
        conn = sqlite3.connect(DB_PATH, timeout=15.0)
        _configure_conn(conn)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Veritabanı bağlantısı alınırken hata oluştu: {e}")
        return None


@contextmanager
def get_db():
    """Repository metodları için bağlantı context manager'ı.

    Kullanım:
        with get_db() as conn:
            conn.execute(sql, params)

    Başarıda commit, hata durumunda rollback yapar ve bağlantıyı kapatır.
    """
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    _configure_conn(conn)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()