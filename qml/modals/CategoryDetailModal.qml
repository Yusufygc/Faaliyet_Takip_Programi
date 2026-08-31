// qml/modals/CategoryDetailModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property string categoryName: ""
    property string modalTitle: "KATEGORİ DETAYLARI"
    property var activityList: []

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openForCategory(catName) {
        categoryName = catName || ""
        modalTitle = "KATEGORİ DETAYLARI"
        activityList = statsBridge.getCategoryDetails(catName) || []
        opacity = 1.0
    }

    function openCategory(catName) {
        openForCategory(catName)
    }

    function openForMonth(prefix, monthName, category) {
        categoryName = category || "Hepsi"
        modalTitle = prefix + " (" + (monthName || "") + ") DETAYLARI"
        activityList = statsBridge.getMonthDetails(prefix, category || "Hepsi") || []
        opacity = 1.0
    }

    function openMonth(prefix, monthName, category) {
        openForMonth(prefix, monthName, category)
    }

    function close() {
        opacity = 0.0
    }

    // Modal Pencere
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 500)
        implicitHeight: contentCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.categoryColor(root.categoryName)
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

                    Row {
                        spacing: 8
                        Badge {
                            text: root.categoryName
                            badgeColor: Theme.categoryColor(root.categoryName)
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: root.modalTitle
                            font.pixelSize: Theme.fontLg
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: "Seçili dönemde eklenen toplam " + root.activityList.length + " kayıt"
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

            // Liste
            ListView {
                id: detailsList
                width: parent.width
                height: Math.min(contentHeight, 260)
                clip: true
                model: root.activityList
                spacing: 6

                delegate: Rectangle {
                    width: detailsList.width
                    height: 40
                    radius: Theme.radiusSm
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 14

                        Text {
                            text: modelData.name
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.textPrimary
                            width: parent.width - 120
                            elide: Text.ElideRight
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.date
                            font.pixelSize: Theme.fontXs
                            color: Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }

            Row {
                anchors.right: parent.right
                topPadding: 8

                CustomButton {
                    text: "Kapat"
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
