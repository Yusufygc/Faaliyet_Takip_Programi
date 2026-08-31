# bridges/stats_bridge.py
import os
import threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool, QRunnable
from database.repository import ActivityRepository
from services.pdf_service import PDFService
from bridges.activity_bridge import get_type_color
from logger_setup import logger


MONTH_NAMES = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


class PdfWorker(QRunnable):
    """PDF oluşturma işlemini UI thread'ini dondurmadan arka planda çalıştırır."""

    def __init__(self, target_path: str, title: str, summary: dict, details: list, callback):
        super().__init__()
        self.target_path = target_path
        self.title = title
        self.summary = summary
        self.details = details
        self.callback = callback

    def run(self):
        try:
            pdf_service = PDFService()
            success, message = pdf_service.create_report(
                self.target_path,
                self.title,
                self.summary,
                self.details
            )
            self.callback(success, message, self.target_path)
        except Exception as e:
            logger.error(f"PdfWorker error: {e}")
            self.callback(False, str(e), self.target_path)


class StatsBridge(QObject):
    """İstatistikler, KPI'lar, Grafik Verileri ve PDF Dışa Aktarma Köprüsü."""

    statsLoaded = Signal()
    trendLoaded = Signal()
    pdfExportingChanged = Signal(bool)
    pdfExportResult = Signal(bool, str, str)  # success, message, file_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = ActivityRepository()
        self._thread_pool = QThreadPool.globalInstance()

        self._kpi_total = 0
        self._kpi_avg_rating = 0.0
        self._kpi_top_category = "-"
        self._kpi_top_category_count = 0
        self._category_distribution = []
        self._monthly_distribution = []
        self._heatmap_data = {}
        self._is_exporting_pdf = False

        self._current_year = datetime.now().year
        self._current_month = datetime.now().month
        self._date_prefix = f"{self._current_year}-{self._current_month:02d}"
        self._year_only = False
        self._all_time = False

        # Trend analizi değişkenleri
        self._trend_year = self._current_year
        self._trend_category = "Hepsi"
        self._trend_data = []
        self._trend_total = 0
        self._trend_monthly_avg = 0.0
        self._trend_peak_month_name = "-"
        self._trend_peak_month_count = 0

        self.loadStats(self._date_prefix, False, False)
        self.loadTrend(self._trend_year, "Hepsi")

    # --- Property Tanımları ---

    @Property(int, notify=statsLoaded)
    def kpiTotal(self) -> int:
        return self._kpi_total

    @Property(float, notify=statsLoaded)
    def kpiAvgRating(self) -> float:
        return self._kpi_avg_rating

    @Property(str, notify=statsLoaded)
    def kpiTopCategory(self) -> str:
        return self._kpi_top_category

    @Property(int, notify=statsLoaded)
    def kpiTopCategoryCount(self) -> int:
        return self._kpi_top_category_count

    @Property(list, notify=statsLoaded)
    def categoryDistribution(self) -> list:
        return self._category_distribution

    @Property(list, notify=statsLoaded)
    def monthlyDistribution(self) -> list:
        return self._monthly_distribution

    @Property(dict, notify=statsLoaded)
    def heatmapData(self) -> dict:
        return self._heatmap_data

    @Property(bool, notify=pdfExportingChanged)
    def isExportingPdf(self) -> bool:
        return self._is_exporting_pdf

    @Property(str, notify=statsLoaded)
    def datePrefix(self) -> str:
        return self._date_prefix

    @Property(bool, notify=statsLoaded)
    def isYearOnly(self) -> bool:
        return self._year_only

    @Property(bool, notify=statsLoaded)
    def isAllTime(self) -> bool:
        return self._all_time

    # --- Trend Analizi Property'leri ---

    @Property(int, notify=trendLoaded)
    def trendYear(self) -> int:
        return self._trend_year

    @Property(str, notify=trendLoaded)
    def trendCategory(self) -> str:
        return self._trend_category

    @Property(list, notify=trendLoaded)
    def trendData(self) -> list:
        return self._trend_data

    @Property(int, notify=trendLoaded)
    def trendTotal(self) -> int:
        return self._trend_total

    @Property(float, notify=trendLoaded)
    def trendMonthlyAvg(self) -> float:
        return self._trend_monthly_avg

    @Property(str, notify=trendLoaded)
    def trendPeakMonthName(self) -> str:
        return self._trend_peak_month_name

    @Property(int, notify=trendLoaded)
    def trendPeakMonthCount(self) -> int:
        return self._trend_peak_month_count

    @Property(list, constant=True)
    def availableYears(self) -> list:
        cy = datetime.now().year
        return [str(y) for y in range(cy - 4, cy + 2)]


    # --- İstatistik Yükleme Metodu ---

    @Slot(str, bool, bool)
    def loadStats(self, date_prefix: str = "", year_only: bool = False, all_time: bool = False):
        """Seçilen döneme göre istatistikleri ve grafik verilerini hazırlar."""
        self._date_prefix = date_prefix
        self._year_only = year_only
        self._all_time = all_time

        try:
            # 1. Kategori bazlı istatistikler
            stats_raw = self._repo.get_stats_by_type(
                date_prefix=date_prefix,
                year_only=year_only,
                ignore_dates=all_time
            )

            total_acts = sum(row[1] for row in stats_raw) if stats_raw else 0
            self._kpi_total = total_acts

            if total_acts > 0 and stats_raw:
                self._kpi_top_category = stats_raw[0][0]
                self._kpi_top_category_count = stats_raw[0][1]

                # Ağırlıklı ortalama puan
                rated_items = [row for row in stats_raw if row[2] is not None]
                if rated_items:
                    weighted_sum = sum(row[1] * row[2] for row in rated_items)
                    rated_count = sum(row[1] for row in rated_items)
                    self._kpi_avg_rating = round(weighted_sum / rated_count, 1) if rated_count > 0 else 0.0
                else:
                    self._kpi_avg_rating = 0.0

                # QML Chart için Kategori Dağılım Listesi
                cat_list = []
                for row in stats_raw:
                    cat_name = row[0]
                    count = row[1]
                    avg_puan = round(row[2], 1) if row[2] is not None else 0.0
                    percent = round((count / total_acts) * 100, 1) if total_acts > 0 else 0.0
                    cat_list.append({
                        "type": cat_name,
                        "count": count,
                        "avgRating": avg_puan,
                        "percent": percent,
                        "color": get_type_color(cat_name)
                    })
                self._category_distribution = cat_list
            else:
                self._kpi_top_category = "-"
                self._kpi_top_category_count = 0
                self._kpi_avg_rating = 0.0
                self._category_distribution = []

            # 2. Aylık trend dökümü (12 Ay)
            target_year = int(date_prefix[:4]) if (date_prefix and len(date_prefix) >= 4) else self._current_year
            monthly_raw = self._repo.get_monthly_activity_counts(target_year)
            month_dict = {m: 0 for m in range(1, 13)}
            for m, count in monthly_raw:
                month_dict[m] = count

            self._monthly_distribution = [
                {"month": m, "monthName": MONTH_NAMES[m - 1], "count": month_dict[m]}
                for m in range(1, 13)
            ]

            # 3. Isı haritası verileri
            self._heatmap_data = self._repo.get_daily_activity_counts(target_year)

        except Exception as e:
            logger.error(f"StatsBridge loadStats error: {e}")
        finally:
            self.statsLoaded.emit()

    @Slot(str, result=list)
    def getCategoryDetails(self, cat_type: str) -> list:
        """Kategoriye tıklandığında altındaki faaliyetleri döndürür."""
        try:
            raw_details = self._repo.get_details_for_type(
                activity_type=cat_type,
                date_prefix=self._date_prefix,
                year_only=self._year_only,
                ignore_dates=self._all_time
            )
            return [{"name": row[0], "date": row[1]} for row in raw_details]
        except Exception as e:
            logger.error(f"StatsBridge getCategoryDetails error: {e}")
            return []

    @Slot(int, str)
    def loadTrend(self, year: int, category: str = "Hepsi"):
        """Yıl ve kategori bazında zaman serisi trend verilerini yükler."""
        self._trend_year = year
        self._trend_category = category

        try:
            cat_param = None if (not category or category == "Hepsi") else category
            monthly_raw = self._repo.get_monthly_activity_counts(year, cat_param)

            month_dict = {m: 0 for m in range(1, 13)}
            for m, count in monthly_raw:
                month_dict[m] = count

            total = sum(month_dict.values())
            self._trend_total = total
            self._trend_monthly_avg = round(total / 12.0, 1)

            # Zirve ayı bul
            peak_m = max(month_dict, key=month_dict.get) if total > 0 else 1
            peak_count = month_dict[peak_m]
            self._trend_peak_month_name = MONTH_NAMES[peak_m - 1] if peak_count > 0 else "-"
            self._trend_peak_month_count = peak_count

            self._trend_data = [
                {
                    "month": m,
                    "monthName": MONTH_NAMES[m - 1],
                    "count": month_dict[m],
                    "year": year,
                    "datePrefix": f"{year}-{m:02d}"
                }
                for m in range(1, 13)
            ]
        except Exception as e:
            logger.error(f"StatsBridge loadTrend error: {e}")
        finally:
            self.trendLoaded.emit()

    @Slot(str, str, result=list)
    def getMonthDetails(self, year_month: str, category: str = "Hepsi") -> list:
        """Grafikte bir aya tıklandığında o aydaki faaliyetleri listeler."""
        try:
            cat_param = None if (not category or category == "Hepsi") else category
            rows = self._repo.get_activity_details_by_month(year_month, cat_param)
            return [{"name": r[0], "date": r[1]} for r in rows]
        except Exception as e:
            logger.error(f"StatsBridge getMonthDetails error: {e}")
            return []

    # --- ✨ 2. UX Değişikliği: PDF Rapor Entegrasyonu ---

    @Slot(str, result=str)
    def getDefaultPdfPath(self, date_prefix: str = "") -> str:
        """Varsayılan PDF kayıt yolunu oluşturur."""
        prefix = date_prefix or (self._date_prefix if not self._all_time else "TumZamanlar")
        filename = f"Faaliyet_Raporu_{prefix or 'TumZamanlar'}.pdf"
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            desktop = os.path.expanduser("~")
        return os.path.join(desktop, filename).replace("\\", "/")

    @Slot(str, str, str)
    def exportPdf(self, date_prefix: str, target_path: str, custom_title: str = ""):
        """PDF Raporu asenkron olarak üretir ve tamamlanınca sinyal yayar."""
        if not target_path:
            self.pdfExportResult.emit(False, "Kayıt dosyası yolu belirtilmedi.", "")
            return

        self._is_exporting_pdf = True
        self.pdfExportingChanged.emit(True)

        prefix = date_prefix if date_prefix else ""
        raw_data = self._repo.get_detailed_data_for_pdf(prefix)

        if not raw_data:
            self._is_exporting_pdf = False
            self.pdfExportingChanged.emit(False)
            self.pdfExportResult.emit(False, "Seçilen dönem için kayıtlı veri bulunamadı.", target_path)
            return

        period_title = prefix if prefix else "Tüm Zamanlar"
        title = custom_title or f"{period_title} Faaliyet Raporu"

        summary = {
            "Rapor Dönemi": period_title,
            "Toplam Faaliyet Sayısı": len(raw_data),
            "Rapor Türü": "Yıllık" if len(prefix) == 4 else ("Tüm Zamanlar" if not prefix else "Aylık")
        }

        def on_done(success: bool, message: str, fpath: str):
            try:
                self._is_loading_pdf = False
                self.pdfExportingChanged.emit(False)
                self.pdfExportResult.emit(success, message, fpath)
            except RuntimeError:
                pass

        worker = PdfWorker(target_path, title, summary, raw_data, on_done)
        self._thread_pool.start(worker)
