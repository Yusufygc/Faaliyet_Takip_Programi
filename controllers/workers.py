# controllers/workers.py
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from logger_setup import logger
from exceptions import DatabaseError, ApiError, RateLimitError

_DEFAULT_TIMEOUT_MS = 12_000  # 12 saniye — image 8s + semaphore 8s bekleme içerir


class DbWorker(QThread):
    """Arka plan görevi çalıştırıcı. Timeout ve iptal desteği içerir."""

    finished = pyqtSignal(object)
    timed_out = pyqtSignal()

    def __init__(self, func, *args, timeout_ms=None, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._timeout_ms = timeout_ms if timeout_ms is not None else _DEFAULT_TIMEOUT_MS
        self._cancelled = False
        self._timer = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Worker'ı başlatır; timeout > 0 ise ana thread'de QTimer kurar."""
        if self._timeout_ms > 0:
            self._timer = QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._on_timeout)
            # finished sinyal gelince timer dursun (queued connection, thread-safe)
            self.finished.connect(self._timer.stop)
            self._timer.start(self._timeout_ms)
        super().start()

    def cancel(self):
        """İptal işareti koy. Devam eden bloklayıcı işlem kesilmez,
        ancak sonuç finished sinyaliyle yayınlanmaz."""
        self._cancelled = True
        if self._timer:
            self._timer.stop()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_timeout(self):
        self._cancelled = True
        func_name = getattr(self.func, '__name__', repr(self.func))
        logger.warning(f"Worker timeout ({self._timeout_ms}ms): {func_name}")
        self.timed_out.emit()

    def run(self):
        if self._cancelled:
            return
        try:
            result = self.func(*self.args, **self.kwargs)
            if not self._cancelled:
                self.finished.emit(result)
        except RateLimitError as e:
            if not self._cancelled:
                logger.warning(f"Worker rate limit: {e}")
                self.finished.emit(None)
        except ApiError as e:
            if not self._cancelled:
                logger.error(f"Worker API hatası [{e.status_code}]: {e}")
                self.finished.emit(None)
        except DatabaseError as e:
            if not self._cancelled:
                logger.error(f"Worker veritabanı hatası: {e}")
                self.finished.emit(None)
        except Exception as e:
            if not self._cancelled:
                logger.error(f"Worker beklenmeyen hata [{type(e).__name__}]: {e}")
                self.finished.emit(None)
