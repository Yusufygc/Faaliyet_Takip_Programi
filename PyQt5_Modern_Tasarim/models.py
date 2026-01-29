from dataclasses import dataclass
from typing import Optional

@dataclass
class ActivityFilter:
    """Filtreleme parametrelerini taşıyan sınıf."""
    type_filter: str = "Hepsi"
    search_term: str = ""
    date_filter: str = "" # "YYYY-MM" veya "YYYY"
    page: int = 1
    items_per_page: int = 15


class Activity:
    def __init__(self, id, type, name, date, comment, rating, end_date=None):
        self.id = id
        self.type = type
        self.name = name
        self.date = date
        self.end_date = end_date
        self.comment = comment
        self.rating = rating

    @classmethod
    def from_row(cls, row):
        """Veritabanından gelen bir satırı Activity nesnesine çevirir."""
        # Row sırası repository select sorgusuna göre değişebilir ama genelde:
        # id, type, name, date, comment, rating, end_date
        # Eğer eski bir sorgu ise end_date olmayabilir, güvenli olması için *row kullanıyoruz
        # Ancak repository güncellendiğinde sıra önemli.
        return cls(*row)

    def __str__(self):
        puan = self.rating if self.rating else 'N/A'
        date_str = self.date
        if self.end_date:
            date_str += f" -> {self.end_date}"
        return f"[{date_str}] {self.type.upper()}: {self.name} ({puan}/10)"