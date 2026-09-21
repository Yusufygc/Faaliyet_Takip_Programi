// qml/components/Sidebar.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property int activeIndex: 0
    property bool isCollapsed: false
    signal navigate(int index, string route)

    implicitWidth: isCollapsed ? 70 : 255
    implicitHeight: parent ? parent.height : 800
    color: Theme.bgSidebar
    border.color: Theme.borderSubtle
    border.width: 1
    clip: false // Tooltip'lerin taşabilmesi için

    Behavior on implicitWidth {
        NumberAnimation { duration: Theme.animNormal; easing.type: Easing.InOutQuad }
    }

    readonly property var menuItems: [
        { "title": "Faaliyetler",   "icon": Icons.nav_list,     "route": "activities" },
        { "title": "İstatistikler", "icon": Icons.nav_stats,    "route": "stats" },
        { "title": "Hedefler",      "icon": Icons.nav_plans,    "route": "plans" },
        { "title": "Keşfet",        "icon": Icons.nav_discover, "route": "discover" },
        { "title": "Karşılaştır",   "icon": Icons.nav_compare,  "route": "compare" },
        { "title": "Ayarlar",       "icon": Icons.nav_settings, "route": "settings" }
    ]

    // --- 1. Üst Kısım: Hamburger Menü Butonu & Logo ---
    Item {
        id: headerArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 84

        // Genişletilmiş Durum: Hamburger + Logo + Başlık
        Row {
            anchors.left: parent.left
            anchors.leftMargin: root.isCollapsed ? 17 : 14
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            // Hamburger Menü Aç/Kapat Butonu
            Rectangle {
                width: 36
                height: 36
                radius: Theme.radiusMd
                color: burgerHover.containsMouse ? Theme.bgCardElevated : "transparent"
                border.color: burgerHover.containsMouse ? Theme.borderLight : "transparent"
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                Icon {
                    name: Icons.menu
                    size: 15
                    color: burgerHover.containsMouse ? Theme.primaryLight : Theme.textSecondary
                    anchors.centerIn: parent
                }

                MouseArea {
                    id: burgerHover
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.isCollapsed = !root.isCollapsed
                }
            }

            // Logo & Başlık Alanı (Daralınca yumuşakça kaybolur)
            Row {
                spacing: 8
                anchors.verticalCenter: parent.verticalCenter
                opacity: root.isCollapsed ? 0.0 : 1.0
                visible: opacity > 0.01

                Behavior on opacity {
                    NumberAnimation { duration: Theme.animFast }
                }

                Rectangle {
                    width: 30
                    height: 30
                    radius: Theme.radiusMd
                    color: Theme.primary
                    anchors.verticalCenter: parent.verticalCenter

                    Icon {
                        name: Icons.app_logo
                        size: 15
                        color: "#FFFFFF"
                        anchors.centerIn: parent
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 1

                    Text {
                        text: "FAALİYET TAKİP"
                        font.pixelSize: Theme.fontSm + 1
                        font.bold: true
                        font.letterSpacing: 0.8
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "Aktivite & Planlama"
                        font.pixelSize: Theme.fontXs - 1
                        font.family: Theme.fontFamily
                        color: Theme.textMuted
                    }
                }
            }
        }

        // Ayırıcı Çizgi
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: root.isCollapsed ? 8 : 14
            anchors.rightMargin: root.isCollapsed ? 8 : 14
            height: 1
            color: Theme.borderSubtle
        }
    }

    // --- 2. Menü Butonları Listesi ---
    ListView {
        id: menuList
        anchors.top: headerArea.bottom
        anchors.bottom: footerArea.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: 16
        anchors.bottomMargin: 16
        clip: false
        model: root.menuItems
        spacing: 6

        delegate: Rectangle {
            id: navItem
            width: root.isCollapsed ? 46 : (menuList.width - 24)
            height: 46
            anchors.horizontalCenter: parent.horizontalCenter
            radius: Theme.radiusMd

            property bool isSelected: root.activeIndex === index

            color: isSelected ? Theme.primaryGlow : (itemMouse.containsMouse ? Theme.bgCardElevated : "transparent")
            border.color: isSelected ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.4) : "transparent"
            border.width: isSelected ? 1 : 0

            Behavior on color { ColorAnimation { duration: Theme.animFast } }
            Behavior on width { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.InOutQuad } }

            // Sol Aktif Çubuk
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.topMargin: 8
                anchors.bottomMargin: 8
                width: 3
                radius: 2
                color: Theme.primary
                visible: navItem.isSelected
            }

            // İkon + Başlık Düzeni
            Item {
                anchors.fill: parent

                // İkon (Daraltılmışken ortalanır, genişken solda hizalanır)
                Icon {
                    name: modelData.icon
                    size: 18
                    color: navItem.isSelected ? Theme.primaryLight : (itemMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: root.isCollapsed ? undefined : parent.left
                    anchors.leftMargin: root.isCollapsed ? 0 : 16
                    anchors.horizontalCenter: root.isCollapsed ? parent.horizontalCenter : undefined
                }

                // Başlık Metni (Genişletilmişken görünür)
                Text {
                    text: modelData.title
                    font.pixelSize: Theme.fontSm + 1
                    font.bold: navItem.isSelected
                    font.family: Theme.fontFamily
                    color: navItem.isSelected ? Theme.primaryLight : (itemMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                    anchors.left: parent.left
                    anchors.leftMargin: 48
                    anchors.verticalCenter: parent.verticalCenter
                    opacity: root.isCollapsed ? 0.0 : 1.0
                    visible: opacity > 0.01

                    Behavior on opacity {
                        NumberAnimation { duration: Theme.animFast }
                    }
                }
            }

            // Tıklama & Hover Alanı
            MouseArea {
                id: itemMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    root.activeIndex = index
                    root.navigate(index, modelData.route)
                }
            }

            // Daraltılmış Modda Sağda Açılan Floating Hover Tooltip Balonu
            Rectangle {
                id: floatingTooltip
                visible: root.isCollapsed && itemMouse.containsMouse
                anchors.left: parent.right
                anchors.leftMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                width: tooltipText.implicitWidth + 20
                height: 32
                radius: Theme.radiusSm
                color: Theme.bgCardElevated
                border.color: Theme.primary
                border.width: 1
                z: 1000

                Text {
                    id: tooltipText
                    anchors.centerIn: parent
                    text: modelData.title
                    font.pixelSize: Theme.fontSm
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }
            }
        }
    }

    // --- 3. Alt Bilgi (Tema Değiştirici & Sürüm) ---
    Rectangle {
        id: footerArea
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 88
        color: "transparent"

        Rectangle {
            id: footerSeparator
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: root.isCollapsed ? 8 : 14
            anchors.rightMargin: root.isCollapsed ? 8 : 14
            height: 1
            color: Theme.borderSubtle
        }

        Column {
            anchors.top: footerSeparator.bottom
            anchors.topMargin: 12
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8

            ThemeToggle {
                isCollapsed: root.isCollapsed
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: root.isCollapsed ? "v2.0" : "v2.0 • Modern QML Edition"
                font.pixelSize: Theme.fontXs - 1
                font.family: Theme.fontFamily
                color: Theme.textMuted
            }
        }
    }
}
