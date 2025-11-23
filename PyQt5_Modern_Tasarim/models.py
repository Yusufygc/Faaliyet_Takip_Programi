# models.py

class Activity:
    def __init__(self, id, type, name, date, comment, rating):
        self.id = id
        self.type = type
        self.name = name
        self.date = date
        self.comment = comment
        self.rating = rating

    @classmethod
    def from_row(cls, row):
        """Veritabanından gelen bir satırı Activity nesnesine çevirir."""
        return cls(*row)

    def __str__(self):
        puan = self.rating if self.rating else 'N/A'
        return f"[{self.date}] {self.type.upper()}: {self.name} ({puan}/10)"