# controllers/main_controller.py
"""
Facade controller — view kodu değişmeden domain controller'lara delege eder.
Signal wrapping gerektiren mutasyon metodları açıkça tanımlanmıştır;
geri kalan pure-delegation metodlar __getattr__ ile yönlendirilir.
Bu yaklaşım, tekrarlı `return self._x.y(...)` kalıbını ortadan kaldırır.
"""
from PyQt5.QtCore import QObject, pyqtSignal
from database.repository import ActivityRepository
from database.plan_repository import PlanRepository
from database.type_repository import TypeRepository
from controllers.activity_controller import ActivityController
from controllers.type_controller import TypeController
from controllers.plan_controller import PlanController
from controllers.settings_controller import SettingsController


class MainController(QObject):
    activity_changed = pyqtSignal()
    plan_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        repository = ActivityRepository()
        plan_repo = PlanRepository()
        type_repo = TypeRepository()

        self._activity = ActivityController(repository)
        self._type = TypeController(type_repo)
        self._plan = PlanController(plan_repo)
        self._settings = SettingsController(type_repo)

        self._type.synchronize_types()

    # --- Sinyal sarmalayıcılar ---

    def _emit_activity_changed(self, callback):
        def wrapped(result):
            if callback:
                callback(result)
            if isinstance(result, tuple) and result[0]:
                self.activity_changed.emit()
        return wrapped

    def _emit_plan_changed(self, callback):
        def wrapped(result):
            if callback:
                callback(result)
            if isinstance(result, tuple) and result[0]:
                self.plan_changed.emit()
        return wrapped

    # --- Sinyal gerektiren mutasyon metodları (açık tanım zorunlu) ---

    def add_activity(self, type_val, name, date_val, comment, rating_val, callback, end_date=None):
        return self._activity.add_activity(type_val, name, date_val, comment, rating_val, self._emit_activity_changed(callback), end_date)

    def update_activity(self, activity_id, type_val, name, date_val, comment, rating_val, callback, original_activity=None, end_date=None):
        return self._activity.update_activity(activity_id, type_val, name, date_val, comment, rating_val, self._emit_activity_changed(callback), original_activity, end_date)

    def delete_activity(self, activity_id, callback):
        return self._activity.delete_activity(activity_id, self._emit_activity_changed(callback))

    def add_plan(self, title, description, scope, year, month, priority, folder_id, callback):
        return self._plan.add_plan(title, description, scope, year, month, priority, folder_id, self._emit_plan_changed(callback))

    def update_plan(self, plan_id, title, description, status, progress, priority, folder_id, callback):
        return self._plan.update_plan(plan_id, title, description, status, progress, priority, folder_id, self._emit_plan_changed(callback))

    def delete_plan(self, plan_id, callback):
        return self._plan.delete_plan(plan_id, self._emit_plan_changed(callback))

    def add_folder(self, name, callback):
        return self._plan.add_folder(name, self._emit_plan_changed(callback))

    def update_folder(self, folder_id, name, callback):
        return self._plan.update_folder(folder_id, name, self._emit_plan_changed(callback))

    def delete_folder(self, folder_id, callback):
        return self._plan.delete_folder(folder_id, self._emit_plan_changed(callback))

    # --- Pure delegation: __getattr__ ile yönlendirilir ---

    def __getattr__(self, name: str):
        """Signal wrapping gerektirmeyen metodları sub-controller'lara yönlendir.
        Sıra önemlidir: _activity → _type → _plan → _settings.
        """
        for sub in ('_activity', '_type', '_plan', '_settings'):
            try:
                ctrl = super().__getattribute__(sub)
                if hasattr(ctrl, name):
                    return getattr(ctrl, name)
            except AttributeError:
                pass
        raise AttributeError(f"'MainController' has no attribute '{name}'")
