// qml/components/ToastNotification.qml
import QtQuick
import "../theme"

Item {
    id: root

    property string toastType: "info"
    property string title: ""
    property string message: ""
    property int duration: 4000

    implicitWidth: 340
    implicitHeight: 74
    opacity: 0
    y: 20
    visible: opacity > 0

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }
    Behavior on y { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutCubic } }

    function show(type, titleText, messageText, customDuration) {
        toastType = type || "info"
        title = titleText || ""
        message = messageText || ""
        if (customDuration) duration = customDuration
        opacity = 1.0
        y = 0
        dismissTimer.restart()
    }

    function dismiss() {
        opacity = 0.0
        y = -20
    }

    Timer {
        id: dismissTimer
        interval: root.duration
        onTriggered: root.dismiss()
    }

    function getAccentColor() {
        if (toastType === "success") return Theme.success
        if (toastType === "error") return Theme.danger
        if (toastType === "warning") return Theme.warning
        return Theme.primary
    }

    function getIconText() {
        if (toastType === "success") return "✓"
        if (toastType === "error") return "✕"
        if (toastType === "warning") return "⚠"
        return "ℹ"
    }

    Rectangle {
        id: toastCard
        anchors.fill: parent
        radius: Theme.radiusMd
        color: Theme.bgSidebar
        border.color: root.getAccentColor()
        border.width: 1

        Rectangle {
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: 4
            color: root.getAccentColor()
            radius: Theme.radiusSm
        }

        Row {
            anchors.fill: parent
            anchors.margins: 12
            anchors.leftMargin: 16
            spacing: 12

            // İkon Rozeti
            Rectangle {
                width: 32
                height: 32
                radius: 16
                color: Qt.rgba(root.getAccentColor().r, root.getAccentColor().g, root.getAccentColor().b, 0.2)
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    anchors.centerIn: parent
                    text: root.getIconText()
                    font.pixelSize: 14
                    font.bold: true
                    color: root.getAccentColor()
                }
            }

            // Metinler
            Column {
                width: parent.width - 70
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                Text {
                    text: root.title
                    font.pixelSize: Theme.fontSm
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                    elide: Text.ElideRight
                    width: parent.width
                }

                Text {
                    text: root.message
                    font.pixelSize: Theme.fontXs
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    elide: Text.ElideRight
                    width: parent.width
                }
            }

            // Kapat Butonu
            Text {
                text: "✕"
                font.pixelSize: 12
                color: closeMouse.containsMouse ? Theme.textPrimary : Theme.textMuted
                anchors.verticalCenter: parent.verticalCenter

                MouseArea {
                    id: closeMouse
                    anchors.fill: parent
                    anchors.margins: -4
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.dismiss()
                }
            }
        }
    }
}
