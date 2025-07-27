# widgets.py
import customtkinter as ctk
from datetime import datetime


def build_month_year_picker(parent):
    """Yıl ve ay seçimi için özel bir picker."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    now = datetime.now()
    years = [str(y) for y in range(now.year - 10, now.year + 1)]
    months = [f"{m:02d}" for m in range(1, 13)]

    year_var = ctk.StringVar(value=str(now.year))
    month_var = ctk.StringVar(value=f"{now.month:02d}")

    year_menu = ctk.CTkOptionMenu(frame, variable=year_var, values=years)
    month_menu = ctk.CTkOptionMenu(frame, variable=month_var, values=months)

    year_menu.grid(row=0, column=0, padx=5)
    month_menu.grid(row=0, column=1, padx=5)

    frame.year_var = year_var
    frame.month_var = month_var
    return frame


def get_formatted_date_from_picker(picker_frame):
    """build_month_year_picker ile oluşturulmuş picker'dan YYYY-MM formatında tarih döndürür."""
    year = picker_frame.year_var.get()
    month = picker_frame.month_var.get()
    return f"{year}-{month}"
