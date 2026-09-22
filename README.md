# 📊 Faaliyet Takip Programı

Kişisel aktivitelerinizi (Film, Dizi, Oyun, Kitap vb.) takip etmenizi, istatistiklerini görmenizi ve yeni içerik önerileri almanızı sağlayan modern bir masaüstü uygulaması.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-QtQuick%2FQML-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## 📸 Ekran Görüntüleri

### Ana Sayfa - Dashboard
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: Ana sayfa görünümü - KPI kartları ve aktivite listesi]**

### Faaliyet Listesi
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: Liste sayfası - Filtreleme ve aktivite kartları]**

### İstatistik Paneli
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: İstatistik sayfası - Grafikler ve tablolar]**

### Keşfet & Öneriler
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: Öneri sayfası - Film/Dizi/Oyun/Kitap kartları]**

### Rastgele Öneri Modalı
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: Rastgele öneri popup penceresi]**

### Planlar Sayfası
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: Yıllık ve aylık planlar görünümü]**

### Karşılaştırma Sayfası
> 📷 **[EKRAN GÖRÜNTÜSÜ EKLE: İki dönem karşılaştırma görünümü]**

---

## ✨ Özellikler

### 📝 Aktivite Yönetimi
- **Ekleme/Düzenleme/Silme**: Film, dizi, oyun, kitap ve özel kategoriler ekleyin
- **Puanlama**: 1-10 arası puanlama sistemi
- **Tarih Aralığı**: Başlangıç ve bitiş tarihi desteği (diziler için ideal)
- **Yorum**: Her aktiviteye detaylı yorum ekleyin
- **Dinamik Türler**: Kendi özel kategorilerinizi oluşturun

### 📊 İstatistikler
- **Özet Kartlar (KPI)**: Toplam faaliyet, ortalama puan, en aktif kategori
- **Görsel Grafikler**: Bar ve pasta grafikleri ile dağılım analizi
- **Dönemsel Filtreleme**: Ay, yıl veya tüm zamanlar bazında analiz
- **Detay Görünümü**: Kategoriye tıklayarak detaylı liste

### 🚀 Keşfet & Öneriler Sistemi
- **Çoklu Kategori**: Film, Dizi, Oyun, Kitap önerileri
- **Dönem Seçenekleri**:
  - 📅 Bu Ayın Trendleri
  - 🆕 Yeni Çıkanlar
  - 🏆 Tüm Zamanların En İyileri
  - ⭐ Mutlaka İzlenmeli
  - 🎭 Kült Klasikler
  - 💎 Gizli Hazineler
  - 🔜 Yakında Gelecekler
- **Tür Filtreleme**: Her kategori için ayrı tür seçenekleri
- **🇹🇷 Türkçe Yapımlar Filtresi**: Sadece Türk yapımlarını görün
- **🎲 Rastgele Öneri**: Karar veremediğinizde tek tıkla rastgele öneri alın
- **📂 Veritabanı Önbelleği**: API sonuçları 7 gün önbelleğe alınır
- **➕ Sayfalama**: "Daha Fazla Göster" ile yeni içerikler yükleyin

### 📅 Hedef & Plan Yönetimi
- **Aylık Planlar**: Her ay için hedefler belirleyin
- **Yıllık Planlar**: Uzun vadeli hedefler oluşturun
- **İlerleme Takibi**: %0-100 arası ilerleme çubuğu
- **Durum Yönetimi**: Planlandı, Devam Ediyor, Tamamlandı, Arşivlendi
- **Öncelik Seviyeleri**: Düşük, Orta, Yüksek

### 📈 Karşılaştırma
- **Dönem Karşılaştırma**: İki farklı dönemin aktivitelerini karşılaştırın
- **Görsel Analiz**: Hangi dönemde neyi daha çok yaptığınızı görün

### 📄 PDF Raporu
- **Detaylı Rapor**: Seçilen dönemin PDF raporunu oluşturun
- **Otomatik Kayıt**: Masaüstüne otomatik kayıt

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Repoyu Klonlayın
```bash
git clone https://github.com/Yusufygc/Faaliyet_Takip_Programi.git
cd Faaliyet_Takip_Programi
```

### Adım 2: Sanal Ortam Oluşturun (Önerilen)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Uygulamayı Başlatın
```bash
python main.py
```

### Adım 5: API Anahtarlarını Ayarlayın (İsteğe Bağlı, Keşfet için)
`.env` dosyası **kullanılmaz**. Anahtarlar uygulama içinden, **Ayarlar → API Anahtarları**
bölümünden girilir ve işletim sisteminin güvenli kasasında (Windows Credential
Manager / macOS Keychain / Linux Secret Service — Python `keyring` paketi üzerinden)
şifreli olarak saklanır; arayüzde tekrar düz metin olarak gösterilmez.

**API Anahtarı Alma:**
- **TMDB**: [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
- **RAWG**: [https://rawg.io/apidocs](https://rawg.io/apidocs)
- **Google Books**: API anahtarı gerektirmez (ücretsiz)

---

## 📁 Proje Yapısı

Mimari: **QML Views/Modals ↔ Python Bridges ↔ Database Repositories & Services ↔ SQLite / Harici API'ler**

```
P001-Faaliyet_Takip_Programi/
├── main.py                 # PySide6 başlatıcı, QML engine + Bridge enjeksiyonu
├── constants.py            # Sabit değerler
├── models.py               # Veri modelleri (Activity, Plan, Folder, ActivityFilter)
├── logger_setup.py         # Loglama yapılandırması
│
├── qml/
│   ├── Main.qml             # Ana pencere kabuğu, TitleBar, Sidebar, Toast
│   ├── theme/                # Theme.qml singleton (renk/tipografi), ikon fontu
│   ├── views/                 # ActivityListView, StatsView, DiscoverView, CompareView, PlansView, SettingsView
│   ├── modals/                # ActivityFormModal, MediaPreviewModal, RandomPickModal, PdfExportModal...
│   └── components/            # CustomButton, ComparePanel, CategoryMonthHeatmap, CategoryPieChart...
│
├── bridges/                 # QML ↔ Python köprüleri (Q_PROPERTY / Slot / Signal)
│   ├── activity_bridge.py
│   ├── stats_bridge.py
│   ├── plan_bridge.py
│   ├── discover_bridge.py
│   ├── compare_bridge.py
│   ├── settings_bridge.py
│   └── app_bridge.py
│
├── database/                # Veritabanı katmanı
│   ├── connection.py        # SQLite bağlantısı
│   ├── repository.py        # ActivityRepository — CRUD + istatistik sorguları
│   ├── plan_repository.py
│   ├── type_repository.py
│   └── recommendation_repository.py  # Öneri önbelleği
│
├── services/                # Harici servis entegrasyonları
│   ├── _base_api_service.py # Ortak HTTP istemcisi (retry, throttle, keyring okuma)
│   ├── movie_api_service.py / series_api_service.py  # TMDB
│   ├── game_api_service.py  # RAWG
│   ├── book_api_service.py  # Google Books
│   ├── pdf_service.py
│   └── recommendation_config.py
│
├── icons/ fonts/ assets/    # Statik kaynaklar
└── tests/                   # pytest test paketi
```

---

## 🔌 Kullanılan API'ler

| API | Kullanım Alanı | Ücretsiz Limit |
|-----|----------------|----------------|
| **TMDB** | Film ve Dizi verileri | Günlük ~1000 istek |
| **RAWG** | Oyun verileri | Aylık 20,000 istek |
| **Google Books** | Kitap verileri | Sınırsız (anonim) |

---

## 🎨 Teknoloji Yığını

| Teknoloji | Kullanım |
|-----------|----------|
| **Python 3.10+** | Ana programlama dili |
| **PySide6 (QtQuick/QML)** | GUI framework |
| **SQLite** | Yerel veritabanı |
| **Requests** | HTTP istekleri |
| **keyring** | API anahtarlarının OS kasasında şifreli saklanması |
| **ReportLab** | PDF oluşturma |

---

## 📱 Özellik Detayları

### Keşfet & Öneriler Sistemi

#### Kategori Türleri

**🎬 Film Türleri:**
Aksiyon, Komedi, Dram, Korku, Bilim Kurgu, Romantik, Animasyon, Gerilim, Suç, Belgesel, Fantezi, Macera, Savaş, Western

**📺 Dizi Türleri:**
Aksiyon & Macera, Komedi, Dram, Suç, Belgesel, Aile, Animasyon, Gizem, Bilim Kurgu & Fantezi, Reality

**🎮 Oyun Türleri:**
Aksiyon, RPG, Strateji, Spor, Yarış, Macera, Bulmaca, Shooter, Platform, Simülasyon, Dövüş, Indie

**📚 Kitap Türleri:**
Dünya Klasikleri, Türk Klasikleri, Gerilim, Romantik, Bilim Kurgu, Fantastik, Korku, Tarih, Gizem, Polisiye, Biyografi, Felsefe, Psikoloji, Kişisel Gelişim

#### Önbellek Sistemi
- API sonuçları SQLite veritabanında 7 gün saklanır
- Tekrar eden istekler önbellekten karşılanır (hızlı)
- "Yenile" butonu ile taze veri çekilebilir
- "Eski Verileri Göster" ile önceki tüm çekilen veriler görüntülenebilir

---

## ⚙️ Yapılandırma

### Veritabanı Konumu
- **Windows**: `%LOCALAPPDATA%\FaaliyetTakip\faaliyetler.db`

### Log Dosyası
- `app.log` dosyasında uygulama logları tutulur

---

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

---

## Teşekkürler

- [TMDB](https://www.themoviedb.org/) - Film ve dizi verileri için
- [RAWG](https://rawg.io/) - Oyun verileri için
- [Google Books](https://books.google.com/) - Kitap verileri için
- [PySide6 (Qt for Python)](https://doc.qt.io/qtforpython/) - GUI framework için

---

## İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
