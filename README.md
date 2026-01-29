# 📊 Faaliyet Takip Programı

Kişisel aktivitelerinizi (Film, Dizi, Oyun, Kitap vb.) takip etmenizi, istatistiklerini görmenizi ve yeni içerik önerileri almanızı sağlayan modern bir masaüstü uygulaması.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
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
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Repoyu Klonlayın
```bash
git clone https://github.com/kullanici/faaliyet-takip.git
cd faaliyet-takip/PyQt5_Modern_Tasarim
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
pip install PyQt5 matplotlib requests python-dotenv reportlab
```

### Adım 4: API Anahtarlarını Ayarlayın
`.env` dosyası oluşturun veya mevcut olanı düzenleyin:

```env
TMDB_API_KEY=your_tmdb_api_key_here
RAWG_API_KEY=your_rawg_api_key_here
```

**API Anahtarı Alma:**
- **TMDB**: [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
- **RAWG**: [https://rawg.io/apidocs](https://rawg.io/apidocs)
- **Google Books**: API anahtarı gerektirmez (ücretsiz)

### Adım 5: Uygulamayı Başlatın
```bash
python main.py
```

---

## 📁 Proje Yapısı

```
PyQt5_Modern_Tasarim/
├── main.py                 # Uygulama giriş noktası
├── constants.py            # Sabit değerler
├── models.py               # Veri modelleri (Activity, Plan, Filter)
├── utils.py                # Yardımcı fonksiyonlar
├── logger_setup.py         # Loglama yapılandırması
│
├── controllers/            # İş mantığı katmanı
│   ├── activity_controller.py
│   ├── recommendation_controller.py
│   └── workers.py          # Asenkron işlemler (DbWorker)
│
├── database/               # Veritabanı katmanı
│   ├── connection.py       # SQLite bağlantısı
│   ├── repository.py       # CRUD işlemleri
│   └── recommendation_repository.py  # Öneri önbelleği
│
├── services/               # Harici servis entegrasyonları
│   ├── api_service.py      # TMDB, RAWG, Google Books API
│   └── recommendation_config.py  # Öneri yapılandırmaları
│
├── views/                  # Kullanıcı arayüzü
│   ├── main_window.py      # Ana pencere
│   ├── styles.py           # Global stiller
│   ├── widgets/            # Yeniden kullanılabilir bileşenler
│   ├── pages/              # Sayfa görünümleri
│   │   ├── dashboard.py
│   │   ├── list_page.py
│   │   ├── stats_page.py
│   │   ├── suggestion_page.py
│   │   ├── plans_page.py
│   │   ├── compare_page.py
│   │   └── pdfcreate_page.py
│   └── dialogs/            # Diyalog pencereleri
│
├── icons/                  # Uygulama ikonları
├── fonts/                  # Özel fontlar
└── .env                    # API anahtarları (git'e eklenmez)
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
| **Python 3.8+** | Ana programlama dili |
| **PyQt5** | GUI framework |
| **SQLite** | Yerel veritabanı |
| **Matplotlib** | Grafik görselleştirme |
| **Requests** | HTTP istekleri |
| **python-dotenv** | Ortam değişkenleri |
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
- **Windows**: `%LOCALAPPDATA%\FaaliyetTakip\faaliyet_takip.db`
- **macOS/Linux**: `~/.config/FaaliyetTakip/faaliyet_takip.db`

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
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework için

---

## İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
