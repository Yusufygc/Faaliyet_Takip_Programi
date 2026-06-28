# controllers/activity_controller.py
from datetime import datetime
from models import Activity, ActivityFilter
from controllers._base_controller import _BaseController
from logger_setup import logger


class ActivityController(_BaseController):
    def __init__(self, repository):
        super().__init__()
        self.repository = repository

    def get_all_activities(self, callback, type_filter="Hepsi", search_term="", date_filter="", page=1, items_per_page=15):
        filter_obj = ActivityFilter(
            type_filter=type_filter,
            search_term=search_term,
            date_filter=date_filter,
            page=page,
            items_per_page=items_per_page,
        )
        self._run_async(self.repository.get_all_filtered, callback, filter_obj)

    def get_all_activity_names(self, callback):
        self._run_async(self.repository.get_unique_names, callback)

    def get_activity(self, activity_id, callback):
        self._run_async(self.repository.get_by_id, callback, activity_id)

    def add_activity(self, type_val, name, date_val, comment, rating_val, callback, end_date=None):
        if not name or not name.strip():
            callback((False, "Faaliyet adı boş bırakılamaz."))
            return
        if not date_val:
            callback((False, "Tarih seçimi zorunludur."))
            return
        try:
            if len(date_val.split('-')) == 2:
                year, month = map(int, date_val.split('-'))
                selected_date = datetime(year, month, 1)
            else:
                selected_date = datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            callback((False, "Tarih formatı geçersiz."))
            return
        if end_date:
            try:
                dt_end = datetime.strptime(end_date, "%Y-%m-%d")
                if dt_end < selected_date:
                    callback((False, "Bitiş tarihi, başlangıç tarihinden önce olamaz."))
                    return
            except ValueError:
                callback((False, "Bitiş tarihi formatı geçersiz."))
                return
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return

        new_activity = Activity(None, type_val, name.strip(), date_val, comment.strip(), rating, end_date)

        def save_operation():
            success = self.repository.add(new_activity)
            if success:
                return True, "Faaliyet başarıyla eklendi!"
            return False, "Veritabanına eklenirken bir hata oluştu."

        self._run_async(save_operation, callback)

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity=None, end_date=None):
        if not name or not name.strip():
            callback((False, "Faaliyet adı boş bırakılamaz."))
            return
        try:
            rating = int(rating_val) if rating_val and rating_val != "Seçiniz" else 0
        except ValueError:
            callback((False, "Geçersiz puan değeri."))
            return
        if end_date and end_date < date_val:
            callback((False, "Bitiş tarihi, başlangıç tarihinden önce olamaz."))
            return
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
            return False, "Güncelleme sırasında hata oluştu."

        self._run_async(update_operation, callback)

    def delete_activity(self, activity_id, callback):
        def delete_operation():
            success = self.repository.delete(activity_id)
            if success:
                return True, "Kayıt başarıyla silindi."
            return False, "Silme işlemi başarısız oldu."
        self._run_async(delete_operation, callback)

    def get_dashboard_stats(self, callback, date_prefix="", year_only=False, ignore_dates=False):
        self._run_async(self.repository.get_stats_by_type, callback, date_prefix, year_only, ignore_dates)

    def get_comparison_data(self, callback, date_prefix):
        self._run_async(self.repository.get_comparison_data, callback, date_prefix)

    def get_available_periods(self, callback, period_type="month"):
        self._run_async(self.repository.get_available_periods, callback, period_type)

    def get_activity_details_by_type(self, callback, activity_type, date_prefix="", year_only=False, ignore_dates=False):
        self._run_async(self.repository.get_details_for_type, callback, activity_type, date_prefix, year_only, ignore_dates)

    def get_pdf_data(self, callback, date_prefix):
        self._run_async(self.repository.get_detailed_data_for_pdf, callback, date_prefix)

    def get_trend_data(self, callback, year, category=None):
        if not str(year).isdigit() or len(str(year)) != 4:
            callback([])
            return
        self._run_async(self.repository.get_monthly_activity_counts, callback, int(year), category)

    def get_activity_details_by_month(self, callback, date_str, category=None):
        self._run_async(self.repository.get_activity_details_by_month, callback, date_str, category)
