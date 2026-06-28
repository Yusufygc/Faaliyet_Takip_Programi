# API Entegrasyonları

3 harici API: TMDB (film/dizi), RAWG (oyun), Google Books (kitap). Tümü `ApiService` sınıfı üzerinden erişilir.

Bağlantılar: [[index]] | [[log]] | [[servisler]] | [[mimari_genel_bakis]] | [[veritabani]]

---

## API Özeti

| API | Kategori | Kimlik Doğrulama | Ücretsiz Limit |
|-----|----------|-----------------|----------------|
| TMDB v3 | Film, Dizi | `api_key` query param | ~1000 istek/gün |
| RAWG | Oyun | `key` query param | 20.000 istek/ay |
| Google Books v1 | Kitap | Anonim (API key gerekmez) | Sınırsız |

API anahtarları `keyring` ile güvenli saklanır, `.env` kullanılmaz. Detay: [[kontrolcüler]]

---

## TMDB

**Base URL:** `https://api.themoviedb.org/3`

### Kullanılan Endpoint'ler

| Endpoint | Kullanım |
|----------|----------|
| `/discover/movie` | Tarih aralığı, tür, ülke filtreli film arama |
| `/movie/top_rated` | En iyi filmler |
| `/movie/popular` | En popüler filmler |
| `/movie/upcoming` | Yakında çıkacaklar |
| `/movie/{id}` | Kült film detayı (tek tek çekme) |
| `/discover/tv` | Dizi keşif |
| `/tv/top_rated` | En iyi diziler |
| `/tv/popular` | En popüler diziler |
| `/tv/on_the_air` | Yakında başlayacak diziler |
| `/tv/{id}` | Kült dizi detayı |

### Ortak Parametreler
- `language=tr-TR` — Türkçe içerik
- `with_origin_country=TR` — Türkçe yapım filtresi
- `page` — Sayfalama
- Poster URL: `https://image.tmdb.org/t/p/w500{poster_path}`

### Sayfa Başına İçerik
`ITEMS_PER_PAGE = 12` (services/api_service.py)

---

## RAWG

**Base URL:** `https://api.rawg.io/api`

### Kullanılan Endpoint'ler

| Endpoint | Kullanım |
|----------|----------|
| `/games` | Tüm oyun sorguları (filtreler parametre ile) |

### Önemli Parametreler
- `ordering=-added` → Popüler
- `ordering=-metacritic`, `metacritic=80,100` → En iyi
- `ordering=released` → Yakında çıkacaklar
- `dates=YYYY-MM-DD,YYYY-MM-DD` → Tarih aralığı
- `genres=<slug>` → Tür filtresi (örn: `action`, `rpg`)

**Not:** RAWG'da Türkçe yapım filtresi yoktur; `is_turkish` bayrağı oyunlar için görmezden gelinir.

---

## Google Books

**Base URL:** `https://www.googleapis.com/books/v1/volumes`

### Parametreler
- `q=subject:{subject}` — Konu bazlı arama (örn: `subject:fiction`)
- `langRestrict=tr` — Türkçe kitaplar
- `orderBy=relevance|newest`
- `startIndex=(page-1)*12` — Sayfalama
- `maxResults=12`
- Rating: `averageRating * 2` (5 üzerinden → 10 üzerinden)

---

## Öneri Periyotları

`services/recommendation_config.py::PERIODS` tanımlar:

| Periyot Key | Label | Tip |
|-------------|-------|-----|
| `this_month` | Bu Ayın Trendleri | `date_range` |
| `new_releases` | Yeni Çıkanlar | `new` |
| `all_time_best` | Tüm Zamanların En İyileri | `top_rated` |
| `must_see` | Mutlaka İzlenmeli | `popular` |
| `cult_classics` | Kült Klasikler | `cult` |
| `hidden_gems` | Gizli Hazineler | `hidden` |
| `upcoming` | Yakında Gelecekler | `upcoming` |

---

## Önbellek Sistemi

API sonuçları `recommendation_cache` tablosunda 7 gün saklanır:
- Cache hit → API çağrısı yapılmaz
- "Yenile" butonu → Cache temizlenir, taze veri çekilir
- "Eski Verileri Göster" → Cache'deki tüm önceki veriler görüntülenir

Detay: [[veritabani]]

---

## Rastgele Öneri

`ApiService.get_random_recommendation(category=None)`:
- Kategori belirtilmezse rastgele seçilir
- Periyotlar: `['all_time_best', 'must_see', 'cult_classics', 'hidden_gems']`
- Sayfa: 1-3 arası rastgele
- Fallback: başarısız olursa `must_see` kategori 1. sayfasından seçer
