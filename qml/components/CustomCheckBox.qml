// qml/components/CustomCheckBox.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root

    property bool checked: false
    property string text: ""
    property bool enabled: true
    signal toggled(bool isChecked)

    implicitWidth: checkRow.implicitWidth
    implicitHeight: 32

    Row {
        id: checkRow
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        // Şık Kutu Göstergesi
        Rectangle {
            id: boxIndicator
            width: 18
            height: 18
            radius: 4
            color: root.checked ? Theme.primary : Theme.bgInput
            border.color: root.checked ? Theme.primary : (chkMouse.containsMouse ? Theme.primaryLight : Theme.borderLight)
            border.width: 1
            anchors.verticalCenter: parent.verticalCenter

            Behavior on color { ColorAnimation { duration: Theme.animFast } }
            Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

            Image {
                source: "../../assets/icons/check.svg"
                sourceSize: Qt.size(12, 12)
                width: 12
                height: 12
                anchors.centerIn: parent
                visible: root.checked
                scale: root.checked ? 1.0 : 0.0
                Behavior on scale { NumberAnimation { duration: Theme.animFast; easing.type: Easing.OutBack } }
            }
        }

        Text {
            id: label
            text: root.text
            visible: root.text !== ""
            font.pixelSize: Theme.fontSm
            font.family: Theme.fontFamily
            color: !root.enabled ? Theme.textMuted : (chkMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    MouseArea {
        id: chkMouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled
        onClicked: {
            root.checked = !root.checked
            root.toggled(root.checked)
        }
    }
}
