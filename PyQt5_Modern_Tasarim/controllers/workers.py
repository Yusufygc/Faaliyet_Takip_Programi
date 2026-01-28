# controllers/workers.py
from PyQt5.QtCore import QThread, pyqtSignal
from logger_setup import logger

class DbWorker(QThread):
    """
    Veritabanı işlemlerini arka planda (ayrı bir thread'de) çalıştırmak için kullanılır.
    Arayüzün donmasını engeller.
    """
    # İşlem bittiğinde sonucu taşıyan sinyal
    finished = pyqtSignal(object)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Fonksiyonu çalıştır
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Worker hatası: {e}")
            # Hata durumunda None veya özel bir hata objesi dönebiliriz
            self.finished.emit(None)
