# controllers/main_controller.py
from database.repository import ActivityRepository
from models import Activity
from utils import is_valid_yyyymm, extract_year_month
from datetime import datetime

class MainController:
    """
    Uygulamanın iş mantığını yöneten sınıf.
    Arayüz (View) ve Veri (Model/Repository) arasındaki iletişimi sağlar.
    """

    def __init__(self):
        # Repository nesnesini başlatıyoruz
        self.repository = ActivityRepository()

    def get_all_activities(self, type_filter="Hepsi", search_term="", date_filter=""):
        """Filtrelenmiş aktivite listesini döndürür."""
        return self.repository.get_all_filtered(type_filter, search_term, date_filter)

    def add_activity(self, type_val, name, date_val, comment, rating_val):
        """
        Yeni bir aktivite ekler. Önce verileri doğrular.
        Dönüş: (Başarı Durumu: bool, Mesaj: str)
        """
        # 1. Doğrulamalar (Validations) - Eskiden add_page.py içindeydi
        if not name or not name.strip():
            return False, "Faaliyet adı boş bırakılamaz."

        if not date_val:
            return False, "Tarih seçimi zorunludur."

        if not is_valid_yyyymm(date_val):
            return False, "Geçersiz tarih formatı (YYYY-MM olmalı)."

        # Gelecek tarih kontrolü
        try:
            year, month = map(int, date_val.split('-'))
            selected_date = datetime(year, month, 1)
            current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if selected_date > current_date:
                return False, "Gelecekteki bir tarihi seçemezsiniz."
        except ValueError:
            return False, "Tarih işlenirken hata oluştu."

        # Puan kontrolü
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            return False, "Geçersiz puan değeri."

        # 2. Nesne Oluşturma
        # ID veritabanında otomatik atanacak, o yüzden None gönderiyoruz
        new_activity = Activity(None, type_val, name.strip(), date_val, comment.strip(), rating)

        # 3. Veritabanına Kayıt
        success = self.repository.add(new_activity)
        
        if success:
            return True, "Faaliyet başarıyla eklendi!"
        else:
            return False, "Veritabanına eklenirken bir hata oluştu."

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, original_activity=None):
        """
        Mevcut bir aktiviteyi günceller.
        """
        # Basit doğrulamalar (Ekleme ile benzer)
        if not name or not name.strip():
            return False, "Faaliyet adı boş bırakılamaz."
            
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            return False, "Geçersiz puan değeri."

        # Değişiklik Kontrolü (Opsiyonel ama iyi bir pratik)
        if original_activity:
            is_same = (
                original_activity.type == type_val and
                original_activity.name == name and
                original_activity.date == date_val and
                original_activity.comment == comment and
                original_activity.rating == rating
            )
            if is_same:
                return False, "Herhangi bir değişiklik yapılmadı."

        # Güncelleme işlemi
        updated_activity = Activity(activity_id, type_val, name.strip(), date_val, comment.strip(), rating)
        success = self.repository.update(updated_activity)

        if success:
            return True, "Kayıt başarıyla güncellendi."
        else:
            return False, "Güncelleme sırasında hata oluştu."

    def delete_activity(self, activity_id):
        """Bir aktiviteyi siler."""
        success = self.repository.delete(activity_id)
        if success:
            return True, "Kayıt başarıyla silindi."
        else:
            return False, "Silme işlemi başarısız oldu."

    def get_dashboard_stats(self, date_prefix="", year_only=False, ignore_dates=False):
        """İstatistik sayfası için verileri hazırlar."""
        return self.repository.get_stats_by_type(date_prefix, year_only, ignore_dates)
        
    def get_comparison_data(self, date_prefix):
        """Karşılaştırma sayfası için verileri çeker."""
        return self.repository.get_comparison_data(date_prefix)

    def get_available_periods(self, period_type="month"):
        """Mevcut dönem listesini çeker."""
        return self.repository.get_available_periods(period_type)
    
    def get_activity_details_by_type(self, activity_type, date_prefix="", year_only=False, ignore_dates=False):
        """İstatistik detayları için liste döndürür."""
        return self.repository.get_details_for_type(activity_type, date_prefix, year_only, ignore_dates)
    
    def get_activity(self, activity_id):
        """ID'ye göre tek bir aktivite getirir."""
        return self.repository.get_by_id(activity_id)
    
    def get_all_activities(self, type_filter="Hepsi", search_term="", date_filter="", page=1, items_per_page=15):
        """
        Filtrelenmiş aktivite listesini ve toplam sayıyı döndürür.
        """
        return self.repository.get_all_filtered(type_filter, search_term, date_filter, page, items_per_page)
    
    def get_all_activity_names(self):
        """Otomatik tamamlama için isim listesini döndürür."""
        return self.repository.get_unique_names()