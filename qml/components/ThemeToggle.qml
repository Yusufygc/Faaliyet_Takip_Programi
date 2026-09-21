// qml/components/ThemeToggle.qml
import QtQuick
import "../theme"

Item {
    id: root

    property bool isCollapsed: false

    implicitWidth: isCollapsed ? 36 : 52
    implicitHeight: isCollapsed ? 36 : 28

    // --- Daraltılmış Mod: İkon Buton (hamburger buton deseniyle aynı) ---
    Rectangle {
        visible: root.isCollapsed
        anchors.fill: parent
        radius: Theme.radiusMd
        color: collapsedHover.containsMouse ? Theme.bgCardElevated : "transparent"
        border.color: collapsedHover.containsMouse ? Theme.borderLight : "transparent"
        border.width: 1

        Icon {
            name: Theme.isDark ? Icons.moon : Icons.sun
            size: 15
            color: collapsedHover.containsMouse ? Theme.primaryLight : Theme.textSecondary
            anchors.centerIn: parent
        }

        MouseArea {
            id: collapsedHover
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: settingsBridge.toggleTheme()
        }
    }

    // --- Genişletilmiş Mod: Pill Switch ---
    Rectangle {
        id: track
        visible: !root.isCollapsed
        anchors.fill: parent
        radius: height / 2
        color: Theme.bgInput
        border.color: Theme.borderSubtle
        border.width: 1

        Rectangle {
            id: thumb
            width: parent.height - 4
            height: parent.height - 4
            radius: height / 2
            anchors.verticalCenter: parent.verticalCenter
            x: Theme.isDark ? parent.width - width - 2 : 2
            color: Theme.primary

            Behavior on x {
                NumberAnimation { duration: Theme.animNormal; easing.type: Easing.InOutQuad }
            }

            Icon {
                name: Theme.isDark ? Icons.moon : Icons.sun
                size: 11
                color: "#FFFFFF"
                anchors.centerIn: parent
            }
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: settingsBridge.toggleTheme()
        }
    }
}
