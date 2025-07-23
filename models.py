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
        return cls(*row)

    def __str__(self):
        return f"[{self.date}] {self.type.upper()}: {self.name} ({self.rating}/10)"
