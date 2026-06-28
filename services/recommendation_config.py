# -*- coding: utf-8 -*-
"""
Keşfet & Öneriler modülü için yapılandırma dosyası.
Periyotlar, türler ve API sabitleri burada tanımlanır.
"""

# ============================================================================
# PERİYOT / DÖNEM TANIMLARI
# ============================================================================
# Her periyodun bir key'i, görünen adı ve API parametreleri var

PERIODS = {
    "this_month": {
        "name": "📅 Bu Ayın Trendleri",
        "description": "Bu ay çıkan popüler içerikler",
        "type": "date_range"
    },
    "last_year": {
        "name": "🗓️ Geçen Yılın Efsaneleri",
        "description": "Geçen yıl çıkan en iyiler",
        "type": "date_range"
    },
    "all_time_best": {
        "name": "🏆 Tüm Zamanların En İyileri",
        "description": "Tüm zamanların en yüksek puanlı içerikleri",
        "type": "top_rated"
    },
    "must_see": {
        "name": "⭐ Mutlaka İzlenmeli/Oynanmalı",
        "description": "En popüler ve beğenilen içerikler",
        "type": "popular"
    },
    "cult_classics": {
        "name": "🎭 Kült Klasikler",
        "description": "Kült statüsü kazanmış efsaneler",
        "type": "cult"
    },
    "hidden_gems": {
        "name": "💎 Gizli Hazineler",
        "description": "Az bilinen ama kaliteli içerikler",
        "type": "hidden"
    },
    "new_releases": {
        "name": "🆕 Yeni Çıkanlar",
        "description": "Son 3 ayda çıkan içerikler",
        "type": "new"
    },
    "upcoming": {
        "name": "🔜 Yakında Gelecekler",
        "description": "Yakında çıkacak beklenen içerikler",
        "type": "upcoming"
    }
}

# Period key listesi (UI için sıralı)
PERIOD_ORDER = [
    "this_month",
    "new_releases",
    "all_time_best",
    "must_see",
    "cult_classics",
    "hidden_gems",
    "last_year",
    "upcoming"
]

# ============================================================================
# TÜR / KATEGORİ TANIMLARI
# ============================================================================

# TMDB Film Türleri
FILM_GENRES = {
    "Tümü": None,
    "Aksiyon": 28,
    "Komedi": 35,
    "Dram": 18,
    "Korku": 27,
    "Bilim Kurgu": 878,
    "Romantik": 10749,
    "Animasyon": 16,
    "Gerilim": 53,
    "Suç": 80,
    "Belgesel": 99,
    "Fantezi": 14,
    "Macera": 12,
    "Savaş": 10752,
    "Western": 37
}

# TMDB Dizi Türleri
DIZI_GENRES = {
    "Tümü": None,
    "Aksiyon & Macera": 10759,
    "Komedi": 35,
    "Dram": 18,
    "Suç": 80,
    "Belgesel": 99,
    "Aile": 10751,
    "Animasyon": 16,
    "Gizem": 9648,
    "Bilim Kurgu & Fantezi": 10765,
    "Reality": 10764
}

# RAWG Oyun Türleri
OYUN_GENRES = {
    "Tümü": None,
    "Aksiyon": "action",
    "RPG": "role-playing-games-rpg",
    "Strateji": "strategy",
    "Spor": "sports",
    "Yarış": "racing",
    "Macera": "adventure",
    "Bulmaca": "puzzle",
    "Shooter": "shooter",
    "Platform": "platformer",
    "Simülasyon": "simulation",
    "Dövüş": "fighting",
    "Indie": "indie"
}

# Google Books Kitap Türleri (subject search)
KITAP_GENRES = {
    "Tümü": "fiction",
    "Dünya Klasikleri": "classic literature",
    "Türk Klasikleri": "turkish literature classics",
    "Gerilim": "thriller",
    "Romantik": "romance",
    "Bilim Kurgu": "science fiction",
    "Fantastik": "fantasy",
    "Korku": "horror",
    "Tarih": "history",
    "Gizem": "mystery",
    "Polisiye": "detective fiction",
    "Biyografi": "biography",
    "Felsefe": "philosophy",
    "Psikoloji": "psychology",
    "Kişisel Gelişim": "self-help"
}

# ============================================================================
# KÜLT KLASİKLER LİSTESİ (TMDB ID'leri)
# ============================================================================
# Bu manuel listeler, API'nin bulamayacağı klasikleri garantilemek için

CULT_MOVIE_IDS = [
    550,    # Fight Club
    680,    # Pulp Fiction
    238,    # The Godfather
    424,    # Schindler's List
    389,    # 12 Angry Men
    129,    # Spirited Away
    497,    # The Green Mile
    13,     # Forrest Gump
    155,    # The Dark Knight
    278,    # The Shawshank Redemption
]

CULT_SERIES_IDS = [
    1396,   # Breaking Bad
    1399,   # Game of Thrones
    60625,  # Rick and Morty
    1418,   # The Big Bang Theory
    1100,   # How I Met Your Mother
    456,    # The Simpsons
    2316,   # The Office
    4614,   # Lost
    1402,   # The Walking Dead
    66732,  # Stranger Things
]

# ============================================================================
# API YAPILANDIRMASI
# ============================================================================

# Minimum puan eşikleri
MIN_VOTE_COUNT = 100  # Minimum oy sayısı (gizli hazineler hariç)
MIN_RATING_ALL_TIME = 8.0  # Tüm zamanların en iyileri için min puan
MIN_RATING_CULT = 7.5  # Kült klasikler için min puan
