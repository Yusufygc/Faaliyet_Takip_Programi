# bridges/discover_bridge.py
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool, QRunnable
from services.api_service import ApiService
from services.recommendation_config import PERIODS, PERIOD_ORDER, FILM_GENRES, DIZI_GENRES, OYUN_GENRES, KITAP_GENRES
from logger_setup import logger


class FetchRecommendationsWorker(QRunnable):
    """API isteklerini arka planda çalıştırır."""

    def __init__(self, api_service: ApiService, category: str, period: str, genre, page: int, is_turkish: bool, callback):
        super().__init__()
        self.api_service = api_service
        self.category = category
        self.period = period
        self.genre = genre
        self.page = page
        self.is_turkish = is_turkish
        self.callback = callback

    def run(self):
        try:
            results = self.api_service.get_recommendations(
                category=self.category,
                period=self.period,
                genre=self.genre,
                page=self.page,
                is_turkish=self.is_turkish
            )
            # Poster ve veri temizliği
            sanitized = []
            for item in (results or []):
                p_url = str(item.get("poster") or item.get("image") or item.get("poster_path") or item.get("cover") or "")
                if p_url and p_url.startswith("/") and not p_url.startswith("http"):
                    p_url = f"https://image.tmdb.org/t/p/w500{p_url}"
                sanitized.append({
                    "title": str(item.get("title") or item.get("name") or "İsimsiz"),
                    "category": self.category,
                    "poster": p_url,
                    "image": p_url,
                    "rating": float(item.get("rating") or item.get("vote_average") or 0.0),
                    "year": str(item.get("year") or item.get("release_date") or item.get("date") or "")[:4],
                    "overview": str(item.get("overview") or item.get("description") or "Açıklama bulunmuyor."),
                    "genre": str(item.get("genre") or ""),
                    "id": item.get("id")
                })
            self.callback(True, self.category, sanitized)
        except Exception as e:
            logger.error(f"FetchRecommendationsWorker error: {e}")
            self.callback(False, self.category, [])


class RandomRecommendationWorker(QRunnable):
    """Rastgele öneri aramasını arka planda çalıştırır."""

    def __init__(self, api_service: ApiService, category: str, callback):
        super().__init__()
        self.api_service = api_service
        self.category = category
        self.callback = callback

    def run(self):
        try:
            cat = self.category if self.category != "Tümü" else None
            res = self.api_service.get_random_recommendation(cat)
            if res:
                p_url = str(res.get("poster") or res.get("image") or res.get("poster_path") or res.get("cover") or "")
                if p_url and p_url.startswith("/") and not p_url.startswith("http"):
                    p_url = f"https://image.tmdb.org/t/p/w500{p_url}"
                cleaned = {
                    "title": str(res.get("title") or res.get("name") or "İsimsiz"),
                    "category": str(res.get("random_category") or self.category),
                    "poster": p_url,
                    "image": p_url,
                    "rating": float(res.get("rating") or res.get("vote_average") or 0.0),
                    "year": str(res.get("year") or res.get("release_date") or res.get("date") or "")[:4],
                    "overview": str(res.get("overview") or res.get("description") or "Açıklama bulunmuyor."),
                    "genre": str(res.get("genre") or "")
                }
                self.callback(True, cleaned)
            else:
                self.callback(False, {})
        except Exception as e:
            logger.error(f"RandomRecommendationWorker error: {e}")
            self.callback(False, {})


class DiscoverBridge(QObject):
    """Keşfet & İçerik Önerileri Köprüsü."""

    recommendationsLoaded = Signal(list)
    randomRecommendationFound = Signal(dict)
    loadingChanged = Signal(bool)
    categoryChanged = Signal()
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api = ApiService()
        self._thread_pool = QThreadPool.globalInstance()

        self._active_category = "Film"
        self._active_period = "this_month"
        self._active_genre_name = "Tümü"
        self._is_turkish = False
        self._page = 1
        self._is_loading = False
        self._items = []

    # --- Property Tanımları ---

    @Property(list, notify=recommendationsLoaded)
    def items(self) -> list:
        return self._items

    @Property(bool, notify=loadingChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(str, notify=categoryChanged)
    def activeCategory(self) -> str:
        return self._active_category

    @Property(str, notify=recommendationsLoaded)
    def activePeriod(self) -> str:
        return self._active_period

    @Property(list, notify=categoryChanged)
    def availableGenres(self) -> list:
        return self.getGenresForCategory(self._active_category)

    @Property(list, constant=True)
    def periods(self) -> list:
        return [
            {"key": k, "name": PERIODS[k]["name"], "description": PERIODS[k]["description"]}
            for k in PERIOD_ORDER if k in PERIODS
        ]

    # --- Slotlar: Veri Çekme ---

    @Slot()
    def fetchRecommendations(self):
        """Mevcut ayarlarla API'den içerik önerilerini çeker."""
        self._is_loading = True
        self.loadingChanged.emit(True)

        genre_val = self._get_genre_value(self._active_category, self._active_genre_name)

        def on_done(success: bool, category: str, results: list):
            try:
                self._is_loading = False
                self.loadingChanged.emit(False)
                if success:
                    self._items = results
                    self.recommendationsLoaded.emit(results)
                else:
                    self._items = []
                    self.recommendationsLoaded.emit([])
                    self.errorOccurred.emit("İçerikler yüklenirken API hatası oluştu.")
            except RuntimeError:
                pass  # Bridge closed during background worker

        worker = FetchRecommendationsWorker(
            self._api,
            self._active_category,
            self._active_period,
            genre_val,
            self._page,
            self._is_turkish,
            on_done
        )
        self._thread_pool.start(worker)

    @Slot(str)
    def setCategory(self, category: str):
        if self._active_category != category:
            self._active_category = category
            self._active_genre_name = "Tümü"
            self._page = 1
            self.categoryChanged.emit()
            self.fetchRecommendations()

    @Slot(str)
    def setPeriod(self, period_key: str):
        if self._active_period != period_key:
            self._active_period = period_key
            self._page = 1
            self.fetchRecommendations()

    @Slot(str)
    def setGenre(self, genre_name: str):
        if self._active_genre_name != genre_name:
            self._active_genre_name = genre_name
            self._page = 1
            self.fetchRecommendations()

    @Slot(bool)
    def setTurkishOnly(self, turkish_only: bool):
        if self._is_turkish != turkish_only:
            self._is_turkish = turkish_only
            self._page = 1
            self.fetchRecommendations()

    @Slot(str)
    def getRandomRecommendation(self, category: str = "Tümü"):
        """🎲 Rastgele öneri bulur."""
        self._is_loading = True
        self.loadingChanged.emit(True)

        def on_done(success: bool, result: dict):
            try:
                self._is_loading = False
                self.loadingChanged.emit(False)
                if success and result:
                    self.randomRecommendationFound.emit(result)
                else:
                    self.errorOccurred.emit("Rastgele öneri bulunamadı. Lütfen tekrar deneyin.")
            except RuntimeError:
                pass

        worker = RandomRecommendationWorker(self._api, category, on_done)
        self._thread_pool.start(worker)

    @Slot(str, result=list)
    def getGenresForCategory(self, category: str) -> list:
        if category == "Film":
            return list(FILM_GENRES.keys())
        elif category == "Dizi":
            return list(DIZI_GENRES.keys())
        elif category == "Oyun":
            return list(OYUN_GENRES.keys())
        elif category == "Kitap":
            return list(KITAP_GENRES.keys())
        return ["Tümü"]

    def _get_genre_value(self, category: str, genre_name: str):
        if genre_name == "Tümü" or not genre_name:
            return None
        if category == "Film":
            return FILM_GENRES.get(genre_name)
        elif category == "Dizi":
            return DIZI_GENRES.get(genre_name)
        elif category == "Oyun":
            return OYUN_GENRES.get(genre_name)
        elif category == "Kitap":
            return KITAP_GENRES.get(genre_name)
        return None
