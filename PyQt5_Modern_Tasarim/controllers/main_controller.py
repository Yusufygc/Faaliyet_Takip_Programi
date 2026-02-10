# controllers/main_controller.py
from database.repository import ActivityRepository
from models import Activity, ActivityFilter, Plan
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
        
        # Başlangıçta türleri senkronize et
        self.synchronize_types()

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
        # Filtre objesini oluştur
        filter_obj = ActivityFilter(
            type_filter=type_filter,
            search_term=search_term,
            date_filter=date_filter,
            page=page,
            items_per_page=items_per_page
        )
        
        self._run_async(
            self.repository.get_all_filtered, 
            callback, 
            filter_obj
        )

    def get_all_activity_names(self, callback):
        """Otomatik tamamlama için isim listesini asenkron getirir."""
        self._run_async(self.repository.get_unique_names, callback)

    def get_activity(self, activity_id, callback):
        """ID'ye göre aktiviteyi asenkron getirir."""
        self._run_async(self.repository.get_by_id, callback, activity_id)

    def add_activity(self, type_val, name, date_val, comment, rating_val, callback, end_date=None):
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

        # Tarih kontrolü (YYYY-MM veya YYYY-MM-DD olabilir)
        try:
            # Sadece format kontrolü yapalım, gün geçerliliği datetime ile kontrol edilir
            if len(date_val.split('-')) == 2:
                # Eski format (YYYY-MM) - Geriye dönük uyumluluk için, ama arayüzden artık tam tarih geliyor
                year, month = map(int, date_val.split('-'))
                selected_date = datetime(year, month, 1)
            else:
                # Yeni format (YYYY-MM-DD)
                selected_date = datetime.strptime(date_val, "%Y-%m-%d")

            current_date = datetime.now()
            # Gelecek kontrolü (Opsiyonel - Geleceğe kayıt girilebilir mi? Kullanıcı isteğinde yasak yok
            # ama mevcut kodda yasak vardı. Bunu koruyalım veya esnetelim.
            # Kodda: current_date.replace(day=1...) kullanılmıştı. Tam tarih için:
            
            # Gelecek kontrolünü kaldıralım veya sadece yıl/ay bazlı yapalım. 
            # Kullanıcı planlama da yapıyor olabilir. Ama mevcut kuralı koruyalım:
            # if selected_date > current_date:
            #    callback((False, "Gelecekteki bir tarihi seçemezsiniz."))
            #    return
             
        except ValueError:
            callback((False, "Tarih formatı geçersiz."))
            return
            
        # Bitiş Tarihi Kontrolü
        if end_date:
            try:
                dt_end = datetime.strptime(end_date, "%Y-%m-%d")
                if dt_end < selected_date:
                     callback((False, "Bitiş tarihi, başlangıç tarihinden önce olamaz."))
                     return
            except ValueError:
                callback((False, "Bitiş tarihi formatı geçersiz."))
                return

        # Puan kontrolü
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return

        # Nesne Oluşturma
        new_activity = Activity(None, type_val, name.strip(), date_val, comment.strip(), rating, end_date)

        # Veritabanına Kayıt (Asenkron)
        def save_operation():
            success = self.repository.add(new_activity)
            if success:
                return True, "Faaliyet başarıyla eklendi!"
            else:
                return False, "Veritabanına eklenirken bir hata oluştu."
        
        self._run_async(save_operation, callback)

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity=None, end_date=None):
        """Mevcut bir aktiviteyi günceller (Asenkron)."""
        if not name or not name.strip():
            callback((False, "Faaliyet adı boş bırakılamaz."))
            return
            
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return
            
        # Tarih Validasyonu (Basit)
        if end_date:
             if end_date < date_val: # String karşılaştırma YYYY-MM-DD için çalışır
                 callback((False, "Bitiş tarihi, başlangıç tarihinden önce olamaz."))
                 return

        # Değişiklik Kontrolü
        if original_activity:
            is_same = (
                original_activity.type == type_val and
                original_activity.name == name and
                original_activity.date == date_val and
                original_activity.comment == comment and
                original_activity.rating == rating and
                getattr(original_activity, 'end_date', None) == end_date
            )
            if is_same:
                callback((False, "Herhangi bir değişiklik yapılmadı."))
                return

        updated_activity = Activity(activity_id, type_val, name.strip(), date_val, comment.strip(), rating, end_date)

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

    def get_trend_data(self, callback, year, category=None):
        """Trend analizi verilerini asenkron çeker."""
        # Yıl validasyonu
        if not str(year).isdigit() or len(str(year)) != 4:
            callback([])
            return
        self._run_async(self.repository.get_monthly_activity_counts, callback, int(year), category)
    
    def get_activity_details_by_month(self, callback, date_str, category=None):
        """Belirli bir aydaki aktivite detaylarını çeker (isim, tarih)"""
        self._run_async(self.repository.get_activity_details_by_month, callback, date_str, category)

    # --- Ayarlar / Tür Yönetimi ---

    def get_all_activity_types(self, callback):
        """Tüm türleri asenkron getirir."""
        self._run_async(self.repository.get_all_types, callback)

    def add_activity_type(self, name, callback):
        """Yeni tür ekleme (Asenkron)."""
        if not name or not name.strip():
            callback((False, "Tür adı boş olamaz."))
            return
        self._run_async(self.repository.add_type, callback, name.strip())

    def update_activity_type(self, old_name, new_name, callback):
        """Tür güncelleme (Asenkron)."""
        if not new_name or not new_name.strip():
            callback((False, "Yeni tür adı boş olamaz."))
            return
        if old_name == new_name:
            callback((False, "Herhangi bir değişiklik yapılmadı."))
            return
            
        self._run_async(self.repository.update_type, callback, old_name, new_name.strip())

    def delete_activity_type(self, name, callback):
        """Tür silme (Asenkron)."""
        self._run_async(self.repository.delete_type, callback, name)

    def synchronize_types(self):
        """Eksik türleri senkronize et (Arka planda çalışır, callback gerekmez)."""
        self._run_async(self.repository.synchronize_types, None)

    # --- Plan / Hedef İşlemleri ---

    def add_plan(self, title, description, scope, year, month, priority, folder_id, callback):
        """Yeni plan ekler."""
        if not title:
            callback((False, "Başlık boş olamaz."))
            return
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Yeni plan status='planned', progress=0 başlar
        plan = Plan(None, title, description, scope, year, month, 'planned', 0, priority, created_at, folder_id)
        
        def op():
            return self.repository.add_plan(plan), "Plan eklendi."
            
        self._run_async(lambda: op(), lambda res: callback((res[0], res[1]) if isinstance(res, tuple) else (res, "")))

    def update_plan(self, plan_id, title, description, status, progress, priority, folder_id, callback):
        """Plan günceller."""
        if not title:
            callback((False, "Başlık boş olamaz."))
            return

        # Modeli oluştur (ID ve diğer alanlarla)
        # Not: Created_at, Scope, Year, Month değişmez varsayıyoruz düzenlemede
        # Hızlı çözüm: Repository sadece ilgili alanları güncelliyor, o yüzden dummy değerler verebiliriz
        # ama en doğrusu repository update metoduna uygun nesne yollamak.
        # Repository update_plan sql: title=?, description=?, status=?, progress=?, priority=?, folder_id=? WHERE id=?
        # Diğer alanlar (scope, year, month) kullanılmıyor.
        
        plan = Plan(plan_id, title, description, "", 0, 0, status, progress, priority, "", folder_id)
        
        def op():
            return self.repository.update_plan(plan), "Plan güncellendi."
            
        self._run_async(lambda: op(), lambda res: callback((res[0], res[1])))

    def update_plan_progress(self, plan_id, progress, status, callback):
        """İlerleme durumu günceller."""
        def op():
            return self.repository.update_plan_progress(plan_id, progress, status)
        self._run_async(op, callback)

    def delete_plan(self, plan_id, callback):
        """Plan siler."""
        def op():
            return self.repository.delete_plan(plan_id), "Plan silindi."
        self._run_async(lambda: op(), lambda res: callback((res[0], res[1])))

    def get_plans(self, scope, year, month, callback):
        """Planları getirir."""
        self._run_async(self.repository.get_plans, callback, scope, year, month)

    # --- Folder (Klasör) İşlemleri ---

    def get_folders(self, callback):
        """Klasörleri getirir."""
        self._run_async(self.repository.get_folders, callback)

    def add_folder(self, name, callback):
        """Yeni klasör ekler."""
        if not name or not name.strip():
            callback((False, "Klasör adı boş olamaz."))
            return
        
        def op():
            return self.repository.add_folder(name.strip()), "Klasör eklendi."
        self._run_async(lambda: op(), lambda res: callback(res))

    def update_folder(self, folder_id, name, callback):
        """Klasör adını günceller."""
        if not name or not name.strip():
            callback((False, "Klasör adı boş olamaz."))
            return
            
        def op():
            return self.repository.update_folder(folder_id, name.strip()), "Klasör güncellendi."
        self._run_async(lambda: op(), lambda res: callback(res))

    def delete_folder(self, folder_id, callback):
        """Klasör siler."""
        def op():
            return self.repository.delete_folder(folder_id), "Klasör silindi."
        self._run_async(lambda: op(), lambda res: callback(res))

    # --- API Anahtarı Yönetimi ---

    def get_api_keys(self, callback):
        """Kaydedilmiş API anahtarlarını getirir."""
        def op():
            tmdb = self.repository.get_setting("tmdb_api_key") or ""
            rawg = self.repository.get_setting("rawg_api_key") or ""
            return {"tmdb_api_key": tmdb, "rawg_api_key": rawg}
        self._run_async(op, callback)

    def save_api_keys(self, tmdb_key, rawg_key, callback):
        """API anahtarlarını kaydeder."""
        def op():
            r1 = self.repository.set_setting("tmdb_api_key", tmdb_key.strip())
            r2 = self.repository.set_setting("rawg_api_key", rawg_key.strip())
            if r1 and r2:
                return True, "API anahtarları başarıyla kaydedildi."
            else:
                return False, "Kayıt sırasında hata oluştu."
        self._run_async(op, callback)