# CLAUDE.md — Faaliyet Takip Programı

## Wiki — Önce Oku

Her sohbet başında `docs/wiki/index.md` okunur. Proje bağlamı, mimari kararlar ve geçmiş değişiklikler burada birikir. Detaylı operasyon kuralları için `docs/wiki/Rules.md`.

---

## Proje Tanımı

Kişisel aktivite (film, dizi, oyun, kitap, kurs, şehir) takip masaüstü uygulaması. PyQt5 GUI, SQLite yerel veritabanı, harici API'lerden içerik önerisi.

**Giriş noktası:** `main.py`

---

## Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| Dil | Python 3.8+ |
| GUI | PyQt5 5.15.11 |
| Veritabanı | SQLite 3 (stdlib) |
| Grafik | Matplotlib 3.10.8 |
| PDF | ReportLab 4.4.9 |
| HTTP | Requests 2.32.5 |
| Credential | keyring ≥25.0.0 |

---

## Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```

**Kurulum (Windows):**
```bash
setup.bat
```

**DB konumu:** `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db`

---

## Mimari Özeti

```
View (views/)  →  Controller (controllers/)  →  Repository (database/)
                         ↕
                   Service (services/)   ←→   Harici API'ler
```

Tüm DB işlemleri `DbWorker` (QThread) ile asenkron çalışır. Senkron validasyon yapıldıktan sonra `_run_async(func, callback)` ile işlem arka plana atılır.

Detay: `docs/wiki/mimari_genel_bakis.md`

---

## Kritik Dosyalar

| Dosya | Rol |
|-------|-----|
| `controllers/main_controller.py` | Merkezi iş mantığı — tüm View→DB operasyonları |
| `database/repository.py` | `ActivityRepository` — CRUD + istatistik sorguları |
| `database/connection.py` | DB path ve bağlantı yönetimi |
| `models.py` | `Activity`, `Plan`, `Folder`, `ActivityFilter` |
| `constants.py` | `FAALIYET_TURLERI`, `APP_NAME`, `DB_FILENAME` |
| `services/api_service.py` | TMDB, RAWG, Google Books API çağrıları |
| `views/main_window.py` | Ana pencere + `QStackedWidget` navigasyonu |

---

## Geliştirme Notları

### Yeni sayfa eklemek
1. `views/pages/` altında yeni dosya oluştur
2. `views/main_window.py` içinde `stack`'e ekle
3. `docs/wiki/ui_katmani.md` güncelle

### Yeni DB kolonu eklemek
`database/repository.py::ActivityRepository.check_and_migrate_schema()` içine `ALTER TABLE` ekle. Tablo şeması: `docs/wiki/veritabani.md`

### API anahtarları
`keyring` üzerinden saklanır (`.env` kullanılmaz):
- Okuma: `keyring.get_password("FaaliyetTakip", "tmdb_api_key")`
- Yazma: `SettingsPage` → `MainController.save_api_keys()`
- **Uyarı:** `RecommendationController` eski DB tabanlı yolu kullanıyor; keys boş gelebilir. Detay: `docs/wiki/kontrolcüler.md`

### Faaliyet türleri
Varsayılan türler `constants.py::FAALIYET_TURLERI`'nde. Kullanıcı özel türler `SettingsPage`'den ekler; `activity_types` tablosunda saklanır.

---

## Test

```bash
python -m pytest tests/
```

Mevcut test: `tests/test_date_range.py`

---

## Loglama

`logger_setup.py` → `app.log` dosyasına yazar. DB hatalarında `logger.error()`, kritik başlatma hatalarında `logger.critical()`.
