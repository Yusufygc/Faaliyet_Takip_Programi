// qml/theme/Icons.qml
pragma Singleton
import QtQuick

QtObject {
    id: icons

    // — Navigasyon & Logo —
    readonly property string app_logo: "\uf200"        // chart-pie
    readonly property string menu: "\uf0c9"            // bars (hamburger)
    readonly property string nav_list: "\uf03a"        // list
    readonly property string nav_stats: "\ue473"       // chart-simple
    readonly property string nav_plans: "\uf140"       // bullseye / target
    readonly property string nav_discover: "\uf14e"    // compass
    readonly property string nav_compare: "\uf24e"     // scale-balanced
    readonly property string nav_settings: "\uf013"    // gear
    
    // — CRUD Eylemleri —
    readonly property string add: "\uf067"             // plus
    readonly property string edit: "\uf044"            // pen-to-square
    readonly property string delete_icon: "\uf2ed"     // trash-can
    readonly property string save: "\uf0c7"            // floppy-disk
    readonly property string refresh: "\uf021"         // rotate / sync
    readonly property string search: "\uf002"          // magnifying-glass
    readonly property string random: "\uf522"          // dice
    readonly property string close: "\uf00d"           // xmark
    readonly property string filter: "\uf0b0"          // filter
    
    // — Görünüm & Göstergeler —
    readonly property string list_view: "\uf03a"       // list
    readonly property string grid_view: "\uf009"       // table-cells-large
    readonly property string pdf: "\uf1c1"             // file-pdf
    readonly property string calendar: "\uf133"        // calendar-days
    readonly property string star: "\uf005"            // star
    readonly property string check: "\uf058"           // circle-check
    readonly property string warning: "\uf071"         // triangle-exclamation
    readonly property string error: "\uf057"           // circle-xmark
    readonly property string trophy: "\uf091"          // trophy
    readonly property string pin: "\uf08d"             // thumbtack
    readonly property string key: "\uf084"             // key
    readonly property string clock: "\uf017"           // clock
    
    // — Klasör & Hedefler —
    readonly property string folder: "\uf07b"          // folder
    readonly property string folder_open: "\uf07c"     // folder-open
    readonly property string folder_plus: "\uf65e"     // folder-plus
    
    // — Faaliyet Türleri —
    readonly property string film: "\uf008"            // film
    readonly property string tv: "\uf26c"              // tv
    readonly property string game: "\uf11b"            // gamepad
    readonly property string book: "\uf02d"            // book
    readonly property string course: "\uf19d"          // graduation-cap
    readonly property string city: "\uf3c5"            // location-dot
    
    // — Oklar & Sayfalama —
    readonly property string arrow_left: "\uf060"      // arrow-left
    readonly property string arrow_right: "\uf061"     // arrow-right
    readonly property string chevron_left: "\uf053"    // chevron-left
    readonly property string chevron_right: "\uf054"   // chevron-right
    readonly property string chevron_down: "\uf078"    // chevron-down
}
