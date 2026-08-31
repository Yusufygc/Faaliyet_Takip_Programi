// qml/components/Icon.qml
import QtQuick
import "../theme"

Text {
    id: root

    property string name: ""
    property int size: 16

    text: name
    font.family: Theme.iconFontFamily
    font.pixelSize: size
    color: Theme.textSecondary
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter

    Behavior on color { ColorAnimation { duration: Theme.animFast } }
    Behavior on scale { NumberAnimation { duration: Theme.animFast } }
}
