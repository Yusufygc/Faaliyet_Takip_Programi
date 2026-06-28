# services/series_api_service.py
import datetime
from logger_setup import logger
from services._base_api_service import _BaseApiService, ITEMS_PER_PAGE
from services.recommendation_config import PERIODS, CULT_SERIES_IDS
from constants import KEYRING_KEY_TMDB
from exceptions import RateLimitError, ApiError

_TMDB_BASE = "https://api.themoviedb.org/3"


class SeriesApiService(_BaseApiService):

    def fetch(self, period, genre_id=None, page=1, is_turkish=False) -> list:
        period_type = PERIODS.get(period, {}).get('type', 'date_range')
        try:
            if period_type == 'date_range':
                return self._by_date(period, genre_id, page, is_turkish)
            elif period_type == 'top_rated':
                return self._top_rated(genre_id, page, is_turkish)
            elif period_type == 'popular':
                return self._popular(genre_id, page, is_turkish)
            elif period_type == 'cult':
                return self._cult(page)
            elif period_type == 'hidden':
                return self._hidden(genre_id, page, is_turkish)
            elif period_type == 'new':
                return self._by_date('new_releases', genre_id, page, is_turkish)
            elif period_type == 'upcoming':
                return self._upcoming(genre_id, page, is_turkish)
            else:
                return self._popular(genre_id, page, is_turkish)
        except RateLimitError as e:
            logger.warning(f"Dizi API rate limit aşıldı: {e.url}")
            return []
        except ApiError as e:
            logger.error(f"Dizi API hatası: {e}")
            return []
        except Exception as e:
            logger.error(f"Dizi API beklenmeyen hata: {e}")
            return []

    def _parse_item(self, item) -> dict:
        return {
            'title': item.get('name'),
            'description': item.get('overview', '')[:200] + "..." if item.get('overview') else '',
            'rating': item.get('vote_average', 0),
            'image': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
            'date': item.get('first_air_date', ''),
            'type': 'Dizi',
            'id': item.get('id'),
        }

    def _by_date(self, period, genre_id=None, page=1, is_turkish=False) -> list:
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        params = {
            'api_key': self._get_key(KEYRING_KEY_TMDB),
            'language': 'tr-TR',
            'sort_by': 'popularity.desc',
            'first_air_date.gte': start_date,
            'first_air_date.lte': end_date,
            'page': page,
        }
        if genre_id:
            params['with_genres'] = genre_id
        if is_turkish:
            params['with_origin_country'] = 'TR'
        return self._fetch_paginated(f"{_TMDB_BASE}/discover/tv", params, self._parse_item)

    def _top_rated(self, genre_id=None, page=1, is_turkish=False) -> list:
        if is_turkish:
            url = f"{_TMDB_BASE}/discover/tv"
            params = {
                'api_key': self._get_key(KEYRING_KEY_TMDB),
                'language': 'tr-TR',
                'sort_by': 'vote_average.desc',
                'vote_count.gte': 50,
                'with_origin_country': 'TR',
                'page': page,
            }
        else:
            url = f"{_TMDB_BASE}/tv/top_rated"
            params = {'api_key': self._get_key(KEYRING_KEY_TMDB), 'language': 'tr-TR', 'page': page}
        return self._fetch_paginated(url, params, self._parse_item, genre_id=genre_id)

    def _popular(self, genre_id=None, page=1, is_turkish=False) -> list:
        if is_turkish:
            url = f"{_TMDB_BASE}/discover/tv"
            params = {
                'api_key': self._get_key(KEYRING_KEY_TMDB),
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'with_origin_country': 'TR',
                'page': page,
            }
        else:
            url = f"{_TMDB_BASE}/tv/popular"
            params = {'api_key': self._get_key(KEYRING_KEY_TMDB), 'language': 'tr-TR', 'page': page}
        return self._fetch_paginated(url, params, self._parse_item, genre_id=genre_id)

    def _cult(self, page=1) -> list:
        start_idx = (page - 1) * ITEMS_PER_PAGE
        series_ids = CULT_SERIES_IDS[start_idx:start_idx + ITEMS_PER_PAGE]
        results = []
        for series_id in series_ids:
            try:
                resp = self._request_with_retry(
                    f"{_TMDB_BASE}/tv/{series_id}",
                    {'api_key': self._get_key(KEYRING_KEY_TMDB), 'language': 'tr-TR'},
                )
                parsed = self._parse_item(resp.json())
                if parsed['image']:
                    results.append(parsed)
            except (ApiError, RateLimitError):
                continue
            except Exception:
                continue
        return results

    def _hidden(self, genre_id=None, page=1, is_turkish=False) -> list:
        params = {
            'api_key': self._get_key(KEYRING_KEY_TMDB),
            'language': 'tr-TR',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 20,
            'vote_count.lte': 200,
            'vote_average.gte': 7.5,
            'page': page,
        }
        if genre_id:
            params['with_genres'] = genre_id
        if is_turkish:
            params['with_origin_country'] = 'TR'
            params['vote_count.gte'] = 10
            params['vote_count.lte'] = 100
        return self._fetch_paginated(f"{_TMDB_BASE}/discover/tv", params, self._parse_item)

    def _upcoming(self, genre_id=None, page=1, is_turkish=False) -> list:
        if is_turkish:
            url = f"{_TMDB_BASE}/discover/tv"
            params = {
                'api_key': self._get_key(KEYRING_KEY_TMDB),
                'language': 'tr-TR',
                'sort_by': 'popularity.desc',
                'first_air_date.gte': datetime.datetime.now().strftime("%Y-%m-%d"),
                'with_origin_country': 'TR',
                'page': page,
            }
        else:
            url = f"{_TMDB_BASE}/tv/on_the_air"
            params = {'api_key': self._get_key(KEYRING_KEY_TMDB), 'language': 'tr-TR', 'page': page}
        return self._fetch_paginated(url, params, self._parse_item, genre_id=genre_id)
