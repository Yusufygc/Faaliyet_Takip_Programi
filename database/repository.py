# database/repository.py
from .connection import get_db, get_connection, init_db
from models import Activity, ActivityFilter
from utils import is_valid_yyyymm, is_valid_yyyy
from logger_setup import logger


class ActivityRepository:
    """Faaliyet kayıtları için CRUD ve istatistik sorguları."""

    def __init__(self):
        init_db()
        self.check_and_migrate_schema()

    def check_and_migrate_schema(self):
        """Veritabanı şemasını kontrol eder ve eksik kolonları ekler."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()

                cursor.execute("PRAGMA table_info(activities)")
                columns = [row[1] for row in cursor.fetchall()]

                if "end_date" not in columns:
                    logger.info("Şema güncelleniyor: 'end_date' kolonu ekleniyor...")
                    cursor.execute("ALTER TABLE activities ADD COLUMN end_date TEXT")

                cursor.execute("PRAGMA index_list(activities)")
                indexes = [row[1] for row in cursor.fetchall()]

                if "idx_activities_date" not in indexes:
                    cursor.execute("CREATE INDEX idx_activities_date ON activities(date)")
                    logger.info("İndeks oluşturuldu: idx_activities_date")

                if "idx_activities_type" not in indexes:
                    cursor.execute("CREATE INDEX idx_activities_type ON activities(type)")
                    logger.info("İndeks oluşturuldu: idx_activities_type")

                cursor.execute("PRAGMA table_info(plans)")
                plan_columns = [row[1] for row in cursor.fetchall()]

                if plan_columns and "folder_id" not in plan_columns:
                    logger.info("Şema güncelleniyor: plans tablosuna 'folder_id' kolonu ekleniyor...")
                    cursor.execute("ALTER TABLE plans ADD COLUMN folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL")

        except Exception as e:
            logger.error(f"Hata (ActivityRepository.check_and_migrate_schema): {e}")

    def add(self, activity: Activity) -> bool:
        """Yeni bir faaliyeti veritabanına ekler."""
        sql = '''
            INSERT INTO activities (type, name, date, comment, rating, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        try:
            with get_db() as conn:
                conn.execute(sql, (
                    activity.type, activity.name, activity.date,
                    activity.comment, activity.rating, activity.end_date
                ))
            logger.info(f"Yeni faaliyet eklendi: {activity.name} ({activity.type})")
            return True
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.add): {e}")
            return False

    def update(self, activity: Activity) -> bool:
        """Mevcut bir faaliyeti ID'sine göre günceller."""
        sql = '''
            UPDATE activities
            SET type = ?, name = ?, date = ?, comment = ?, rating = ?, end_date = ?
            WHERE id = ?
        '''
        try:
            with get_db() as conn:
                conn.execute(sql, (
                    activity.type, activity.name, activity.date,
                    activity.comment, activity.rating, activity.end_date,
                    activity.id
                ))
            logger.info(f"Faaliyet güncellendi: ID {activity.id} - {activity.name}")
            return True
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.update): {e}")
            return False

    def delete(self, activity_id: int) -> bool:
        """Bir faaliyeti ID'sine göre siler."""
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
            logger.info(f"Faaliyet silindi: ID {activity_id}")
            return True
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.delete): {e}")
            return False

    def get_by_id(self, activity_id: int):
        """ID'ye göre tek bir faaliyet kaydını döndürür."""
        sql = "SELECT id, type, name, date, comment, rating, end_date FROM activities WHERE id = ?"
        try:
            with get_db() as conn:
                row = conn.execute(sql, (activity_id,)).fetchone()
            return Activity.from_row(row) if row else None
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_by_id): {e}")
            return None

    def get_all_filtered(self, filter_obj: ActivityFilter):
        """Filtrelenmiş ve sayfalanmış faaliyet listesini döndürür."""
        base_query_parts = ["FROM activities WHERE 1=1"]
        params = []

        if filter_obj.type_filter != "Hepsi":
            base_query_parts.append("AND lower(type) = lower(?)")
            params.append(filter_obj.type_filter)

        if filter_obj.search_term:
            base_query_parts.append("AND name LIKE ?")
            params.append(f"%{filter_obj.search_term}%")

        if filter_obj.date_filter:
            date_f = filter_obj.date_filter
            start_date, end_date = None, None

            if is_valid_yyyymm(date_f):
                start_date = f"{date_f}"
                end_date = f"{date_f}-31"
            elif is_valid_yyyy(date_f):
                start_date = f"{date_f}"
                end_date = f"{date_f}-12-31"

            if start_date and end_date:
                base_query_parts.append("AND date <= ? AND COALESCE(end_date, date) >= ?")
                params.append(end_date)
                params.append(start_date)

        base_query = " ".join(base_query_parts)

        try:
            with get_db() as conn:
                total_count = conn.execute(f"SELECT COUNT(*) {base_query}", params).fetchone()[0]

                offset = (filter_obj.page - 1) * filter_obj.items_per_page
                data_query = (
                    f"SELECT id, type, name, date, comment, rating, end_date {base_query} "
                    f"ORDER BY date DESC, id DESC LIMIT ? OFFSET ?"
                )
                rows = conn.execute(data_query, params + [filter_obj.items_per_page, offset]).fetchall()

            return [Activity.from_row(row) for row in rows], total_count

        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_all_filtered): {e}")
            return [], 0

    def get_unique_names(self) -> list:
        """Otomatik tamamlama için benzersiz faaliyet isimlerini getirir."""
        sql = "SELECT DISTINCT name FROM activities ORDER BY name"
        try:
            with get_db() as conn:
                return [row[0] for row in conn.execute(sql).fetchall()]
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_unique_names): {e}")
            return []

    # --- İstatistik, Karşılaştırma ve Rapor Sorguları ---

    def get_stats_by_type(self, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list:
        """StatsPage için gruplanmış istatistikleri çeker. Dönüş: (type, count, average_rating)"""
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

        query += " GROUP BY type ORDER BY COUNT(*) DESC"

        try:
            with get_db() as conn:
                return conn.execute(query, params).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_stats_by_type): {e}")
            return []

    def get_details_for_type(self, activity_type: str, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list:
        """StatsPage detayları için (isim, tarih) listesini çeker."""
        query = "SELECT name, date FROM activities WHERE lower(type) = ?"
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
            with get_db() as conn:
                return conn.execute(query, params).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_details_for_type): {e}")
            return []

    def get_comparison_data(self, date_prefix: str) -> list:
        """ComparePage için (tür, isim) listesini çeker."""
        try:
            with get_db() as conn:
                return conn.execute(
                    "SELECT type, name FROM activities WHERE date LIKE ?",
                    (f"{date_prefix}%",)
                ).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_comparison_data): {e}")
            return []

    def get_available_periods(self, period_type: str = "month") -> list:
        """ComparePage için mevcut dönemleri (YYYY-MM veya YYYY) çeker."""
        if period_type == "month":
            query = "SELECT DISTINCT substr(date, 1, 7) as period FROM activities ORDER BY period DESC"
        else:
            query = "SELECT DISTINCT substr(date, 1, 4) as period FROM activities ORDER BY period DESC"

        try:
            with get_db() as conn:
                return [row[0] for row in conn.execute(query).fetchall()]
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_available_periods): {e}")
            return []

    def get_detailed_data_for_pdf(self, date_prefix: str) -> list:
        """PDF Raporu için tüm detaylı veriyi çeker."""
        query = "SELECT type, name, date, comment, rating, id, end_date FROM activities WHERE date LIKE ? ORDER BY date, type, name"
        try:
            with get_db() as conn:
                return conn.execute(query, (f"{date_prefix}%",)).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_detailed_data_for_pdf): {e}")
            return []

    def get_monthly_activity_counts(self, year: int, category: str = None) -> list:
        """Trend Analizi için aylık aktivite sayılarını çeker. Dönüş: [(ay_numarası, sayi), ...]"""
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
            with get_db() as conn:
                return conn.execute(query, params).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_monthly_activity_counts): {e}")
            return []

    def get_activity_details_by_month(self, date_str: str, category: str = None) -> list:
        """Belirli bir aydaki aktivitelerin detaylarını getirir. Dönüş: [(name, date), ...]"""
        query = "SELECT name, date FROM activities WHERE substr(date, 1, 7) = ?"
        params = [date_str]

        if category and category != "Hepsi":
            query += " AND type = ?"
            params.append(category)

        query += " ORDER BY date DESC, name ASC"

        try:
            with get_db() as conn:
                return conn.execute(query, params).fetchall()
        except Exception as e:
            logger.error(f"Hata (ActivityRepository.get_activity_details_by_month): {e}")
            return []
