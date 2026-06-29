# services/_base_api_service.py
import time
import threading
import requests
import datetime
from logger_setup import logger
from services.recommendation_config import PERIODS
from exceptions import RateLimitError, ApiError

ITEMS_PER_PAGE = 12

_MAX_RETRIES = 3
_BASE_DELAY = 1.0  # saniye

# İstekler arası minimum bekleme (host başına) — 429 baskısını düşürür.
_MIN_REQUEST_INTERVAL = 0.4  # saniye
_last_request_times: dict[str, float] = {}
_throttle_lock = threading.Lock()


def _throttle(url: str) -> None:
    """Aynı host'a art arda istek arasında en az _MIN_REQUEST_INTERVAL bekletir."""
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    with _throttle_lock:
        now = time.monotonic()
        wait = _MIN_REQUEST_INTERVAL - (now - _last_request_times.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_request_times[host] = time.monotonic()


class _BaseApiService:
    def _get_key(self, name: str) -> str:
        try:
            import keyring
            from constants import KEYRING_APP_NAME
            return keyring.get_password(KEYRING_APP_NAME, name) or ""
        except Exception:
            return ""

    def get_date_range(self, period):
        now = datetime.datetime.now()

        if period == 'this_month':
            return now.replace(day=1).strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
        elif period == 'last_year':
            last_year = now.year - 1
            return (
                datetime.datetime(last_year, 1, 1).strftime("%Y-%m-%d"),
                datetime.datetime(last_year, 12, 31).strftime("%Y-%m-%d"),
            )
        elif period == 'new_releases':
            return (
                (now - datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
                now.strftime("%Y-%m-%d"),
            )
        elif period == 'upcoming':
            return (
                now.strftime("%Y-%m-%d"),
                (now + datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
            )
        return None, None

    def _request_with_retry(self, url: str, params: dict, timeout: int = 10) -> requests.Response:
        """Exponential backoff retry ile GET isteği atar.

        Retry: 429, 5xx, network/timeout hatası.
        No retry: 4xx (401, 403, 404 vb.).
        Raises ApiError veya RateLimitError on failure.
        """
        last_exc = None
        for attempt in range(_MAX_RETRIES):
            _throttle(url)
            try:
                resp = requests.get(url, params=params, timeout=timeout)
            except requests.Timeout:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(f"Timeout ({attempt + 1}/{_MAX_RETRIES}): {url}")
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(delay)
                last_exc = ApiError(f"Timeout: {url}")
                continue
            except requests.ConnectionError as e:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(f"Bağlantı hatası ({attempt + 1}/{_MAX_RETRIES}): {url}: {e}")
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(delay)
                last_exc = ApiError(f"Bağlantı hatası: {url}")
                continue
            except requests.RequestException as e:
                logger.error(f"Ağ hatası: {url}: {e}")
                raise ApiError(f"Ağ hatası: {url}: {e}")

            if resp.status_code == 429:
                retry_after = float(resp.headers.get('Retry-After', _BASE_DELAY * (2 ** attempt)))
                logger.warning(f"Rate limit (429): {url} — {retry_after:.0f}s bekleniyor")
                time.sleep(retry_after)
                last_exc = RateLimitError(url)
                continue

            if resp.status_code >= 500:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(f"Sunucu hatası ({resp.status_code}, {attempt + 1}/{_MAX_RETRIES}): {url} — {delay}s bekleniyor")
                time.sleep(delay)
                last_exc = ApiError(f"HTTP {resp.status_code}: {url}", status_code=resp.status_code)
                continue

            if resp.status_code >= 400:
                logger.error(f"İstemci hatası ({resp.status_code}): {url}")
                raise ApiError(f"HTTP {resp.status_code}: {url}", status_code=resp.status_code)

            return resp  # başarı

        raise last_exc or ApiError(f"Tüm denemeler başarısız: {url}")

    def _fetch_paginated(self, url: str, params: dict, parser_fn, genre_id=None, timeout: int = 10) -> list:
        """Retry destekli GET + sonuç parse. ApiError/RateLimitError raise edebilir."""
        resp = self._request_with_retry(url, params, timeout)

        results = []
        for item in resp.json().get("results", []):
            if genre_id and genre_id not in item.get("genre_ids", []):
                continue
            parsed = parser_fn(item)
            if parsed.get("image"):
                results.append(parsed)
            if len(results) >= ITEMS_PER_PAGE:
                break
        return results
