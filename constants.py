# constants.py
"""
Uygulama genelindeki sabit değerleri ve konfigürasyonları tutar.
"""

# Faaliyet türleri (list_page, add_page, edit_page tarafından kullanılır)
FAALIYET_TURLERI = ["Dizi", "Film", "Kitap", "Oyun", "Kurs", "Şehir"]

# ListPage için "Tümü" seçeneği
LIST_PAGE_FILTRE_SECENEKLERI = ["Hepsi"] + FAALIYET_TURLERI

# ComparePage için sabit sıralama
COMPARE_PAGE_DATA_ORDER = ["DIZI", "FILM", "KITAP", "KURS", "OYUN", "ŞEHIR"]

# --- Konfigürasyon ve Sabitler ---
APP_NAME = "FaaliyetTakip"
DB_FILENAME = "faaliyetler.db"
LOG_FILENAME = "app.log"
THEME_NAME = "Fusion"

# Dizin Adları
DATA_DIR_NAME = "FaaliyetTakip"

# Keyring sabitleri — tek kaynak, tüm kontrolcüler buradan import eder
KEYRING_APP_NAME = APP_NAME
KEYRING_KEY_TMDB = "tmdb_api_key"
KEYRING_KEY_RAWG = "rawg_api_key"
KEYRING_KEY_GOOGLE_BOOKS = "google_books_api_key"
