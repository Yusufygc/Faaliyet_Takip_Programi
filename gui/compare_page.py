# compare_page.py
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from database import get_connection

class ComparePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Karşılaştırma Sayfası", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Bir Önceki Ay ile Karşılaştır", command=self.compare_last_month).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Bir Önceki Yıl ile Karşılaştır", command=self.compare_last_year).pack(side="left", padx=10)

        self.result_text = ctk.CTkTextbox(self, height=500, width=1100, font=("Consolas", 13))
        self.result_text.pack(padx=15, pady=10, fill="both", expand=True)

    def compare_last_month(self):
        today = datetime.today()
        current_month = today.strftime("%Y-%m")
        last_month_date = today.replace(day=1) - timedelta(days=1)
        last_month = last_month_date.strftime("%Y-%m")
        self.show_comparison(last_month, current_month, "Ay")

    def compare_last_year(self):
        today = datetime.today()
        current_year = today.strftime("%Y")
        last_year = str(int(current_year) - 1)
        self.show_comparison(last_year, current_year, "Yıl")

    def show_comparison(self, earlier_period, current_period, mode):
        self.result_text.delete("1.0", "end")

        conn = get_connection()
        cursor = conn.cursor()

        def fetch_data(period, is_year):
            if is_year:
                cursor.execute("""
                    SELECT type, name, COUNT(*) FROM activities
                    WHERE date LIKE ? GROUP BY type, name
                """, (period + "%",))
            else:
                cursor.execute("""
                    SELECT type, name, COUNT(*) FROM activities
                    WHERE date = ? GROUP BY type, name
                """, (period,))
            return cursor.fetchall()

        is_year = mode == "Yıl"
        data_prev = fetch_data(earlier_period, is_year)
        data_now = fetch_data(current_period, is_year)

        def format_section(title, data):
            lines = [f"{title} ({'Yıl' if is_year else 'Ay'}: {title}):"]
            grouped = {}
            for t, n, c in data:
                grouped.setdefault(t, []).append((n, c))
            for t in grouped:
                lines.append(f"  {t}:")
                for n, c in grouped[t]:
                    lines.append(f"    - {n} ({c})")
            return lines

        self.result_text.insert("end", "\n".join(format_section(earlier_period, data_prev)) + "\n\n")
        self.result_text.insert("end", "\n".join(format_section(current_period, data_now)))

        conn.close()
