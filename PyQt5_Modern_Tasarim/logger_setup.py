# logger_setup.py
import logging
import sys
import os

# Log formatı
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logger():
    """Logger yapılandırmasını oluşturur ve döndürür."""
    logger = logging.getLogger("FaaliyetTakip")
    logger.setLevel(logging.DEBUG)

    # Console Handler (Terminal çıktısı)
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.DEBUG)
    c_formatter = logging.Formatter(LOG_FORMAT)
    c_handler.setFormatter(c_formatter)
    logger.addHandler(c_handler)

    return logger

# Global logger nesnesi
logger = setup_logger()
