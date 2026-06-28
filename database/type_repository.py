# database/type_repository.py
from .connection import get_db
from logger_setup import logger


class TypeRepository:
    """Faaliyet türleri ve uygulama ayarları için veritabanı işlemleri."""

    def __init__(self):
        self.ensure_types_table_exists()
        self.ensure_settings_table_exists()

    # --- Tür Tablosu ---

    def ensure_types_table_exists(self):
        """activity_types tablosunun varlığını kontrol eder ve oluşturur."""
        from constants import FAALIYET_TURLERI
        sql_create = '''
            CREATE TABLE IF NOT EXISTS activity_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        '''
        try:
            with get_db() as conn:
                conn.execute(sql_create)
                count = conn.execute("SELECT COUNT(*) FROM activity_types").fetchone()[0]
                if count == 0:
                    for t in FAALIYET_TURLERI:
                        try:
                            conn.execute("INSERT INTO activity_types (name) VALUES (?)", (t,))
                        except Exception:
                            pass
                    logger.info("Varsayılan faaliyet türleri eklendi.")
        except Exception as e:
            logger.error(f"Hata (TypeRepository.ensure_types_table_exists): {e}")

    def normalize_activity_types(self):
        """Veritabanındaki tüm tür isimlerini 'Başlık Düzeni'ne çevirir."""
        try:
            with get_db() as conn:
                unique_types = [
                    row[0] for row in conn.execute("SELECT DISTINCT type FROM activities").fetchall()
                    if row[0]
                ]
                for old_type in unique_types:
                    _s = old_type.strip()
                    new_type = (_s[0].upper() + _s[1:]) if _s else _s
                    if old_type != new_type:
                        logger.info(f"Normalizasyon: '{old_type}' -> '{new_type}' çevriliyor...")
                        conn.execute("UPDATE activities SET type = ? WHERE type = ?", (new_type, old_type))

                registered_types = [
                    row[0] for row in conn.execute("SELECT name FROM activity_types").fetchall()
                ]
                for old_name in registered_types:
                    _s = old_name.strip()
                    new_name = (_s[0].upper() + _s[1:]) if _s else _s
                    if old_name != new_name:
                        exists = conn.execute(
                            "SELECT COUNT(*) FROM activity_types WHERE name = ?", (new_name,)
                        ).fetchone()[0] > 0
                        if exists:
                            conn.execute("DELETE FROM activity_types WHERE name = ?", (old_name,))
                        else:
                            conn.execute("UPDATE activity_types SET name = ? WHERE name = ?", (new_name, old_name))
        except Exception as e:
            logger.error(f"Hata (TypeRepository.normalize_activity_types): {e}")

    def synchronize_types(self):
        """Activities tablosunda olup activity_types tablosunda olmayan türleri senkronize eder."""
        self.normalize_activity_types()

        sql_find_missing = '''
            SELECT DISTINCT type FROM activities
            WHERE type NOT IN (SELECT name FROM activity_types)
        '''
        try:
            with get_db() as conn:
                missing_types = [
                    row[0] for row in conn.execute(sql_find_missing).fetchall()
                    if row[0] and row[0].strip()
                ]
                for t in missing_types:
                    try:
                        conn.execute("INSERT INTO activity_types (name) VALUES (?)", (t,))
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Hata (TypeRepository.synchronize_types): {e}")

    def get_all_types(self) -> list:
        """Tüm aktif türleri alfabetik sırayla döndürür (kayıtlı + kullanılan)."""
        self.ensure_types_table_exists()
        sql = """
            SELECT DISTINCT name FROM (
                SELECT name FROM activity_types
                UNION
                SELECT DISTINCT type as name FROM activities WHERE type IS NOT NULL AND type != ''
            )
            ORDER BY name ASC
        """
        try:
            with get_db() as conn:
                return [row[0] for row in conn.execute(sql).fetchall()]
        except Exception as e:
            logger.error(f"Hata (TypeRepository.get_all_types): {e}")
            return []

    def add_type(self, name: str) -> tuple:
        """Yeni bir tür ekler."""
        try:
            with get_db() as conn:
                conn.execute("INSERT INTO activity_types (name) VALUES (?)", (name,))
            return True, "Tür başarıyla eklendi."
        except Exception as e:
            logger.error(f"Hata (TypeRepository.add_type): {e}")
            if "UNIQUE constraint failed" in str(e):
                return False, "Bu tür zaten mevcut."
            return False, f"Hata: {e}"

    def update_type(self, old_name: str, new_name: str) -> tuple:
        """Bir türü yeniden adlandırır. Yeni isim zaten varsa BİRLEŞTİRİR."""
        try:
            with get_db() as conn:
                target_exists = conn.execute(
                    "SELECT COUNT(*) FROM activity_types WHERE name = ?", (new_name,)
                ).fetchone()[0] > 0

                if target_exists:
                    conn.execute("UPDATE activities SET type = ? WHERE type = ?", (new_name, old_name))
                    conn.execute("DELETE FROM activity_types WHERE name = ?", (old_name,))
                    return True, f"'{old_name}' türü mevcut '{new_name}' türü ile birleştirildi."
                else:
                    conn.execute("UPDATE activity_types SET name = ? WHERE name = ?", (new_name, old_name))
                    conn.execute("UPDATE activities SET type = ? WHERE type = ?", (new_name, old_name))
                    return True, f"'{old_name}' ismi '{new_name}' olarak değiştirildi."
        except Exception as e:
            logger.error(f"Hata (TypeRepository.update_type): {e}")
            return False, f"Hata: {e}"

    def delete_type(self, name: str) -> tuple:
        """Bir türü siler. (Kullanımdaki kayıtlara dokunmaz, sadece listeden kaldırır)"""
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM activity_types WHERE name = ?", (name,))
            return True, "Tür silindi."
        except Exception as e:
            logger.error(f"Hata (TypeRepository.delete_type): {e}")
            return False, f"Hata: {e}"

    # --- Ayarlar ---

    def ensure_settings_table_exists(self):
        """Ayarlar tablosunu oluşturur."""
        sql = '''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        '''
        try:
            with get_db() as conn:
                conn.execute(sql)
        except Exception as e:
            logger.error(f"Hata (TypeRepository.ensure_settings_table_exists): {e}")

    def get_setting(self, key: str):
        """Belirtilen anahtarın değerini döndürür."""
        try:
            with get_db() as conn:
                row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Hata (TypeRepository.get_setting): {e}")
            return None

    def set_setting(self, key: str, value: str) -> bool:
        """Ayarı kaydeder veya günceller."""
        try:
            with get_db() as conn:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            return True
        except Exception as e:
            logger.error(f"Hata (TypeRepository.set_setting): {e}")
            return False
