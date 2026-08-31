# services/cover_fetch_service.py
from __future__ import annotations

import requests
from PyQt5.QtCore import QTimer

from controllers.workers import DbWorker
from constants import KEYRING_KEY_TMDB, KEYRING_KEY_RAWG, KEYRING_KEY_GOOGLE_BOOKS
from logger_setup import logger

_TMDB_BASE   = "https://api.themoviedb.org/3"
_RAWG_BASE   = "https://api.rawg.io/api"
_GBOOKS_URL  = "https://www.googleapis.com/books/v1/volumes"
_TIMEOUT     = 8  # seconds per request


def _get_key(name: str) -> str:
    try:
        import keyring
        from constants import KEYRING_APP_NAME
        return keyring.get_password(KEYRING_APP_NAME, name) or ""
    except Exception:
        return ""


class CoverFetchService:
    """Aktivite adı + türüne göre kapak görseli URL'si arar.

    In-memory session cache ile tekrar eden aramalar engellenir.
    Ağ çağrısı DbWorker (QThread) üzerinden asenkron yapılır.
    """

    _cache: dict[tuple[str, str], str | None] = {}
    _active_workers: set[DbWorker] = set()

    @classmethod
    def get_cover_async(cls, name: str, activity_type: str, callback) -> None:
        """Kapak URL'sini asenkron getirir. callback(url_or_None) döner."""
        key = (name.strip().lower(), activity_type)

        if key in cls._cache:
            QTimer.singleShot(0, lambda: callback(cls._cache[key]))
            return

        worker = DbWorker(cls._search_cover, name, activity_type, timeout_ms=10_000)

        def _on_done(url):
            cls._cache[key] = url
            cls._active_workers.discard(worker)
            callback(url)

        worker.finished.connect(_on_done)
        worker.timed_out.connect(lambda: cls._active_workers.discard(worker))
        cls._active_workers.add(worker)
        worker.start()

    @classmethod
    def _search_cover(cls, name: str, activity_type: str) -> str | None:
        try:
            if activity_type in ("Film",):
                return cls._tmdb_movie(name)
            elif activity_type in ("Dizi",):
                return cls._tmdb_tv(name)
            elif activity_type in ("Oyun",):
                return cls._rawg(name)
            elif activity_type in ("Kitap",):
                return cls._google_books(name)
        except Exception as e:
            logger.debug(f"CoverFetchService._search_cover hata [{activity_type}] {name!r}: {e}")
        return None

    # ── TMDB ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _tmdb_movie(name: str) -> str | None:
        key = _get_key(KEYRING_KEY_TMDB)
        if not key:
            return None
        resp = requests.get(
            f"{_TMDB_BASE}/search/movie",
            params={"api_key": key, "query": name, "language": "tr-TR", "page": 1},
            timeout=_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        results = resp.json().get("results", [])
        for item in results:
            path = item.get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w300{path}"
        return None

    @staticmethod
    def _tmdb_tv(name: str) -> str | None:
        key = _get_key(KEYRING_KEY_TMDB)
        if not key:
            return None
        resp = requests.get(
            f"{_TMDB_BASE}/search/tv",
            params={"api_key": key, "query": name, "language": "tr-TR", "page": 1},
            timeout=_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        results = resp.json().get("results", [])
        for item in results:
            path = item.get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w300{path}"
        return None

    # ── RAWG ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _rawg(name: str) -> str | None:
        key = _get_key(KEYRING_KEY_RAWG)
        params: dict = {"search": name, "page_size": 5}
        if key:
            params["key"] = key
        resp = requests.get(f"{_RAWG_BASE}/games", params=params, timeout=_TIMEOUT)
        if resp.status_code != 200:
            return None
        for item in resp.json().get("results", []):
            img = item.get("background_image")
            if img:
                return img
        return None

    # ── Google Books ───────────────────────────────────────────────────────────

    @staticmethod
    def _google_books(name: str) -> str | None:
        key = _get_key(KEYRING_KEY_GOOGLE_BOOKS)
        params: dict = {"q": name, "maxResults": 5, "printType": "books"}
        if key:
            params["key"] = key
        resp = requests.get(_GBOOKS_URL, params=params, timeout=_TIMEOUT)
        if resp.status_code != 200:
            return None
        for item in resp.json().get("items", []):
            links = item.get("volumeInfo", {}).get("imageLinks", {})
            url = links.get("thumbnail") or links.get("smallThumbnail")
            if url:
                return url.replace("http://", "https://")
        return None
