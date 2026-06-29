# controllers/settings_controller.py
from controllers._base_controller import _BaseController
from logger_setup import logger
from constants import KEYRING_APP_NAME, KEYRING_KEY_TMDB, KEYRING_KEY_RAWG, KEYRING_KEY_GOOGLE_BOOKS


class SettingsController(_BaseController):
    def __init__(self, type_repo):
        super().__init__()
        self.type_repo = type_repo

    def get_api_keys(self, callback):
        def op():
            import keyring
            tmdb = keyring.get_password(KEYRING_APP_NAME, KEYRING_KEY_TMDB)
            rawg = keyring.get_password(KEYRING_APP_NAME, KEYRING_KEY_RAWG)
            gbooks = keyring.get_password(KEYRING_APP_NAME, KEYRING_KEY_GOOGLE_BOOKS)
            if tmdb is None:
                tmdb = self.type_repo.get_setting(KEYRING_KEY_TMDB) or ""
                if tmdb:
                    keyring.set_password(KEYRING_APP_NAME, KEYRING_KEY_TMDB, tmdb)
                    self.type_repo.set_setting(KEYRING_KEY_TMDB, "")
            if rawg is None:
                rawg = self.type_repo.get_setting(KEYRING_KEY_RAWG) or ""
                if rawg:
                    keyring.set_password(KEYRING_APP_NAME, KEYRING_KEY_RAWG, rawg)
                    self.type_repo.set_setting(KEYRING_KEY_RAWG, "")
            return {
                KEYRING_KEY_TMDB: tmdb or "",
                KEYRING_KEY_RAWG: rawg or "",
                KEYRING_KEY_GOOGLE_BOOKS: gbooks or "",
            }
        self._run_async(op, callback)

    def save_api_keys(self, tmdb_key, rawg_key, google_books_key, callback):
        def op():
            try:
                import keyring
                keyring.set_password(KEYRING_APP_NAME, KEYRING_KEY_TMDB, tmdb_key.strip())
                keyring.set_password(KEYRING_APP_NAME, KEYRING_KEY_RAWG, rawg_key.strip())
                keyring.set_password(KEYRING_APP_NAME, KEYRING_KEY_GOOGLE_BOOKS, google_books_key.strip())
                self.type_repo.set_setting(KEYRING_KEY_TMDB, "")
                self.type_repo.set_setting(KEYRING_KEY_RAWG, "")
                return True, "API anahtarları başarıyla kaydedildi."
            except Exception as e:
                logger.error(f"API key kayıt hatası: {e}")
                return False, "Kayıt sırasında hata oluştu."
        self._run_async(op, callback)
