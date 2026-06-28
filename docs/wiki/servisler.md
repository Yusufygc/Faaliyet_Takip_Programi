# Servisler

Harici API erişimi ve PDF üretimi: `services/` klasörü.

Bağlantılar: [[index]] | [[log]] | [[api_entegrasyonlari]] | [[mimari_genel_bakis]] | [[kontrolcüler]] | [[veritabani]]

---

## api_service.py — ApiService

Tüm harici API çağrıları bu sınıf üzerinden yapılır.

```python
class ApiService:
    tmdb_base_url = "https://api.themoviedb.org/3"
    rawg_base_url = "https://api.rawg.io/api"
```

### Temel Metodlar

| Metod | Açıklama |
|-------|----------|
| `get_recommendations(category, period, genre, page, is_turkish)` | Ana dispatch metodu; kategori → fetch_* metoduna yönlendirir |
| `fetch_movies(period, genre_id, page, is_turkish)` | TMDB film çekimi |
| `fetch_series(period, genre_id, page, is_turkish)` | TMDB dizi çekimi |
| `fetch_games(period, genre_slug, page, is_turkish)` | RAWG oyun çekimi |
| `fetch_books(period, subject, page, is_turkish)` | Google Books çekimi |
| `get_random_recommendation(category)` | Rastgele tek öneri |

### Standart Çıktı Formatı

Her `fetch_*` metodu şu yapıda dict listesi döner:
```python
{
    'title': str,
    'description': str,  # max 200 karakter
    'rating': float,     # 0-10 arası
    'image': str|None,   # thumbnail URL
    'date': str,         # yayın tarihi
    'type': str,         # 'Film' | 'Dizi' | 'Oyun' | 'Kitap'
    'id': int|str
}
```

### Sayfalama
`ITEMS_PER_PAGE = 12` — her sayfada maksimum 12 kart gösterilir.

---

## recommendation_config.py

Öneri sistemi için statik konfigürasyon.

| Sabit | Açıklama |
|-------|----------|
| `PERIODS` | Periyot key → `{label, type}` dict mapping |
| `PERIOD_ORDER` | Periyot sıralama listesi |
| `FILM_GENRES` | Film türü label → TMDB genre_id mapping |
| `DIZI_GENRES` | Dizi türü label → TMDB genre_id mapping |
| `OYUN_GENRES` | Oyun türü label → RAWG slug mapping |
| `KITAP_GENRES` | Kitap konusu label → Google Books subject string |
| `CULT_MOVIE_IDS` | Kült film TMDB ID listesi |
| `CULT_SERIES_IDS` | Kült dizi TMDB ID listesi |
| `MIN_VOTE_COUNT` | "Gizli hazine" için minimum oy sayısı eşiği |
| `MIN_RATING_ALL_TIME` | "En iyiler" için minimum rating |

---

## pdf_service.py — PdfService

ReportLab ile PDF raporu üretimi.

- Giriş: `repository.get_detailed_data_for_pdf(date_prefix)` çıktısı
- Çıkış: Masaüstüne `FaaliyetRaporu_YYYY-MM.pdf` olarak kaydedilir
- İçerik: Seçilen dönemin tüm aktiviteleri (tür, isim, tarih, yorum, puan)
