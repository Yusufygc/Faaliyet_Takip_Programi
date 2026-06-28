# -*- coding: utf-8 -*-
"""
Öneri servisi ile UI arasındaki bağlantıyı yönetir.
Cache yönetimi ve pagination destekler.
"""

from services.api_service import ApiService
from services.recommendation_config import (
    PERIODS, PERIOD_ORDER, FILM_GENRES, DIZI_GENRES, OYUN_GENRES, KITAP_GENRES
)
from database.recommendation_repository import RecommendationRepository
from controllers._base_controller import _BaseController
from logger_setup import logger


class RecommendationController(_BaseController):
    """
    Öneri servisi ile UI arasındaki bağlantıyı yönetir.
    Cache-first stratejisi ile API çağrılarını minimize eder.
    """

    def __init__(self):
        super().__init__()
        self.api_service = ApiService()
        self.cache_repo = RecommendationRepository()
        self._cleanup_old_cache()

    def _cleanup_old_cache(self):
        self._run_async(self.cache_repo.clear_expired_cache, None)

    # =========================================================================
    # PERİYOT YÖNETİMİ
    # =========================================================================

    def get_periods(self):
        return PERIOD_ORDER

    def get_period_info(self, period_key):
        return PERIODS.get(period_key, {})

    def get_period_name(self, period_key):
        return PERIODS.get(period_key, {}).get('name', period_key)

    def get_all_period_names(self):
        return [(key, PERIODS[key]['name']) for key in PERIOD_ORDER if key in PERIODS]

    # =========================================================================
    # TÜR YÖNETİMİ
    # =========================================================================

    def get_genres_for_category(self, category):
        mapping = {
            'Film': FILM_GENRES,
            'Dizi': DIZI_GENRES,
            'Oyun': OYUN_GENRES,
            'Kitap': KITAP_GENRES,
        }
        return list(mapping.get(category, {}).keys())

    def get_genre_value(self, category, genre_name):
        mapping = {
            'Film': FILM_GENRES,
            'Dizi': DIZI_GENRES,
            'Oyun': OYUN_GENRES,
            'Kitap': KITAP_GENRES,
        }
        return mapping.get(category, {}).get(genre_name)

    # =========================================================================
    # CACHE YÖNETİMİ
    # =========================================================================

    def has_cached_data(self, category, period, genre=None, is_turkish=False, page=1):
        genre_key = str(genre) if genre else 'all'
        return self.cache_repo.has_valid_cache(category, period, genre_key, is_turkish, page)

    def get_max_cached_page(self, category, period, genre=None, is_turkish=False):
        genre_key = str(genre) if genre else 'all'
        return self.cache_repo.get_max_cached_page(category, period, genre_key, is_turkish)

    def clear_cache(self):
        return self.cache_repo.clear_all_cache()

    # =========================================================================
    # ÖNERİ ALMA
    # =========================================================================

    def get_recommendations(self, callback, category, period, genre=None,
                            page=1, is_turkish=False, force_refresh=False):
        genre_key = str(genre) if genre else 'all'

        def task():
            if not force_refresh and self.cache_repo.has_valid_cache(
                category, period, genre_key, is_turkish, page
            ):
                logger.info(f"Cache'den yükleniyor: {category}/{period}/{page}")
                return self.cache_repo.get_cached_recommendations(
                    category, period, genre_key, is_turkish, page
                )

            logger.info(f"API'den çekiliyor: {category}/{period}/{page}")
            results = self.api_service.get_recommendations(
                category, period, genre, page, is_turkish
            )
            if results:
                self.cache_repo.add_recommendations(
                    results, category, period, genre_key, is_turkish, page
                )
            return results

        self._run_async(task, callback)

    def get_next_page(self, callback, category, period, genre=None,
                      current_page=1, is_turkish=False):
        self.get_recommendations(callback, category, period, genre, current_page + 1, is_turkish)

    def get_previous_data(self, callback, category, period, genre=None,
                          is_turkish=False, max_page=None):
        genre_key = str(genre) if genre else 'all'

        def task():
            cached_max = max_page if max_page is not None else \
                self.cache_repo.get_max_cached_page(category, period, genre_key, is_turkish)
            all_results = []
            for page in range(1, cached_max + 1):
                all_results.extend(
                    self.cache_repo.get_cached_recommendations(
                        category, period, genre_key, is_turkish, page
                    )
                )
            return all_results

        self._run_async(task, callback)

    def get_random_recommendation(self, callback, category=None):
        self._run_async(self.api_service.get_random_recommendation, callback, category)
