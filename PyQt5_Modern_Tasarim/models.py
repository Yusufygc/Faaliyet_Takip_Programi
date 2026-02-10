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

@dataclass
class Folder:
    """Proje/Klasör Modeli."""
    id: int
    name: str
    created_at: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)

@dataclass
class Plan:
    """Yıllık ve Aylık Plan/Hedef Modeli."""
    id: int
    title: str
    description: str
    scope: str # 'monthly' | 'yearly'
    year: int
    month: Optional[int] # yearly için None
    status: str # 'planned', 'in_progress', 'completed', 'archived'
    progress: int # 0-100
    priority: str # 'low', 'medium', 'high'
    created_at: str
    folder_id: Optional[int] = None # Proje/Klasör ID'si

    @classmethod
    def from_row(cls, row):
        """Veritabanı satırından Plan oluşturur."""
        return cls(*row)
