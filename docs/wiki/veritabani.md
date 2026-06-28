# Veritabanı

SQLite tabanlı yerel depolama; repository pattern ile erişim; otomatik şema migrasyonu.

Bağlantılar: [[index]] | [[log]] | [[mimari_genel_bakis]] | [[modeller]] | [[kontrolcüler]]

---

## Tablolar

### `activities`
```sql
CREATE TABLE IF NOT EXISTS activities (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    type     TEXT NOT NULL,     -- 'Dizi', 'Film', 'Kitap', 'Oyun', 'Kurs', 'Şehir' veya özel
    name     TEXT NOT NULL,
    date     TEXT NOT NULL,     -- başlangıç tarihi (YYYY-MM-DD veya YYYY-MM)
    comment  TEXT,
    rating   INTEGER,           -- 1-10 arası (0 = puansız)
    end_date TEXT               -- bitiş tarihi (diziler için, nullable) — migration ile eklendi
)
```

İndeksler:
- `idx_activities_date` ON `activities(date)`
- `idx_activities_type` ON `activities(type)`

### `plans`
```sql
CREATE TABLE IF NOT EXISTS plans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    scope       TEXT,   -- 'monthly' | 'yearly'
    year        INTEGER,
    month       INTEGER,         -- yearly için NULL
    status      TEXT,   -- 'planned' | 'in_progress' | 'completed' | 'archived'
    progress    INTEGER,         -- 0-100
    priority    TEXT,   -- 'low' | 'medium' | 'high'
    created_at  TEXT,
    folder_id   INTEGER REFERENCES folders(id) ON DELETE SET NULL  -- migration ile eklendi
)
```

### `folders`
```sql
CREATE TABLE IF NOT EXISTS folders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    created_at TEXT
)
```

### `recommendation_cache`
Öneri API sonuçları 7 gün TTL ile saklanır. Detay: [[servisler]]

### `activity_types`
Dinamik faaliyet türleri. Başlangıç türleri: `constants.py::FAALIYET_TURLERI`.

### `settings`
Anahtar-değer çifti deposu. API key migration için kullanılmış, artık temizlenmiş durumdadır.

---

## Repository Sınıfları

| Sınıf | Dosya | Sorumluluk |
|-------|-------|------------|
| `ActivityRepository` | `database/repository.py` | CRUD, filtreleme, istatistik, trend, PDF verisi |
| `PlanRepository` | `database/plan_repository.py` | Plan + Folder CRUD |
| `TypeRepository` | `database/type_repository.py` | Tür yönetimi + settings get/set |
| `RecommendationRepository` | `database/recommendation_repository.py` | Öneri önbelleği |

---

## Önemli Metodlar (ActivityRepository)

| Metod | Açıklama |
|-------|----------|
| `get_all_filtered(filter_obj)` | Sayfalama + filtre ile liste çeker |
| `get_stats_by_type(date_prefix, year_only, ignore_dates)` | Stats sayfası için (type, count, avg_rating) |
| `get_comparison_data(date_prefix)` | Compare sayfası için (type, name) |
| `get_monthly_activity_counts(year, category)` | Trend analizi için (ay, sayı) |
| `get_detailed_data_for_pdf(date_prefix)` | PDF için tam kayıt listesi |
| `check_and_migrate_schema()` | `end_date` ve `folder_id` migration'ları otomatik yapılır |

---

## Şema Migration Stratejisi

`ActivityRepository.__init__()` her çalışmada `check_and_migrate_schema()` çağırır:
- `activities.end_date` kolonu yoksa `ALTER TABLE` ile ekler
- `plans.folder_id` kolonu yoksa ekler
- Eksik indeksler oluşturulur

Yeni migration gerektiğinde bu metoda eklenir; mevcut veri korunur.

---

## Bağlantı Yönetimi

`database/connection.py`:
- `get_connection()` → `sqlite3.connect(DB_PATH)` + `row_factory = sqlite3.Row`
- Her metod kendi bağlantısını açar, `finally` bloğunda kapatır
- `Row` factory sayesinde kolonlara isimle erişilir (`row['type']`)
