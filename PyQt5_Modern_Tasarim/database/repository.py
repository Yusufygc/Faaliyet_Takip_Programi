# database/repository.py
from .connection import get_connection, init_db
from models import Activity
from utils import is_valid_yyyymm, is_valid_yyyy
from logger_setup import logger

class ActivityRepository:
    """
    Veritabanı işlemleri (CRUD - Create, Read, Update, Delete) 
    ve istatistik sorguları için merkezi sınıf.
    """
    
    def __init__(self):
        """Repository başlatıldığında veritabanının hazır olduğundan emin olur."""
        init_db()

    def add(self, activity: Activity) -> bool:
        """Yeni bir faaliyeti veritabanına ekler."""
        sql = '''
            INSERT INTO activities (type, name, date, comment, rating)
            VALUES (?, ?, ?, ?, ?)
        '''
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (
                activity.type,
                activity.name,
                activity.date,
                activity.comment,
                activity.rating
            ))
            conn.commit()
            logger.info(f"Yeni faaliyet eklendi: {activity.name} ({activity.type})")
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.add): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update(self, activity: Activity) -> bool:
        """Mevcut bir faaliyeti ID'sine göre günceller."""
        sql = '''
            UPDATE activities
            SET type = ?, name = ?, date = ?, comment = ?, rating = ?
            WHERE id = ?
        '''
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (
                activity.type,
                activity.name,
                activity.date,
                activity.comment,
                activity.rating,
                activity.id
            ))
            conn.commit()
            logger.info(f"Faaliyet güncellendi: ID {activity.id} - {activity.name}")
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.update): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete(self, activity_id: int) -> bool:
        """Bir faaliyeti ID'sine göre siler."""
        sql = "DELETE FROM activities WHERE id = ?"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (activity_id,))
            conn.commit()
            logger.info(f"Faaliyet silindi: ID {activity_id}")
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.delete): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_by_id(self, activity_id: int) -> Activity | None:
        """ID'ye göre tek bir faaliyet kaydını döndürür."""
        sql = "SELECT id, type, name, date, comment, rating FROM activities WHERE id = ?"
        try:
            conn = get_connection()
            if not conn: return None
            cursor = conn.cursor()
            cursor.execute(sql, (activity_id,))
            row = cursor.fetchone()
            return Activity.from_row(row) if row else None
        except Exception as e:
            logger.error(f"Hata (Repository.get_by_id): {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_all_filtered(self, 
                         activity_type_filter: str = "Hepsi", 
                         search_term: str = "", 
                         date_filter: str = "",
                         page: int = 1,
                         items_per_page: int = 15) -> tuple[list[Activity], int]:
        """
        Filtrelenmiş ve sayfalanmış faaliyet listesini döndürür.
        Dönüş: (activities_list, total_count)
        """
        # Temel Sorgu (WHERE koşulları için)
        base_query = "FROM activities WHERE 1=1"
        params = []

        if activity_type_filter != "Hepsi":
            # SQLite'da varsayılan LIKE case-insensitive çalışır (ASCII için)
            # UTF-8 karakterler için lower() kullanımı daha garantidir.
            base_query += " AND lower(type) = lower(?)"
            params.append(activity_type_filter)

        if search_term:
            base_query += " AND name LIKE ?"
            params.append(f"%{search_term}%")

        if date_filter:
            # date_filter boşsa ("") buraya girmez, yani TÜM YILLAR gelir.
            if is_valid_yyyymm(date_filter):
                base_query += " AND date = ?"
                params.append(date_filter)
            elif is_valid_yyyy(date_filter):
                base_query += " AND date LIKE ?"
                params.append(f"{date_filter}%")

        try:
            conn = get_connection()
            if not conn: return [], 0
            cursor = conn.cursor()

            # 1. Toplam Sayıyı Bul (Pagination hesaplaması için gerekli)
            count_query = f"SELECT COUNT(*) {base_query}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # 2. Sayfalanmış Veriyi Çek
            # LIMIT ve OFFSET ekle
            offset = (page - 1) * items_per_page
            data_query = f"SELECT id, type, name, date, comment, rating {base_query} ORDER BY date DESC, id DESC LIMIT ? OFFSET ?"
            
            # Limit ve Offset parametrelerini ekle
            current_params = params + [items_per_page, offset]
            
            cursor.execute(data_query, current_params)
            rows = cursor.fetchall()
            
            activities = [Activity.from_row(row) for row in rows]
            return activities, total_count

        except Exception as e:
            logger.error(f"Hata (Repository.get_all_filtered): {e}")
            return [], 0
        finally:
            if conn:
                conn.close()
    
    def get_unique_names(self) -> list[str]:
        """Otomatik tamamlama için benzersiz faaliyet isimlerini getirir."""
        sql = "SELECT DISTINCT name FROM activities ORDER BY name"
        try:
            conn = get_connection()
            if not conn: return []
            cursor = conn.cursor()
            cursor.execute(sql)
            # [(name1,), (name2,), ...] formatından düz listeye çevir: [name1, name2]
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Hata (Repository.get_unique_names): {e}")
            return []
        finally:
            if conn:
                conn.close()

    # --- İstatistik, Karşılaştırma ve Rapor Sorguları ---

    def get_stats_by_type(self, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list[tuple]:
        """
        StatsPage için gruplanmış istatistikleri çeker.
        Dönüş: (type, count, average_rating)
        """
        # Puanı 0'dan büyük olanların ortalamasını al (NULLIF veya CASE kullanımı)
        query = "SELECT type, COUNT(*), AVG(CASE WHEN rating > 0 THEN rating END) FROM activities"
        params = []

        if not ignore_dates:
            if year_only:
                if not date_prefix or not is_valid_yyyy(date_prefix): return []
                query += " WHERE date LIKE ?"
                params.append(date_prefix + "%")
            else:
                if not date_prefix or not is_valid_yyyymm(date_prefix): return []
                query += " WHERE date = ?"
                params.append(date_prefix)
        
        query += " GROUP BY type ORDER BY COUNT(*) DESC" # Sayıya göre çoktan aza sırala
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_stats_by_type): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_details_for_type(self, activity_type: str, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list[tuple]:
        """
        StatsPage detayları için (isim, tarih) listesini çeker.
        Büyük/küçük harf ayrımı yapmadan tüm varyasyonları getirir.
        """
        # DEĞİŞİKLİK BURADA: 'type = ?' yerine 'lower(type) = ?' kullanıyoruz.
        query = "SELECT name, date FROM activities WHERE lower(type) = ?"
        
        # Gelen parametreyi de küçük harfe çevirerek eşleştiriyoruz.
        params = [activity_type.lower()]

        if not ignore_dates:
            if year_only:
                if not date_prefix or not is_valid_yyyy(date_prefix): return []
                query += " AND date LIKE ?"
                params.append(date_prefix + "%")
            else:
                if not date_prefix or not is_valid_yyyymm(date_prefix): return []
                query += " AND date = ?"
                params.append(date_prefix)
        
        query += " ORDER BY date DESC"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_details_for_type): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_comparison_data(self, date_prefix: str) -> list[tuple]:
        """
        ComparePage için (tür, isim) listesini çeker.
        (compare_page.py'deki fetch_data_by_date mantığı)
        """
        query = "SELECT type, name FROM activities WHERE date LIKE ?"
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (f"{date_prefix}%",))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_comparison_data): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_available_periods(self, period_type: str = "month") -> list[str]:
        """
        ComparePage için mevcut dönemleri (YYYY-MM veya YYYY) çeker.
        (compare_page.py'deki get_available_periods mantığı)
        """
        if period_type == "month":
            query = "SELECT DISTINCT substr(date, 1, 7) as period FROM activities ORDER BY period DESC"
        else:
            query = "SELECT DISTINCT substr(date, 1, 4) as period FROM activities ORDER BY period DESC"
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Hata (Repository.get_available_periods): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_detailed_data_for_pdf(self, date_prefix: str) -> list[tuple]:
        """
        PDF Raporu için tüm detaylı veriyi çeker.
        (pdfcreate_page.py'deki get_detailed_activity_data mantığı)
        """
        query = "SELECT type, name, date, comment, rating, id FROM activities WHERE date LIKE ? ORDER BY date, type, name"
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (f"{date_prefix}%",))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_detailed_data_for_pdf): {e}")
            return []
            if conn:
                conn.close()

    # --- Ayarlar / Tür Yönetimi ---

    def ensure_types_table_exists(self):
        """activity_types tablosunun varlığını kontrol eder ve oluşturur."""
        sql_create = '''
            CREATE TABLE IF NOT EXISTS activity_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        '''
        # Varsayılan türleri ekle (Eğer tablo boşsa)
        sql_check_empty = "SELECT COUNT(*) FROM activity_types"
        sql_insert_default = "INSERT INTO activity_types (name) VALUES (?)"
        
        from constants import FAALIYET_TURLERI # Circular import riskine karşı burada import

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
                    except:
                        pass # Duplicate hatası olursa geç
                conn.commit()
                logger.info("Varsayılan faaliyet türleri eklendi.")
                
        except Exception as e:
            logger.error(f"Hata (Repository.ensure_types_table_exists): {e}")
        finally:
            if conn:
                conn.close()

    def normalize_activity_types(self):
        """
        Veritabanındaki tüm tür isimlerini 'Başlık Düzeni'ne (Title Case) çevirir.
        Örn: 'dizi' -> 'Dizi', 'FILM' -> 'Film'.
        Bu işlem hem activities hem de activity_types tablolarını düzeltir.
        """
        conn = get_connection()
        if not conn: return
        
        try:
            cursor = conn.cursor()
            
            # 1. Activities tablosundaki benzersiz türleri çek
            cursor.execute("SELECT DISTINCT type FROM activities")
            unique_types = [row[0] for row in cursor.fetchall() if row[0]]
            
            for old_type in unique_types:
                new_type = old_type.strip().title() # "dizi " -> "Dizi"
                
                if old_type != new_type:
                    # Eski türü yeni türe güncelle
                    logger.info(f"Normalizasyon: '{old_type}' -> '{new_type}' çevriliyor...")
                    cursor.execute("UPDATE activities SET type = ? WHERE type = ?", (new_type, old_type))
            
            # 2. Activity_types tablosundaki türleri çek ve düzelt
            cursor.execute("SELECT name FROM activity_types")
            registered_types = [row[0] for row in cursor.fetchall()]
            
            for old_name in registered_types:
                new_name = old_name.strip().title()
                
                if old_name != new_name:
                    # Yeni isim zaten var mı?
                    cursor.execute("SELECT COUNT(*) FROM activity_types WHERE name = ?", (new_name,))
                    exists = cursor.fetchone()[0] > 0
                    
                    if exists:
                        # Zaten doğrusu varsa, eskisini sil
                        cursor.execute("DELETE FROM activity_types WHERE name = ?", (old_name,))
                    else:
                        # Yoksa yeniden adlandır
                        cursor.execute("UPDATE activity_types SET name = ? WHERE name = ?", (new_name, old_name))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Hata (Repository.normalize_activity_types): {e}")
        finally:
            if conn:
                conn.close()

    def synchronize_types(self):
        """
        Activities tablosunda olup Activity_types tablosunda olmayan türleri senkronize eder.
        Data tutarlılığı için kullanılır.
        """
        # Önce veriyi normalize et (Küçük harf/büyük harf karmaşasını çöz)
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
            
            # Eksik türleri bul
            cursor.execute(sql_find_missing)
            missing_types = [row[0] for row in cursor.fetchall() if row[0] and row[0].strip()]
            
            if missing_types:
                count = 0
                for t in missing_types:
                   try:
                       cursor.execute(sql_insert, (t,))
                       count += 1
                   except:
                       pass # Zaten varsa geç
                conn.commit()
                # logger.info(f"{count} adet eksik tür senkronize edildi: {missing_types}")
                
        except Exception as e:
            logger.error(f"Hata (Repository.synchronize_types): {e}")
        finally:
            if conn:
                conn.close()

    def get_all_types(self) -> list[str]:
        """Tüm aktif türleri alfabetik sırayla döndürür."""
        # Tablo yoksa oluştur (Güvenlik için)
        self.ensure_types_table_exists()
        
        sql = "SELECT name FROM activity_types ORDER BY name ASC"
        try:
            conn = get_connection()
            if not conn: return []
            cursor = conn.cursor()
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Hata (Repository.get_all_types): {e}")
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
            logger.error(f"Hata (Repository.add_type): {e}")
            if "UNIQUE constraint failed" in str(e):
                return False, "Bu tür zaten mevcut."
            return False, f"Hata: {e}"
        finally:
            if conn:
                conn.close()

    def update_type(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """
        Bir türü yeniden adlandırır ve activities tablosundaki eski kayıtları günceller.
        Eğer yeni isim zaten varsa, iki türü BİRLEŞTİRİR (Merge).
        """
        sql_update_type = "UPDATE activity_types SET name = ? WHERE name = ?"
        sql_update_activities = "UPDATE activities SET type = ? WHERE type = ?"
        sql_delete_old_type = "DELETE FROM activity_types WHERE name = ?"
        sql_check_exists = "SELECT COUNT(*) FROM activity_types WHERE name = ?"
        
        conn = get_connection()
        if not conn: return False, "Veritabanı bağlantısı yok."
        
        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION") # Atomik işlem başlat
            
            # Hedef isim (new_name) zaten var mı?
            cursor.execute(sql_check_exists, (new_name,))
            target_exists = cursor.fetchone()[0] > 0
            
            if target_exists:
                # BİRLEŞTİRME SENARYOSU (Merge)
                # 1. Eski kayıtları yeni isme taşı
                cursor.execute(sql_update_activities, (new_name, old_name))
                # 2. Eski türü tablodan sil (Çünkü artık kullanıcı sadece yeni ismi görecek)
                cursor.execute(sql_delete_old_type, (old_name,))
                conn.commit()
                return True, f"'{old_name}' türü mevcut '{new_name}' türü ile birleştirildi."
            else:
                # YENİDEN ADLANDIRMA SENARYOSU (Rename)
                # 1. Tür tablosunu güncelle
                cursor.execute(sql_update_type, (new_name, old_name))
                # 2. Etkilenen kayıtları güncelle
                cursor.execute(sql_update_activities, (new_name, old_name))
                conn.commit()
                return True, f"'{old_name}' ismi '{new_name}' olarak değiştirildi."
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Hata (Repository.update_type): {e}")
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
            logger.error(f"Hata (Repository.delete_type): {e}")
            return False, f"Hata: {e}"
        finally:
            if conn:
                conn.close()