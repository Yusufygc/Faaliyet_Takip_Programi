# views/widgets/async_image.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QSemaphore
from PyQt5.QtGui import QPixmap, QImage
import requests
from controllers.workers import DbWorker

# Aynı anda en fazla 5 image thread → sunucu satürasyonu + thread yarışması önlenir.
_IMAGE_SEMAPHORE = QSemaphore(5)


class AsyncImage(QLabel):
    """URL'den resim yükleyen QLabel. Global semaphore ile eşzamanlılık sınırlı."""

    def __init__(self, url, width=100, height=150):
        super().__init__()
        self._workers = []
        self.setFixedSize(width, height)
        self.setStyleSheet("background-color: #333; border-radius: 8px;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("...")
        self.url = url
        if url:
            self.load_image()

    def load_image(self):
        # fetch_image timeout: 12s (worker global 12s ile hizalı; iç requests 8s)
        worker = DbWorker(self.fetch_image, timeout_ms=12_000)
        worker.finished.connect(self.set_image)
        worker.finished.connect(lambda: self._workers.remove(worker) if worker in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def fetch_image(self):
        # Slot bekle (max 8s); alamazsak hemen None döndür, thread birikmez.
        acquired = _IMAGE_SEMAPHORE.tryAcquire(1, 8_000)
        if not acquired:
            return None
        try:
            response = requests.get(self.url, stream=True, timeout=8)
            if response.status_code == 200:
                img = QImage()
                img.loadFromData(response.content)
                return img
        except Exception:
            return None
        finally:
            _IMAGE_SEMAPHORE.release()
        return None

    def set_image(self, image):
        if image and not image.isNull():
            self.setPixmap(QPixmap.fromImage(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))
            self.setText("")
        else:
            from services.icon_service import IconService
            self.setPixmap(IconService.pixmap("image", 48))
