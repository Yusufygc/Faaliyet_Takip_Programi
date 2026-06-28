# UI Katmanı

PyQt5 tabanlı masaüstü arayüzü; tek ana pencere + QStackedWidget ile sayfa navigasyonu.

Bağlantılar: [[index]] | [[log]] | [[mimari_genel_bakis]] | [[kontrolcüler]] | [[servisler]] | [[modeller]]

---

## Ana Pencere

`views/main_window.py` — `QMainWindow` alt sınıfı.

- Sol kenar çubuğu (sidebar): navigasyon butonları
- Merkez: `QStackedWidget` ile aktif sayfayı gösterir
- `MainController` instance'ı tüm sayfalara geçilir (dependency injection)

---

## Sayfalar

| Dosya | Sınıf | Açıklama |
|-------|-------|----------|
| `views/pages/add_page.py` | `AddPage` | Faaliyet ekleme formu; tarih picker, tür seçimi, puan |
| `views/pages/edit_dialog.py` | `EditDialog` | Faaliyet düzenleme diyalogu (QDialog) |
| `views/pages/list_page.py` | `ListPage` | Filtrelenmiş faaliyet listesi; sayfalama, arama |
| `views/pages/stats_page.py` | `StatsPage` | Bar/pasta grafikleri, KPI kartlar, dönem filtresi |
| `views/pages/suggestion_page.py` | `SuggestionPage` | API'den gelen kart grid; periyot, tür, Türkçe filtre |
| `views/pages/plans_page.py` | `PlansPage` | Grid kart sıralama, klasörleme (commit 47d1480) |
| `views/pages/compare_page.py` | `ComparePage` | İki dönem karşılaştırma |
| `views/pages/pdf_page.py` | `PdfPage` | PDF rapor sayfası |
| `views/pages/settings_page.py` | `SettingsPage` | Tür yönetimi, API anahtarı kayıt |
| `views/analysis/trend_analysis.py` | `TrendAnalysis` | Aylık trend grafiği (matplotlib) |
| `views/dialogs/compare_selection_dialog.py` | — | Karşılaştırma dönem seçimi diyalogu |

---

## Widget'lar

`views/widgets.py` — Yeniden kullanılabilir bileşenler.

---

## Stil Sistemi

`views/styles.py` — Global QSS (Qt Style Sheets).

- `down_arrow.svg` programatik oluşturulur (commit `6affa8d`; harici dosyaya bağımlılık kaldırıldı)
- Tema: `QApplication.setStyle("Fusion")` (`constants.py::THEME_NAME`)

---

## Sayfa Yaşam Döngüsü

1. `MainWindow.__init__()` → tüm sayfaları oluşturur, `stack`'e ekler
2. Sidebar butonu tıklanınca `stack.setCurrentWidget(page)` çağrılır
3. Sayfalar async callback sistemiyle controller'dan veri çeker
4. Callback UI thread'inde çalışır (Qt sinyal mekanizması)

---

## Plans Sayfası Özel Not (commit 47d1480)

Grid mantığı ile kart sıralama ve klasörleme özelliği eklendi:
- Planlar klasörlere (`Folder`) atanabilir
- Sayfada klasöre göre gruplama yapılır
- Drag-drop veya buton sıralaması ile kart konumu değiştirilebilir
