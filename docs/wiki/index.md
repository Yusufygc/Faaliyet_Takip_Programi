# Wiki — Faaliyet Takip Programı

Her yeni sohbette **önce bu dosya okunur**, sonra gerekli alt sayfalara geçilir.

Bağlantılar: [[log]] | [[Rules]]

---

## Navigasyon

### Mimari & Genel
- [[mimari_genel_bakis]] — MVC katmanları, dosya haritası, async model, teknoloji yığını

### Veri Katmanı
- [[veritabani]] — SQLite tabloları, repository sınıfları, şema migration stratejisi
- [[modeller]] — Activity, Plan, Folder, ActivityFilter dataclass tanımları

### Servisler & API
- [[servisler]] — ApiService, pdf_service, recommendation_config
- [[api_entegrasyonlari]] — TMDB, RAWG, Google Books endpoint'leri, önbellek, periyotlar

### İş Mantığı
- [[kontrolcüler]] — MainController, RecommendationController, DbWorker (QThread)

### Arayüz
- [[ui_katmani]] — PyQt5 sayfa yapısı, navigasyon, stil sistemi, Plans grid özelliği

### Sistem
- [[Rules]] — Wiki çalışma kuralları ve operasyon komutları (INGEST, QUERY, LINT)
- [[log]] — Kronolojik değişiklik kaydı

---

## Proje Özeti

**Ne yapar:** Kişisel aktivite (film, dizi, oyun, kitap, kurs, şehir) takip uygulaması.

**Stack:** Python 3.8+ / PyQt5 5.15 / SQLite / Matplotlib / ReportLab / Requests / keyring

**Giriş noktası:** `main.py`

**DB konumu:** `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db` (Windows)

**API güvenlik:** API anahtarları `keyring`'de (OS güvenli depolama); `.env` kullanılmaz.

**Son önemli değişiklikler:**
- Proje kökü yeniden düzenlendi (`PyQt5_Modern_Tasarim` → kök)
- `.env` bağımlılığı kaldırıldı; API anahtarları keyring'e taşındı
- Plans sayfasına grid kart sıralama + klasörleme eklendi
- `down_arrow.svg` programatik oluşturuluyor
