# logger_setup.py
import logging
import sys
import os

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


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
    logger = logging.getLogger("FaaliyetTakip")
    logger.setLevel(logging.DEBUG)

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(c_handler)

    # Dosya Handler — INFO+ AppData/FaaliyetTakip/app.log
    try:
        f_handler = logging.FileHandler(_get_log_file_path(), encoding="utf-8")
        f_handler.setLevel(logging.INFO)
        f_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(f_handler)
    except Exception:
        pass

    return logger

# Global logger nesnesi
logger = setup_logger()
