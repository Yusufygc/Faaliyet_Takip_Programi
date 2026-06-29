# services/icon_service.py
import qtawesome as qta
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


class IconService:
    """
    Merkezi icon yöneticisi — qtawesome (FontAwesome 5) tabanlı.

    Tema değişimi: IconService.set_theme({'content': '#1E1E1E', ...})
    ile tüm renk anahtarları güncellenir. Mevcut tema: dark sidebar + light content.
    """

    # Renk anahtarları. Tema sistemi eklenince sadece bu dict güncellenir.
    _THEME = {
        "sidebar":  "#FFFFFF",   # Koyu sidebar üzeri — beyaz
        "primary":  "#3B82F6",   # Mavi — birincil eylem
        "success":  "#22C55E",   # Yeşil — başarı / ekle
        "warning":  "#F59E0B",   # Amber — uyarı / yıldız
        "danger":   "#EF4444",   # Kırmızı — sil / hata
        "muted":    "#64748B",   # Gri — ikincil/pasif
        "content":  "#2C3E50",   # Koyu lacivert — içerik alanı
    }

    # (fontawesome_id, renk_anahtarı)
    _ICONS = {
        # — Sidebar navigasyon —
        "nav_add":       ("fa5s.plus-circle",          "sidebar"),
        "nav_list":      ("fa5s.list-ul",              "sidebar"),
        "nav_stats":     ("fa5s.chart-bar",            "sidebar"),
        "nav_compare":   ("fa5s.columns",              "sidebar"),
        "nav_pdf":       ("fa5s.file-pdf",             "sidebar"),
        "nav_plans":     ("fa5s.bullseye",             "sidebar"),
        "nav_discover":  ("fa5s.rocket",               "sidebar"),
        "nav_settings":  ("fa5s.cog",                 "sidebar"),
        "app_logo":      ("fa5s.chart-pie",            "sidebar"),

        # — CRUD eylemleri —
        "add":           ("fa5s.plus",                 "success"),
        "edit":          ("fa5s.edit",                "primary"),
        "delete":        ("fa5s.trash-alt",            "danger"),
        "save":          ("fa5s.save",                 "sidebar"),
        "save_dark":     ("fa5s.save",                 "primary"),
        "refresh":       ("fa5s.sync-alt",             "sidebar"),
        "load_more":     ("fa5s.chevron-down",         "sidebar"),
        "random":        ("fa5s.random",               "sidebar"),
        "search":        ("fa5s.search",               "muted"),
        "key":           ("fa5s.key",                  "muted"),
        "menu":          ("fa5s.bars",                 "sidebar"),

        # — Durum göstergeleri —
        "star":          ("fa5s.star",                 "warning"),
        "check":         ("fa5s.check-circle",         "success"),
        "warning":       ("fa5s.exclamation-triangle", "warning"),
        "error":         ("fa5s.times-circle",         "danger"),
        "clock":         ("fa5s.clock",                "muted"),
        "inbox":         ("fa5s.inbox",                "muted"),
        "archive":       ("fa5s.box",                  "muted"),

        # — UI öğeleri —
        "calendar":      ("fa5s.calendar-alt",         "muted"),
        "folder":        ("fa5s.folder",               "warning"),
        "folder_open":   ("fa5s.folder-open",          "warning"),
        "folder_add":    ("fa5s.folder-plus",          "primary"),
        "pin":           ("fa5s.thumbtack",            "primary"),
        "image":         ("fa5s.image",                "muted"),
        "chart_line":    ("fa5s.chart-line",           "primary"),
        "chart_bar":     ("fa5s.chart-bar",            "primary"),
        "trophy":        ("fa5s.trophy",               "warning"),
        "prev":          ("fa5s.angle-double-left",    "content"),
        "compare":       ("fa5s.calendar-week",        "content"),
        "custom":        ("fa5s.sliders-h",            "danger"),
        "tasks":         ("fa5s.bookmark",             "primary"),
    }

    @classmethod
    def get(cls, name: str, color_override: str = None) -> QIcon:
        """QIcon döndürür — QPushButton ve QAction için kullan."""
        entry = cls._ICONS.get(name)
        if not entry:
            return QIcon()
        fa_id, color_key = entry
        color = color_override or cls._THEME.get(color_key, "#2C3E50")
        return qta.icon(fa_id, color=color)

    @classmethod
    def pixmap(cls, name: str, size: int = 20, color_override: str = None) -> QPixmap:
        """QPixmap döndürür — QLabel için kullan."""
        return cls.get(name, color_override).pixmap(QSize(size, size))

    @classmethod
    def set_theme(cls, updates: dict):
        """Renk anahtarlarını günceller. Gelecekte tema sistemi için."""
        cls._THEME.update(updates)

    @classmethod
    def title_widget(cls, icon_name: str, text: str, style: str = "",
                     icon_size: int = 24) -> QWidget:
        """Icon + metin içeren başlık widget'ı döndürür (QLabel yerine kullan)."""
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(cls.pixmap(icon_name, icon_size))
        lbl_icon.setStyleSheet("background: transparent;")
        lay.addWidget(lbl_icon)

        lbl_text = QLabel(text)
        lbl_text.setStyleSheet(style)
        lay.addWidget(lbl_text)
        lay.addStretch()

        return w
