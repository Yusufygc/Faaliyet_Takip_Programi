# bridges/compare_bridge.py
from PySide6.QtCore import QObject, Signal, Slot, Property
from database.repository import ActivityRepository
from database.type_repository import TypeRepository
from bridges.activity_bridge import get_type_color
from logger_setup import logger


class CompareBridge(QObject):
    """İki dönemi (ay/yıl) tür bazında karşılaştırma köprüsü."""

    comparisonLoaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = ActivityRepository()
        self._type_repo = TypeRepository()

        self._period_a = ""
        self._period_b = ""
        self._total_a = 0
        self._total_b = 0
        self._columns = []
        self._items_a = []
        self._items_b = []

    # --- Property Tanımları ---

    @Property(str, notify=comparisonLoaded)
    def periodA(self) -> str:
        return self._period_a

    @Property(str, notify=comparisonLoaded)
    def periodB(self) -> str:
        return self._period_b

    @Property(int, notify=comparisonLoaded)
    def totalA(self) -> int:
        return self._total_a

    @Property(int, notify=comparisonLoaded)
    def totalB(self) -> int:
        return self._total_b

    @Property(list, notify=comparisonLoaded)
    def columns(self) -> list:
        return self._columns

    @Property(list, notify=comparisonLoaded)
    def itemsA(self) -> list:
        return self._items_a

    @Property(list, notify=comparisonLoaded)
    def itemsB(self) -> list:
        return self._items_b

    # --- Slotlar ---

    @Slot(str, result=list)
    def getAvailablePeriods(self, period_type: str = "month") -> list:
        """Kullanılabilir dönemleri (YYYY-MM veya YYYY) döndürür."""
        return self._repo.get_available_periods(period_type)

    @Slot(str, str, str, str)
    def compare(self, scope_a: str, period_a: str, scope_b: str, period_b: str):
        """İki dönemi (her biri kendi ölçeğinde) tür bazında karşılaştırır.

        Not: date_prefix ile LIKE eşleşmesi (ör. "2026" veya "2026-09")
        hem ay hem yıl ölçeği için aynı şekilde çalıştığından, scope_a/scope_b
        burada sorgu davranışını değiştirmez; sadece etiket olarak saklanır.
        """
        self._period_a = period_a
        self._period_b = period_b

        try:
            data_a = self._repo.get_comparison_data(period_a)
            data_b = self._repo.get_comparison_data(period_b)

            names_a = {}
            for t, name in data_a:
                names_a.setdefault(t, []).append(name)

            names_b = {}
            for t, name in data_b:
                names_b.setdefault(t, []).append(name)

            all_types = self._type_repo.get_all_types()

            self._columns = [{"name": t, "color": get_type_color(t)} for t in all_types]
            self._items_a = [names_a.get(t, []) for t in all_types]
            self._items_b = [names_b.get(t, []) for t in all_types]
            self._total_a = len(data_a)
            self._total_b = len(data_b)
        except Exception as e:
            logger.error(f"CompareBridge compare error: {e}")
            self._columns = []
            self._items_a = []
            self._items_b = []
            self._total_a = 0
            self._total_b = 0
        finally:
            self.comparisonLoaded.emit()
