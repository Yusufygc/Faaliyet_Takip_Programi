# database/type_repository.py
from .connection import get_connection
from logger_setup import logger


class TypeRepository:
    """Faaliyet türleri ve uygulama ayarları için veritabanı işlemleri."""

    def __init__(self):
        self.ensure_types_table_exists()
        self.ensure_settings_table_exists()

    # --- Tür Tablosu ---

    def ensure_types_table_exists(self):
        """activity_types tablosunun varlığını kontrol eder ve oluşturur."""
        sql_create = '''
            CREATE TABLE IF NOT EXISTS activity_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        '''
        sql_check_empty = "SELECT COUNT(*) FROM activity_types"
        sql_insert_default = "INSERT INTO activity_types (name) VALUES (?)"

        from constants import FAALIYET_TURLERI

        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(sql_create)

            cursor.execute(sql_check_empty)
            count = cursor.fetchone()[0]

            if count == 0:
                for t in FAALIYET_TURLERI:
                    try:
                        cursor.execute(sql_insert_default, (t,))
                    except Exception:
                        pass
                conn.commit()
                logger.info("Varsayılan faaliyet türleri eklendi.")

        except Exception as e:
            logger.error(f"Hata (TypeRepository.ensure_types_table_exists): {e}")
        finally:
            if conn:
                conn.close()

    def normalize_activity_types(self):
        """Veritabanındaki tüm tür isimlerini 'Başlık Düzeni'ne çevirir."""
        conn = get_connection()
        if not conn: return

        try:
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT type FROM activities")
            unique_types = [row[0] for row in cursor.fetchall() if row[0]]

            for old_type in unique_types:
                _s = old_type.strip()
                new_type = (_s[0].upper() + _s[1:]) if _s else _s

                if old_type != new_type:
                    logger.info(f"Normalizasyon: '{old_type}' -> '{new_type}' çevriliyor...")
                    cursor.execute("UPDATE activities SET type = ? WHERE type = ?", (new_type, old_type))

            cursor.execute("SELECT name FROM activity_types")
            registered_types = [row[0] for row in cursor.fetchall()]

            for old_name in registered_types:
                _s = old_name.strip()
                new_name = (_s[0].upper() + _s[1:]) if _s else _s

                if old_name != new_name:
                    cursor.execute("SELECT COUNT(*) FROM activity_types WHERE name = ?", (new_name,))
                    exists = cursor.fetchone()[0] > 0

                    if exists:
                        cursor.execute("DELETE FROM activity_types WHERE name = ?", (old_name,))
                    else:
                        cursor.execute("UPDATE activity_types SET name = ? WHERE name = ?", (new_name, old_name))

            conn.commit()
        except Exception as e:
            logger.error(f"Hata (TypeRepository.normalize_activity_types): {e}")
        finally:
            if conn:
                conn.close()

    def synchronize_types(self):
        """Activities tablosunda olup activity_types tablosunda olmayan türleri senkronize eder."""
        self.normalize_activity_types()

        sql_find_missing = '''
            SELECT DISTINCT type FROM activities
            WHERE type NOT IN (SELECT name FROM activity_types)
        '''
        sql_insert = "INSERT INTO activity_types (name) VALUES (?)"

        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()

            cursor.execute(sql_find_missing)
            missing_types = [row[0] for row in cursor.fetchall() if row[0] and row[0].strip()]

            if missing_types:
                count = 0
                for t in missing_types:
                    try:
                        cursor.execute(sql_insert, (t,))
                        count += 1
                    except Exception:
                        pass
                conn.commit()

        except Exception as e:
            logger.error(f"Hata (TypeRepository.synchronize_types): {e}")
        finally:
            if conn:
                conn.close()

    def get_all_types(self) -> list[str]:
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
            conn = get_connection()
            if not conn: return []
            cursor = conn.cursor()
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Hata (TypeRepository.get_all_types): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_type(self, name: str) -> tuple[bool, str]:
        """Yeni bir tür ekler."""
        sql = "INSERT INTO activity_types (name) VALUES (?)"
        try:
            conn = get_connection()
            if not conn: return False, "Veritabanı bağlantısı yok."
            cursor = conn.cursor()
            cursor.execute(sql, (name,))
            conn.commit()
            return True, "Tür başarıyla eklendi."
        except Exception as e:
            logger.error(f"Hata (TypeRepository.add_type): {e}")
            if "UNIQUE constraint failed" in str(e):
                return False, "Bu tür zaten mevcut."
            return False, f"Hata: {e}"
        finally:
            if conn:
                conn.close()

    def update_type(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """Bir türü yeniden adlandırır. Yeni isim zaten varsa BİRLEŞTİRİR."""
        sql_update_type = "UPDATE activity_types SET name = ? WHERE name = ?"
        sql_update_activities = "UPDATE activities SET type = ? WHERE type = ?"
        sql_delete_old_type = "DELETE FROM activity_types WHERE name = ?"
        sql_check_exists = "SELECT COUNT(*) FROM activity_types WHERE name = ?"

        conn = get_connection()
        if not conn: return False, "Veritabanı bağlantısı yok."

        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")

            cursor.execute(sql_check_exists, (new_name,))
            target_exists = cursor.fetchone()[0] > 0

            if target_exists:
                cursor.execute(sql_update_activities, (new_name, old_name))
                cursor.execute(sql_delete_old_type, (old_name,))
                conn.commit()
                return True, f"'{old_name}' türü mevcut '{new_name}' türü ile birleştirildi."
            else:
                cursor.execute(sql_update_type, (new_name, old_name))
                cursor.execute(sql_update_activities, (new_name, old_name))
                conn.commit()
                return True, f"'{old_name}' ismi '{new_name}' olarak değiştirildi."

        except Exception as e:
            conn.rollback()
            logger.error(f"Hata (TypeRepository.update_type): {e}")
            return False, f"Hata: {e}"
        finally:
            if conn:
                conn.close()

    def delete_type(self, name: str) -> tuple[bool, str]:
        """Bir türü siler. (Kullanımdaki kayıtlara dokunmaz, sadece listeden kaldırır)"""
        sql = "DELETE FROM activity_types WHERE name = ?"
        try:
            conn = get_connection()
            if not conn: return False, "Veritabanı bağlantısı yok."
            cursor = conn.cursor()
            cursor.execute(sql, (name,))
            conn.commit()
            return True, "Tür silindi."
        except Exception as e:
            logger.error(f"Hata (TypeRepository.delete_type): {e}")
            return False, f"Hata: {e}"
        finally:
            if conn:
                conn.close()

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
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logger.error(f"Hata (TypeRepository.ensure_settings_table_exists): {e}")
        finally:
            if conn: conn.close()

    def get_setting(self, key: str) -> str | None:
        """Belirtilen anahtarın değerini döndürür."""
        sql = "SELECT value FROM settings WHERE key = ?"
        try:
            conn = get_connection()
            if not conn: return None
            cursor = conn.cursor()
            cursor.execute(sql, (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Hata (TypeRepository.get_setting): {e}")
            return None
        finally:
            if conn: conn.close()

    def set_setting(self, key: str, value: str) -> bool:
        """Ayarı kaydeder veya günceller."""
        sql = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (key, value))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (TypeRepository.set_setting): {e}")
            return False
        finally:
            if conn: conn.close()
