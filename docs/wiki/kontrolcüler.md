# Kontrolcüler

İş mantığı ve async iş akışı: `controllers/` klasörü.

Bağlantılar: [[index]] | [[log]] | [[mimari_genel_bakis]] | [[veritabani]] | [[modeller]] | [[servisler]]

---

## MainController

`controllers/main_controller.py` — Uygulamanın merkezi iş mantığı sınıfı.

View ile Repository/Service katmanı arasında köprü görevi görür. Tüm DB operasyonları `DbWorker` aracılığıyla asenkron çalıştırılır.

### Bağımlılıklar

```python
self.repository  = ActivityRepository()      # CRUD + istatistik
self.plan_repo   = PlanRepository()          # Plan + Folder
self.type_repo   = TypeRepository()          # Tür yönetimi + settings
self.workers     = set()                     # Aktif worker referansları
```

### Async Çalışma Mekanizması

```python
def _run_async(self, func, callback, *args, **kwargs):
    worker = DbWorker(func, *args, **kwargs)
    worker.finished.connect(callback)
    worker.finished.connect(lambda: self._cleanup_worker(worker))
    self.workers.add(worker)
    worker.start()
```

- `self.workers` set'i worker'ları garbage collection'dan korur
- Callback `None` geçilebilir (fire-and-forget pattern)

### Önemli Metodlar

**Aktivite İşlemleri:**

| Metod | Açıklama |
|-------|----------|
| `get_all_activities(callback, ...)` | Filtrelenmiş liste (async) |
| `add_activity(type_val, name, date_val, comment, rating_val, callback, end_date)` | Validasyon senkron; kayıt async |
| `update_activity(activity_id, ..., callback, original_activity, end_date)` | Değişiklik kontrolü dahil |
| `delete_activity(activity_id, callback)` | Async silme |

**İstatistik & Rapor:**

| Metod | Açıklama |
|-------|----------|
| `get_dashboard_stats(callback, date_prefix, year_only, ignore_dates)` | Stats sayfası |
| `get_comparison_data(callback, date_prefix)` | Compare sayfası |
| `get_trend_data(callback, year, category)` | Trend analizi (aylık sayılar) |
| `get_pdf_data(callback, date_prefix)` | PDF için tam veri |

**Plan & Klasör:**

| Metod | Açıklama |
|-------|----------|
| `add_plan(...)` | `scope='monthly'/'yearly'`, priority, folder_id ile |
| `update_plan_progress(plan_id, progress, status, callback)` | İlerleme güncelle |
| `get_plans(scope, year, month, callback)` | Filtrelenmiş plan listesi |
| `add_folder / update_folder / delete_folder` | Klasör yönetimi |

**API Anahtar Yönetimi:**

```
get_api_keys(callback):
    1. keyring.get_password("FaaliyetTakip", "tmdb_api_key")
    2. Yoksa DB settings'den oku + keyring'e migrate et + DB'yi temizle

save_api_keys(tmdb_key, rawg_key, callback):
    1. keyring.set_password() ile güvenli sakla
    2. DB'deki eski plaintext kopyayı sil
```

---

## RecommendationController

`controllers/recommendation_controller.py` — Cache-first öneri sistemi.

`ApiService`, `RecommendationRepository` ve `DbWorker` kullanır.

### Başlatma

```python
def __init__(self):
    repo = ActivityRepository()
    tmdb_key = repo.get_setting("tmdb_api_key")   # DB'den okur (eski yol)
    rawg_key = repo.get_setting("rawg_api_key")
    self.api_service = ApiService(tmdb_key, rawg_key)
    self.cache_repo = RecommendationRepository()
    self._cleanup_old_cache()   # Süresi dolmuş cache'i arka planda temizle
```

**Not:** `MainController` API anahtarlarını `keyring`'den okurken, `RecommendationController` hâlâ DB `settings` tablosundan okumaktadır. `settings` tablosu keyring migration sonrası temizlendiğinden bu path boş dönebilir — API anahtarlarının çalışmaması durumunda ilk bakılacak yer burasıdır.

### Metodlar

| Metod | Açıklama |
|-------|----------|
| `get_recommendations(callback, category, period, genre, page, is_turkish, force_refresh)` | Cache-first; cache yoksa API → cache'e yaz |
| `get_next_page(callback, category, period, genre, current_page, is_turkish)` | Sayfa +1 ile `get_recommendations` çağırır |
| `get_previous_data(callback, category, period, genre, is_turkish, max_page)` | Cache'deki tüm sayfaları birleştirerek döner |
| `get_random_recommendation(callback, category)` | `ApiService.get_random_recommendation` wrapper |
| `clear_cache()` | Tüm öneri cache'ini temizler |
| `get_genres_for_category(category)` | Kategoriye göre tür listesi |
| `get_genre_value(category, genre_name)` | Tür adı → API değeri (ID veya slug) |
| `get_all_period_names()` | `[(key, name), ...]` sıralı periyot listesi |

---

## DbWorker

`controllers/workers.py` — `QThread` alt sınıfı; DB işlemlerini ana thread dışında çalıştırır.

```python
class DbWorker(QThread):
    finished = pyqtSignal(object)  # Sonucu callback'e iletir

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        result = self.func(*self.args, **self.kwargs)
        self.finished.emit(result)
```

UI donmasını engeller. Callback her zaman `finished` sinyali üzerinden UI thread'inde çalışır.
