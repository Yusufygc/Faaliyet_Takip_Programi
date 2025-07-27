from datetime import datetime
from collections import Counter

def sayim_yap_kategorilere_gore(rows):
    """
    Gelen kayıtlar arasında 'type' alanına göre sayım yapar.
    """
    turler = [row[1] for row in rows]  # index 1 = type
    return Counter(turler)

def is_valid_yyyymm(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m")
        return True
    except ValueError:
        return False

def is_valid_yyyy(date_str):
    try:
        datetime.strptime(date_str, "%Y")
        return True
    except ValueError:
        return False

def extract_year_month(date_str):
    if is_valid_yyyymm(date_str):
        dt = datetime.strptime(date_str, "%Y-%m")
        return dt.year, dt.month
    elif is_valid_yyyy(date_str):
        return int(date_str), None
    return None, None