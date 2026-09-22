// qml/modals/MediaPreviewModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property var currentItem: null
    property var detailInfo: ({})

    signal addRequested(string category, string title, real rating)

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openWith(item) {
        currentItem = item || null
        detailInfo = {}
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
    }

    function buildDetailRows() {
        var rows = []
        var d = root.detailInfo || {}
        if (d.genres) rows.push({ label: "Tür", value: d.genres })
        if (d.runtime) rows.push({ label: "Süre", value: d.runtime })
        if (d.seasons) rows.push({ label: "Sezon", value: d.seasons })
        if (d.episodes) rows.push({ label: "Bölüm", value: d.episodes })
        if (d.cast) rows.push({ label: "Oyuncular", value: d.cast })
        if (d.platforms) rows.push({ label: "Platformlar", value: d.platforms })
        if (d.author) rows.push({ label: "Yazar", value: d.author })
        if (d.publisher) rows.push({ label: "Yayınevi", value: d.publisher })
        if (d.pageCount) rows.push({ label: "Sayfa Sayısı", value: d.pageCount + " sayfa" })
        if (d.tagline) rows.push({ label: "Slogan", value: d.tagline })
        return rows
    }

    Connections {
        target: discoverBridge
        function onItemDetailsLoaded(details) {
            root.detailInfo = details
        }
    }

    // Önizleme Kartı
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 620)
        implicitHeight: modalContent.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.accent
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
            id: modalContent
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            // Başlık
            Row {
                width: parent.width

                Column {
                    width: parent.width - 40
                    spacing: 4

                    Row {
                        spacing: 8
                        Icon {
                            name: Icons.search
                            size: 16
                            color: Theme.accent
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "İÇERİK ÖNİZLEME"
                            font.pixelSize: Theme.fontLg
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        BusyIndicator {
                            width: 16
                            height: 16
                            running: discoverBridge.isLoadingDetails
                            visible: discoverBridge.isLoadingDetails
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }

                Rectangle {
                    width: 32
                    height: 32
                    radius: 16
                    color: closeHover.containsMouse ? Theme.bgCardElevated : "transparent"

                    Icon {
                        name: Icons.close
                        size: 12
                        color: closeHover.containsMouse ? Theme.textPrimary : Theme.textSecondary
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        id: closeHover
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.borderSubtle
            }

            // İçerik (Poster + Bilgiler)
            Row {
                id: contentRow
                width: parent.width
                spacing: 20

                // Poster
                Rectangle {
                    width: 180
                    height: 270
                    radius: Theme.radiusMd
                    color: Theme.bgInput
                    border.color: Theme.borderSubtle
                    border.width: 1
                    clip: true

                    Image {
                        id: previewPosterImg
                        anchors.fill: parent
                        source: root.currentItem ? (root.currentItem.poster || root.currentItem.image || "") : ""
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                    }

                    Icon {
                        anchors.centerIn: parent
                        name: root.currentItem && root.currentItem.category === "Dizi" ? Icons.tv : (root.currentItem && root.currentItem.category === "Oyun" ? Icons.game : (root.currentItem && root.currentItem.category === "Kitap" ? Icons.book : Icons.film))
                        size: 40
                        color: Theme.textMuted
                        visible: previewPosterImg.status !== Image.Ready
                    }
                }

                // Detaylar
                Column {
                    id: detailsColumn
                    width: parent.width - 200
                    spacing: 10

                    Row {
                        spacing: 8

                        Badge {
                            text: root.currentItem ? root.currentItem.category : ""
                            badgeColor: Theme.categoryColor(root.currentItem ? root.currentItem.category : "")
                        }

                        Badge {
                            text: root.detailInfo ? (root.detailInfo.genres || "") : ""
                            badgeColor: Theme.textMuted
                            visible: text !== ""
                        }

                        Badge {
                            text: root.currentItem ? (root.currentItem.year || "") : ""
                            badgeColor: Theme.textMuted
                            visible: text !== ""
                        }

                        // Puan Rozeti
                        Rectangle {
                            height: 22
                            implicitWidth: rateRow.implicitWidth + 12
                            radius: Theme.radiusSm
                            color: Qt.rgba(0, 0, 0, 0.6)
                            border.color: Theme.borderSubtle
                            border.width: 1

                            Row {
                                id: rateRow
                                anchors.centerIn: parent
                                spacing: 4

                                Icon {
                                    name: Icons.star
                                    size: 10
                                    color: Theme.warning
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: root.currentItem && root.currentItem.rating ? root.currentItem.rating.toFixed(1) : "-"
                                    font.pixelSize: Theme.fontXs
                                    font.bold: true
                                    color: "#FFFFFF"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }
                    }

                    Text {
                        text: root.currentItem ? root.currentItem.title : ""
                        font.pixelSize: Theme.fontLg + 2
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }

                    Text {
                        text: (root.detailInfo && root.detailInfo.description) ? root.detailInfo.description : (root.currentItem ? (root.currentItem.overview || "Açıklama bulunmuyor.") : "")
                        font.pixelSize: Theme.fontSm
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        width: parent.width
                        lineHeight: 1.3
                    }

                    // Ek Detay Bilgileri (API detay uç noktasından)
                    Column {
                        width: parent.width
                        spacing: 4
                        visible: repeaterDetails.count > 0

                        Repeater {
                            id: repeaterDetails
                            model: root.buildDetailRows()

                            Row {
                                spacing: 6

                                Text {
                                    text: modelData.label + ":"
                                    font.pixelSize: Theme.fontXs
                                    font.bold: true
                                    font.family: Theme.fontFamily
                                    color: Theme.textMuted
                                }

                                Text {
                                    text: modelData.value
                                    font.pixelSize: Theme.fontXs
                                    font.family: Theme.fontFamily
                                    color: Theme.textSecondary
                                    wrapMode: Text.WordWrap
                                    width: detailsColumn.width - 90
                                }
                            }
                        }
                    }
                }
            }

            // Butonlar
            Row {
                anchors.right: parent.right
                spacing: 12
                topPadding: 8

                CustomButton {
                    text: "Kapat"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CustomButton {
                    text: "Faaliyetlerime Ekle"
                    icon: Icons.add
                    variant: "primary"
                    onClicked: {
                        if (root.currentItem) {
                            root.addRequested(
                                root.currentItem.category,
                                root.currentItem.title,
                                root.currentItem.rating || 0.0
                            )
                        }
                        root.close()
                    }
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        z: -1
        onClicked: root.close()
    }
}
