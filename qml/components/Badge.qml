// qml/components/Badge.qml
import QtQuick
import "../theme"

Rectangle {
    id: root

    property string text: ""
    property color badgeColor: Theme.primary
    property int fontSize: Theme.fontXs
    property bool filled: false
    property color dotColor: "transparent"

    implicitWidth: contentRow.implicitWidth + 16
    implicitHeight: textItem.implicitHeight + 8
    radius: Theme.radiusSm
    color: filled ? badgeColor : Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.15)
    border.color: filled ? "transparent" : Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.4)
    border.width: filled ? 0 : 1

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 5

        Rectangle {
            width: 6
            height: 6
            radius: 3
            color: root.dotColor
            visible: root.dotColor.a > 0
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            id: textItem
            text: root.text
            font.pixelSize: root.fontSize
            font.bold: true
            font.family: Theme.fontFamily
            color: root.filled ? "#FFFFFF" : root.badgeColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
