# constants.py
"""
Uygulama genelindeki sabit değerleri ve konfigürasyonları tutar.
"""

# Faaliyet türleri (list_page, add_page, edit_page tarafından kullanılır)
FAALIYET_TURLERI = ["Dizi", "Film", "Kitap", "Oyun", "Kurs", "Şehir"]

# ListPage için "Tümü" seçeneği
LIST_PAGE_FILTRE_SECENEKLERI = ["Hepsi"] + FAALIYET_TURLERI

# ComparePage için sabit sıralama
COMPARE_PAGE_DATA_ORDER = ["DIZI", "FILM", "KITAP", "KURS", "OYUN", "ŞEHIR"]