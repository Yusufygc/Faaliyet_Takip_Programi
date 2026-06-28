# controllers/_base_controller.py
from controllers.workers import DbWorker


class _BaseController:
    def __init__(self):
        self.workers = set()

    def _run_async(self, func, callback, *args, timeout_ms=None, **kwargs):
        worker = DbWorker(func, *args, timeout_ms=timeout_ms, **kwargs)
        if callback:
            worker.finished.connect(callback)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.timed_out.connect(lambda: self._cleanup_worker(worker))
        self.workers.add(worker)
        worker.start()

    def _cleanup_worker(self, worker):
        self.workers.discard(worker)

    def cancel_all(self):
        """Tüm aktif worker'ları iptal eder. Sayfa değişimi veya kapatma sırasında çağrılır."""
        for worker in list(self.workers):
            worker.cancel()
        self.workers.clear()
