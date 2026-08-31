// qml/modals/FolderManageModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function open() {
        newFolderField.text = ""
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
    }

    // Modal Gövde
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 460)
        implicitHeight: contentCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.borderLight
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
            id: contentCol
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            // Başlık
            Row {
                width: parent.width

                Column {
                    width: parent.width - 40
                    spacing: 4

                    Text {
                        text: "📁 KLASÖRLERİ YÖNET"
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "Hedeflerinizi gruplamak için klasörler oluşturun veya silin"
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

                    Text {
                        text: "✕"
                        font.pixelSize: 14
                        color: Theme.textSecondary
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

            // Yeni Klasör Ekleme Satırı
            Row {
                width: parent.width
                spacing: 8

                CustomTextField {
                    id: newFolderField
                    width: parent.width - 110
                    placeholderText: "Yeni klasör adı..."
                    iconText: "📁"
                    onAccepted: addBtn.clicked()
                }

                CustomButton {
                    id: addBtn
                    text: "＋ Ekle"
                    variant: "primary"
                    onClicked: {
                        var name = newFolderField.text.trim()
                        if (name) {
                            planBridge.addFolder(name)
                            newFolderField.text = ""
                        }
                    }
                }
            }

            // Mevcut Klasörler Listesi
            Text {
                text: "Mevcut Klasörler"
                font.pixelSize: Theme.fontXs
                font.bold: true
                color: Theme.textSecondary
                topPadding: 6
            }

            ListView {
                id: folderList
                width: parent.width
                height: Math.min(contentHeight, 180)
                clip: true
                model: planBridge.folders.filter(function(f) { return f.id > 0 })
                spacing: 6

                delegate: Rectangle {
                    width: folderList.width
                    height: 38
                    radius: Theme.radiusSm
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 8

                        Text {
                            text: "📁"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.name
                            font.pixelSize: Theme.fontSm
                            color: Theme.textPrimary
                            width: parent.width - 70
                            elide: Text.ElideRight
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Rectangle {
                            width: 26
                            height: 26
                            radius: 13
                            color: delHover.containsMouse ? Theme.danger : "transparent"
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: "🗑"
                                font.pixelSize: 13
                                anchors.centerIn: parent
                            }

                            MouseArea {
                                id: delHover
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: planBridge.deleteFolder(modelData.id)
                            }
                        }
                    }
                }
            }

            Row {
                anchors.right: parent.right
                topPadding: 8

                CustomButton {
                    text: "Tamam"
                    variant: "secondary"
                    onClicked: root.close()
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
