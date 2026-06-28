# -*- coding: utf-8 -*-
"""
Öneri sistemi için veritabanı repository.
API'den çekilen verileri cache'ler ve pagination destekler.
"""

import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
from database.connection import get_connection
from logger_setup import logger


@dataclass
class CachedRecommendation:
    """Cache'lenmiş öneri modeli."""
    id: int
    category: str           # Film, Dizi, Oyun, Kitap
    period: str             # this_month, all_time_best, vb.
    genre: str              # Tür (None olabilir -> "all")
    is_turkish: bool        # Türkçe yapım mı?
    external_id: str        # API'deki ID (tekrar çekmemek için)
    title: str
    description: str
    rating: float
    image_url: str
    release_date: str
    content_type: str       # Film, Dizi, vb. (API'den gelen)
    page: int               # Sayfa numarası
    fetched_at: str         # ISO format tarih
    
    @classmethod
    def from_row(cls, row):
        """Veritabanı satırından nesne oluşturur."""
        return cls(*row)
    
    def to_display_dict(self):
        """UI için dict formatına çevirir."""
        return {
            'title': self.title,
            'description': self.description,
            'rating': self.rating,
            'image': self.image_url,
            'date': self.release_date,
            'type': self.content_type,
            'id': self.external_id
        }


class RecommendationRepository:
    """
    Öneri cache'i için repository.
    API sonuçlarını DB'ye kaydeder ve sayfalama destekler.
    """
    
    CACHE_EXPIRY_DAYS = 7
    ITEMS_PER_PAGE = 10
    
    def __init__(self):
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Cache tablosunu oluşturur."""
        conn = get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendation_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    period TEXT NOT NULL,
                    genre TEXT DEFAULT 'all',
                    is_turkish INTEGER DEFAULT 0,
                    external_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    rating REAL DEFAULT 0,
                    image_url TEXT,
                    release_date TEXT,
                    content_type TEXT,
                    page INTEGER DEFAULT 1,
                    fetched_at TEXT NOT NULL,
                    UNIQUE(category, period, genre, is_turkish, external_id)
                )
            ''')
            
            # Index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_lookup 
                ON recommendation_cache(category, period, genre, is_turkish, page)
            ''')
            
            conn.commit()
            logger.info("Recommendation cache tablosu hazır.")
        except Exception as e:
            logger.error(f"Cache tablosu oluşturulurken hata: {e}")
        finally:
            conn.close()
    
    def add_recommendations(self, recommendations: List[dict], category: str, 
                           period: str, genre: str = None, is_turkish: bool = False,
                           page: int = 1) -> bool:
        """
        API'den gelen önerileri cache'e ekler.
        """
        conn = get_connection()
        if not conn:
            return False
        
        genre_key = genre if genre else 'all'
        fetched_at = datetime.now().isoformat()
        
        try:
            cursor = conn.cursor()
            
            for item in recommendations:
                cursor.execute('''
                    INSERT OR REPLACE INTO recommendation_cache 
                    (category, period, genre, is_turkish, external_id, title, 
                     description, rating, image_url, release_date, content_type, 
                     page, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category,
                    period,
                    genre_key,
                    1 if is_turkish else 0,
                    str(item.get('id', item.get('title', ''))),
                    item.get('title', 'Başlıksız'),
                    item.get('description', ''),
                    item.get('rating', 0) or 0,
                    item.get('image', ''),
                    item.get('date', ''),
                    item.get('type', category),
                    page,
                    fetched_at
                ))
            
            conn.commit()
            logger.info(f"Cache'e {len(recommendations)} öneri eklendi. ({category}/{period}/{page})")
            return True
            
        except Exception as e:
            logger.error(f"Cache'e ekleme hatası: {e}")
            return False
        finally:
            conn.close()
    
    def get_cached_recommendations(self, category: str, period: str, 
                                   genre: str = None, is_turkish: bool = False,
                                   page: int = 1) -> List[dict]:
        """
        Cache'den önerileri çeker.
        Süresi dolmuşsa boş liste döner.
        """
        conn = get_connection()
        if not conn:
            return []
        
        genre_key = genre if genre else 'all'
        
        try:
            cursor = conn.cursor()
            
            # Expiry check
            expiry_date = (datetime.now() - timedelta(days=self.CACHE_EXPIRY_DAYS)).isoformat()
            
            cursor.execute('''
                SELECT id, category, period, genre, is_turkish, external_id,
                       title, description, rating, image_url, release_date,
                       content_type, page, fetched_at
                FROM recommendation_cache
                WHERE category = ? AND period = ? AND genre = ? 
                      AND is_turkish = ? AND page = ?
                      AND fetched_at > ?
                ORDER BY id ASC
            ''', (category, period, genre_key, 1 if is_turkish else 0, page, expiry_date))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                rec = CachedRecommendation.from_row(row)
                results.append(rec.to_display_dict())
            
            logger.debug(f"Cache'den {len(results)} öneri çekildi. ({category}/{period}/{page})")
            return results
            
        except Exception as e:
            logger.error(f"Cache'den çekme hatası: {e}")
            return []
        finally:
            conn.close()
    
    def get_max_cached_page(self, category: str, period: str, 
                            genre: str = None, is_turkish: bool = False) -> int:
        """
        Mevcut cache'deki en yüksek sayfa numarasını döndürür.
        """
        conn = get_connection()
        if not conn:
            return 0
        
        genre_key = genre if genre else 'all'
        
        try:
            cursor = conn.cursor()
            expiry_date = (datetime.now() - timedelta(days=self.CACHE_EXPIRY_DAYS)).isoformat()
            
            cursor.execute('''
                SELECT MAX(page) FROM recommendation_cache
                WHERE category = ? AND period = ? AND genre = ? 
                      AND is_turkish = ? AND fetched_at > ?
            ''', (category, period, genre_key, 1 if is_turkish else 0, expiry_date))
            
            result = cursor.fetchone()
            return result[0] if result[0] else 0
            
        except Exception as e:
            logger.error(f"Max page sorgusu hatası: {e}")
            return 0
        finally:
            conn.close()
    
    def has_valid_cache(self, category: str, period: str, 
                        genre: str = None, is_turkish: bool = False,
                        page: int = 1) -> bool:
        """
        Belirtilen parametereler için geçerli (süresi dolmamış) cache var mı?
        """
        conn = get_connection()
        if not conn:
            return False
        
        genre_key = genre if genre else 'all'
        
        try:
            cursor = conn.cursor()
            expiry_date = (datetime.now() - timedelta(days=self.CACHE_EXPIRY_DAYS)).isoformat()
            
            cursor.execute('''
                SELECT COUNT(*) FROM recommendation_cache
                WHERE category = ? AND period = ? AND genre = ? 
                      AND is_turkish = ? AND page = ?
                      AND fetched_at > ?
            ''', (category, period, genre_key, 1 if is_turkish else 0, page, expiry_date))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Cache kontrol hatası: {e}")
            return False
        finally:
            conn.close()
    
    def clear_expired_cache(self) -> int:
        """
        Süresi dolmuş cache kayıtlarını siler.
        Silinen kayıt sayısını döndürür.
        """
        conn = get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            expiry_date = (datetime.now() - timedelta(days=self.CACHE_EXPIRY_DAYS)).isoformat()
            
            cursor.execute('''
                DELETE FROM recommendation_cache
                WHERE fetched_at < ?
            ''', (expiry_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Süresi dolmuş {deleted_count} cache kaydı silindi.")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache temizleme hatası: {e}")
            return 0
        finally:
            conn.close()
    
    def clear_all_cache(self) -> bool:
        """Tüm cache'i temizler."""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM recommendation_cache')
            conn.commit()
            logger.info("Tüm öneri cache'i temizlendi.")
            return True
        except Exception as e:
            logger.error(f"Cache silme hatası: {e}")
            return False
        finally:
            conn.close()
