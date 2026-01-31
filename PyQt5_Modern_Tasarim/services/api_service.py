# -*- coding: utf-8 -*-
"""
Keşfet & Öneriler modülü için API servisi.
Dış API'lerden veri çeker (TMDB, RAWG, Open Library).
Pagination ve Türkçe içerik filtresi destekler.
"""

import requests
import datetime
import os
from dotenv import load_dotenv
from services.recommendation_config import (
    PERIODS, PERIOD_ORDER, FILM_GENRES, DIZI_GENRES, OYUN_GENRES, KITAP_GENRES,
    CULT_MOVIE_IDS, CULT_SERIES_IDS, MIN_VOTE_COUNT, MIN_RATING_ALL_TIME
)

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

# Sayfa başına öğe sayısı
ITEMS_PER_PAGE = 12


class ApiService:
    def __init__(self):
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.rawg_base_url = "https://api.rawg.io/api"

    # =========================================================================
    # YARDIMCI METODLAR
    # =========================================================================
    
    def get_date_range(self, period):
        """Periyoda göre tarih aralığı döndürür."""
        now = datetime.datetime.now()
        
        if period == 'this_month':
            start_date = now.replace(day=1)
            end_date = now
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            
        elif period == 'last_year':
            last_year = now.year - 1
            start_date = datetime.datetime(last_year, 1, 1)
            end_date = datetime.datetime(last_year, 12, 31)
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        
        elif period == 'new_releases':
            start_date = now - datetime.timedelta(days=90)
            end_date = now
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        
        elif period == 'upcoming':
            start_date = now
            end_date = now + datetime.timedelta(days=90)
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            
        return None, None

    def _parse_movie_item(self, item):
        """TMDB film verisini standart formata çevirir."""
        return {
            'title': item.get('title'),
            'description': item.get('overview', '')[:200] + "..." if item.get('overview') else '',
            'rating': item.get('vote_average', 0),
            'image': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
            'date': item.get('release_date', ''),
            'type': 'Film',
            'id': item.get('id')
        }

    def _parse_series_item(self, item):
        """TMDB dizi verisini standart formata çevirir."""
        return {
            'title': item.get('name'),
            'description': item.get('overview', '')[:200] + "..." if item.get('overview') else '',
            'rating': item.get('vote_average', 0),
            'image': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
            'date': item.get('first_air_date', ''),
            'type': 'Dizi',
            'id': item.get('id')
        }

    def _parse_game_item(self, item):
        """RAWG oyun verisini standart formata çevirir."""
        return {
            'title': item.get('name'),
            'description': f"Rating: {item.get('rating', 0)}/5 ⭐ {item.get('ratings_count', 0)} oy",
            'rating': item.get('rating', 0) * 2,
            'image': item.get('background_image'),
            'date': item.get('released', ''),
            'type': 'Oyun',
            'id': item.get('id')
        }

    # =========================================================================
    # FİLM API'leri
    # =========================================================================

    def fetch_movies(self, period, genre_id=None, page=1, is_turkish=False):
        """Periyoda göre film önerileri çeker."""
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_movies_by_date(period, genre_id, page, is_turkish)
            elif period_type == 'top_rated':
                return self._fetch_movies_top_rated(genre_id, page, is_turkish)
            elif period_type == 'popular':
                return self._fetch_movies_popular(genre_id, page, is_turkish)
            elif period_type == 'cult':
                return self._fetch_movies_cult(page)
            elif period_type == 'hidden':
                return self._fetch_movies_hidden(genre_id, page, is_turkish)
            elif period_type == 'new':
                return self._fetch_movies_by_date('new_releases', genre_id, page, is_turkish)
            elif period_type == 'upcoming':
                return self._fetch_movies_upcoming(genre_id, page, is_turkish)
            else:
                return self._fetch_movies_popular(genre_id, page, is_turkish)
        except Exception as e:
            print(f"Movie API Error: {e}")
            return []

    def _fetch_movies_by_date(self, period, genre_id=None, page=1, is_turkish=False):
        """Tarih aralığına göre filmler."""
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        
        url = f"{self.tmdb_base_url}/discover/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'popularity.desc',
            'primary_release_date.gte': start_date,
            'primary_release_date.lte': end_date,
            'page': page
        }
        
        if genre_id:
            params['with_genres'] = genre_id
        
        if is_turkish:
            params['with_origin_country'] = 'TR'
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:ITEMS_PER_PAGE]:
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_movies_top_rated(self, genre_id=None, page=1, is_turkish=False):
        """Tüm zamanların en iyi filmleri."""
        if is_turkish:
            # Türkçe için discover endpoint kullan
            url = f"{self.tmdb_base_url}/discover/movie"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'vote_average.desc',
                'vote_count.gte': 100,
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/movie/top_rated"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_movies_popular(self, genre_id=None, page=1, is_turkish=False):
        """En popüler filmler."""
        if is_turkish:
            url = f"{self.tmdb_base_url}/discover/movie"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/movie/popular"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_movies_cult(self, page=1):
        """Kült klasik filmler."""
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        movie_ids = CULT_MOVIE_IDS[start_idx:end_idx]
        
        results = []
        for movie_id in movie_ids:
            url = f"{self.tmdb_base_url}/movie/{movie_id}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR'
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    item = response.json()
                    parsed = self._parse_movie_item(item)
                    if parsed['image']:
                        results.append(parsed)
            except:
                continue
        return results

    def _fetch_movies_hidden(self, genre_id=None, page=1, is_turkish=False):
        """Gizli hazineler."""
        url = f"{self.tmdb_base_url}/discover/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 50,
            'vote_count.lte': 500,
            'vote_average.gte': 7.5,
            'page': page
        }
        
        if genre_id:
            params['with_genres'] = genre_id
        
        if is_turkish:
            params['with_origin_country'] = 'TR'
            params['vote_count.gte'] = 20
            params['vote_count.lte'] = 200
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:ITEMS_PER_PAGE]:
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_movies_upcoming(self, genre_id=None, page=1, is_turkish=False):
        """Yakında çıkacak filmler."""
        if is_turkish:
            start_date, end_date = self.get_date_range('upcoming')
            url = f"{self.tmdb_base_url}/discover/movie"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'primary_release_date.gte': start_date,
                'primary_release_date.lte': end_date,
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/movie/upcoming"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'region': 'TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    # =========================================================================
    # DİZİ API'leri
    # =========================================================================

    def fetch_series(self, period, genre_id=None, page=1, is_turkish=False):
        """Periyoda göre dizi önerileri çeker."""
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_series_by_date(period, genre_id, page, is_turkish)
            elif period_type == 'top_rated':
                return self._fetch_series_top_rated(genre_id, page, is_turkish)
            elif period_type == 'popular':
                return self._fetch_series_popular(genre_id, page, is_turkish)
            elif period_type == 'cult':
                return self._fetch_series_cult(page)
            elif period_type == 'hidden':
                return self._fetch_series_hidden(genre_id, page, is_turkish)
            elif period_type == 'new':
                return self._fetch_series_by_date('new_releases', genre_id, page, is_turkish)
            elif period_type == 'upcoming':
                return self._fetch_series_upcoming(genre_id, page, is_turkish)
            else:
                return self._fetch_series_popular(genre_id, page, is_turkish)
        except Exception as e:
            print(f"Series API Error: {e}")
            return []

    def _fetch_series_by_date(self, period, genre_id=None, page=1, is_turkish=False):
        """Tarih aralığına göre diziler."""
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        
        url = f"{self.tmdb_base_url}/discover/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'popularity.desc',
            'first_air_date.gte': start_date,
            'first_air_date.lte': end_date,
            'page': page
        }
        
        if genre_id:
            params['with_genres'] = genre_id
        
        if is_turkish:
            params['with_origin_country'] = 'TR'
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:ITEMS_PER_PAGE]:
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_series_top_rated(self, genre_id=None, page=1, is_turkish=False):
        """Tüm zamanların en iyi dizileri."""
        if is_turkish:
            url = f"{self.tmdb_base_url}/discover/tv"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'vote_average.desc',
                'vote_count.gte': 50,
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/tv/top_rated"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_series_popular(self, genre_id=None, page=1, is_turkish=False):
        """En popüler diziler."""
        if is_turkish:
            url = f"{self.tmdb_base_url}/discover/tv"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/tv/popular"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_series_cult(self, page=1):
        """Kült diziler."""
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        series_ids = CULT_SERIES_IDS[start_idx:end_idx]
        
        results = []
        for series_id in series_ids:
            url = f"{self.tmdb_base_url}/tv/{series_id}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR'
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    item = response.json()
                    parsed = self._parse_series_item(item)
                    if parsed['image']:
                        results.append(parsed)
            except:
                continue
        return results

    def _fetch_series_hidden(self, genre_id=None, page=1, is_turkish=False):
        """Gizli hazine diziler."""
        url = f"{self.tmdb_base_url}/discover/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 20,
            'vote_count.lte': 200,
            'vote_average.gte': 7.5,
            'page': page
        }
        
        if genre_id:
            params['with_genres'] = genre_id
        
        if is_turkish:
            params['with_origin_country'] = 'TR'
            params['vote_count.gte'] = 10
            params['vote_count.lte'] = 100
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:ITEMS_PER_PAGE]:
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_series_upcoming(self, genre_id=None, page=1, is_turkish=False):
        """Yakında başlayacak diziler."""
        if is_turkish:
            url = f"{self.tmdb_base_url}/discover/tv"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'first_air_date.gte': datetime.datetime.now().strftime("%Y-%m-%d"),
                'with_origin_country': 'TR',
                'page': page
            }
        else:
            url = f"{self.tmdb_base_url}/tv/on_the_air"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'tr-TR',
                'page': page
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    # =========================================================================
    # OYUN API'leri
    # =========================================================================

    def fetch_games(self, period, genre_slug=None, page=1, is_turkish=False):
        """Periyoda göre oyun önerileri çeker. (Türkçe filtre oyunlarda yoktur)"""
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_games_by_date(period, genre_slug, page)
            elif period_type == 'top_rated':
                return self._fetch_games_top_rated(genre_slug, page)
            elif period_type == 'popular':
                return self._fetch_games_popular(genre_slug, page)
            elif period_type in ['cult', 'hidden']:
                return self._fetch_games_top_rated(genre_slug, page)
            elif period_type == 'new':
                return self._fetch_games_by_date('new_releases', genre_slug, page)
            elif period_type == 'upcoming':
                return self._fetch_games_upcoming(genre_slug, page)
            else:
                return self._fetch_games_popular(genre_slug, page)
        except Exception as e:
            print(f"Game API Error: {e}")
            return []

    def _fetch_games_by_date(self, period, genre_slug=None, page=1):
        """Tarih aralığına göre oyunlar."""
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'dates': f"{start_date},{end_date}",
            'ordering': '-added',
            'page_size': ITEMS_PER_PAGE,
            'page': page
        }
        
        if genre_slug:
            params['genres'] = genre_slug
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            parsed = self._parse_game_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_games_top_rated(self, genre_slug=None, page=1):
        """En iyi oyunlar."""
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'ordering': '-metacritic',
            'metacritic': '80,100',
            'page_size': ITEMS_PER_PAGE,
            'page': page
        }
        
        if genre_slug:
            params['genres'] = genre_slug
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            parsed = self._parse_game_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_games_popular(self, genre_slug=None, page=1):
        """En popüler oyunlar."""
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'ordering': '-added',
            'page_size': ITEMS_PER_PAGE,
            'page': page
        }
        
        if genre_slug:
            params['genres'] = genre_slug
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            parsed = self._parse_game_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    def _fetch_games_upcoming(self, genre_slug=None, page=1):
        """Yakında çıkacak oyunlar."""
        now = datetime.datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + datetime.timedelta(days=180)).strftime("%Y-%m-%d")
        
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'dates': f"{start_date},{end_date}",
            'ordering': 'released',
            'page_size': ITEMS_PER_PAGE,
            'page': page
        }
        
        if genre_slug:
            params['genres'] = genre_slug
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            parsed = self._parse_game_item(item)
            if parsed['image']:
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results

    # =========================================================================
    # KİTAP API'leri (Google Books)
    # =========================================================================

    def fetch_books(self, period, subject="fiction", page=1, is_turkish=False):
        """Google Books API'den kitap önerileri çeker."""
        if not subject:
            subject = "fiction"
        
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'popular')
        
        try:
            # Google Books API pagination: startIndex = (page-1) * maxResults
            start_index = (page - 1) * ITEMS_PER_PAGE
            
            # Arama sorgusu oluştur
            query = f"subject:{subject}"
            
            # Türkçe kitaplar için dil filtresi
            lang_restrict = "tr" if is_turkish else None
            
            # Periyot tipine göre sıralama
            if period_type == 'top_rated':
                order_by = "relevance"  # En alakalı (genelde yüksek puanlı)
            elif period_type == 'new':
                order_by = "newest"
            else:
                order_by = "relevance"
            
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': query,
                'startIndex': start_index,
                'maxResults': ITEMS_PER_PAGE,
                'orderBy': order_by,
                'printType': 'books'
            }
            
            if lang_restrict:
                params['langRestrict'] = lang_restrict
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            results = []
            seen_titles = set()
            
            for item in items:
                volume_info = item.get('volumeInfo', {})
                title = volume_info.get('title', '')
                
                # Tekrarlayan başlıkları atla
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                # Kapak resmi
                image_links = volume_info.get('imageLinks', {})
                img_url = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                
                if not img_url:
                    continue  # Resimsiz kitapları atla
                
                # HTTPS kullan
                img_url = img_url.replace('http://', 'https://')
                
                # Yazar bilgisi
                authors = volume_info.get('authors', [])
                author_name = ', '.join(authors[:2]) if authors else 'Bilinmiyor'
                
                # Yayın tarihi
                published_date = volume_info.get('publishedDate', '')
                year = published_date[:4] if published_date else 'Bilinmiyor'
                
                # Rating (Google Books'ta averageRating)
                rating = volume_info.get('averageRating', 0) or 0
                # Google 5 üzerinden veriyor, 10'a çevirelim
                rating = rating * 2
                
                # Açıklama
                description = volume_info.get('description', '')
                if description:
                    description = description[:150] + "..." if len(description) > 150 else description
                else:
                    description = f"Yazar: {author_name}"
                
                results.append({
                    'title': title,
                    'description': description,
                    'rating': rating,
                    'image': img_url,
                    'date': year,
                    'type': 'Kitap',
                    'id': item.get('id', title)
                })
                
                if len(results) >= ITEMS_PER_PAGE:
                    break

            return results
            
        except Exception as e:
            print(f"Google Books API Error: {e}")
            return []

    # =========================================================================
    # ANA METOD
    # =========================================================================

    def get_recommendations(self, category, period, genre=None, page=1, is_turkish=False):
        """Kategori, periyot, tür ve sayfa için önerileri getirir."""
        if category == 'Film':
            return self.fetch_movies(period, genre, page, is_turkish)
        elif category == 'Dizi':
            return self.fetch_series(period, genre, page, is_turkish)
        elif category == 'Oyun':
            return self.fetch_games(period, genre, page, is_turkish)
        elif category == 'Kitap':
            return self.fetch_books(period, genre, page, is_turkish)
        return []

    # =========================================================================
    # RANDOM ÖNERİ
    # =========================================================================

    def get_random_recommendation(self, category=None):
        """
        Rastgele bir periyot ve türden tek bir öneri getirir.
        category: Belirtilirse o kategoriden, None ise rastgele kategoriden seçer.
        """
        import random
        
        # Kategori belirtilmemişse rastgele seç
        if not category:
            categories = ['Film', 'Dizi', 'Oyun', 'Kitap']
            category = random.choice(categories)
        
        # Rastgele periyot seç
        periods = ['all_time_best', 'must_see', 'cult_classics', 'hidden_gems']
        period = random.choice(periods)
        
        # Rastgele sayfa (1-3 arası)
        page = random.randint(1, 3)
        
        try:
            # Önerileri çek
            results = self.get_recommendations(category, period, None, page, False)
            
            if results:
                # Rastgele bir tane seç
                selected = random.choice(results)
                selected['random_category'] = category
                selected['random_period'] = period
                return selected
            
            # Boş geldiyse varsayılan dene
            return self._get_fallback_random(category)
            
        except Exception as e:
            print(f"Random recommendation error: {e}")
            return self._get_fallback_random(category)
    
    def _get_fallback_random(self, category=None):
        """Fallback olarak popüler içeriklerden rastgele seçer."""
        import random
        
        try:
            # Belirtilen kategoriden veya Film'den dene
            cat = category or 'Film'
            results = self.get_recommendations(cat, 'must_see', None, 1, False)
            if results:
                selected = random.choice(results)
                selected['random_category'] = cat
                selected['random_period'] = 'must_see'
                return selected
        except:
            pass
        
        return None

