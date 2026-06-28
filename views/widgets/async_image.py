# views/widgets/async_image.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import requests
from controllers.workers import DbWorker


class AsyncImage(QLabel):
    """URL'den resim yükleyen QLabel."""

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
        worker = DbWorker(self.fetch_image)
        worker.finished.connect(self.set_image)
        worker.finished.connect(lambda: self._workers.remove(worker) if worker in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def fetch_image(self):
        try:
            response = requests.get(self.url, stream=True, timeout=10)
            if response.status_code == 200:
                img = QImage()
                img.loadFromData(response.content)
                return img
        except Exception:
            return None
        return None

    def set_image(self, image):
        if image and not image.isNull():
            self.setPixmap(QPixmap.fromImage(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))
            self.setText("")
        else:
            self.setText("📷")
