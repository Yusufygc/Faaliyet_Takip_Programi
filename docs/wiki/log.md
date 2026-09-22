# Log — Kronolojik Değişiklik Kaydı

Yeni işlemler dosyanın **en üstüne** eklenir.

Bağlantılar: [[index]] | [[Rules]]

---

## [2026-09-23] FIX | API anahtarları artık arayüzde düz metin olarak kalmıyor

`SettingsBridge` (`bridges/settings_bridge.py`) TMDB/RAWG/Google Books anahtarlarının
gerçek değerini artık QML katmanına hiç göndermiyor — `tmdbKey`/`rawgKey`/`googleBooksKey`
string property'leri kaldırıldı, yerine `hasTmdbKey`/`hasRawgKey`/`hasGoogleBooksKey`
boolean'ları geldi. `SettingsView.qml`'de input alanları artık kayıtlı anahtarla önceden
doldurulmuyor (sadece "✓ Kayıtlı" rozeti + placeholder gösteriliyor), kaydedince alan
temizleniyor. Depolama zaten OS Keyring üzerinden şifreliydi (Windows DPAPI / Credential
Manager) — bu değişmedi; asıl sorun anahtarın QML text field'ında düz metin olarak
"kalması"ydı. Gerçek değerler hâlâ yalnızca `services/_base_api_service.py` tarafından
doğrudan keyring'den okunuyor, `SettingsBridge` üzerinden hiç geçmiyor.

## [2026-09-23] FEAT | Keşfet, Karşılaştırma ve İstatistik sayfalarında kapsamlı redesign

Tek oturumda birbirini izleyen bağımsız kullanıcı istekleriyle yapıldı:
- **Keşfet** (`DiscoverView.qml`, `discover_bridge.py`, `services/*_api_service.py`): ilk
  açılışta veri gelmeme hatası (eksik `Component.onCompleted`) düzeltildi; kart taşmaları
  (buton/açıklama kırpılması) giderildi; tıklanan içerik için zengin API detaylarını
  gösteren `MediaPreviewModal.qml` eklendi (TMDB `append_to_response=credits`, RAWG ve
  Google Books detay uçları — `fetch_details()` her serviste); `RandomPickModal.qml`'deki
  bozuk yükseklik hesaplaması düzeltildi; "Daha Fazla Yükle" sayfalama eklendi (`loadMore`,
  `hasMore`).
- **Karşılaştırma** (`CompareView.qml`, `ComparePanel.qml` [yeni], `compare_bridge.py`):
  sayfa sıfırdan tasarlandı — iki bağımsız panel (her biri kendi ay/yıl seçimiyle), tür
  bazlı kolonlar, kolonlarda tek sayı yerine faaliyet isimleri alt alta listeleniyor,
  kolonlar pencereye orantılı yayılıp gerekirse yatay kaydırıyor, kısa kesilen isimlerde
  `ToolTip` var.
- **İstatistikler** (`StatsView.qml`, `CategoryMonthHeatmap.qml` [yeni]): eski dar "Zamana
  Göre Kategori Payı" streamgraph'ı (`CategoryTimelineChart.qml`, silindi) yerine tam
  genişlikte Kategori × Ay ısı haritası kondu; pasta grafiği + liste artık kendi bloğunda
  ortalanıyor. Backend değişmedi (`monthlyCategoryDistribution` zaten uygun şekildeydi).
- **Genel UI temizliği:** başlık çubuğundan emoji + "FaaliyetTakip" yazısı kaldırıldı,
  sidebar'dan "Modern QML Edition" kaldırıldı, Ayarlar'dan "Uygulama Bilgileri" kaldırıldı,
  Tür Yönetimi + API Anahtarları kutucukları yan yana ve eşit boyutlu yapıldı.
- Ardından çalıştırılan `/code-review`: iki yarış durumu (Keşfet'te `loadMore` /
  `fetchItemDetails` stale-response) istek sıra numarası (`_request_seq` / `_details_seq`)
  ile, `ComparePanel.qml`'de kullanıcı seçiminde kopan ComboBox `currentIndex` binding'i
  `Connections` ile elle senkronlayarak, `TypeRepository.get_all_types()`'daki her
  çağrıda tekrarlanan gereksiz tablo-varlık kontrolü kaldırılarak düzeltildi.

**Not:** Bu wiki hâlâ PyQt5 dönemine ait eski mimari sayfaları içeriyor
(`mimari_genel_bakis.md`, `ui_katmani.md`, `kontrolcüler.md`, `Rules.md`'deki "UI
framework: PyQt5" notu) — proje PySide6 + QtQuick/QML + Bridge mimarisine geçeli birkaç
commit oldu ama bu sayfalar o geçişte güncellenmemiş. Kapsamlı bir [LINT] geçişi önerilir.

## [2026-06-28] FIX | RecommendationController başlatma hatası giderildi

`ActivityRepository` üzerinde `get_setting` çağrısı `AttributeError` atıyordu.
`TypeRepository` + keyring öncelikli okuma ile düzeltildi (`MainController` ile tutarlı).
Lint sırasında tespit edilmişti ([[kontrolcüler]] sayfasında belgelenmişti).

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
