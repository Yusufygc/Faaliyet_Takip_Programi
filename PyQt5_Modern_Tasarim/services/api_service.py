# -*- coding: utf-8 -*-
"""
Keşfet & Öneriler modülü için API servisi.
Dış API'lerden veri çeker (TMDB, RAWG, Open Library).
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
            # Son 3 ay
            start_date = now - datetime.timedelta(days=90)
            end_date = now
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        
        elif period == 'upcoming':
            # Gelecek 3 ay
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

    # =========================================================================
    # FİLM API'leri
    # =========================================================================

    def fetch_movies(self, period, genre_id=None):
        """Periyoda göre film önerileri çeker."""
        
        # Periyot tipine göre farklı endpoint/parametre kullan
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_movies_by_date(period, genre_id)
            elif period_type == 'top_rated':
                return self._fetch_movies_top_rated(genre_id)
            elif period_type == 'popular':
                return self._fetch_movies_popular(genre_id)
            elif period_type == 'cult':
                return self._fetch_movies_cult()
            elif period_type == 'hidden':
                return self._fetch_movies_hidden(genre_id)
            elif period_type == 'new':
                return self._fetch_movies_by_date('new_releases', genre_id)
            elif period_type == 'upcoming':
                return self._fetch_movies_upcoming(genre_id)
            else:
                return self._fetch_movies_popular(genre_id)
        except Exception as e:
            print(f"Movie API Error: {e}")
            return []

    def _fetch_movies_by_date(self, period, genre_id=None):
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
            'page': 1
        }
        if genre_id:
            params['with_genres'] = genre_id
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:10]:
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_movies_top_rated(self, genre_id=None):
        """Tüm zamanların en iyi filmleri."""
        url = f"{self.tmdb_base_url}/movie/top_rated"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'page': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            if genre_id and genre_id not in item.get('genre_ids', []):
                continue
            parsed = self._parse_movie_item(item)
            if parsed['image'] and parsed['rating'] >= MIN_RATING_ALL_TIME:
                results.append(parsed)
            if len(results) >= 10:
                break
        return results

    def _fetch_movies_popular(self, genre_id=None):
        """En popüler filmler."""
        url = f"{self.tmdb_base_url}/movie/popular"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'page': 1
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
            if len(results) >= 10:
                break
        return results

    def _fetch_movies_cult(self):
        """Kült klasik filmler (önceden tanımlanmış liste)."""
        results = []
        for movie_id in CULT_MOVIE_IDS[:10]:
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

    def _fetch_movies_hidden(self, genre_id=None):
        """Gizli hazineler - yüksek puanlı ama az bilinen filmler."""
        url = f"{self.tmdb_base_url}/discover/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 50,
            'vote_count.lte': 500,  # Az oy almış
            'vote_average.gte': 7.5,
            'page': 1
        }
        if genre_id:
            params['with_genres'] = genre_id
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:10]:
            parsed = self._parse_movie_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_movies_upcoming(self, genre_id=None):
        """Yakında çıkacak filmler."""
        url = f"{self.tmdb_base_url}/movie/upcoming"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'region': 'TR',
            'page': 1
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
            if len(results) >= 10:
                break
        return results

    # =========================================================================
    # DİZİ API'leri
    # =========================================================================

    def fetch_series(self, period, genre_id=None):
        """Periyoda göre dizi önerileri çeker."""
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_series_by_date(period, genre_id)
            elif period_type == 'top_rated':
                return self._fetch_series_top_rated(genre_id)
            elif period_type == 'popular':
                return self._fetch_series_popular(genre_id)
            elif period_type == 'cult':
                return self._fetch_series_cult()
            elif period_type == 'hidden':
                return self._fetch_series_hidden(genre_id)
            elif period_type == 'new':
                return self._fetch_series_by_date('new_releases', genre_id)
            elif period_type == 'upcoming':
                return self._fetch_series_upcoming(genre_id)
            else:
                return self._fetch_series_popular(genre_id)
        except Exception as e:
            print(f"Series API Error: {e}")
            return []

    def _fetch_series_by_date(self, period, genre_id=None):
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
            'page': 1
        }
        if genre_id:
            params['with_genres'] = genre_id
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:10]:
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_series_top_rated(self, genre_id=None):
        """Tüm zamanların en iyi dizileri."""
        url = f"{self.tmdb_base_url}/tv/top_rated"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'page': 1
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
            if len(results) >= 10:
                break
        return results

    def _fetch_series_popular(self, genre_id=None):
        """En popüler diziler."""
        url = f"{self.tmdb_base_url}/tv/popular"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'page': 1
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
            if len(results) >= 10:
                break
        return results

    def _fetch_series_cult(self):
        """Kült diziler."""
        results = []
        for series_id in CULT_SERIES_IDS[:10]:
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

    def _fetch_series_hidden(self, genre_id=None):
        """Gizli hazine diziler."""
        url = f"{self.tmdb_base_url}/discover/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 20,
            'vote_count.lte': 200,
            'vote_average.gte': 7.5,
            'page': 1
        }
        if genre_id:
            params['with_genres'] = genre_id
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:10]:
            parsed = self._parse_series_item(item)
            if parsed['image']:
                results.append(parsed)
        return results

    def _fetch_series_upcoming(self, genre_id=None):
        """Yakında başlayacak diziler."""
        url = f"{self.tmdb_base_url}/tv/on_the_air"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'tr-TR',
            'page': 1
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
            if len(results) >= 10:
                break
        return results

    # =========================================================================
    # OYUN API'leri
    # =========================================================================

    def fetch_games(self, period, genre_slug=None):
        """Periyoda göre oyun önerileri çeker."""
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'date_range')
        
        try:
            if period_type == 'date_range':
                return self._fetch_games_by_date(period, genre_slug)
            elif period_type == 'top_rated':
                return self._fetch_games_top_rated(genre_slug)
            elif period_type == 'popular':
                return self._fetch_games_popular(genre_slug)
            elif period_type in ['cult', 'hidden']:
                return self._fetch_games_top_rated(genre_slug)  # RAWG'da cult yok
            elif period_type == 'new':
                return self._fetch_games_by_date('new_releases', genre_slug)
            elif period_type == 'upcoming':
                return self._fetch_games_upcoming(genre_slug)
            else:
                return self._fetch_games_popular(genre_slug)
        except Exception as e:
            print(f"Game API Error: {e}")
            return []

    def _parse_game_item(self, item):
        """RAWG oyun verisini standart formata çevirir."""
        return {
            'title': item.get('name'),
            'description': f"Rating: {item.get('rating', 0)}/5 ⭐ {item.get('ratings_count', 0)} oy",
            'rating': item.get('rating', 0) * 2,  # 5 üzerinden 10'a çevir
            'image': item.get('background_image'),
            'date': item.get('released', ''),
            'type': 'Oyun',
            'id': item.get('id')
        }

    def _fetch_games_by_date(self, period, genre_slug=None):
        """Tarih aralığına göre oyunlar."""
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'dates': f"{start_date},{end_date}",
            'ordering': '-added',
            'page_size': 15
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
            if len(results) >= 10:
                break
        return results

    def _fetch_games_top_rated(self, genre_slug=None):
        """En iyi oyunlar."""
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'ordering': '-metacritic',
            'metacritic': '80,100',
            'page_size': 15
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
            if len(results) >= 10:
                break
        return results

    def _fetch_games_popular(self, genre_slug=None):
        """En popüler oyunlar."""
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'ordering': '-added',
            'page_size': 15
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
            if len(results) >= 10:
                break
        return results

    def _fetch_games_upcoming(self, genre_slug=None):
        """Yakında çıkacak oyunlar."""
        now = datetime.datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + datetime.timedelta(days=180)).strftime("%Y-%m-%d")
        
        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'dates': f"{start_date},{end_date}",
            'ordering': 'released',
            'page_size': 15
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
            if len(results) >= 10:
                break
        return results

    # =========================================================================
    # KİTAP API'leri (Open Library)
    # =========================================================================

    def fetch_books(self, period, subject="fiction"):
        """Periyoda göre kitap önerileri çeker."""
        if not subject:
            subject = "fiction"
        
        period_config = PERIODS.get(period, {})
        period_type = period_config.get('type', 'popular')
        
        try:
            url = f"https://openlibrary.org/subjects/{subject}.json"
            params = {
                'limit': 25,
                'details': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            works = data.get('works', [])
            
            # Periyot tipine göre sırala
            if period_type == 'top_rated':
                works = sorted(works, key=lambda x: x.get('ratings_average', 0) or 0, reverse=True)
            elif period_type in ['cult', 'hidden']:
                # Eski ama yüksek puanlı kitaplar
                works = [w for w in works if w.get('first_publish_year', 2000) < 2000]
                works = sorted(works, key=lambda x: x.get('ratings_average', 0) or 0, reverse=True)
            
            results = []
            seen_titles = set()
            
            for work in works:
                title = work.get('title', '')
                
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                cover_id = work.get('cover_id')
                if cover_id:
                    img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                else:
                    continue
                
                authors = work.get('authors', [])
                author_name = authors[0].get('name', 'Bilinmiyor') if authors else 'Bilinmiyor'
                
                first_publish_year = work.get('first_publish_year', '')
                
                results.append({
                    'title': title,
                    'description': f"Yazar: {author_name}",
                    'rating': work.get('ratings_average', 0) or 0,
                    'image': img_url,
                    'date': str(first_publish_year) if first_publish_year else 'Bilinmiyor',
                    'type': 'Kitap'
                })
                
                if len(results) >= 10:
                    break

            return results
        except Exception as e:
            print(f"Open Library API Error: {e}")
            return []

    # =========================================================================
    # ANA METOD
    # =========================================================================

    def get_recommendations(self, category, period, genre=None):
        """Kategori, periyot ve türe göre önerileri getirir."""
        if category == 'Film':
            return self.fetch_movies(period, genre)
        elif category == 'Dizi':
            return self.fetch_series(period, genre)
        elif category == 'Oyun':
            return self.fetch_games(period, genre)
        elif category == 'Kitap':
            return self.fetch_books(period, genre)
        return []
