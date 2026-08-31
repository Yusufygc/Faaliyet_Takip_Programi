# bridges/compare_bridge.py
from PySide6.QtCore import QObject, Signal, Slot, Property
from database.repository import ActivityRepository
from bridges.activity_bridge import get_type_color
from logger_setup import logger


class CompareBridge(QObject):
    """İki farklı dönemi karşılaştırma köprüsü."""

    comparisonLoaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = ActivityRepository()

        self._period_a = ""
        self._period_b = ""
        self._total_a = 0
        self._total_b = 0
        self._category_comparison = []

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
    def categoryComparison(self) -> list:
        return self._category_comparison

    # --- Slotlar ---

    @Slot(str, result=list)
    def getAvailablePeriods(self, period_type: str = "month") -> list:
        """Kullanılabilir dönemleri (YYYY-MM veya YYYY) döndürür."""
        return self._repo.get_available_periods(period_type)

    @Slot(str, str)
    def compare(self, period_a: str, period_b: str):
        """İki dönemi karşılaştırır ve sonuçları hazırlar."""
        self._period_a = period_a
        self._period_b = period_b

        try:
            data_a = self._repo.get_comparison_data(period_a)
            data_b = self._repo.get_comparison_data(period_b)

            self._total_a = len(data_a)
            self._total_b = len(data_b)

            counts_a = {}
            for t, _ in data_a:
                counts_a[t] = counts_a.get(t, 0) + 1

            counts_b = {}
            for t, _ in data_b:
                counts_b[t] = counts_b.get(t, 0) + 1

            all_types = sorted(list(set(list(counts_a.keys()) + list(counts_b.keys()))))

            comp_list = []
            for t in all_types:
                ca = counts_a.get(t, 0)
                cb = counts_b.get(t, 0)
                diff = ca - cb
                comp_list.append({
                    "type": t,
                    "countA": ca,
                    "countB": cb,
                    "difference": diff,
                    "diffText": f"+{diff}" if diff > 0 else str(diff),
                    "color": get_type_color(t)
                })

            self._category_comparison = comp_list
        except Exception as e:
            logger.error(f"CompareBridge compare error: {e}")
            self._category_comparison = []
        finally:
            self.comparisonLoaded.emit()
