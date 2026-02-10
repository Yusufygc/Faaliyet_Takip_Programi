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
from database.repository import ActivityRepository
from controllers.workers import DbWorker
from logger_setup import logger


class RecommendationController:
    """
    Öneri servisi ile UI arasındaki bağlantıyı yönetir.
    Cache-first stratejisi ile API çağrılarını minimize eder.
    """
    
    def __init__(self):
        # API anahtarlarını çek
        repo = ActivityRepository()
        tmdb_key = repo.get_setting("tmdb_api_key")
        rawg_key = repo.get_setting("rawg_api_key")
        
        self.api_service = ApiService(tmdb_key, rawg_key)
        self.cache_repo = RecommendationRepository()
        self.workers = set()
        
        # Başlangıçta eski cache'i temizle
        self._cleanup_old_cache()

    def _cleanup_worker(self, worker):
        if worker in self.workers:
            self.workers.discard(worker)

    def _cleanup_old_cache(self):
        """Eski cache kayıtlarını arka planda temizler."""
        def task():
            return self.cache_repo.clear_expired_cache()
        
        worker = DbWorker(task)
        worker.start()
        self.workers.add(worker)

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
    # CACHE YÖNETİMİ
    # =========================================================================
    
    def has_cached_data(self, category, period, genre=None, is_turkish=False, page=1):
        """Belirtilen parametreler için geçerli cache var mı?"""
        genre_key = str(genre) if genre else 'all'
        return self.cache_repo.has_valid_cache(category, period, genre_key, is_turkish, page)
    
    def get_max_cached_page(self, category, period, genre=None, is_turkish=False):
        """Cache'deki maksimum sayfa numarasını döndürür."""
        genre_key = str(genre) if genre else 'all'
        return self.cache_repo.get_max_cached_page(category, period, genre_key, is_turkish)
    
    def clear_cache(self):
        """Tüm cache'i temizler."""
        return self.cache_repo.clear_all_cache()

    # =========================================================================
    # ÖNERİ ALMA (Ana Metod)
    # =========================================================================
    
    def get_recommendations(self, callback, category, period, genre=None, 
                           page=1, is_turkish=False, force_refresh=False):
        """
        Belirtilen parametreler için önerileri asenkron getirir.
        
        Önce cache'i kontrol eder:
        - Cache varsa ve geçerliyse -> DB'den çeker
        - Cache yoksa veya force_refresh -> API'den çeker ve cache'ler
        
        Args:
            callback: Sonuçları alacak fonksiyon
            category: Film, Dizi, Oyun, Kitap
            period: Periyot anahtarı
            genre: Tür değeri (API ID veya None)
            page: Sayfa numarası (1'den başlar)
            is_turkish: Sadece Türkçe yapımlar mı?
            force_refresh: Cache'i yoksay, API'den taze veri çek
        """
        genre_key = str(genre) if genre else 'all'
        
        def task():
            # Cache kontrolü
            if not force_refresh and self.cache_repo.has_valid_cache(
                category, period, genre_key, is_turkish, page
            ):
                logger.info(f"Cache'den yükleniyor: {category}/{period}/{page}")
                return self.cache_repo.get_cached_recommendations(
                    category, period, genre_key, is_turkish, page
                )
            
            # API'den çek
            logger.info(f"API'den çekiliyor: {category}/{period}/{page}")
            results = self.api_service.get_recommendations(
                category, period, genre, page, is_turkish
            )
            
            # Cache'e kaydet
            if results:
                self.cache_repo.add_recommendations(
                    results, category, period, genre_key, is_turkish, page
                )
            
            return results

        worker = DbWorker(task)
        worker.finished.connect(callback)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.workers.add(worker)
        worker.start()
    
    def get_next_page(self, callback, category, period, genre=None, 
                      current_page=1, is_turkish=False):
        """
        Bir sonraki sayfayı getirir.
        Önce cache'de var mı kontrol eder, yoksa API'den çeker.
        """
        next_page = current_page + 1
        self.get_recommendations(
            callback, category, period, genre, next_page, is_turkish
        )
    
    def get_previous_data(self, callback, category, period, genre=None,
                          is_turkish=False, max_page=None):
        """
        Eski/önceki verileri DB'den çeker.
        Tüm cache'lenmiş sayfaları birleştirir.
        """
        genre_key = str(genre) if genre else 'all'
        
        def task():
            all_results = []
            
            if max_page is None:
                cached_max = self.cache_repo.get_max_cached_page(
                    category, period, genre_key, is_turkish
                )
            else:
                cached_max = max_page
            
            for page in range(1, cached_max + 1):
                page_results = self.cache_repo.get_cached_recommendations(
                    category, period, genre_key, is_turkish, page
                )
                all_results.extend(page_results)
            
            return all_results

        worker = DbWorker(task)
        worker.finished.connect(callback)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.workers.add(worker)
        worker.start()

    def get_random_recommendation(self, callback, category=None):
        """
        Rastgele bir öneri getirir.
        category: Belirtilirse o kategoriden, None ise rastgele kategoriden seçer.
        """
        def task():
            return self.api_service.get_random_recommendation(category)

        worker = DbWorker(task)
        worker.finished.connect(callback)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.workers.add(worker)
        worker.start()
