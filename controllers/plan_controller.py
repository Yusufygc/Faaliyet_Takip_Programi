# controllers/plan_controller.py
from datetime import datetime
from models import Plan
from controllers._base_controller import _BaseController


class PlanController(_BaseController):
    def __init__(self, plan_repo):
        super().__init__()
        self.plan_repo = plan_repo

    # --- Plan ---

    def add_plan(self, title, description, scope, year, month, priority, folder_id, callback):
        if not title:
            callback((False, "Başlık boş olamaz."))
            return
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan = Plan(None, title, description, scope, year, month, 'planned', 0, priority, created_at, folder_id)

        def op():
            return self.plan_repo.add_plan(plan), "Plan eklendi."

        self._run_async(lambda: op(), lambda res: callback((res[0], res[1]) if isinstance(res, tuple) else (res, "")))

    def update_plan(self, plan_id, title, description, status, progress, priority, folder_id, callback):
        if not title:
            callback((False, "Başlık boş olamaz."))
            return
        plan = Plan(plan_id, title, description, "", 0, 0, status, progress, priority, "", folder_id)

        def op():
            return self.plan_repo.update_plan(plan), "Plan güncellendi."

        self._run_async(lambda: op(), lambda res: callback((res[0], res[1])))

    def update_plan_progress(self, plan_id, progress, status, callback):
        def op():
            return self.plan_repo.update_plan_progress(plan_id, progress, status)
        self._run_async(op, callback)

    def delete_plan(self, plan_id, callback):
        def op():
            return self.plan_repo.delete_plan(plan_id), "Plan silindi."
        self._run_async(lambda: op(), lambda res: callback((res[0], res[1])))

    def get_plans(self, scope, year, month, callback):
        self._run_async(self.plan_repo.get_plans, callback, scope, year, month)

    # --- Klasör ---

    def get_folders(self, callback):
        self._run_async(self.plan_repo.get_folders, callback)

    def add_folder(self, name, callback):
        if not name or not name.strip():
            callback((False, "Klasör adı boş olamaz."))
            return

        def op():
            return self.plan_repo.add_folder(name.strip()), "Klasör eklendi."

        self._run_async(lambda: op(), lambda res: callback(res))

    def update_folder(self, folder_id, name, callback):
        if not name or not name.strip():
            callback((False, "Klasör adı boş olamaz."))
            return

        def op():
            return self.plan_repo.update_folder(folder_id, name.strip()), "Klasör güncellendi."

        self._run_async(lambda: op(), lambda res: callback(res))

    def delete_folder(self, folder_id, callback):
        def op():
            return self.plan_repo.delete_folder(folder_id), "Klasör silindi."
        self._run_async(lambda: op(), lambda res: callback(res))
