# controllers/main_controller.py
"""
Facade controller — view kodu değişmeden domain controller'lara delege eder.
"""
from database.repository import ActivityRepository
from database.plan_repository import PlanRepository
from database.type_repository import TypeRepository
from controllers.activity_controller import ActivityController
from controllers.type_controller import TypeController
from controllers.plan_controller import PlanController
from controllers.settings_controller import SettingsController


class MainController:
    def __init__(self):
        repository = ActivityRepository()
        plan_repo = PlanRepository()
        type_repo = TypeRepository()

        self._activity = ActivityController(repository)
        self._type = TypeController(type_repo)
        self._plan = PlanController(plan_repo)
        self._settings = SettingsController(type_repo)

        self._type.synchronize_types()

    # --- Faaliyet ---

    def get_all_activities(self, callback, type_filter="Hepsi", search_term="", date_filter="", page=1, items_per_page=15):
        return self._activity.get_all_activities(callback, type_filter, search_term, date_filter, page, items_per_page)

    def get_all_activity_names(self, callback):
        return self._activity.get_all_activity_names(callback)

    def get_activity(self, activity_id, callback):
        return self._activity.get_activity(activity_id, callback)

    def add_activity(self, type_val, name, date_val, comment, rating_val, callback, end_date=None):
        return self._activity.add_activity(type_val, name, date_val, comment, rating_val, callback, end_date)

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity=None, end_date=None):
        return self._activity.update_activity(activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity, end_date)

    def delete_activity(self, activity_id, callback):
        return self._activity.delete_activity(activity_id, callback)

    def get_dashboard_stats(self, callback, date_prefix="", year_only=False, ignore_dates=False):
        return self._activity.get_dashboard_stats(callback, date_prefix, year_only, ignore_dates)

    def get_comparison_data(self, callback, date_prefix):
        return self._activity.get_comparison_data(callback, date_prefix)

    def get_available_periods(self, callback, period_type="month"):
        return self._activity.get_available_periods(callback, period_type)

    def get_activity_details_by_type(self, callback, activity_type, date_prefix="", year_only=False, ignore_dates=False):
        return self._activity.get_activity_details_by_type(callback, activity_type, date_prefix, year_only, ignore_dates)

    def get_pdf_data(self, callback, date_prefix):
        return self._activity.get_pdf_data(callback, date_prefix)

    def get_trend_data(self, callback, year, category=None):
        return self._activity.get_trend_data(callback, year, category)

    def get_activity_details_by_month(self, callback, date_str, category=None):
        return self._activity.get_activity_details_by_month(callback, date_str, category)

    # --- Tür ---

    def get_all_activity_types(self, callback):
        return self._type.get_all_activity_types(callback)

    def add_activity_type(self, name, callback):
        return self._type.add_activity_type(name, callback)

    def update_activity_type(self, old_name, new_name, callback):
        return self._type.update_activity_type(old_name, new_name, callback)

    def delete_activity_type(self, name, callback):
        return self._type.delete_activity_type(name, callback)

    def synchronize_types(self):
        return self._type.synchronize_types()

    # --- Plan ---

    def add_plan(self, title, description, scope, year, month, priority, folder_id, callback):
        return self._plan.add_plan(title, description, scope, year, month, priority, folder_id, callback)

    def update_plan(self, plan_id, title, description, status, progress, priority, folder_id, callback):
        return self._plan.update_plan(plan_id, title, description, status, progress, priority, folder_id, callback)

    def update_plan_progress(self, plan_id, progress, status, callback):
        return self._plan.update_plan_progress(plan_id, progress, status, callback)

    def delete_plan(self, plan_id, callback):
        return self._plan.delete_plan(plan_id, callback)

    def get_plans(self, scope, year, month, callback):
        return self._plan.get_plans(scope, year, month, callback)

    # --- Klasör ---

    def get_folders(self, callback):
        return self._plan.get_folders(callback)

    def add_folder(self, name, callback):
        return self._plan.add_folder(name, callback)

    def update_folder(self, folder_id, name, callback):
        return self._plan.update_folder(folder_id, name, callback)

    def delete_folder(self, folder_id, callback):
        return self._plan.delete_folder(folder_id, callback)

    # --- API Anahtarları ---

    def get_api_keys(self, callback):
        return self._settings.get_api_keys(callback)

    def save_api_keys(self, tmdb_key, rawg_key, callback):
        return self._settings.save_api_keys(tmdb_key, rawg_key, callback)
