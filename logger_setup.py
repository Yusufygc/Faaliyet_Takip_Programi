# logger_setup.py
import logging
import logging.handlers
import sys
import os

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_LOG_BACKUP_COUNT = 3


def _get_log_file_path():
    from constants import DATA_DIR_NAME, LOG_FILENAME
    if sys.platform == "win32":
        base = os.environ.get('LOCALAPPDATA') or os.path.expanduser("~")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
    log_dir = os.path.join(base, DATA_DIR_NAME)
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, LOG_FILENAME)


def setup_logger():
    """Logger yapılandırmasını oluşturur ve döndürür."""
    from constants import APP_NAME
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    # Console Handler — INFO ve üzeri (DEBUG iç detayları kullanıcıya gösterme)
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(c_handler)

    # Dosya Handler — RotatingFileHandler: 5 MB × 3 backup
    try:
        f_handler = logging.handlers.RotatingFileHandler(
            _get_log_file_path(),
            maxBytes=_LOG_MAX_BYTES,
            backupCount=_LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        f_handler.setLevel(logging.INFO)
        f_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(f_handler)
    except Exception as e:
        print(f"[logger_setup] Dosya handler oluşturulamadı: {e}", file=sys.stderr)

    return logger

# Global logger nesnesi
logger = setup_logger()
