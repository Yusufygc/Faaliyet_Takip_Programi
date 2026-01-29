import requests
import datetime
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

# Tür/Kategori Tanımlamaları (API ID'leri)
# TMDB Film Türleri: https://api.themoviedb.org/3/genre/movie/list
FILM_GENRES = {
    "Tümü": None,
    "Aksiyon": 28,
    "Komedi": 35,
    "Dram": 18,
    "Korku": 27,
    "Bilim Kurgu": 878,
    "Romantik": 10749,
    "Animasyon": 16,
    "Gerilim": 53
}

# TMDB Dizi Türleri
DIZI_GENRES = {
    "Tümü": None,
    "Aksiyon": 10759,
    "Komedi": 35,
    "Dram": 18,
    "Suç": 80,
    "Belgesel": 99,
    "Aile": 10751,
    "Animasyon": 16
}

# RAWG Oyun Türleri (slug)
OYUN_GENRES = {
    "Tümü": None,
    "Aksiyon": "action",
    "RPG": "role-playing-games-rpg",
    "Strateji": "strategy",
    "Spor": "sports",
    "Yarış": "racing",
    "Macera": "adventure",
    "Bulmaca": "puzzle"
}

# Open Library Kitap Türleri (subject)
KITAP_GENRES = {
    "Tümü": "fiction",
    "Gerilim": "thriller",
    "Romantik": "romance",
    "Bilim Kurgu": "science_fiction",
    "Fantastik": "fantasy",
    "Korku": "horror",
    "Tarih": "history"
}

class ApiService:
    def __init__(self):
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.rawg_base_url = "https://api.rawg.io/api"
        self.google_books_base_url = "https://www.googleapis.com/books/v1/volumes"

    def get_date_range(self, period):
        """
        'this_month' veya 'last_year' için başlangıç ve bitiş tarihlerini döndürür.
        Format: YYYY-MM-DD
        """
        now = datetime.datetime.now()
        
        if period == 'this_month':
            start_date = now.replace(day=1)
            end_date = now # Bugüne kadar
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            
        elif period == 'last_year':
            last_year = now.year - 1
            start_date = datetime.datetime(last_year, 1, 1)
            end_date = datetime.datetime(last_year, 12, 31)
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            
        return None, None

    def fetch_movies(self, period, genre_id=None):
        """TMDB API'den film önerileri çeker."""
        start_date, end_date = self.get_date_range(period)
        if not start_date: return []

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
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get('results', [])[:10]: # İlk 10
                results.append({
                    'title': item.get('title'),
                    'description': item.get('overview'),
                    'rating': item.get('vote_average'),
                    'image': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                    'date': item.get('release_date'),
                    'type': 'Film'
                })
            return results
        except Exception as e:
            print(f"Movie API Error: {e}")
            return []

    def fetch_series(self, period, genre_id=None):
        """TMDB API'den dizi önerileri çeker."""
        start_date, end_date = self.get_date_range(period)
        if not start_date: return []

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
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get('results', [])[:10]:
                results.append({
                    'title': item.get('name'),
                    'description': item.get('overview'),
                    'rating': item.get('vote_average'),
                    'image': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                    'date': item.get('first_air_date'),
                    'type': 'Dizi'
                })
            return results
        except Exception as e:
            print(f"Series API Error: {e}")
            return []

    def fetch_games(self, period, genre_slug=None):
        """RAWG API'den oyun önerileri çeker."""
        start_date, end_date = self.get_date_range(period)
        if not start_date: return []

        url = f"{self.rawg_base_url}/games"
        params = {
            'key': RAWG_API_KEY,
            'dates': f"{start_date},{end_date}",
            'ordering': '-added',
            'page_size': 10
        }
        
        if genre_slug:
            params['genres'] = genre_slug
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get('results', []):
                results.append({
                    'title': item.get('name'),
                    'description': f"Rating: {item.get('rating')}/5",
                    'rating': item.get('rating'),
                    'image': item.get('background_image'),
                    'date': item.get('released'),
                    'type': 'Oyun'
                })
            return results
        except Exception as e:
            print(f"Game API Error: {e}")
            return []

    def fetch_books(self, period, subject="fiction"):
        """Open Library API'den kitap önerileri çeker."""
        # Open Library API: https://openlibrary.org/dev/docs/api/search
        
        # Varsayılan subject kontrolü
        if not subject:
            subject = "fiction"

        url = "https://openlibrary.org/subjects/" + subject + ".json"
        params = {
            'limit': 20,
            'details': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = []
            
            works = data.get('works', [])
            
            # Rating'e göre sırala (last_year için)
            if period == 'last_year':
                works = sorted(works, key=lambda x: x.get('ratings_average', 0) or 0, reverse=True)
            
            seen_titles = set()
            
            for work in works:
                title = work.get('title', '')
                
                # Tekrar eden kitapları engelle
                if title in seen_titles: 
                    continue
                seen_titles.add(title)
                
                # Kapak resmi
                cover_id = work.get('cover_id')
                if cover_id:
                    img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                else:
                    continue  # Resimsizleri atla
                
                # Yazar bilgisi
                authors = work.get('authors', [])
                author_name = authors[0].get('name', 'Bilinmiyor') if authors else 'Bilinmiyor'
                
                # Yayın yılı
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
