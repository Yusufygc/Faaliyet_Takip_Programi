# controllers/main_controller.py
from database.repository import ActivityRepository
from models import Activity
from utils import is_valid_yyyymm, extract_year_month
from datetime import datetime
from controllers.workers import DbWorker
from logger_setup import logger

class MainController:
    """
    Uygulamanın iş mantığını yöneten sınıf.
    Arayüz (View) ve Veri (Model/Repository) arasındaki iletişimi sağlar.
    ASENKRON YAPI: İşlemler DbWorker ile arka planda yapılır.
    """

    def __init__(self):
        # Repository nesnesini başlatıyoruz
        self.repository = ActivityRepository()
        self.workers = set() # Aktif worker'ları takip etmek için

    def _run_async(self, func, callback, *args, **kwargs):
        """Yardımcı metod: Verilen fonksiyonu asenkron çalıştırır."""
        worker = DbWorker(func, *args, **kwargs)
        
        if callback:
            worker.finished.connect(callback)
            
        # Worker bittiğinde listeden temizle
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        # Referansı sakla ve başlat
        self.workers.add(worker)
        worker.start()
    
    def _cleanup_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)

    def get_all_activities(self, callback, type_filter="Hepsi", search_term="", date_filter="", page=1, items_per_page=15):
        """Filtrelenmiş aktivite listesini asenkron getirir."""
        self._run_async(
            self.repository.get_all_filtered, 
            callback, 
            type_filter, search_term, date_filter, page, items_per_page
        )

    def get_all_activity_names(self, callback):
        """Otomatik tamamlama için isim listesini asenkron getirir."""
        self._run_async(self.repository.get_unique_names, callback)

    def get_activity(self, activity_id, callback):
        """ID'ye göre aktiviteyi asenkron getirir."""
        self._run_async(self.repository.get_by_id, callback, activity_id)

    def add_activity(self, type_val, name, date_val, comment, rating_val, callback):
        """
        Yeni bir aktivite ekler (Önce validasyon, sonra asenkron kayıt).
        Validasyon senkron yapılır çünkü çok hızlıdır.
        """
        # Doğrulamalar (Senkron)
        if not name or not name.strip():
            callback((False, "Faaliyet adı boş bırakılamaz."))
            return

        if not date_val:
            callback((False, "Tarih seçimi zorunludur."))
            return

        # Tarih kontrolü
        try:
            year, month = map(int, date_val.split('-'))
            selected_date = datetime(year, month, 1)
            current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if selected_date > current_date:
                callback((False, "Gelecekteki bir tarihi seçemezsiniz."))
                return
        except ValueError:
            callback((False, "Tarih işlenirken hata oluştu."))
            return

        # Puan kontrolü
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return

        # Nesne Oluşturma
        new_activity = Activity(None, type_val, name.strip(), date_val, comment.strip(), rating)

        # Veritabanına Kayıt (Asenkron)
        def save_operation():
            success = self.repository.add(new_activity)
            if success:
                return True, "Faaliyet başarıyla eklendi!"
            else:
                return False, "Veritabanına eklenirken bir hata oluştu."
        
        self._run_async(save_operation, callback)

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity=None):
        """Mevcut bir aktiviteyi günceller (Asenkron)."""
        if not name or not name.strip():
            callback((False, "Faaliyet adı boş bırakılamaz."))
            return
            
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return

        # Değişiklik Kontrolü
        if original_activity:
            is_same = (
                original_activity.type == type_val and
                original_activity.name == name and
                original_activity.date == date_val and
                original_activity.comment == comment and
                original_activity.rating == rating
            )
            if is_same:
                callback((False, "Herhangi bir değişiklik yapılmadı."))
                return

        updated_activity = Activity(activity_id, type_val, name.strip(), date_val, comment.strip(), rating)

        def update_operation():
            success = self.repository.update(updated_activity)
            if success:
                return True, "Kayıt başarıyla güncellendi."
            else:
                return False, "Güncelleme sırasında hata oluştu."

        self._run_async(update_operation, callback)

    def delete_activity(self, activity_id, callback):
        """Bir aktiviteyi asenkron siler."""
        def delete_operation():
            success = self.repository.delete(activity_id)
            if success:
                return True, "Kayıt başarıyla silindi."
            else:
                return False, "Silme işlemi başarısız oldu."
        
        self._run_async(delete_operation, callback)

    def get_dashboard_stats(self, callback, date_prefix="", year_only=False, ignore_dates=False):
        """İstatistik verilerini asenkron çeker."""
        self._run_async(self.repository.get_stats_by_type, callback, date_prefix, year_only, ignore_dates)
        
    def get_comparison_data(self, callback, date_prefix):
        """Karşılaştırma verilerini asenkron çeker."""
        self._run_async(self.repository.get_comparison_data, callback, date_prefix)

    def get_available_periods(self, callback, period_type="month"):
        """Dönem listesini asenkron çeker."""
        self._run_async(self.repository.get_available_periods, callback, period_type)
    
    def get_activity_details_by_type(self, callback, activity_type, date_prefix="", year_only=False, ignore_dates=False):
        """Detay listesini asenkron çeker."""
        self._run_async(self.repository.get_details_for_type, callback, activity_type, date_prefix, year_only, ignore_dates)

    def get_pdf_data(self, callback, date_prefix):
        """PDF verisini asenkron çeker."""
        self._run_async(self.repository.get_detailed_data_for_pdf, callback, date_prefix)