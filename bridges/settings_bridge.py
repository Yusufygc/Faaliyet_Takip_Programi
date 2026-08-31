# bridges/settings_bridge.py
import keyring
from PySide6.QtCore import QObject, Signal, Slot, Property
from database.type_repository import TypeRepository
from logger_setup import logger

SERVICE_NAME = "FaaliyetTakip"


class SettingsBridge(QObject):
    """Ayarlar, Tür Yönetimi ve Keyring API Anahtarları Köprüsü."""

    typesChanged = Signal()
    apiKeysLoaded = Signal()
    notification = Signal(str, str, str)  # type, title, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._type_repo = TypeRepository()
        self._types = []

        self._tmdb_key = ""
        self._rawg_key = ""
        self._google_books_key = ""

        self.loadTypes()
        self.loadApiKeys()

    # --- Property Tanımları ---

    @Property(list, notify=typesChanged)
    def typesList(self) -> list:
        return self._types

    @Property(str, notify=apiKeysLoaded)
    def tmdbKey(self) -> str:
        return self._tmdb_key

    @Property(str, notify=apiKeysLoaded)
    def rawgKey(self) -> str:
        return self._rawg_key

    @Property(str, notify=apiKeysLoaded)
    def googleBooksKey(self) -> str:
        return self._google_books_key

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

    @Slot(str, str, result=bool)
    def renameType(self, old_name: str, new_name: str) -> bool:
        """Faaliyet türünü yeniden adlandırır."""
        new_name = (new_name or "").strip()
        if not new_name:
            self.notification.emit("warning", "Uyarı", "Yeni tür adı boş olamaz.")
            return False

        success, msg = self._type_repo.rename_type(old_name, new_name)
        if success:
            self.notification.emit("success", "Başarılı", f"Tür güncellendi: '{old_name}' -> '{new_name}'")
            self.loadTypes()
            return True
        else:
            self.notification.emit("error", "Hata", msg)
            return False

    # --- API Anahtarları (Keyring) Slotları ---

    @Slot()
    def loadApiKeys(self):
        """OS Keyring'den API anahtarlarını okur."""
        try:
            self._tmdb_key = keyring.get_password(SERVICE_NAME, "tmdb_api_key") or ""
            self._rawg_key = keyring.get_password(SERVICE_NAME, "rawg_api_key") or ""
            self._google_books_key = keyring.get_password(SERVICE_NAME, "google_books_api_key") or ""
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
                self._tmdb_key = key_val
            elif key_name == "rawg":
                keyring.set_password(SERVICE_NAME, "rawg_api_key", key_val)
                self._rawg_key = key_val
            elif key_name == "google_books":
                keyring.set_password(SERVICE_NAME, "google_books_api_key", key_val)
                self._google_books_key = key_val
            else:
                return False

            self.apiKeysLoaded.emit()
            self.notification.emit("success", "Kaydedildi", f"{key_name.upper()} API anahtarı güvenli şekilde saklandı.")
            return True
        except Exception as e:
            logger.error(f"SettingsBridge saveApiKey error: {e}")
            self.notification.emit("error", "Hata", f"API anahtarı kaydedilemedi: {e}")
            return False
