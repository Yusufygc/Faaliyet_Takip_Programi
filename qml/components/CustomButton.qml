// qml/components/CustomButton.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property string text: ""
    property string icon: ""
    property string iconText: ""
    property string variant: "primary" // primary, secondary, success, danger, ghost
    property bool busy: false
    property int fontSize: Theme.fontSm
    property bool fullWidth: false
    property alias enabled: mouseArea.enabled

    signal clicked()

    implicitWidth: fullWidth ? parent.width : (contentRow.implicitWidth + 32)
    implicitHeight: 40
    radius: Theme.radiusMd
    color: getBackgroundColor()
    border.color: getBorderColor()
    border.width: variant === "secondary" || variant === "ghost" ? 1 : 0

    Behavior on color { ColorAnimation { duration: Theme.animFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
    Behavior on scale { NumberAnimation { duration: Theme.animFast } }

    function getBackgroundColor() {
        if (!enabled) return "#1E293B"
        if (mouseArea.pressed) {
            if (variant === "primary") return Theme.primaryHover
            if (variant === "success") return "#059669"
            if (variant === "danger") return "#DC2626"
            if (variant === "secondary") return Theme.bgCardElevated
            return "transparent"
        }
        if (mouseArea.containsMouse) {
            if (variant === "primary") return Theme.primaryLight
            if (variant === "success") return "#34D399"
            if (variant === "danger") return "#F87171"
            if (variant === "secondary") return Theme.bgCardElevated
            if (variant === "ghost") return "#1E293B"
            return Theme.primaryHover
        }
        if (variant === "primary") return Theme.primary
        if (variant === "success") return Theme.success
        if (variant === "danger") return Theme.danger
        if (variant === "secondary") return Theme.bgCard
        if (variant === "ghost") return "transparent"
        return Theme.primary
    }

    function getBorderColor() {
        if (!enabled) return Theme.borderSubtle
        if (mouseArea.containsMouse) {
            if (variant === "secondary" || variant === "ghost") return Theme.primary
        }
        if (variant === "secondary") return Theme.borderSubtle
        return "transparent"
    }

    function getTextColor() {
        if (!enabled) return Theme.textMuted
        if (variant === "ghost" || variant === "secondary") {
            return mouseArea.containsMouse ? Theme.textPrimary : Theme.textSecondary
        }
        return "#FFFFFF"
    }

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 8
        opacity: busy ? 0 : 1

        Icon {
            name: root.icon
            size: root.fontSize + 2
            visible: root.icon !== ""
            color: root.getTextColor()
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.iconText
            visible: root.iconText !== "" && root.icon === ""
            font.pixelSize: root.fontSize + 2
            font.family: Theme.fontFamily
            color: root.getTextColor()
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.text
            visible: root.text !== ""
            font.pixelSize: root.fontSize
            font.bold: true
            font.family: Theme.fontFamily
            color: root.getTextColor()
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    // Yükleniyor Göstergesi
    BusyIndicator {
        anchors.centerIn: parent
        running: root.busy
        visible: root.busy
        width: 24
        height: 24
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: {
            if (!root.busy) root.clicked()
        }
        onPressed: root.scale = 0.98
        onReleased: root.scale = 1.0
        onCanceled: root.scale = 1.0
    }
}
