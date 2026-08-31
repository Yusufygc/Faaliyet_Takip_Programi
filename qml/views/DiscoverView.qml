// qml/views/DiscoverView.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../modals"

Rectangle {
    id: root

    color: Theme.bgApp

    signal quickAddActivity(string category, string title, real rating)

    function handleQuickAdd(category, title, rating) {
        var now = new Date()
        var dateStr = now.toISOString().split('T')[0]
        activityBridge.addActivity(
            category || "Film",
            title || "",
            dateStr,
            "Keşfet üzerinden eklendi.",
            rating || 0.0,
            ""
        )
        root.quickAddActivity(category, title, rating)
    }

    Column {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 18

        // --- 1. Üst Başlık & Rastgele Butonu ---
        Item {
            width: parent.width
            height: 42

            Column {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4

                Text {
                    text: "Keşfet & Öneriler"
                    font.pixelSize: Theme.fontTitle
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }

                Text {
                    text: "Film, Dizi, Oyun ve Kitap dünyasından trend ve kült öneriler"
                    font.pixelSize: Theme.fontSm
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            CustomButton {
                text: "Rastgele Öneri Al"
                icon: Icons.random
                variant: "primary"
                fontSize: Theme.fontSm + 1
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                busy: discoverBridge.isLoading
                onClicked: discoverBridge.getRandomRecommendation(discoverBridge.activeCategory)
            }
        }

        // --- 2. Kategori Sekmeleri (Vektör İkonlu Film, Dizi, Oyun, Kitap) ---
        Row {
            spacing: 10

            Repeater {
                model: [
                    { "name": "Film",  "icon": Icons.film },
                    { "name": "Dizi",  "icon": Icons.tv },
                    { "name": "Oyun",  "icon": Icons.game },
                    { "name": "Kitap", "icon": Icons.book }
                ]

                Rectangle {
                    height: 42
                    implicitWidth: 125
                    radius: Theme.radiusMd
                    color: discoverBridge.activeCategory === modelData.name ? Theme.primary : (catMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard)
                    border.color: discoverBridge.activeCategory === modelData.name ? "transparent" : Theme.borderSubtle
                    border.width: 1

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }

                    Row {
                        anchors.centerIn: parent
                        spacing: 8

                        Icon {
                            name: modelData.icon
                            size: 15
                            color: discoverBridge.activeCategory === modelData.name ? "#FFFFFF" : Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.name
                            font.pixelSize: Theme.fontSm + 1
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: discoverBridge.activeCategory === modelData.name ? "#FFFFFF" : Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    MouseArea {
                        id: catMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: discoverBridge.setCategory(modelData.name)
                    }
                }
            }
        }

        // --- 3. Filtre Çubuğu (Dönem, Tür & Türkçe Filtresi) ---
        Rectangle {
            width: parent.width
            height: 56
            radius: Theme.radiusLg
            color: Theme.bgCard
            border.color: Theme.borderSubtle
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 8
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 16

                // Dönem
                Row {
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "Dönem:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        width: 210
                        textRole: "name"
                        model: discoverBridge.periods
                        onActivated: {
                            var p = discoverBridge.periods[currentIndex]
                            if (p) discoverBridge.setPeriod(p.key)
                        }
                    }
                }

                // Tür Filtresi
                Row {
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "Tür:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        id: genreCombo
                        width: 160
                        model: discoverBridge.availableGenres
                        onActivated: discoverBridge.setGenre(currentText)
                    }
                }

                // Türkçe Yapımlar Filtresi (Şık CustomCheckBox)
                CustomCheckBox {
                    id: trCheck
                    text: "TR Türkçe Yapımlar"
                    anchors.verticalCenter: parent.verticalCenter
                    visible: discoverBridge.activeCategory === "Film" || discoverBridge.activeCategory === "Dizi"
                    onToggled: function(isChecked) {
                        discoverBridge.setTurkishOnly(isChecked)
                    }
                }

                Item { width: 1; height: 1 }

                CustomButton {
                    text: "Yenile"
                    icon: Icons.refresh
                    variant: "secondary"
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: discoverBridge.fetchRecommendations()
                }
            }
        }

        // --- 4. Medya Kartları Grid Alanı ---
        Item {
            width: parent.width
            height: parent.height - 200
            clip: true

            BusyIndicator {
                anchors.centerIn: parent
                running: discoverBridge.isLoading
                visible: discoverBridge.isLoading
                z: 10
            }

            EmptyState {
                anchors.centerIn: parent
                visible: discoverBridge.items.length === 0 && !discoverBridge.isLoading
                icon: Icons.search
                title: "Sonuç Bulunamadı"
                description: "Seçtiğiniz kriterlere uygun içerik bulunamadı veya API anahtarınızı Ayarlar sayfasından girmeniz gerekiyor olabilir."
                actionText: "Ayarları Aç"
                onActionClicked: sidebar.activeIndex = 5
            }

            GridView {
                id: discoverGrid
                anchors.fill: parent
                visible: discoverBridge.items.length > 0 && !discoverBridge.isLoading
                clip: true
                cellWidth: 235
                cellHeight: 365
                model: discoverBridge.items

                delegate: Rectangle {
                    width: 215
                    height: 345
                    radius: Theme.radiusLg
                    color: mediaMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard
                    border.color: mediaMouse.containsMouse ? Theme.primary : Theme.borderSubtle
                    border.width: 1
                    clip: true

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }

                    Column {
                        anchors.fill: parent
                        spacing: 0

                        // 1. Afiş Görseli (240px Dikey Poster)
                        Rectangle {
                            width: parent.width
                            height: 220
                            color: Theme.bgInput
                            clip: true

                            // Yükleniyor / Yoksa Gradyan
                            Rectangle {
                                anchors.fill: parent
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: Theme.categoryColor(modelData.category) }
                                    GradientStop { position: 1.0; color: Qt.darker(Theme.categoryColor(modelData.category), 2.2) }
                                }
                                opacity: posterImg.status === Image.Ready ? 0 : 0.65
                                Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }
                            }

                            // Kategori İkonu (Resim yokken)
                            Icon {
                                name: modelData.category === "Film" ? Icons.film : (modelData.category === "Dizi" ? Icons.tv : (modelData.category === "Oyun" ? Icons.game : Icons.book))
                                size: 40
                                color: "#FFFFFF"
                                opacity: 0.85
                                anchors.centerIn: parent
                                visible: posterImg.status !== Image.Ready
                            }

                            Image {
                                id: posterImg
                                anchors.fill: parent
                                source: (modelData.poster || modelData.image || "")
                                fillMode: Image.PreserveAspectCrop
                                asynchronous: true
                            }

                            // Kategori Rozeti
                            Badge {
                                anchors.top: parent.top
                                anchors.left: parent.left
                                anchors.margins: 8
                                text: modelData.category
                                badgeColor: Theme.categoryColor(modelData.category)
                            }

                            // Puan Rozeti
                            Rectangle {
                                anchors.top: parent.top
                                anchors.right: parent.right
                                anchors.margins: 8
                                width: 44
                                height: 24
                                radius: Theme.radiusSm
                                color: Qt.rgba(0, 0, 0, 0.75)

                                Row {
                                    anchors.centerIn: parent
                                    spacing: 3

                                    Icon {
                                        name: Icons.star
                                        size: 10
                                        color: Theme.warning
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Text {
                                        text: modelData.rating ? modelData.rating.toFixed(1) : "-"
                                        font.pixelSize: Theme.fontXs
                                        font.bold: true
                                        color: "#FFFFFF"
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }
                            }
                        }

                        // 2. Bilgiler Alanı
                        Column {
                            width: parent.width
                            height: 125
                            padding: 10
                            spacing: 4

                            Text {
                                text: modelData.title
                                font.pixelSize: Theme.fontSm + 1
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                width: parent.width - 20
                            }

                            Text {
                                text: modelData.overview || "Açıklama bulunmuyor."
                                font.pixelSize: Theme.fontXs - 1
                                font.family: Theme.fontFamily
                                color: Theme.textSecondary
                                wrapMode: Text.WordWrap
                                elide: Text.ElideRight
                                maximumLineCount: 2
                                width: parent.width - 20
                            }

                            Item { width: 1; height: 1 }

                            // Faaliyetlerime Ekle Butonu
                            CustomButton {
                                text: "Faaliyetlerime Ekle"
                                icon: Icons.add
                                variant: "primary"
                                fullWidth: true
                                fontSize: Theme.fontXs
                                onClicked: root.handleQuickAdd(modelData.category, modelData.title, modelData.rating)
                            }
                        }
                    }

                    MouseArea {
                        id: mediaMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        z: -1
                    }
                }
            }
        }
    }

    // ✨ Rastgele Öneri Modalı ✨
    RandomPickModal {
        id: randomPickModal
        onAddRequested: function(cat, title, rat) {
            root.handleQuickAdd(cat, title, rat)
        }
    }

    Connections {
        target: discoverBridge
        function onRandomRecommendationFound(item) {
            randomPickModal.openWith(item)
        }
    }
}
