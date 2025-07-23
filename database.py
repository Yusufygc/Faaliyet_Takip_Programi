# database.py
import sqlite3
import os

DB_PATH = "data/faaliyetler.db"

def init_db():
    os.makedirs("data", exist_ok=True)
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
