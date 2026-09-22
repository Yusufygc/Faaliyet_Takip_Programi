# bridges/settings_bridge.py
import keyring
from PySide6.QtCore import QObject, Signal, Slot, Property, QSettings
from database.type_repository import TypeRepository
from logger_setup import logger

SERVICE_NAME = "FaaliyetTakip"


class SettingsBridge(QObject):
    """Ayarlar, Tür Yönetimi, Keyring API Anahtarları ve Tema Köprüsü."""

    typesChanged = Signal()
    apiKeysLoaded = Signal()
    themeChanged = Signal()
    notification = Signal(str, str, str)  # type, title, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._type_repo = TypeRepository()
        self._types = []

        self._has_tmdb_key = False
        self._has_rawg_key = False
        self._has_google_books_key = False

        self._settings = QSettings()
        self._is_dark_theme = self._settings.value("appearance/isDarkTheme", True, type=bool)

        self.loadTypes()
        self.loadApiKeys()

    # --- Property Tanımları ---

    @Property(list, notify=typesChanged)
    def typesList(self) -> list:
        return self._types

    @Property(bool, notify=apiKeysLoaded)
    def hasTmdbKey(self) -> bool:
        return self._has_tmdb_key

    @Property(bool, notify=apiKeysLoaded)
    def hasRawgKey(self) -> bool:
        return self._has_rawg_key

    @Property(bool, notify=apiKeysLoaded)
    def hasGoogleBooksKey(self) -> bool:
        return self._has_google_books_key

    @Property(bool, notify=themeChanged)
    def isDarkTheme(self) -> bool:
        return self._is_dark_theme

    # --- Tema Slotları ---

    @Slot()
    def toggleTheme(self):
        """Açık/Koyu tema arasında geçiş yapar."""
        self.setTheme(not self._is_dark_theme)

    @Slot(bool)
    def setTheme(self, is_dark: bool):
        """Tema modunu ayarlar ve kalıcı olarak saklar."""
        if is_dark == self._is_dark_theme:
            return
        self._is_dark_theme = is_dark
        self._settings.setValue("appearance/isDarkTheme", is_dark)
        self.themeChanged.emit()

    # --- Tür Yönetimi Slotları ---

    @Slot()
    def loadTypes(self):
        """Tüm faaliyet türlerini veritabanından çeker."""
        try:
            self._types = self._type_repo.get_all_types()
            self.typesChanged.emit()
        except Exception as e:
            logger.error(f"SettingsBridge loadTypes error: {e}")

    @Slot(str, result=bool)
    def addType(self, type_name: str) -> bool:
        """Yeni faaliyet türü ekler."""
        name = (type_name or "").strip()
        if not name:
            self.notification.emit("warning", "Uyarı", "Tür adı boş olamaz.")
            return False

        success, msg = self._type_repo.add_type(name)
        if success:
            self.notification.emit("success", "Başarılı", f"'{name}' türü eklendi.")
            self.loadTypes()
            return True
        else:
            self.notification.emit("error", "Hata", msg)
            return False

    @Slot(str, result=bool)
    def deleteType(self, type_name: str) -> bool:
        """Faaliyet türünü siler."""
        success, msg = self._type_repo.delete_type(type_name)
        if success:
            self.notification.emit("success", "Başarılı", f"'{type_name}' türü silindi.")
            self.loadTypes()
            return True
        else:
            self.notification.emit("error", "Hata", msg)
            return False

    # --- API Anahtarları (Keyring) Slotları ---

    @Slot()
    def loadApiKeys(self):
        """OS Keyring'de bir anahtarın kayıtlı olup olmadığını kontrol eder.

        Not: Anahtarların düz metin değeri hiçbir zaman QML katmanına
        aktarılmaz — arayüzde yalnızca "kayıtlı mı" bilgisi gösterilir.
        Gerçek değerler API çağrıları sırasında servisler tarafından
        doğrudan keyring'den okunur (bkz. services/_base_api_service.py)."""
        try:
            self._has_tmdb_key = bool(keyring.get_password(SERVICE_NAME, "tmdb_api_key"))
            self._has_rawg_key = bool(keyring.get_password(SERVICE_NAME, "rawg_api_key"))
            self._has_google_books_key = bool(keyring.get_password(SERVICE_NAME, "google_books_api_key"))
            self.apiKeysLoaded.emit()
        except Exception as e:
            logger.error(f"SettingsBridge loadApiKeys error: {e}")

    @Slot(str, str, result=bool)
    def saveApiKey(self, key_name: str, key_val: str) -> bool:
        """Belirtilen API anahtarını Keyring'e güvenli kaydeder."""
        key_val = (key_val or "").strip()
        try:
            if key_name == "tmdb":
                keyring.set_password(SERVICE_NAME, "tmdb_api_key", key_val)
                self._has_tmdb_key = bool(key_val)
            elif key_name == "rawg":
                keyring.set_password(SERVICE_NAME, "rawg_api_key", key_val)
                self._has_rawg_key = bool(key_val)
            elif key_name == "google_books":
                keyring.set_password(SERVICE_NAME, "google_books_api_key", key_val)
                self._has_google_books_key = bool(key_val)
            else:
                return False

            self.apiKeysLoaded.emit()
            self.notification.emit("success", "Kaydedildi", f"{key_name.upper()} API anahtarı güvenli şekilde saklandı.")
            return True
        except Exception as e:
            logger.error(f"SettingsBridge saveApiKey error: {e}")
            self.notification.emit("error", "Hata", f"API anahtarı kaydedilemedi: {e}")
            return False
