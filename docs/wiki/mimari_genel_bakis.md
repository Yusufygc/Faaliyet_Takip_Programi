# Mimari Genel Bakış

Faaliyet Takip Programı — Python/PyQt5 masaüstü uygulaması, MVC pattern ile 3 katmanlı mimari.

Bağlantılar: [[index]] | [[log]] | [[veritabani]] | [[kontrolcüler]] | [[ui_katmani]] | [[servisler]]

---

## Katmanlar

```
┌─────────────────────────────────┐
│  View (views/)                  │  PyQt5 widget'ları, sayfalar, diyaloglar
├─────────────────────────────────┤
│  Controller (controllers/)      │  İş mantığı, validasyon, async iş akışı
├─────────────────────────────────┤
│  Repository (database/)         │  SQLite CRUD ve istatistik sorguları
└─────────────────────────────────┘
         ↕
┌─────────────────────────────────┐
│  Service (services/)            │  Harici API ve PDF üretimi
└─────────────────────────────────┘
```

---

## Dosya Haritası

```
P001-Faaliyet_Takip_Programi/
├── main.py                        # Giriş noktası: QApplication başlatma
├── constants.py                   # APP_NAME, DB_FILENAME, FAALIYET_TURLERI
├── models.py                      # Activity, Plan, Folder, ActivityFilter
├── utils.py                       # is_valid_yyyymm, extract_year_month
├── logger_setup.py                # app.log konfigürasyonu
│
├── controllers/
│   ├── main_controller.py         # Tüm iş mantığı (async wrapper'larla)
│   ├── recommendation_controller.py  # Öneri sistemi mantığı
│   └── workers.py                 # DbWorker: QThread tabanlı async
│
├── database/
│   ├── connection.py              # get_connection(), init_db(), get_db_path()
│   ├── repository.py              # ActivityRepository: CRUD + istatistik
│   ├── plan_repository.py         # PlanRepository: plan + klasör CRUD
│   ├── recommendation_repository.py  # Öneri önbelleği (7 gün TTL)
│   └── type_repository.py         # TypeRepository: tür yönetimi + ayarlar
│
├── services/
│   ├── api_service.py             # ApiService: TMDB, RAWG, Google Books
│   ├── pdf_service.py             # PDF raporu oluşturma (ReportLab)
│   └── recommendation_config.py  # Periyot, tür ID'leri, kült listeler
│
└── views/
    ├── main_window.py             # Ana pencere + sayfa navigasyonu
    ├── styles.py                  # Global QSS stiller
    ├── widgets.py                 # Yeniden kullanılabilir widget'lar
    ├── pages/
    │   ├── add_page.py            # Faaliyet ekleme formu
    │   ├── edit_dialog.py         # Faaliyet düzenleme diyalogu
    │   ├── list_page.py           # Filtrelenmiş faaliyet listesi
    │   ├── stats_page.py          # İstatistik grafikleri
    │   ├── suggestion_page.py     # Keşfet & Öneriler
    │   ├── plans_page.py          # Hedef & Plan yönetimi (grid + klasör)
    │   ├── compare_page.py        # Dönem karşılaştırma
    │   ├── pdf_page.py            # PDF rapor sayfası
    │   └── settings_page.py       # Ayarlar (tür yönetimi, API anahtarları)
    └── dialogs/
        └── compare_selection_dialog.py
```

---

## Async Çalışma Modeli

Tüm DB operasyonları `DbWorker` (QThread alt sınıfı) üzerinden asenkron çalışır:

```
View → Controller._run_async(func, callback) → DbWorker(QThread) → Repository
                                                       ↓
                                              worker.finished sinyal
                                                       ↓
                                                  callback(result)
                                                       ↓
                                                 View güncelle
```

- Validasyon: controller'da senkron
- DB işlemi: worker thread'de asenkron
- Sonuç: `finished` sinyali ile callback'e iletilir

---

## Veritabanı Konumu

- **Windows:** `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db`
- **macOS/Linux:** `~/.config/FaaliyetTakip/faaliyetler.db`

---

## API Anahtarı Saklama

Commit `6b34a15`'den itibaren `.env` dosyası kaldırıldı. API anahtarları:
1. İlk önce `keyring` (OS güvenli depolama) kontrol edilir.
2. Keyring'de yoksa DB'deki eski plaintext alanından migrate edilir.
3. Migration sonrası DB'deki plaintext alan temizlenir.

Detay: [[kontrolcüler]]

---

## Teknoloji Yığını

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| GUI | PyQt5 | 5.15.11 |
| Grafik | Matplotlib | 3.10.8 |
| DB | SQLite 3 | stdlib |
| PDF | ReportLab | 4.4.9 |
| HTTP | Requests | 2.32.5 |
| Credential | keyring | ≥25.0.0 |
