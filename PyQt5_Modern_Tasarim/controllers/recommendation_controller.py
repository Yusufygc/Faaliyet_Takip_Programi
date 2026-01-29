# -*- coding: utf-8 -*-
"""
Öneri servisi ile UI arasındaki bağlantıyı yönetir.
"""

from services.api_service import ApiService
from services.recommendation_config import (
    PERIODS, PERIOD_ORDER, FILM_GENRES, DIZI_GENRES, OYUN_GENRES, KITAP_GENRES
)
from controllers.workers import DbWorker


class RecommendationController:
    """
    Öneri servisi ile UI arasındaki bağlantıyı yönetir.
    API çağrılarını asenkron yapar.
    """
    
    def __init__(self):
        self.api_service = ApiService()
        self.workers = set()

    def _cleanup_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)

    # =========================================================================
    # PERİYOT YÖNETİMİ
    # =========================================================================
    
    def get_periods(self):
        """Mevcut periyotları döndürür (sıralı liste)."""
        return PERIOD_ORDER
    
    def get_period_info(self, period_key):
        """Periyot bilgilerini döndürür."""
        return PERIODS.get(period_key, {})
    
    def get_period_name(self, period_key):
        """Periyodun görünen adını döndürür."""
        return PERIODS.get(period_key, {}).get('name', period_key)
    
    def get_all_period_names(self):
        """Tüm periyot adlarını sıralı döndürür."""
        return [(key, PERIODS[key]['name']) for key in PERIOD_ORDER if key in PERIODS]

    # =========================================================================
    # TÜR YÖNETİMİ
    # =========================================================================
    
    def get_genres_for_category(self, category):
        """Kategoriye göre mevcut türleri döndürür."""
        if category == 'Film':
            return list(FILM_GENRES.keys())
        elif category == 'Dizi':
            return list(DIZI_GENRES.keys())
        elif category == 'Oyun':
            return list(OYUN_GENRES.keys())
        elif category == 'Kitap':
            return list(KITAP_GENRES.keys())
        return []

    def get_genre_value(self, category, genre_name):
        """Tür adından API değerini döndürür."""
        if category == 'Film':
            return FILM_GENRES.get(genre_name)
        elif category == 'Dizi':
            return DIZI_GENRES.get(genre_name)
        elif category == 'Oyun':
            return OYUN_GENRES.get(genre_name)
        elif category == 'Kitap':
            return KITAP_GENRES.get(genre_name)
        return None

    # =========================================================================
    # ÖNERİ ALMA
    # =========================================================================
    
    def get_recommendations(self, callback, category, period, genre=None):
        """
        Belirtilen kategori, periyot ve tür için önerileri asenkron getirir.
        """
        def task():
            return self.api_service.get_recommendations(category, period, genre)

        worker = DbWorker(task)
        worker.finished.connect(callback)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.workers.add(worker)
        worker.start()
