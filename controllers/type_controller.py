# controllers/type_controller.py
from controllers._base_controller import _BaseController


class TypeController(_BaseController):
    def __init__(self, type_repo):
        super().__init__()
        self.type_repo = type_repo

    def get_all_activity_types(self, callback):
        self._run_async(self.type_repo.get_all_types, callback)

    def add_activity_type(self, name, callback):
        if not name or not name.strip():
            callback((False, "Tür adı boş olamaz."))
            return
        self._run_async(self.type_repo.add_type, callback, name.strip())

    def update_activity_type(self, old_name, new_name, callback):
        if not new_name or not new_name.strip():
            callback((False, "Yeni tür adı boş olamaz."))
            return
        if old_name == new_name:
            callback((False, "Herhangi bir değişiklik yapılmadı."))
            return
        self._run_async(self.type_repo.update_type, callback, old_name, new_name.strip())

    def delete_activity_type(self, name, callback):
        self._run_async(self.type_repo.delete_type, callback, name)

    def synchronize_types(self):
        self._run_async(self.type_repo.synchronize_types, None)
