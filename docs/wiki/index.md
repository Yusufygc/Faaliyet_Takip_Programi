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

**Stack:** Python 3.10+ / **PySide6 (QtQuick/QML)** / SQLite / ReportLab / Requests / keyring

**Giriş noktası:** `main.py`

**DB konumu:** `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db` (Windows)

**API güvenlik:** API anahtarları `keyring`'de (OS güvenli depolama) saklanır; `.env`
kullanılmaz ve anahtarların düz metin değeri hiçbir zaman QML/UI katmanına aktarılmaz
(sadece "kayıtlı mı" bilgisi gösterilir — bkz. [[log]] 2026-09-23).

**Son önemli değişiklikler:**
- Proje **PyQt5'ten PySide6 + QtQuick/QML mimarisine geçti** (`qml/` + `bridges/` klasörleri) —
  ⚠️ [[mimari_genel_bakis]], [[ui_katmani]] ve [[kontrolcüler]] sayfaları bu geçişten önceki
  PyQt5 dönemini anlatıyor ve henüz güncellenmedi, güncel mimari için `CLAUDE.md`'ye ve
  doğrudan `bridges/` + `qml/` kaynak koduna bakın.
- Keşfet, Karşılaştırma ve İstatistikler sayfalarında kapsamlı redesign + API anahtarı
  UI güvenlik düzeltmesi (bkz. [[log]] 2026-09-23)
- `.env` bağımlılığı kaldırıldı; API anahtarları keyring'e taşındı
- Plans sayfasına grid kart sıralama + klasörleme eklendi
