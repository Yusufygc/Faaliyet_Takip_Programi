# Rules — Faaliyet Takip Programı Wiki Kuralları

Bu dosya, `docs/wiki/` sisteminin çalışma anayasasıdır. Her yeni sohbette önce [[index]] okunur, gerekirse bağlantılı sayfalar takip edilir.

Bağlantılar: [[index]] | [[log]]

---

## 1. Zorunlu Çalışma Akışı

- **Önce Oku:** Kod yazmadan veya mimari karar vermeden önce `docs/wiki/index.md` okunur. İhtiyaç duyulursa bağlantılı alt sayfalar da incelenir.
- **Proaktif Güncelleme:** Yeni kütüphane eklendiğinde, bir konfigürasyon yapıldığında veya karmaşık algoritma tasarlandığında ilgili wiki sayfası güncellenir ya da yenisi oluşturulur.
- **Bağlantısallık:** Her sayfada en az `[[index]]` ve `[[log]]` linkleri bulunur. Öksüz (hiçbir yere bağlanmayan) sayfa bırakılmaz.

---

## 2. Operasyon Komutları

### 🟢 [INGEST]
Yeni kaynak, kod parçası veya fikir verildiğinde:
1. Kaynağı oku ve analiz et.
2. `docs/wiki/` içinde yeni özet/konsept sayfası oluştur.
3. Çakışan veya genişleyen bilgiler için mevcut sayfaları güncelle.
4. `index.md` dosyasına yeni sayfanın linkini ekle.
5. `log.md` dosyasının en üstüne işlemi kaydet.

### 🔵 [QUERY]
Projeyle ilgili detaylı soru sorulduğunda:
1. Önce `index.md` üzerinden ilgili wiki sayfalarını bul ve oku.
2. Sadece genel AI bilgisi değil, wiki'deki proje bağlamı kullanılarak cevap verilir.
3. Önemli mimari kararsa, cevap yeni wiki sayfası olarak eklenir.

### 🟠 [LINT]
"Wiki'yi lint et" komutu verildiğinde:
1. Tüm `docs/wiki/` klasörü taranır.
2. Çelişkili bilgiler, güncelliğini yitirmiş kararlar, orphan sayfalar ve kırık linkler tespit edilir.
3. Rapor sunulur, onay alındıktan sonra düzeltmeler yapılır.

---

## 3. Sayfa Oluşturma Kuralları

- Her yeni sayfa `[[index]]` ve `[[log]]`'a link verir.
- İlk satır: `# Başlık`
- İkinci satır: tek cümle açıklama
- Üçüncü satır: `Bağlantılar: [[...]] | [[...]]`
- `log.md` formatı: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa Açıklama`

---

## 4. Bu Projeye Özel Notlar

- Proje dili: Türkçe (yorum ve wiki içerikleri)
- Kod dili: Python 3.8+
- UI framework: PyQt5 — tüm UI değişikliklerinde [[ui_katmani]] güncellenir.
- DB değişikliklerinde [[veritabani]] güncellenir.
- Yeni API entegrasyonlarında [[api_entegrasyonlari]] güncellenir.
- Yeni model/dataclass eklendiğinde [[modeller]] güncellenir.
