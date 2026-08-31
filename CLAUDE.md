# CLAUDE.md — Faaliyet Takip Programı

## Wiki — Önce Oku

Her sohbet başında `docs/wiki/index.md` okunur. Proje bağlamı, mimari kararlar ve geçmiş değişiklikler burada birikir. Detaylı operasyon kuralları için `docs/wiki/Rules.md`.

---

## Proje Tanımı

Kişisel aktivite (film, dizi, oyun, kitap, kurs, şehir) takip masaüstü uygulaması. **PySide6 + QML (QtQuick)** modern arayüz, SQLite yerel veritabanı, harici API'lerden içerik önerisi.

**Giriş noktası:** `main.py`

---

## Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| Dil | Python 3.10+ |
| GUI | PySide6 ≥6.7.0 (QML / QtQuick) |
| Veritabanı | SQLite 3 (stdlib) |
| PDF | ReportLab ≥4.4.0 |
| HTTP | Requests ≥2.32.0 |
| Credential | keyring ≥25.0.0 |

---

## Çalıştırma

```bash
# Conda Ftakip ortamında:
conda activate Ftakip
python main.py
```

**DB konumu:** `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db`

---

## Mimari Özeti

```
QML Views (qml/views/, qml/modals/)
        ↕  (Q_PROPERTY, Slots, Signals, QAbstractListModel)
Python Bridges (bridges/)
        ↕
Database Repositories (database/)  &  Services (services/)
        ↕
SQLite DB  &  External APIs (TMDB, RAWG, Books)
```

---

## Kritik Dosyalar

| Dosya | Rol |
|-------|-----|
| `main.py` | PySide6 başlatıcı, QML engine ve Bridge enjeksiyonu |
| `qml/Main.qml` | Ana pencere kabuğu, TitleBar, Sidebar ve Toast container |
| `bridges/activity_bridge.py` | Faaliyetler Listesi ve Modal Ekleme/Düzenleme köprüsü |
| `bridges/stats_bridge.py` | İstatistikler, KPI'lar ve entegre PDF oluşturma |
| `bridges/plan_bridge.py` | Hedefler/Planlar ve Klasör yönetimi köprüsü |
| `bridges/discover_bridge.py` | TMDB, RAWG, Books API önerileri ve rastgele seçici |
| `database/repository.py` | `ActivityRepository` — CRUD + istatistik sorguları |
| `database/plan_repository.py` | `PlanRepository` — Plan ve Klasör CRUD |
| `models.py` | `Activity`, `Plan`, `Folder`, `ActivityFilter` |
| `constants.py` | `FAALIYET_TURLERI`, `APP_NAME`, `VERSION`, `DB_FILENAME` |

---

## Geliştirme Notları

### 1. Sayfa & Modül Ekleme
- QML arayüz dosyaları `qml/views/` altında yer alır.
- Modal ve popuplar `qml/modals/` altında yer alır.
- Tekrar kullanılabilir arayüz elemanları `qml/components/` altındadır.
- Global renk ve tipografi `qml/theme/Theme.qml` singleton'ındadır.

### 2. UX Akış Kuralları
- **Ekleme & Düzenleme:** Liste sayfasından `ActivityFormModal` ile modal diyalog olarak açılır.
- **PDF Raporu:** İstatistikler sayfasından `PdfExportModal` ile doğrudan üretilir.

### 3. API Anahtarları
`keyring` üzerinden saklanır (`.env` kullanılmaz):
- Okuma/Yazma: `SettingsBridge` üzerinden OS Keychain/Keyring kullanılır.

---

## Test

```bash
python -m pytest tests/
```
