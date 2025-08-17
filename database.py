# database.py
import sqlite3
import os
import sys

# Windows, macOS ve Linux sistemlerinde uyumlu bir yol bulur
def get_db_path():
    if sys.platform == "win32":
        # Windows'ta AppData/Local klasörünü kullan
        app_data_path = os.environ.get('LOCALAPPDATA')
        if app_data_path:
            return os.path.join(app_data_path, "FaaliyetTakip", "faaliyetler.db")
    
    # Diğer sistemler için kullanıcının ana dizinini kullan
    home_path = os.path.expanduser("~")
    return os.path.join(home_path, "FaaliyetTakip", "faaliyetler.db")

DB_PATH = get_db_path()

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,         -- dizi, film, kitap, vs.
        name TEXT NOT NULL,
        date TEXT NOT NULL,         -- YYYY-MM formatında saklanacak
        comment TEXT,
        rating INTEGER             -- 1-10 arasında opsiyonel puanlama
    )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)