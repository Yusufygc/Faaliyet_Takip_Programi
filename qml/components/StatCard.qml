// qml/components/StatCard.qml
import QtQuick
import "../theme"

Rectangle {
    id: root

    property string title: ""
    property string value: "0"
    property string subtitle: ""
    property string icon: ""
    property string iconText: "📊"
    property color accentColor: Theme.primary

    implicitWidth: 220
    implicitHeight: 110
    radius: Theme.radiusLg
    color: Theme.bgCard
    border.color: mouseArea.containsMouse ? root.accentColor : Theme.borderSubtle
    border.width: 1
    clip: true

    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
    Behavior on scale { NumberAnimation { duration: Theme.animFast } }

    // Üstteki renkli çizgi
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 3
        color: root.accentColor
    }

    // Arkaplan yumuşak parlama
    Rectangle {
        anchors.top: parent.top
        anchors.right: parent.right
        width: 80
        height: 80
        radius: 40
        color: Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.06)
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 6

        Row {
            width: parent.width
            spacing: 10

            // Şık Yuvarlak İkon Rozeti
            Rectangle {
                width: 28
                height: 28
                radius: 14
                color: Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.15)
                border.color: Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.3)
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                Icon {
                    name: root.icon !== "" ? root.icon : Icons.app_logo
                    size: 13
                    color: root.accentColor
                    anchors.centerIn: parent
                    visible: root.icon !== ""
                }

                Text {
                    text: root.iconText
                    font.pixelSize: 14
                    anchors.centerIn: parent
                    visible: root.icon === "" && root.iconText !== ""
                }
            }

            Text {
                text: root.title.toUpperCase()
                font.pixelSize: Theme.fontXs
                font.bold: true
                font.letterSpacing: 0.8
                font.family: Theme.fontFamily
                color: Theme.textMuted
                elide: Text.ElideRight
                width: parent.width - 40
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Text {
            text: root.value
            font.pixelSize: Theme.fontTitle
            font.bold: true
            font.family: Theme.fontFamily
            color: Theme.textPrimary
        }

        Text {
            text: root.subtitle
            visible: root.subtitle !== ""
            font.pixelSize: Theme.fontXs
            font.family: Theme.fontFamily
            color: Theme.textSecondary
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onEntered: root.scale = 1.02
        onExited: root.scale = 1.0
    }
}
