# 📊 Faaliyet Takip Sistemi

**Faaliyet Takip Sistemi**, kullanıcıların günlük veya dönemsel faaliyetlerini kolayca yönetmesini sağlayan modern bir masaüstü uygulamasıdır. Dizi, film, kitap, oyun, kurs, şehir gibi çeşitli faaliyetleri kaydedebilir, istatistiklerini görüntüleyebilir, karşılaştırabilir ve PDF raporları oluşturabilirsiniz.

---

## 🚀 Özellikler

- 🎮 **Faaliyet Ekleme**: Dizi, film, kitap vb. faaliyetleri ad, tarih, yorum ve puan ile kaydedin.
- 📋 **Faaliyet Listeleme**: Tüm faaliyetleri görüntüleyin, tür, ad veya tarihe göre filtreleyin.
- ✏️ **Düzenleme / Silme**: Listelenmiş verileri kayıtlarını güncelleyin veya kaldırın.
- 📈 **İstatistik Görüntüleme**: Grafiklerle yıllık veya aylık analizler.Listelenmiş verilere tıklayarak veri içeriğini görüntüleyin
- 🔄 **Dönem Karşılaştırma**: İki farklı yıl veya ay arasındaki faaliyetleri karşılaştırın.
- 📄 **PDF Raporu Oluşturma**: Belirli dönemlere ait grafik ve özet içeren PDF raporları üretin.
- 🎨 **Kullanıcı Dostu Arayüz**: CustomTkinter ile modern ve sezgisel kullanım.
- 🗂️ **Yerel Veritabanı**: Tüm veriler güvenli şekilde SQLite veritabanında saklanır.

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



