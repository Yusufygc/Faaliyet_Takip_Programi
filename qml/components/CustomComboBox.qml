// qml/components/CustomComboBox.qml
import QtQuick
import QtQuick.Controls
import "../theme"

ComboBox {
    id: control

    property int customRadius: Theme.radiusMd

    implicitWidth: 180
    implicitHeight: 42

    font.pixelSize: Theme.fontSm
    font.family: Theme.fontFamily

    delegate: ItemDelegate {
        id: itemDelegate
        width: control.width
        height: 38
        highlighted: control.highlightedIndex === index

        contentItem: Text {
            text: (control.textRole && typeof modelData === "object" && modelData !== null && modelData[control.textRole] !== undefined)
                  ? String(modelData[control.textRole])
                  : (modelData !== undefined && modelData !== null ? String(modelData) : "")
            color: itemDelegate.hovered || control.currentIndex === index ? Theme.textPrimary : Theme.textSecondary
            font.pixelSize: Theme.fontSm
            font.bold: control.currentIndex === index
            font.family: Theme.fontFamily
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
            leftPadding: 12
        }

        background: Rectangle {
            color: control.currentIndex === index ? Theme.primaryGlow : (itemDelegate.hovered ? Theme.bgCardElevated : "transparent")
            radius: Theme.radiusSm
            anchors.fill: parent
            anchors.margins: 2
        }
    }

    indicator: Canvas {
        id: canvas
        x: control.width - width - 12
        y: control.topPadding + (control.availableHeight - height) / 2
        width: 10
        height: 6
        contextType: "2d"

        Connections {
            target: control
            function onPressedChanged() { canvas.requestPaint(); }
        }

        onPaint: {
            context.reset();
            context.moveTo(0, 0);
            context.lineTo(width, 0);
            context.lineTo(width / 2, height);
            context.closePath();
            context.fillStyle = control.pressed ? Theme.primary : Theme.textSecondary;
            context.fill();
        }
    }

    contentItem: Text {
        leftPadding: 14
        rightPadding: control.indicator.width + 20
        text: control.displayText
        font: control.font
        color: Theme.textPrimary
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: 140
        implicitHeight: 42
        color: control.popup.visible ? Theme.bgInput : Theme.bgCard
        border.color: control.popup.visible ? Theme.primary : Theme.borderSubtle
        border.width: control.popup.visible ? 2 : 1
        radius: control.customRadius

        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
    }

    popup: Popup {
        y: control.height + 4
        width: control.width
        implicitHeight: Math.min(contentItem.implicitHeight + 12, 240)
        padding: 6

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator {}
        }

        background: Rectangle {
            color: Theme.bgSidebar
            border.color: Theme.borderLight
            border.width: 1
            radius: Theme.radiusMd

            // Hafif gölge efekti
            Rectangle {
                anchors.fill: parent
                anchors.margins: -1
                color: "transparent"
                border.color: "#20000000"
                radius: Theme.radiusMd
                z: -1
            }
        }
    }
}
