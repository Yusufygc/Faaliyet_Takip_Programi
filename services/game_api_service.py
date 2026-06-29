# services/game_api_service.py
import datetime
from logger_setup import logger
from services._base_api_service import _BaseApiService, ITEMS_PER_PAGE
from services.recommendation_config import PERIODS
from constants import KEYRING_KEY_RAWG
from exceptions import RateLimitError, ApiError

_RAWG_BASE = "https://api.rawg.io/api"


class GameApiService(_BaseApiService):

    def fetch(self, period, genre_slug=None, page=1, is_turkish=False) -> list:
        period_type = PERIODS.get(period, {}).get('type', 'date_range')
        try:
            if period_type == 'date_range':
                return self._by_date(period, genre_slug, page)
            elif period_type == 'top_rated':
                return self._top_rated(genre_slug, page)
            elif period_type == 'popular':
                return self._popular(genre_slug, page)
            elif period_type in ('cult', 'hidden'):
                return self._top_rated(genre_slug, page)
            elif period_type == 'new':
                return self._by_date('new_releases', genre_slug, page)
            elif period_type == 'upcoming':
                return self._upcoming(genre_slug, page)
            else:
                return self._popular(genre_slug, page)
        except RateLimitError as e:
            logger.warning(f"Oyun API rate limit aşıldı: {e.url}")
            return []
        except ApiError as e:
            logger.error(f"Oyun API hatası: {e}")
            return []
        except Exception as e:
            logger.error(f"Oyun API beklenmeyen hata: {e}")
            return []

    def _parse_item(self, item) -> dict:
        return {
            'title': item.get('name'),
            'description': f"Rating: {item.get('rating', 0)}/5 | {item.get('ratings_count', 0)} oy",
            'rating': item.get('rating', 0) * 2,
            'image': item.get('background_image'),
            'date': item.get('released', ''),
            'type': 'Oyun',
            'id': item.get('id'),
        }

    def _by_date(self, period, genre_slug=None, page=1) -> list:
        start_date, end_date = self.get_date_range(period)
        if not start_date:
            return []
        params = {
            'key': self._get_key(KEYRING_KEY_RAWG),
            'dates': f"{start_date},{end_date}",
            'ordering': '-added',
            'page_size': ITEMS_PER_PAGE,
            'page': page,
        }
        if genre_slug:
            params['genres'] = genre_slug
        return self._fetch_paginated(f"{_RAWG_BASE}/games", params, self._parse_item)

    def _top_rated(self, genre_slug=None, page=1) -> list:
        params = {
            'key': self._get_key(KEYRING_KEY_RAWG),
            'ordering': '-metacritic',
            'metacritic': '80,100',
            'page_size': ITEMS_PER_PAGE,
            'page': page,
        }
        if genre_slug:
            params['genres'] = genre_slug
        return self._fetch_paginated(f"{_RAWG_BASE}/games", params, self._parse_item)

    def _popular(self, genre_slug=None, page=1) -> list:
        params = {
            'key': self._get_key(KEYRING_KEY_RAWG),
            'ordering': '-added',
            'page_size': ITEMS_PER_PAGE,
            'page': page,
        }
        if genre_slug:
            params['genres'] = genre_slug
        return self._fetch_paginated(f"{_RAWG_BASE}/games", params, self._parse_item)

    def _upcoming(self, genre_slug=None, page=1) -> list:
        now = datetime.datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + datetime.timedelta(days=180)).strftime("%Y-%m-%d")
        params = {
            'key': self._get_key(KEYRING_KEY_RAWG),
            'dates': f"{start_date},{end_date}",
            'ordering': 'released',
            'page_size': ITEMS_PER_PAGE,
            'page': page,
        }
        if genre_slug:
            params['genres'] = genre_slug
        return self._fetch_paginated(f"{_RAWG_BASE}/games", params, self._parse_item)
