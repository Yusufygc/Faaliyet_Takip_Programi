# database/repository.py
from .connection import get_connection, init_db
from .connection import get_connection, init_db
from .connection import get_connection, init_db
from models import Activity, ActivityFilter, Plan, Folder
from utils import is_valid_yyyymm, is_valid_yyyy
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
        self.check_and_migrate_schema()
        self.check_and_migrate_schema()
        self.ensure_plans_table_exists()
        self.ensure_folders_table_exists()

    def check_and_migrate_schema(self):
        """Veritabanı şemasını kontrol eder ve eksik kolonları ekler."""
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            
            # activities tablosundaki kolonları al
            cursor.execute("PRAGMA table_info(activities)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "end_date" not in columns:
                logger.info("Şema güncelleniyor: 'end_date' kolonu ekleniyor...")
                cursor.execute("ALTER TABLE activities ADD COLUMN end_date TEXT")
                conn.commit()

            # İndeksleri Kontrol Et ve Ekle (Performans için)
            cursor.execute("PRAGMA index_list(activities)")
            indexes = [row[1] for row in cursor.fetchall()]
            
            if "idx_activities_date" not in indexes:
                cursor.execute("CREATE INDEX idx_activities_date ON activities(date)")
                logger.info("İndeks oluşturuldu: idx_activities_date")
                
            if "idx_activities_type" not in indexes:
                # Type aramalarında COLLATE NOCASE önemli olabilir ama şimdilik standart indeks
                cursor.execute("CREATE INDEX idx_activities_type ON activities(type)")
                logger.info("İndeks oluşturuldu: idx_activities_type")
            
            # Plans tablosu şema kontrolü (folder_id)
            cursor.execute("PRAGMA table_info(plans)")
            plan_columns = [row[1] for row in cursor.fetchall()]
            
            if "folder_id" not in plan_columns:
                logger.info("Şema güncelleniyor: plans tablosuna 'folder_id' kolonu ekleniyor...")
                cursor.execute("ALTER TABLE plans ADD COLUMN folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL")
                conn.commit()
                
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Hata (Repository.check_and_migrate_schema): {e}")

    def add(self, activity: Activity) -> bool:
        """Yeni bir faaliyeti veritabanına ekler."""
        sql = '''
            INSERT INTO activities (type, name, date, comment, rating, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
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
                activity.end_date
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
            SET type = ?, name = ?, date = ?, comment = ?, rating = ?, end_date = ?
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
                activity.end_date,
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
        sql = "SELECT id, type, name, date, comment, rating, end_date FROM activities WHERE id = ?"
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

    def get_all_filtered(self, filter_obj: ActivityFilter) -> tuple[list[Activity], int]:
        """
        Filtrelenmiş ve sayfalanmış faaliyet listesini döndürür.
        Artık ActivityFilter nesnesi alıyor.
        """
        base_query_parts = ["FROM activities WHERE 1=1"]
        params = []

        # 1. Tür Filtresi
        if filter_obj.type_filter != "Hepsi":
            base_query_parts.append("AND lower(type) = lower(?)")
            params.append(filter_obj.type_filter)

        # 2. Arama Filtresi
        if filter_obj.search_term:
            base_query_parts.append("AND name LIKE ?")
            params.append(f"%{filter_obj.search_term}%")

        # 3. Tarih Filtresi
        if filter_obj.date_filter:
            date_f = filter_obj.date_filter
            start_date, end_date = None, None

            if is_valid_yyyymm(date_f):
                start_date = f"{date_f}" # "YYYY-MM" (DB'deki "YYYY-MM" verisini de kapsamak için -01 eklemiyoruz)
                end_date = f"{date_f}-31" 
            elif is_valid_yyyy(date_f):
                start_date = f"{date_f}" # "YYYY" (DB'deki "YYYY-01" veya "YYYY-MM" verisini kapsamak için -01-01 eklemiyoruz)
                end_date = f"{date_f}-12-31"

            if start_date and end_date:
                # Kapsama Mantığı: (Start <= End of Period) AND (End >= Start of Period)
                base_query_parts.append("AND date <= ? AND COALESCE(end_date, date) >= ?")
                params.append(end_date)
                params.append(start_date)

        base_query = " ".join(base_query_parts)

        try:
            conn = get_connection()
            if not conn: return [], 0
            cursor = conn.cursor()

            # A. Toplam Sayı
            count_query = f"SELECT COUNT(*) {base_query}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # B. Veri (Pagination)
            offset = (filter_obj.page - 1) * filter_obj.items_per_page
            data_query = f"SELECT id, type, name, date, comment, rating, end_date {base_query} ORDER BY date DESC, id DESC LIMIT ? OFFSET ?"
            
            # Parametreleri birleştir
            current_params = params + [filter_obj.items_per_page, offset]
            
            cursor.execute(data_query, current_params)
            rows = cursor.fetchall()
            
            return [Activity.from_row(row) for row in rows], total_count

        except Exception as e:
            logger.error(f"Hata (Repository.get_all_filtered): {e}")
            return [], 0
        finally:
            if conn:
                conn.close()
    
            if conn:
                conn.close()

    # --- Plan / Hedef İşlemleri (Smart Planning) ---

    def ensure_plans_table_exists(self):
        """Plans tablosunu oluşturur."""
        sql = '''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                scope TEXT NOT NULL, -- 'monthly' or 'yearly'
                year INTEGER NOT NULL,
                month INTEGER, -- Nullable for yearly
                status TEXT DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'archived'
                progress INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high'
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL
            )
        '''
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logger.error(f"Hata (Repository.ensure_plans_table_exists): {e}")
        finally:
            if conn: conn.close()
            
    def add_plan(self, plan: Plan) -> bool:
        """Yeni plan ekler."""
        sql = '''
            INSERT INTO plans (title, description, scope, year, month, status, progress, priority, created_at, folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (
                plan.title, plan.description, plan.scope, plan.year, plan.month, 
                plan.status, plan.progress, plan.priority, plan.created_at, plan.folder_id
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.add_plan): {e}")
            return False
        finally:
            if conn: conn.close()

    def update_plan(self, plan: Plan) -> bool:
        """Planı günceller."""
        sql = '''
            UPDATE plans 
            SET title=?, description=?, status=?, progress=?, priority=?, folder_id=?
            WHERE id=?
        '''
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (
                plan.title, plan.description, plan.status, plan.progress, plan.priority, plan.folder_id, plan.id
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.update_plan): {e}")
            return False
        finally:
            if conn: conn.close()
            
    def update_plan_progress(self, plan_id: int, progress: int, status: str) -> bool:
        """Sadece ilerleme ve durumu günceller."""
        sql = "UPDATE plans SET progress=?, status=? WHERE id=?"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (progress, status, plan_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.update_plan_progress): {e}")
            return False
        finally:
            if conn: conn.close()

    def delete_plan(self, plan_id: int) -> bool:
        """Planı siler."""
        sql = "DELETE FROM plans WHERE id=?"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (plan_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.delete_plan): {e}")
            return False
        finally:
            if conn: conn.close()

    def get_plans(self, scope: str, year: int, month: int = None) -> list[Plan]:
        """Filtreye göre planları getirir."""
        query = "SELECT id, title, description, scope, year, month, status, progress, priority, created_at, folder_id FROM plans WHERE scope=? AND year=?"
        params = [scope, year]
        
        if scope == 'monthly' and month is not None:
             query += " AND month=?"
             params.append(month)
             
        query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, id DESC"
        
        try:
            conn = get_connection()
            if not conn: return []
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Plan.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Hata (Repository.get_plans): {e}")
            return []
        finally:
            if conn: conn.close()

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
        query = "SELECT type, name, date, comment, rating, id, end_date FROM activities WHERE date LIKE ? ORDER BY date, type, name"
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

    def get_monthly_activity_counts(self, year: int, category: str = None) -> list[tuple]:
        """
        Trend Analizi için aylık aktivite sayılarını çeker.
        Dönüş: [(ay_numarası, sayi), ...]
        Örn: [(1, 5), (2, 8), ...]
        """
        # date alanı 'YYYY-MM' veya 'YYYY-MM-DD' formatında olduğu için substr kullanıyoruz
        query = """
            SELECT CAST(substr(date, 6, 2) AS INTEGER) as month, COUNT(*) 
            FROM activities 
            WHERE substr(date, 1, 4) = ?
        """
        params = [str(year)]
        
        if category and category != "Hepsi":
            query += " AND type = ?"
            params.append(category)
            
        query += " GROUP BY month ORDER BY month"
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_monthly_activity_counts): {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_activity_details_by_month(self, date_str: str, category: str = None) -> list[tuple]:
        """
        Belirli bir aydaki aktivitelerin detaylarını getirir.
        date_str: 'YYYY-MM' formatında ay bilgisi
        category: Opsiyonel kategori filtresi
        Dönüş: [(name, date), ...]
        """
        query = "SELECT name, date FROM activities WHERE substr(date, 1, 7) = ?"
        params = [date_str]
        
        if category and category != "Hepsi":
            query += " AND type = ?"
            params.append(category)
        
        query += " ORDER BY date DESC, name ASC"
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hata (Repository.get_activity_details_by_month): {e}")
            return []
        finally:
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
        """Tüm aktif türleri alfabetik sırayla döndürür (kayıtlı + kullanılan)."""
        # Tablo yoksa oluştur (Güvenlik için)
        self.ensure_types_table_exists()
        
        # Hem kayıtlı türleri hem de gerçekte kullanılan türleri getir
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

    # --- Klasör (Folder) İşlemleri ---

    def ensure_folders_table_exists(self):
        """Folders tablosunu oluşturur."""
        sql = '''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        '''
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logger.error(f"Hata (Repository.ensure_folders_table_exists): {e}")
        finally:
            if conn: conn.close()

    def get_folders(self) -> list[Folder]:
        """Tüm klasörleri getirir."""
        sql = "SELECT id, name, created_at FROM folders ORDER BY name"
        try:
            conn = get_connection()
            if not conn: return []
            cursor = conn.cursor()
            cursor.execute(sql)
            return [Folder.from_row(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Hata (Repository.get_folders): {e}")
            return []
        finally:
            if conn: conn.close()
            
    def add_folder(self, name: str) -> bool:
        """Yeni klasör ekler."""
        sql = "INSERT INTO folders (name) VALUES (?)"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (name,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.add_folder): {e}")
            return False
        finally:
            if conn: conn.close()

    def update_folder(self, folder_id: int, name: str) -> bool:
        """Klasör ismini günceller."""
        sql = "UPDATE folders SET name=? WHERE id=?"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (name, folder_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.update_folder): {e}")
            return False
        finally:
            if conn: conn.close()
            
    def delete_folder(self, folder_id: int) -> bool:
        """Klasörü siler. Klasör silinince içindeki planların folder_id'si NULL olur (ON DELETE SET NULL)."""
        sql = "DELETE FROM folders WHERE id=?"
        try:
            conn = get_connection()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute(sql, (folder_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Hata (Repository.delete_folder): {e}")
            return False
        finally:
            if conn: conn.close()