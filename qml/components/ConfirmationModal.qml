// qml/components/ConfirmationModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property string title: "Emin misiniz?"
    property string message: "Bu işlemi onaylıyor musunuz?"
    property string confirmText: "Sil"
    property string cancelText: "İptal"
    property bool isDanger: true

    signal confirmed()
    signal cancelled()

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function open() {
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
        cancelled()
    }

    // Modal Pencere Kartı
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 420)
        implicitHeight: contentCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: root.isDanger ? Theme.danger : Theme.primary
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
            id: contentCol
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            Row {
                spacing: 12
                width: parent.width

                Text {
                    text: root.isDanger ? "⚠️" : "ℹ️"
                    font.pixelSize: 24
                }

                Text {
                    text: root.title
                    font.pixelSize: Theme.fontLg
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Text {
                text: root.message
                font.pixelSize: Theme.fontSm
                font.family: Theme.fontFamily
                color: Theme.textSecondary
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Item { width: 1; height: 8 }

            Row {
                anchors.right: parent.right
                spacing: 12

                CustomButton {
                    text: root.cancelText
                    variant: "ghost"
                    onClicked: {
                        root.opacity = 0.0
                        root.cancelled()
                    }
                }

                CustomButton {
                    text: root.confirmText
                    variant: root.isDanger ? "danger" : "primary"
                    onClicked: {
                        root.opacity = 0.0
                        root.confirmed()
                    }
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        z: -1
        onClicked: {
            root.opacity = 0.0
            root.cancelled()
        }
    }
}
