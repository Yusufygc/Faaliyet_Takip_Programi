// qml/components/EmptyState.qml
import QtQuick
import "../theme"

Item {
    id: root

    property string icon: ""
    property string iconText: "📭"
    property string title: "Kayıt Bulunamadı"
    property string description: "Filtreleme kriterlerinize uygun sonuç yok veya henüz veri eklenmedi."
    property string actionText: ""

    signal actionClicked()

    implicitWidth: 320
    implicitHeight: 220

    Column {
        anchors.centerIn: parent
        spacing: 12
        width: Math.min(parent.width - 40, 360)

        Icon {
            name: root.icon
            size: 44
            color: Theme.textMuted
            visible: root.icon !== ""
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: root.iconText
            font.pixelSize: 44
            visible: root.icon === "" && root.iconText !== ""
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: root.title
            font.pixelSize: Theme.fontLg
            font.bold: true
            font.family: Theme.fontFamily
            color: Theme.textPrimary
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: root.description
            font.pixelSize: Theme.fontSm
            font.family: Theme.fontFamily
            color: Theme.textSecondary
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            width: parent.width
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Item {
            width: 1
            height: 4
            visible: root.actionText !== ""
        }

        CustomButton {
            visible: root.actionText !== ""
            text: root.actionText
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: root.actionClicked()
        }
    }
}
