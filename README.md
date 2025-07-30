# 📊 Faaliyet Takip Sistemi

**Faaliyet Takip Sistemi**, kullanıcıların günlük veya dönemsel faaliyetlerini kolayca yönetmesini sağlayan modern bir masaüstü uygulamasıdır. Dizi, film, kitap, oyun, kurs, şehir gibi çeşitli faaliyetleri kaydedebilir, istatistiklerini görüntüleyebilir, karşılaştırabilir ve PDF raporları oluşturabilirsiniz.

---

## 🚀 Özellikler

### ✨ Temel Fonksiyonlar

- 🎮 **Sezgisel Faaliyet Ekleme**: Yeni faaliyetleri tür, ad, tarih (YYYY-MM), detaylı yorum ve 1-10 aralığında puanlama ile kolayca kaydedin.
- 📋 **Gelişmiş Faaliyet Listeleme ve Yönetimi**:
  - Tüm kayıtlı faaliyetleri tablo formatında görüntüleyin.
  - **Dinamik Filtreleme**: Türe, ada (arama çubuğu ile) veya belirli bir tarihe (yıl veya ay) göre anında filtreleyin.
  - **Sayfalama Sistemi**: Sayfa başına 5, 10, 20 veya 50 kayıt seçeneği ile büyük veri setlerinde kolay gezinim.
  - **Detay Görüntüleme**: Liste üzerinden çift tık ile detayları (yorum ve puan dahil) içeren diyalog penceresi.
  - **Hızlı Düzenleme/Silme**: Liste üzerinden çift tık ile seçtiğiniz kaydı kolayca güncelleyin veya onay ile silin.

### 📊 İstatistik ve Karşılaştırma
- 📋**Listelenmiş Veri**: Filtre ile istediğiniz zamandaki veya tüm verinizi listeleyerek veriye çift tıklayıp içeriğini inceleyin
- 📈 **Görsel İstatistikler**: Belirli bir yıl veya ay için faaliyet türlerine göre dağılımı gösteren interaktif histogram ve pasta grafikler.
- 🔄 **Dönem Karşılaştırma**: İki farklı yıl veya ay arasındaki faaliyet verilerini kıyaslayarak eğilimleri analiz edin.
- 📄 **Profesyonel PDF Raporları**: Seçilen döneme ait faaliyet verilerinin özet ve detaylı PDF raporlarını oluşturun ve dışa aktarın.

### 🎨 Arayüz ve Veri Yapısı

- 🌟 **Kullanıcı Dostu Arayüz (UI)**: CustomTkinter ile tasarlanmış modern, temiz ve sezgisel grafik arayüz.
- 🗂️ **Yerel Veri Depolama**: Tüm veriler, hafif ve güvenilir bir SQLite veritabanında yerel olarak saklanır.

---

## 🛠️ Kullanılan Teknolojiler

- **Python 3.x**
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – Modern GUI tasarımı
- **SQLite3** – Yerel veri yönetimi
- **Matplotlib** – Grafik çizimi
- **ReportLab** – PDF rapor üretimi

---

## ⚙️ Kurulum ve Çalıştırma

### 1. Ön Koşullar

- Python 3.8+ (Tavsiye: Conda veya venv kullanın)
- Git (depo klonlama için)

### 2. Depoyu Klonlayın

```bash
git clone https://github.com/Yusufygc/Faaliyet_Takip_Programi.git
cd Faaliyet_Takip_Programi
```

### 3. Sanal Ortam Oluşturun ve Etkinleştirin

#### A. Conda ile (Önerilen)

```bash
conda create -n faaliyet_env python=3.10
conda activate faaliyet_env
cd /d D:\YOL\TO\PROJE\Faaliyet_Takip_Programi  # Kendi yolunuzu yazın
```

#### B. venv ile

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. Bağımlılıkları Kurun

```bash
pip install -r requirements.txt
# Eğer yoksa:
pip freeze > requirements.txt
```

### 5. Uygulamayı Başlatın

```bash
python main.py
```

---

## 📦 EXE Dosyası Oluşturma (Windows)

### 1. PyInstaller Kurulumu

```bash
pip install pyinstaller
```

### 2. Yürütülebilir Dosya Oluşturma

```bash
pyinstaller --noconfirm --windowed --icon=icons/icon.ico --name "AktiviteTakip" ^
--add-data "data;data" ^
--add-data "gui;gui" ^
--add-data "fonts;fonts" ^
--add-binary "C:/Users/KULLANICI_ADINIZ/anaconda3/envs/ORTAM_ADINIZ/Library/bin/*;." ^
--collect-all=numpy ^
--collect-all=matplotlib ^
main.py
```

### EXE Dosyası Nerede?

`dist/AktiviteTakip/AktiviteTakip.exe` yolunda oluşturulur.

---

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak ister misiniz?

- 🧾 Hata bildirin
- 💡 Yeni özellik önerin
- 🔧 Kod iyileştirmeleri yapın

Pull request'ler ve sorun bildirimleri her zaman memnuniyetle karşılanır.

---

## 📧 İletişim

Proje sahibi: **Yusuf Yağcı**\
LinkedIn: [linkedin.com/in/ysfygc](https://www.linkedin.com/in/ysfygc/)\
GitHub: [Yusufygc](https://github.com/Yusufygc)

---



