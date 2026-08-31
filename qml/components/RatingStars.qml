// qml/components/RatingStars.qml
import QtQuick
import "../theme"

Row {
    id: root

    property real rating: 0.0
    property real hoveredRating: 0.0
    property bool readOnly: false
    property int starSize: 22

    signal ratingSelected(real newRating)

    spacing: 4

    Repeater {
        model: 10

        Rectangle {
            id: starItem
            width: root.starSize
            height: root.starSize
            radius: root.starSize / 2
            color: "transparent"

            property int starIndex: index + 1
            property bool isActive: (root.hoveredRating > 0 ? root.hoveredRating >= starIndex : root.rating >= starIndex)

            Text {
                anchors.centerIn: parent
                text: "★"
                font.pixelSize: root.starSize
                color: starItem.isActive ? Theme.warning : Theme.textMuted
                scale: starMouse.containsMouse ? 1.25 : 1.0

                Behavior on scale { NumberAnimation { duration: Theme.animFast } }
                Behavior on color { ColorAnimation { duration: Theme.animFast } }
            }

            MouseArea {
                id: starMouse
                anchors.fill: parent
                hoverEnabled: !root.readOnly
                cursorShape: root.readOnly ? Qt.ArrowCursor : Qt.PointingHandCursor
                onEntered: {
                    if (!root.readOnly) root.hoveredRating = starItem.starIndex
                }
                onExited: {
                    if (!root.readOnly) root.hoveredRating = 0.0
                }
                onClicked: {
                    if (!root.readOnly) {
                        root.rating = starItem.starIndex
                        root.ratingSelected(starItem.starIndex)
                    }
                }
            }
        }
    }

    Text {
        text: (root.hoveredRating > 0 ? root.hoveredRating.toFixed(1) : (root.rating > 0 ? root.rating.toFixed(1) : "-")) + " / 10"
        font.pixelSize: Theme.fontSm
        font.bold: true
        font.family: Theme.fontFamily
        color: root.rating > 0 || root.hoveredRating > 0 ? Theme.warning : Theme.textMuted
        anchors.verticalCenter: parent.verticalCenter
        leftPadding: 8
    }
}
