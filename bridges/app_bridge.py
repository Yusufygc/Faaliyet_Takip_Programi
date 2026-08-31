# bridges/app_bridge.py
import os
import subprocess
import sys
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtGui import QDesktopServices
from constants import APP_NAME, VERSION


class AppBridge(QObject):
    """Genel uygulama işlevleri, pencere kontrolü ve Toast bildirim köprüsü."""

    toastRequested = Signal(str, str, str)  # type (info, success, warning, error), title, message
    windowStateChanged = Signal(bool)       # isMaximized

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_maximized = False
        self._app_name = APP_NAME
        self._app_version = VERSION

    # --- Property Tanımları ---

    @Property(str, constant=True)
    def appName(self) -> str:
        return self._app_name

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return self._app_version

    @Property(bool, notify=windowStateChanged)
    def isMaximized(self) -> bool:
        return self._is_maximized

    @isMaximized.setter
    def isMaximized(self, val: bool):
        if self._is_maximized != val:
            self._is_maximized = val
            self.windowStateChanged.emit(val)

    # --- Bildirim ve Dosya İşlemleri ---

    @Slot(str, str, str)
    def showToast(self, toast_type: str, title: str, message: str):
        """QML tarafında Toast bildirim balonu göstermek için sinyal yayar."""
        self.toastRequested.emit(toast_type, title, message)

    @Slot(str)
    def openUrl(self, url_str: str):
        """Web tarayıcısında URL açar."""
        if url_str:
            QDesktopServices.openUrl(QUrl(url_str))

    @Slot(str)
    def openFile(self, file_path: str):
        """Sistem varsayılan uygulamasıyla dosya açar (PDF, klasör vb.)."""
        if not file_path or not os.path.exists(file_path):
            self.toastRequested.emit("warning", "Uyarı", f"Dosya bulunamadı: {file_path}")
            return

        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            self.toastRequested.emit("error", "Hata", f"Dosya açılamadı: {e}")
