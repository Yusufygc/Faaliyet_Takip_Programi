from datetime import datetime

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