// qml/theme/Theme.qml
pragma Singleton
import QtQuick

QtObject {
    id: theme

    // --- Tema Modu ---
    property bool isDark: true

    // --- Renk Paleti (Modern Dark Navy / Slate + Açık Tema) ---
    property color bgApp: isDark ? "#0F172A" : "#F8FAFC"
    Behavior on bgApp { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color bgSidebar: isDark ? "#1E293B" : "#FFFFFF"
    Behavior on bgSidebar { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color bgCard: isDark ? "#1E293B" : "#FFFFFF"
    Behavior on bgCard { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color bgCardElevated: isDark ? "#334155" : "#F1F5F9"
    Behavior on bgCardElevated { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color bgInput: isDark ? "#0F172A" : "#F1F5F9"
    Behavior on bgInput { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    readonly property color bgModalOverlay: "#B3000000"// %70 karartmalı modal zemin

    // --- Vurgu Renkleri ---
    readonly property color primary: "#3B82F6"        // Ana Mavi
    readonly property color primaryHover: "#2563EB"   // Koyu Mavi Hover
    property color primaryLight: isDark ? "#60A5FA" : "#1D4ED8"
    Behavior on primaryLight { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    readonly property color primaryGlow: "#333B82F6"  // Saydam Mavi Parlama
    readonly property color accent: "#8B5CF6"         // Mor Vurgu
    readonly property color success: "#10B981"        // Yeşil
    readonly property color warning: "#F59E0B"        // Amber / Sarı
    readonly property color danger: "#EF4444"         // Kırmızı
    readonly property color info: "#06B6D4"           // Cyan

    // --- Metin Renkleri ---
    property color textPrimary: isDark ? "#F8FAFC" : "#0F172A"
    Behavior on textPrimary { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color textSecondary: isDark ? "#94A3B8" : "#475569"
    Behavior on textSecondary { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    property color textMuted: isDark ? "#64748B" : "#94A3B8"
    Behavior on textMuted { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }

    // --- Kenarlıklar ---
    property color borderSubtle: isDark ? "#334155" : "#E2E8F0"
    Behavior on borderSubtle { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }
    readonly property color borderFocus: "#3B82F6"    // Odaklanmış kenarlık
    property color borderLight: isDark ? "#475569" : "#CBD5E1"
    Behavior on borderLight { ColorAnimation { duration: theme.animNormal; easing.type: Easing.InOutQuad } }

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
