# bridges/plan_bridge.py
from datetime import datetime
from PySide6.QtCore import (
    QObject, Signal, Slot, Property,
    QAbstractListModel, Qt, QModelIndex, QByteArray
)
from database.plan_repository import PlanRepository
from models import Plan, Folder
from logger_setup import logger

MONTH_NAMES = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def get_priority_color(priority: str) -> str:
    p = (priority or "medium").lower()
    if p == "high":
        return "#EF4444"  # Kırmızı
    elif p == "medium":
        return "#F59E0B"  # Amber/Sarı
    elif p == "low":
        return "#10B981"  # Yeşil
    return "#64748B"


def get_status_color(status: str) -> str:
    s = (status or "planned").lower()
    if s == "completed":
        return "#10B981"  # Yeşil
    elif s == "in_progress":
        return "#3B82F6"  # Mavi
    elif s == "archived":
        return "#94A3B8"  # Gri
    return "#F59E0B"      # Sarı/Turuncu (planned)


class PlanListModel(QAbstractListModel):
    """Hedefler ve Planlar için QML List/Grid modeli."""

    IdRole = Qt.UserRole + 1
    TitleRole = Qt.UserRole + 2
    DescriptionRole = Qt.UserRole + 3
    ScopeRole = Qt.UserRole + 4
    YearRole = Qt.UserRole + 5
    MonthRole = Qt.UserRole + 6
    StatusRole = Qt.UserRole + 7
    ProgressRole = Qt.UserRole + 8
    PriorityRole = Qt.UserRole + 9
    FolderIdRole = Qt.UserRole + 10
    FolderNameRole = Qt.UserRole + 11
    PeriodTextRole = Qt.UserRole + 12
    PriorityColorRole = Qt.UserRole + 13
    StatusColorRole = Qt.UserRole + 14

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plans = []
        self._folder_map = {}

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._plans)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._plans)):
            return None

        p: Plan = self._plans[index.row()]

        if role == self.IdRole:
            return p.id
        elif role == self.TitleRole:
            return p.title or ""
        elif role == self.DescriptionRole:
            return p.description or ""
        elif role == self.ScopeRole:
            return p.scope or "monthly"
        elif role == self.YearRole:
            return p.year
        elif role == self.MonthRole:
            return p.month or 0
        elif role == self.StatusRole:
            return p.status or "planned"
        elif role == self.ProgressRole:
            return p.progress or 0
        elif role == self.PriorityRole:
            return p.priority or "medium"
        elif role == self.FolderIdRole:
            return p.folder_id or 0
        elif role == self.FolderNameRole:
            return self._folder_map.get(p.folder_id, "Genel") if p.folder_id else "Genel"
        elif role == self.PeriodTextRole:
            if p.scope == "monthly" and p.month and 1 <= p.month <= 12:
                return f"{p.year} {MONTH_NAMES[p.month - 1]}"
            return f"{p.year} Yılı"
        elif role == self.PriorityColorRole:
            return get_priority_color(p.priority)
        elif role == self.StatusColorRole:
            return get_status_color(p.status)

        return None

    def roleNames(self) -> dict:
        return {
            self.IdRole: QByteArray(b"planId"),
            self.TitleRole: QByteArray(b"planTitle"),
            self.DescriptionRole: QByteArray(b"planDescription"),
            self.ScopeRole: QByteArray(b"planScope"),
            self.YearRole: QByteArray(b"planYear"),
            self.MonthRole: QByteArray(b"planMonth"),
            self.StatusRole: QByteArray(b"planStatus"),
            self.ProgressRole: QByteArray(b"planProgress"),
            self.PriorityRole: QByteArray(b"planPriority"),
            self.FolderIdRole: QByteArray(b"planFolderId"),
            self.FolderNameRole: QByteArray(b"planFolderName"),
            self.PeriodTextRole: QByteArray(b"periodText"),
            self.PriorityColorRole: QByteArray(b"priorityColor"),
            self.StatusColorRole: QByteArray(b"statusColor"),
        }

    def set_data(self, plans: list, folder_map: dict):
        self.beginResetModel()
        self._plans = plans
        self._folder_map = folder_map
        self.endResetModel()


class PlanBridge(QObject):
    """Hedefler & Planlar Yönetim Köprüsü."""

    plansChanged = Signal()
    foldersChanged = Signal()
    planSaved = Signal(bool, str)
    folderSaved = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = PlanRepository()
        self._model = PlanListModel(self)

        self._active_folder_id = 0  # 0: Hepsi
        self._scope_filter = "all"   # all, yearly, monthly
        self._status_filter = "all"  # all, planned, in_progress, completed
        self._folders = []
        self._folder_map = {}

        self._total_count = 0
        self._completed_count = 0
        self._in_progress_count = 0

        self.loadFolders()
        self.loadPlans()

    # --- Property Tanımları ---

    @Property(QObject, constant=True)
    def model(self) -> PlanListModel:
        return self._model

    @Property(list, notify=foldersChanged)
    def folders(self) -> list:
        return self._folders

    @Property(int, notify=plansChanged)
    def activeFolderId(self) -> int:
        return self._active_folder_id

    @Property(int, notify=plansChanged)
    def totalPlansCount(self) -> int:
        return self._total_count

    @Property(int, notify=plansChanged)
    def completedPlansCount(self) -> int:
        return self._completed_count

    @Property(int, notify=plansChanged)
    def inProgressPlansCount(self) -> int:
        return self._in_progress_count

    @Property(str, notify=plansChanged)
    def scopeFilter(self) -> str:
        return self._scope_filter

    @Property(str, notify=plansChanged)
    def statusFilter(self) -> str:
        return self._status_filter

    # --- Slotlar: Veri Yükleme & Filtreleme ---

    @Slot()
    def loadFolders(self):
        """Klasörleri veritabanından çeker."""
        try:
            raw_folders = self._repo.get_folders()
            self._folder_map = {f.id: f.name for f in raw_folders}
            folder_list = [{"id": 0, "name": "Tüm Planlar"}]
            for f in raw_folders:
                folder_list.append({"id": f.id, "name": f.name})
            self._folders = folder_list
            self.foldersChanged.emit()
        except Exception as e:
            logger.error(f"PlanBridge loadFolders error: {e}")

    @Slot()
    def loadPlans(self):
        """Planları filtreleyerek yükler."""
        try:
            raw_plans = self._repo.get_plans()

            self._total_count = len(raw_plans)
            self._completed_count = sum(1 for p in raw_plans if p.status == "completed")
            self._in_progress_count = sum(1 for p in raw_plans if p.status == "in_progress")

            filtered = []
            for p in raw_plans:
                # Klasör filtresi
                if self._active_folder_id > 0 and p.folder_id != self._active_folder_id:
                    continue

                # Kapsam filtresi
                if self._scope_filter != "all" and p.scope != self._scope_filter:
                    continue

                # Durum filtresi
                if self._status_filter != "all" and p.status != self._status_filter:
                    continue

                filtered.append(p)

            self._model.set_data(filtered, self._folder_map)
            self.plansChanged.emit()
        except Exception as e:
            logger.error(f"PlanBridge loadPlans error: {e}")

    @Slot(int)
    def setActiveFolder(self, folder_id: int):
        if self._active_folder_id != folder_id:
            self._active_folder_id = folder_id
            self.loadPlans()

    @Slot(str)
    def setScopeFilter(self, scope: str):
        if self._scope_filter != scope:
            self._scope_filter = scope
            self.loadPlans()

    @Slot(str)
    def setStatusFilter(self, status: str):
        if self._status_filter != status:
            self._status_filter = status
            self.loadPlans()

    # --- Slotlar: Plan CRUD ---

    @Slot(str, str, str, int, int, str, int, result=bool)
    def addPlan(self, title: str, description: str, scope: str, year: int, month: int, priority: str, folder_id: int) -> bool:
        title = (title or "").strip()
        if not title:
            self.planSaved.emit(False, "Plan başlığı boş bırakılamaz.")
            return False

        fid = folder_id if folder_id and folder_id > 0 else None
        m = month if scope == "monthly" and month and month > 0 else None

        plan = Plan(
            id=None,
            title=title,
            description=(description or "").strip(),
            scope=scope or "monthly",
            year=year or datetime.now().year,
            month=m,
            status="planned",
            progress=0,
            priority=priority or "medium",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            folder_id=fid
        )

        success = self._repo.add_plan(plan)
        if success:
            self.planSaved.emit(True, f"'{title}' planı başarıyla eklendi.")
            self.loadPlans()
            return True
        else:
            self.planSaved.emit(False, "Plan eklenirken hata oluştu.")
            return False

    @Slot(int, str, str, str, int, str, int, result=bool)
    def updatePlan(self, plan_id: int, title: str, description: str, status: str, progress: int, priority: str, folder_id: int) -> bool:
        title = (title or "").strip()
        if not title:
            self.planSaved.emit(False, "Plan başlığı boş bırakılamaz.")
            return False

        existing = self._repo.get_plan_by_id(plan_id)
        fid = folder_id if folder_id and folder_id > 0 else None

        # İlerleme 100 olunca otomatik tamamlandı yap
        if progress >= 100 and status != "completed":
            status = "completed"
            progress = 100
        elif progress < 100 and status == "completed":
            status = "in_progress"

        plan = Plan(
            id=plan_id,
            title=title,
            description=(description or "").strip(),
            scope=existing.scope if existing else "monthly",
            year=existing.year if existing else datetime.now().year,
            month=existing.month if existing else None,
            status=status,
            progress=max(0, min(100, progress)),
            priority=priority,
            created_at=existing.created_at if existing else "",
            folder_id=fid
        )

        success = self._repo.update_plan(plan)

        if success:
            self.planSaved.emit(True, f"'{title}' başarıyla güncellendi.")
            self.loadPlans()
            return True
        else:
            self.planSaved.emit(False, "Plan güncellenirken hata oluştu.")
            return False

    @Slot(int, int)
    def updateProgress(self, plan_id: int, progress: int):
        plan = self._repo.get_plan_by_id(plan_id)
        if plan:
            new_status = "completed" if progress >= 100 else ("in_progress" if progress > 0 else "planned")
            self._repo.update_plan_progress(plan_id, max(0, min(100, progress)), new_status)
            self.loadPlans()

    @Slot(int, str)
    def updateStatus(self, plan_id: int, status: str):
        plan = self._repo.get_plan_by_id(plan_id)
        if plan:
            prog = 100 if status == "completed" else (0 if status == "planned" else plan.progress)
            self._repo.update_plan_progress(plan_id, prog, status)
            self.loadPlans()


    @Slot(int, result=bool)
    def deletePlan(self, plan_id: int) -> bool:
        success = self._repo.delete_plan(plan_id)
        if success:
            self.planSaved.emit(True, "Plan silindi.")
            self.loadPlans()
            return True
        return False

    @Slot(int, result=dict)
    def getPlanById(self, plan_id: int) -> dict:
        plan = self._repo.get_plan_by_id(plan_id)
        if not plan:
            return {}
        return {
            "id": plan.id,
            "title": plan.title,
            "description": plan.description or "",
            "scope": plan.scope,
            "year": plan.year,
            "month": plan.month or 1,
            "status": plan.status,
            "progress": plan.progress,
            "priority": plan.priority,
            "folderId": plan.folder_id or 0
        }

    # --- Slotlar: Klasör Yönetimi ---

    @Slot(str, result=bool)
    def addFolder(self, name: str) -> bool:
        name = (name or "").strip()
        if not name:
            self.folderSaved.emit(False, "Klasör adı boş olamaz.")
            return False
        success = self._repo.add_folder(name)
        if success:
            self.folderSaved.emit(True, f"'{name}' klasörü oluşturuldu.")
            self.loadFolders()
            self.loadPlans()
            return True
        self.folderSaved.emit(False, "Klasör oluşturulamadı.")
        return False

    @Slot(int, str, result=bool)
    def updateFolder(self, folder_id: int, name: str) -> bool:
        name = (name or "").strip()
        if not name:
            self.folderSaved.emit(False, "Klasör adı boş olamaz.")
            return False
        success = self._repo.update_folder(folder_id, name)
        if success:
            self.folderSaved.emit(True, "Klasör güncellendi.")
            self.loadFolders()
            self.loadPlans()
            return True
        return False

    @Slot(int, result=bool)
    def deleteFolder(self, folder_id: int) -> bool:
        success = self._repo.delete_folder(folder_id)
        if success:
            if self._active_folder_id == folder_id:
                self._active_folder_id = 0
            self.folderSaved.emit(True, "Klasör silindi.")
            self.loadFolders()
            self.loadPlans()
            return True
        return False
