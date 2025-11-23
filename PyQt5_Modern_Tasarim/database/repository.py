# database/repository.py
from .connection import get_connection, init_db
from models import Activity
from utils import is_valid_yyyymm, is_valid_yyyy # utils.py dosyanızdan import ediyoruz

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
            return True
        except Exception as e:
            print(f"Hata (Repository.add): {e}")
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
            return True
        except Exception as e:
            print(f"Hata (Repository.update): {e}")
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
            return True
        except Exception as e:
            print(f"Hata (Repository.delete): {e}")
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
            print(f"Hata (Repository.get_by_id): {e}")
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
            base_query += " AND type = ?"
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
            print(f"Hata (Repository.get_all_filtered): {e}")
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
            print(f"Hata (Repository.get_unique_names): {e}")
            return []
        finally:
            if conn:
                conn.close()

    # --- İstatistik, Karşılaştırma ve Rapor Sorguları ---

    def get_stats_by_type(self, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list[tuple]:
        """
        StatsPage için gruplanmış istatistikleri çeker.
        (stats_page.py'deki show_statistics mantığı)
        """
        query = "SELECT type, COUNT(*) FROM activities"
        params = []

        if not ignore_dates:
            if year_only:
                if not date_prefix or not is_valid_yyyy(date_prefix): return [] # Geçersiz yıl
                query += " WHERE date LIKE ?"
                params.append(date_prefix + "%")
            else:
                if not date_prefix or not is_valid_yyyymm(date_prefix): return [] # Geçersiz ay
                query += " WHERE date = ?"
                params.append(date_prefix)
        
        query += " GROUP BY type ORDER BY type"
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Hata (Repository.get_stats_by_type): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_details_for_type(self, activity_type: str, date_prefix: str = "", year_only: bool = False, ignore_dates: bool = False) -> list[tuple]:
        """
        StatsPage detayları için (isim, tarih) listesini çeker.
        (stats_page.py'deki show_details_for_type mantığı)
        """
        query = "SELECT name, date FROM activities WHERE type = ?"
        params = [activity_type]

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
            print(f"Hata (Repository.get_details_for_type): {e}")
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
            print(f"Hata (Repository.get_comparison_data): {e}")
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
            print(f"Hata (Repository.get_available_periods): {e}")
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
            print(f"Hata (Repository.get_detailed_data_for_pdf): {e}")
            return []
        finally:
            if conn:
                conn.close()