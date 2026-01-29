
from dataclasses import dataclass
from typing import Optional

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

    @classmethod
    def from_row(cls, row):
        """Veritabanı satırından Plan oluşturur."""
        return cls(*row)
