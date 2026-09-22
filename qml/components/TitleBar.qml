// qml/components/TitleBar.qml
import QtQuick
import QtQuick.Window
import "../theme"

Rectangle {
    id: root

    property var targetWindow: null
    property string title: "Faaliyet Takip Programı"

    implicitWidth: parent.width
    implicitHeight: 38
    color: Theme.bgSidebar
    border.color: Theme.borderSubtle
    border.width: 1

    // Pencere Sürükleme
    MouseArea {
        anchors.fill: parent
        anchors.rightMargin: windowControls.width
        onPressed: {
            if (root.targetWindow) {
                root.targetWindow.startSystemMove()
            }
        }
        onDoubleClicked: {
            if (root.targetWindow) {
                if (root.targetWindow.visibility === Window.Maximized) {
                    root.targetWindow.showNormal()
                } else {
                    root.targetWindow.showMaximized()
                }
            }
        }
    }

    // Başlık
    Row {
        anchors.left: parent.left
        anchors.leftMargin: 14
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10

        Text {
            text: root.title
            font.pixelSize: Theme.fontSm
            font.bold: true
            font.family: Theme.fontFamily
            color: Theme.textPrimary
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    // Pencere Kontrolleri (Minimize, Maximize, Close)
    Row {
        id: windowControls
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        // Küçült (Minimize)
        Rectangle {
            width: 44
            height: parent.height
            color: minMouse.containsMouse ? Theme.bgCardElevated : "transparent"

            Text {
                text: "—"
                font.pixelSize: 11
                color: Theme.textSecondary
                anchors.centerIn: parent
            }

            MouseArea {
                id: minMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (root.targetWindow) root.targetWindow.showMinimized()
                }
            }
        }

        // Büyüt / Geri Yükle (Maximize/Restore)
        Rectangle {
            width: 44
            height: parent.height
            color: maxMouse.containsMouse ? Theme.bgCardElevated : "transparent"

            Text {
                text: (root.targetWindow && root.targetWindow.visibility === Window.Maximized) ? "❐" : "□"
                font.pixelSize: 13
                color: Theme.textSecondary
                anchors.centerIn: parent
            }

            MouseArea {
                id: maxMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (root.targetWindow) {
                        if (root.targetWindow.visibility === Window.Maximized) {
                            root.targetWindow.showNormal()
                        } else {
                            root.targetWindow.showMaximized()
                        }
                    }
                }
            }
        }

        // Kapat (Close)
        Rectangle {
            width: 46
            height: parent.height
            color: closeMouse.containsMouse ? Theme.danger : "transparent"

            Text {
                text: "✕"
                font.pixelSize: 12
                color: closeMouse.containsMouse ? "#FFFFFF" : Theme.textSecondary
                anchors.centerIn: parent
            }

            MouseArea {
                id: closeMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (root.targetWindow) root.targetWindow.close()
                }
            }
        }
    }
}
