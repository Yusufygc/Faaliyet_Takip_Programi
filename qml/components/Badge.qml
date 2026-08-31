// qml/components/Badge.qml
import QtQuick
import "../theme"

Rectangle {
    id: root

    property string text: ""
    property color badgeColor: Theme.primary
    property int fontSize: Theme.fontXs
    property bool filled: false

    implicitWidth: textItem.implicitWidth + 16
    implicitHeight: textItem.implicitHeight + 8
    radius: Theme.radiusSm
    color: filled ? badgeColor : Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.15)
    border.color: filled ? "transparent" : Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.4)
    border.width: filled ? 0 : 1

    Text {
        id: textItem
        anchors.centerIn: parent
        text: root.text
        font.pixelSize: root.fontSize
        font.bold: true
        font.family: Theme.fontFamily
        color: root.filled ? "#FFFFFF" : root.badgeColor
    }
}
