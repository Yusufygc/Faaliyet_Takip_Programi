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

    def get_item_details(self, category, item_id) -> dict:
        if category == 'Film':
            return self._movies.fetch_details(item_id)
        elif category == 'Dizi':
            return self._series.fetch_details(item_id)
        elif category == 'Oyun':
            return self._games.fetch_details(item_id)
        elif category == 'Kitap':
            return self._books.fetch_details(item_id)
        return {}

    def get_random_recommendation(self, category=None):
        if not category:
            category = random.choice(['Film', 'Dizi', 'Oyun', 'Kitap'])

        period = random.choice(['all_time_best', 'must_see', 'cult_classics', 'hidden_gems'])

        try:
            page1 = self.get_recommendations(category, period, None, 1, False)
            if not page1:
                logger.error(f"Random öneri bulunamadı: {category}/{period}")
                return None

            # Sabit ITEMS_PER_PAGE bağımlılığı kaldırıldı. Gerçek dönen öğe
            # sayısına bakarak sayfa varlığını dinamik kontrol et: >= 10 ise
            # (en kısıtlı servislerin bile tam sayfa boyutu) sayfa 2/3 dene.
            pages = {1: page1}
            if len(page1) >= 10:
                p2 = self.get_recommendations(category, period, None, 2, False)
                if p2:
                    pages[2] = p2
                    p3 = self.get_recommendations(category, period, None, 3, False)
                    if p3:
                        pages[3] = p3

            page = random.choice(list(pages.keys()))
            selected = random.choice(pages[page])
            selected['random_category'] = category
            selected['random_period'] = period
            return selected
        except Exception as e:
            logger.error(f"Random recommendation error: {e}")
            return None
