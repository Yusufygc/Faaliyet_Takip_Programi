# Modeller

`models.py` içindeki veri sınıfları: Activity, Plan, Folder, ActivityFilter.

Bağlantılar: [[index]] | [[log]] | [[veritabani]] | [[kontrolcüler]] | [[mimari_genel_bakis]]

---

## Activity

Normal sınıf (dataclass değil), `from_row()` classmethod'u ile DB satırından oluşturulur.

```python
class Activity:
    id: int | None      # None ise yeni kayıt (DB tarafından atanır)
    type: str           # 'Dizi', 'Film', 'Kitap', 'Oyun', 'Kurs', 'Şehir' veya özel
    name: str           # Zorunlu
    date: str           # Başlangıç tarihi: YYYY-MM-DD veya YYYY-MM
    end_date: str|None  # Bitiş tarihi, nullable (dizi takibi için)
    comment: str        # Yorum metni
    rating: int         # 1-10 arası; 0 = puansız
```

**Not:** `end_date` DB'ye `ALTER TABLE` migration ile eklendi (mevcut kayıtlarda NULL).

---

## ActivityFilter

`@dataclass` — Filtreleme parametrelerini taşır, `repository.get_all_filtered()` 'a geçilir.

```python
@dataclass
class ActivityFilter:
    type_filter: str = "Hepsi"      # 'Hepsi' veya tür adı (case-insensitive)
    search_term: str = ""           # name LIKE %term%
    date_filter: str = ""           # 'YYYY-MM' veya 'YYYY'
    page: int = 1                   # 1-based
    items_per_page: int = 15
```

---

## Plan

`@dataclass` — Aylık veya yıllık hedef/plan.

```python
@dataclass
class Plan:
    id: int
    title: str
    description: str
    scope: str          # 'monthly' | 'yearly'
    year: int
    month: int | None   # yearly için None
    status: str         # 'planned' | 'in_progress' | 'completed' | 'archived'
    progress: int       # 0-100
    priority: str       # 'low' | 'medium' | 'high'
    created_at: str     # 'YYYY-MM-DD HH:MM:SS'
    folder_id: int|None # Klasör atanmamışsa None
```

---

## Folder

`@dataclass` — Plan klasörü/projesi.

```python
@dataclass
class Folder:
    id: int
    name: str
    created_at: str
```

---

## Sabitler (constants.py)

```python
FAALIYET_TURLERI = ["Dizi", "Film", "Kitap", "Oyun", "Kurs", "Şehir"]
LIST_PAGE_FILTRE_SECENEKLERI = ["Hepsi"] + FAALIYET_TURLERI
COMPARE_PAGE_DATA_ORDER = ["DIZI", "FILM", "KITAP", "KURS", "OYUN", "ŞEHIR"]
APP_NAME = "FaaliyetTakip"
DB_FILENAME = "faaliyetler.db"
```

Özel türler kullanıcı tarafından `settings_page` üzerinden eklenir; `activity_types` tablosunda saklanır.
