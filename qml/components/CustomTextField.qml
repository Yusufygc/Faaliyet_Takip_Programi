// qml/components/CustomTextField.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property alias text: input.text
    property alias placeholderText: input.placeholderText
    property alias echoMode: input.echoMode
    property alias readOnly: input.readOnly
    property alias validator: input.validator
    property string icon: ""
    property string iconText: ""
    property bool clearable: true
    property int fontSize: Theme.fontSm
    property alias inputItem: input

    signal accepted()
    signal textEdited(string newText)

    implicitWidth: 260
    implicitHeight: 42
    radius: Theme.radiusMd
    color: input.activeFocus ? Theme.bgInput : Theme.bgCard
    border.color: input.activeFocus ? Theme.primary : Theme.borderSubtle
    border.width: input.activeFocus ? 2 : 1

    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
    Behavior on color { ColorAnimation { duration: Theme.animFast } }

    // 1. Sol İkon (Vektör Icon veya Emoji fallback)
    Icon {
        id: leftIcon
        name: root.icon
        visible: root.icon !== ""
        size: root.fontSize + 2
        color: input.activeFocus ? Theme.primary : Theme.textMuted
        anchors.left: parent.left
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
    }

    Text {
        id: leftEmoji
        text: root.iconText
        visible: root.iconText !== "" && root.icon === ""
        font.pixelSize: root.fontSize + 2
        font.family: Theme.fontFamily
        color: input.activeFocus ? Theme.primary : Theme.textMuted
        anchors.left: parent.left
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
    }

    // 2. Sağ Temizleme Butonu
    Rectangle {
        id: clearBtn
        width: 20
        height: 20
        radius: 10
        color: clearMouse.containsMouse ? Theme.bgCardElevated : "transparent"
        visible: root.clearable && input.text.length > 0 && !root.readOnly
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter

        Icon {
            name: Icons.close
            size: 10
            color: clearMouse.containsMouse ? Theme.textPrimary : Theme.textMuted
            anchors.centerIn: parent
        }

        MouseArea {
            id: clearMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                input.text = ""
                root.textEdited("")
            }
        }
    }

    // 3. Orta Metin Giriş Alanı (İkon ile Temizle butonu arasına pürüzsüz oturur)
    TextField {
        id: input
        anchors.left: (leftIcon.visible || leftEmoji.visible) ? (leftIcon.visible ? leftIcon.right : leftEmoji.right) : parent.left
        anchors.leftMargin: (leftIcon.visible || leftEmoji.visible) ? 8 : 12
        anchors.right: clearBtn.visible ? clearBtn.left : parent.right
        anchors.rightMargin: clearBtn.visible ? 6 : 12
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        verticalAlignment: TextInput.AlignVCenter
        color: Theme.textPrimary
        placeholderTextColor: Theme.textMuted
        font.pixelSize: root.fontSize
        font.family: Theme.fontFamily
        background: Item {}
        selectByMouse: true
        selectionColor: Theme.primaryGlow
        selectedTextColor: Theme.textPrimary

        onAccepted: root.accepted()
        onTextEdited: root.textEdited(text)
    }
}
