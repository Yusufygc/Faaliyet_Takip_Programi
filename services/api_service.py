# services/api_service.py
"""
Öneri servisleri için facade.
RecommendationController bu sınıfı kullanır; iç implementasyon değişebilir.
"""
import random
from logger_setup import logger
from services.movie_api_service import MovieApiService
from services.series_api_service import SeriesApiService
from services.game_api_service import GameApiService
from services.book_api_service import BookApiService


class ApiService:
    def __init__(self):
        self._movies = MovieApiService()
        self._series = SeriesApiService()
        self._games = GameApiService()
        self._books = BookApiService()

    def get_recommendations(self, category, period, genre=None, page=1, is_turkish=False) -> list:
        if category == 'Film':
            return self._movies.fetch(period, genre, page, is_turkish)
        elif category == 'Dizi':
            return self._series.fetch(period, genre, page, is_turkish)
        elif category == 'Oyun':
            return self._games.fetch(period, genre, page, is_turkish)
        elif category == 'Kitap':
            return self._books.fetch(period, genre, page, is_turkish)
        return []

    def get_random_recommendation(self, category=None):
        if not category:
            category = random.choice(['Film', 'Dizi', 'Oyun', 'Kitap'])

        period = random.choice(['all_time_best', 'must_see', 'cult_classics', 'hidden_gems'])

        try:
            # Sayfa 1 sonuç sayısını total_pages proxy olarak kullan.
            # Tam sayfa (12 kayıt) dönüyorsa sayfa 2-3 muhtemelen var.
            from services._base_api_service import ITEMS_PER_PAGE
            page1 = self.get_recommendations(category, period, None, 1, False)
            if not page1:
                logger.error(f"Random öneri bulunamadı: {category}/{period}")
                return None

            max_page = 3 if len(page1) >= ITEMS_PER_PAGE else 1
            page = random.randint(1, max_page)

            results = page1
            if page > 1:
                extra = self.get_recommendations(category, period, None, page, False)
                if extra:
                    results = extra

            selected = random.choice(results)
            selected['random_category'] = category
            selected['random_period'] = period
            return selected
        except Exception as e:
            logger.error(f"Random recommendation error: {e}")
            return None
