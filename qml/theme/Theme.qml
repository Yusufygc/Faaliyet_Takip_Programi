// qml/theme/Theme.qml
pragma Singleton
import QtQuick

QtObject {
    id: theme

    // --- Renk Paleti (Modern Dark Navy / Slate) ---
    readonly property color bgApp: "#0F172A"          // En koyu lacivert zemin
    readonly property color bgSidebar: "#1E293B"      // Sol menü
    readonly property color bgCard: "#1E293B"         // Kart ve yüzeyler
    readonly property color bgCardElevated: "#334155" // Hover ve seçili durum
    readonly property color bgInput: "#0F172A"        // Form girdi alanları
    readonly property color bgModalOverlay: "#B3000000"// %70 karartmalı modal zemin

    // --- Vurgu Renkleri ---
    readonly property color primary: "#3B82F6"        // Ana Mavi
    readonly property color primaryHover: "#2563EB"   // Koyu Mavi Hover
    readonly property color primaryLight: "#60A5FA"   // Açık Mavi
    readonly property color primaryGlow: "#333B82F6"  // Saydam Mavi Parlama
    readonly property color accent: "#8B5CF6"         // Mor Vurgu
    readonly property color success: "#10B981"        // Yeşil
    readonly property color warning: "#F59E0B"        // Amber / Sarı
    readonly property color danger: "#EF4444"         // Kırmızı
    readonly property color info: "#06B6D4"           // Cyan

    // --- Metin Renkleri ---
    readonly property color textPrimary: "#F8FAFC"    // Beyaza yakın ana metin
    readonly property color textSecondary: "#94A3B8"  // Açık gri ikincil metin
    readonly property color textMuted: "#64748B"      // Koyu gri pasif metin

    // --- Kenarlıklar ---
    readonly property color borderSubtle: "#334155"   // İnce ayırıcı
    readonly property color borderFocus: "#3B82F6"    // Odaklanmış kenarlık
    readonly property color borderLight: "#475569"    // Belirgin kenarlık

    // --- Kategori Renkleri ---
    function categoryColor(type) {
        if (!type) return "#64748B"
        var t = type.toLowerCase()
        if (t.indexOf("film") !== -1) return "#3B82F6"      // Mavi
        if (t.indexOf("dizi") !== -1) return "#8B5CF6"      // Mor
        if (t.indexOf("oyun") !== -1) return "#10B981"      // Yeşil
        if (t.indexOf("kitap") !== -1) return "#F59E0B"     // Turuncu
        if (t.indexOf("kurs") !== -1 || t.indexOf("eğitim") !== -1) return "#EC4899" // Pembe
        if (t.indexOf("şehir") !== -1 || t.indexOf("gezi") !== -1) return "#06B6D4" // Turkuaz
        return "#64748B"
    }

    // --- Yuvarlaklık (Border Radius) ---
    readonly property int radiusSm: 6
    readonly property int radiusMd: 10
    readonly property int radiusLg: 16
    readonly property int radiusXl: 24

    // --- Tipografi & İkon Fontu ---
    readonly property string fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
    readonly property FontLoader iconFontLoader: FontLoader {
        source: "../../assets/fonts/fa-solid-900.ttf"
    }
    readonly property string iconFontFamily: iconFontLoader.name !== "" ? iconFontLoader.name : "Font Awesome 6 Free"

    readonly property int fontXs: 11
    readonly property int fontSm: 13
    readonly property int fontMd: 15
    readonly property int fontLg: 18
    readonly property int fontXl: 22
    readonly property int fontTitle: 28

    // --- Animasyon Süreleri ---
    readonly property int animFast: 150
    readonly property int animNormal: 250
    readonly property int animSlow: 400
}
