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
        page = random.randint(1, 3)

        try:
            results = self.get_recommendations(category, period, None, page, False)
            if results:
                selected = random.choice(results)
                selected['random_category'] = category
                selected['random_period'] = period
                return selected
            return self._get_fallback_random(category)
        except Exception as e:
            logger.error(f"Random recommendation error: {e}")
            return self._get_fallback_random(category)

    def _get_fallback_random(self, category=None):
        cat = category or 'Film'
        try:
            results = self.get_recommendations(cat, 'must_see', None, 1, False)
            if results:
                selected = random.choice(results)
                selected['random_category'] = cat
                selected['random_period'] = 'must_see'
                return selected
        except Exception:
            pass
        return None
