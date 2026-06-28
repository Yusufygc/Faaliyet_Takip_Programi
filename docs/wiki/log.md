# Log — Kronolojik Değişiklik Kaydı

Yeni işlemler dosyanın **en üstüne** eklenir.

Bağlantılar: [[index]] | [[Rules]]

---

## [2026-06-28] LINT | Wiki sağlık kontrolü — 4 sorun düzeltildi

- `ui_katmani.md` → `[[modeller]]` bağlantısı eklendi (Plans sayfası Folder modeli kullanıyor)
- `servisler.md` → `[[veritabani]]` bağlantısı eklendi (recommendation_cache referansı var)
- `kontrolcüler.md` → `RecommendationController` bölümü tam metod listesiyle genişletildi
- `index.md` → `[[modeller]]` linki "Mimari & Genel"den "Veri Katmanı"na taşındı
- Ek bulgu: `RecommendationController` API anahtarlarını DB'den okurken `MainController` keyring kullanıyor — keyring migration sonrası bu path boş dönebilir ([[kontrolcüler]] sayfasında not var)

## [2026-06-28] INIT | Wiki sistemi kuruldu

Proje için `docs/wiki/` tabanlı LLM hafıza sistemi oluşturuldu. Tüm temel sayfalar ilk kez yazıldı:
- [[Rules]] — çalışma anayasası
- [[mimari_genel_bakis]] — 3 katmanlı MVC mimarisi
- [[veritabani]] — SQLite şeması ve repository pattern
- [[api_entegrasyonlari]] — TMDB, RAWG, Google Books
- [[modeller]] — Activity, Plan, Folder, ActivityFilter dataclass'ları
- [[ui_katmani]] — PyQt5 sayfa yapısı
- [[servisler]] — api_service, pdf_service, recommendation_config
- [[kontrolcüler]] — MainController, RecommendationController, DbWorker
- [[index]] — içerik haritası
