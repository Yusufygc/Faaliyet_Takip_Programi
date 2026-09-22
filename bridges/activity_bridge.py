# bridges/activity_bridge.py
import math
from PySide6.QtCore import (
    QObject, Signal, Slot, Property,
    QAbstractListModel, Qt, QModelIndex, QByteArray
)
from database.repository import ActivityRepository
from database.type_repository import TypeRepository
from services.cover_fetch_service import CoverFetchService
from models import Activity, ActivityFilter
from utils import is_valid_date
from logger_setup import logger


def get_type_color(activity_type: str) -> str:
    """Aktivite türüne göre modern UI tema rengi döndürür."""
    t = activity_type.lower() if activity_type else ""
    if "film" in t:
        return "#3B82F6"  # Mavi
    elif "dizi" in t:
        return "#8B5CF6"  # Mor
    elif "oyun" in t:
        return "#10B981"  # Zümrüt Yeşili
    elif "kitap" in t:
        return "#F59E0B"  # Amber
    elif "kurs" in t or "eğitim" in t:
        return "#EC4899"  # Pembe
    elif "şehir" in t or "gezi" in t:
        return "#06B6D4"  # Turkuaz
    else:
        return "#64748B"  # Nötr Gri-Mavi


class ActivityListModel(QAbstractListModel):
    """QML ListView ve GridView için yüksek performanslı Activity modeli."""

    IdRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    NameRole = Qt.UserRole + 3
    DateRole = Qt.UserRole + 4
    EndDateRole = Qt.UserRole + 5
    CommentRole = Qt.UserRole + 6
    RatingRole = Qt.UserRole + 7
    DisplayDateRole = Qt.UserRole + 8
    ScoreBadgeRole = Qt.UserRole + 9
    TypeColorRole = Qt.UserRole + 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._activities = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._activities)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._activities)):
            return None

        act: Activity = self._activities[index.row()]

        if role == self.IdRole:
            return act.id
        elif role == self.TypeRole:
            return act.type or ""
        elif role == self.NameRole:
            return act.name or ""
        elif role == self.DateRole:
            return act.date or ""
        elif role == self.EndDateRole:
            return act.end_date or ""
        elif role == self.CommentRole:
            return act.comment or ""
        elif role == self.RatingRole:
            return float(act.rating) if act.rating is not None else 0.0
        elif role == self.DisplayDateRole:
            if act.end_date:
                return f"{act.date}  ➜  {act.end_date}"
            return act.date or ""
        elif role == self.ScoreBadgeRole:
            if act.rating is not None and act.rating > 0:
                return f"{act.rating:.1f}" if isinstance(act.rating, float) else str(act.rating)
            return "-"
        elif role == self.TypeColorRole:
            return get_type_color(act.type)

        return None

    def roleNames(self) -> dict:
        return {
            self.IdRole: QByteArray(b"activityId"),
            self.TypeRole: QByteArray(b"activityType"),
            self.NameRole: QByteArray(b"activityName"),
            self.DateRole: QByteArray(b"activityDate"),
            self.EndDateRole: QByteArray(b"activityEndDate"),
            self.CommentRole: QByteArray(b"activityComment"),
            self.RatingRole: QByteArray(b"activityRating"),
            self.DisplayDateRole: QByteArray(b"displayDate"),
            self.ScoreBadgeRole: QByteArray(b"scoreBadge"),
            self.TypeColorRole: QByteArray(b"typeColor"),
        }

    def set_activities(self, activities: list):
        self.beginResetModel()
        self._activities = activities
        self.endResetModel()


class ActivityBridge(QObject):
    """QML ile Activity CRUD ve filtreleme işlemlerini bağlayan Köprü."""

    activitiesChanged = Signal()
    typesChanged = Signal()
    filterChanged = Signal()
    loadingChanged = Signal(bool)
    activitySaved = Signal(bool, str, int)   # success, message, id
    activityDeleted = Signal(bool, str)      # success, message
    coverLoaded = Signal(str, str)
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = ActivityRepository()
        self._type_repo = TypeRepository()
        self._model = ActivityListModel(self)

        self._current_page = 1
        self._items_per_page = 12
        self._total_count = 0
        self._total_pages = 1
        self._search_term = ""
        self._type_filter = "Hepsi"
        self._date_filter = ""
        self._is_loading = False

        # İlk veri yüklemesi
        self.loadActivities()

    # --- Q_PROPERTY Tanımları ---

    @Property(QObject, constant=True)
    def model(self) -> ActivityListModel:
        return self._model

    @Property(int, notify=activitiesChanged)
    def totalCount(self) -> int:
        return self._total_count

    @Property(int, notify=activitiesChanged)
    def currentPage(self) -> int:
        return self._current_page

    @Property(int, notify=activitiesChanged)
    def pageSize(self) -> int:
        return self._items_per_page

    @Property(int, notify=activitiesChanged)
    def totalPages(self) -> int:
        return self._total_pages

    @Property(bool, notify=activitiesChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(list, notify=typesChanged)
    def availableTypes(self) -> list:
        types = self._type_repo.get_all_types()
        return ["Hepsi"] + types

    # --- Slotlar: Veri Yükleme & Filtreleme ---

    @Slot()
    def loadActivities(self):
        """Mevcut filtrelere göre faaliyet listesini veritabanından çeker."""
        self._is_loading = True
        self.activitiesChanged.emit()

        filter_obj = ActivityFilter(
            type_filter=self._type_filter,
            search_term=self._search_term.strip(),
            date_filter=self._date_filter.strip(),
            page=self._current_page,
            items_per_page=self._items_per_page
        )

        try:
            activities, count = self._repo.get_all_filtered(filter_obj)
            self._total_count = count
            self._total_pages = max(1, math.ceil(count / self._items_per_page))
            if self._current_page > self._total_pages:
                self._current_page = self._total_pages

            self._model.set_activities(activities)
        except Exception as e:
            logger.error(f"ActivityBridge loadActivities error: {e}")
            self.errorOccurred.emit(str(e))
        finally:
            self._is_loading = False
            self.activitiesChanged.emit()

    @Slot(str)
    def setSearchTerm(self, term: str):
        if self._search_term != term:
            self._search_term = term
            self._current_page = 1
            self.filterChanged.emit()
            self.loadActivities()

    @Slot(str)
    def setTypeFilter(self, t: str):
        if self._type_filter != t:
            self._type_filter = t
            self._current_page = 1
            self.filterChanged.emit()
            self.loadActivities()

    @Slot(str)
    def setDateFilter(self, d: str):
        if self._date_filter != d:
            self._date_filter = d
            self._current_page = 1
            self.filterChanged.emit()
            self.loadActivities()

    @Slot()
    def nextPage(self):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.loadActivities()

    @Slot()
    def prevPage(self):
        if self._current_page > 1:
            self._current_page -= 1
            self.loadActivities()

    @Slot(int)
    def setItemsPerPage(self, count: int):
        if count in (15, 30, 50, 100, 12, 24) and count != self._items_per_page:
            self._items_per_page = count
            self._current_page = 1
            self.loadActivities()

    @Slot(str, str, result=str)
    def getCover(self, name: str, activity_type: str) -> str:
        """Önbellekteki kapak görsel URL'sini döndürür."""
        cached = CoverFetchService.get_cached_cover(name, activity_type)
        return cached or ""

    @Slot(str, str)
    def requestCover(self, name: str, activity_type: str):
        """Asenkron olarak kapak görselini arar ve bulununca coverLoaded sinyali yayar."""
        def on_done(url):
            try:
                if url:
                    self.coverLoaded.emit(name, url)
            except RuntimeError:
                pass

        CoverFetchService.get_cover_async(name, activity_type, on_done)

    # --- Slotlar: Ekleme, Düzenleme & Silme (Modal Form Entegrasyonu) ---

    @Slot(str, str, str, str, float, str, result=bool)
    def addActivity(self, type_val: str, name: str, date_val: str, comment: str, rating_val: float, end_date: str = "") -> bool:
        """Yeni faaliyet ekler. Form doğrulaması yapar ve sonucu sinyalle bildirir."""
        type_val = (type_val or "").strip()
        name = (name or "").strip()
        date_val = (date_val or "").strip()
        end_date = (end_date or "").strip() if end_date else None
        comment = (comment or "").strip()

        if not type_val:
            self.activitySaved.emit(False, "Lütfen bir faaliyet türü seçin.", -1)
            return False

        if not name:
            self.activitySaved.emit(False, "Faaliyet adı boş bırakılamaz.", -1)
            return False

        if not date_val or not is_valid_date(date_val):
            self.activitySaved.emit(False, "Geçersiz başlangıç tarihi formatı (YYYY-MM-DD).", -1)
            return False

        if end_date and not is_valid_date(end_date):
            self.activitySaved.emit(False, "Geçersiz bitiş tarihi formatı (YYYY-MM-DD).", -1)
            return False

        if end_date and end_date < date_val:
            self.activitySaved.emit(False, "Bitiş tarihi başlangıç tarihinden önce olamaz.", -1)
            return False

        rating = float(rating_val) if rating_val > 0 else 0.0

        activity = Activity(
            id=None,
            type=type_val,
            name=name,
            date=date_val,
            comment=comment,
            rating=rating,
            end_date=end_date
        )

        success = self._repo.add(activity)
        if success:
            self._type_repo.add_type(type_val)
            self.activitySaved.emit(True, f"'{name}' başarıyla kaydedildi.", 0)
            self.loadActivities()
            self.typesChanged.emit()
            return True
        else:
            self.activitySaved.emit(False, "Kayıt sırasında veritabanı hatası oluştu.", -1)
            return False

    @Slot(int, str, str, str, str, float, str, result=bool)
    def updateActivity(self, act_id: int, type_val: str, name: str, date_val: str, comment: str, rating_val: float, end_date: str = "") -> bool:
        """Mevcut bir faaliyeti günceller."""
        type_val = (type_val or "").strip()
        name = (name or "").strip()
        date_val = (date_val or "").strip()
        end_date = (end_date or "").strip() if end_date else None
        comment = (comment or "").strip()

        if not name:
            self.activitySaved.emit(False, "Faaliyet adı boş bırakılamaz.", act_id)
            return False

        if not is_valid_date(date_val):
            self.activitySaved.emit(False, "Geçersiz tarih formatı.", act_id)
            return False

        if end_date and not is_valid_date(end_date):
            self.activitySaved.emit(False, "Geçersiz bitiş tarihi formatı.", act_id)
            return False

        if end_date and end_date < date_val:
            self.activitySaved.emit(False, "Bitiş tarihi başlangıç tarihinden önce olamaz.", act_id)
            return False

        rating = float(rating_val) if rating_val > 0 else 0.0

        activity = Activity(
            id=act_id,
            type=type_val,
            name=name,
            date=date_val,
            comment=comment,
            rating=rating,
            end_date=end_date
        )

        success = self._repo.update(activity)
        if success:
            self.activitySaved.emit(True, f"'{name}' başarıyla güncellendi.", act_id)
            self.loadActivities()
            return True
        else:
            self.activitySaved.emit(False, "Güncelleme sırasında hata oluştu.", act_id)
            return False

    @Slot(int, result=bool)
    def deleteActivity(self, act_id: int) -> bool:
        """Faaliyeti siler."""
        success = self._repo.delete(act_id)
        if success:
            self.activityDeleted.emit(True, "Faaliyet başarıyla silindi.")
            self.loadActivities()
            return True
        else:
            self.activityDeleted.emit(False, "Silme işlemi sırasında hata oluştu.")
            return False

    @Slot(int, result=dict)
    def getActivityById(self, act_id: int) -> dict:
        """Modal pencerede düzenleme için faaliyet detayını döndürür."""
        act = self._repo.get_by_id(act_id)
        if not act:
            return {}
        return {
            "id": act.id,
            "type": act.type or "",
            "name": act.name or "",
            "date": act.date or "",
            "endDate": act.end_date or "",
            "hasEndDate": bool(act.end_date),
            "comment": act.comment or "",
            "rating": float(act.rating) if act.rating is not None else 0.0
        }

    @Slot(str, result=list)
    def getNameSuggestions(self, prefix: str) -> list:
        """Otomatik tamamlama için kayıtlı isimleri döndürür."""
        all_names = self._repo.get_unique_names()
        if not prefix:
            return all_names[:10]
        prefix_lower = prefix.lower()
        return [n for n in all_names if prefix_lower in n.lower()][:10]
