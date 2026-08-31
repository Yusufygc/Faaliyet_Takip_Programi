// qml/modals/RandomPickModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property var currentItem: null

    signal addRequested(string category, string title, real rating)

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openWith(item) {
        currentItem = item || null
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
    }

    // Modal Kart
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 540)
        implicitHeight: contentRow.implicitHeight + 56
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.accent
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
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
                            name: Icons.random
                            size: 16
                            color: Theme.accent
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "GÜNÜN RASTGELE ÖNERİSİ"
                            font.pixelSize: Theme.fontLg
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: "Karar veremediğinizde algoritmanın sizin için seçtiği yapım"
                        font.pixelSize: Theme.fontXs
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
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
                spacing: 16

                // Poster
                Rectangle {
                    width: 130
                    height: 190
                    radius: Theme.radiusMd
                    color: Theme.bgInput
                    border.color: Theme.borderSubtle
                    border.width: 1
                    clip: true

                    Image {
                        id: randPosterImg
                        anchors.fill: parent
                        source: root.currentItem ? (root.currentItem.poster || root.currentItem.image || "") : ""
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                    }

                    Icon {
                        anchors.centerIn: parent
                        name: root.currentItem && root.currentItem.category === "Dizi" ? Icons.tv : (root.currentItem && root.currentItem.category === "Oyun" ? Icons.game : (root.currentItem && root.currentItem.category === "Kitap" ? Icons.book : Icons.film))
                        size: 32
                        color: Theme.textMuted
                        visible: randPosterImg.status !== Image.Ready
                    }
                }

                // Detaylar
                Column {
                    width: parent.width - 146
                    spacing: 8

                    Row {
                        spacing: 8
                        Badge {
                            text: root.currentItem ? root.currentItem.category : ""
                            badgeColor: Theme.categoryColor(root.currentItem ? root.currentItem.category : "")
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

                        Badge {
                            text: root.currentItem ? (root.currentItem.year || "") : ""
                            badgeColor: Theme.textMuted
                            visible: text !== ""
                        }
                    }

                    Text {
                        text: root.currentItem ? root.currentItem.title : ""
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }

                    Text {
                        text: root.currentItem ? (root.currentItem.overview || "Açıklama bulunmuyor.") : ""
                        font.pixelSize: Theme.fontXs
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        width: parent.width
                        maximumLineCount: 5
                        elide: Text.ElideRight
                    }
                }
            }

            // Butonlar
            Row {
                anchors.right: parent.right
                spacing: 12
                topPadding: 8

                CustomButton {
                    text: "Başka Öneri Bul"
                    icon: Icons.refresh
                    variant: "secondary"
                    busy: discoverBridge.isLoading
                    onClicked: discoverBridge.getRandomRecommendation(root.currentItem ? root.currentItem.category : "Tümü")
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
