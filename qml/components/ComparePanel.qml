// qml/components/ComparePanel.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root

    property string sideTitle: "1. Dönem"
    property color accentColor: Theme.primary
    property var scaleModel: ["Aylık", "Yıllık"]
    property int scaleIndex: 0
    property var periodsModel: []
    property int periodIndex: -1
    property var columns: []   // [{name, color}]
    property var itemsData: [] // [[isim, ...], ...] columns ile hizalı, her tür için faaliyet isimleri
    property int total: 0

    signal scaleActivated(int index)
    signal periodActivated(int index)

    readonly property int colSpacing: 8
    readonly property int minColWidth: 76
    readonly property int colCount: Math.max(root.columns.length, 1)
    readonly property real colWidth: {
        var avail = tableFlick.width - colSpacing * (colCount - 1)
        var even = avail / colCount
        return even > minColWidth ? even : minColWidth
    }

    radius: Theme.radiusLg
    color: Theme.bgCard
    border.color: Theme.borderSubtle
    border.width: 1
    implicitHeight: contentCol.implicitHeight + 40

    Column {
        id: contentCol
        anchors.fill: parent
        anchors.margins: 20
        spacing: 14

        // Başlık
        Row {
            spacing: 10

            Rectangle {
                width: 4
                height: 22
                radius: 2
                color: root.accentColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: root.sideTitle
                font.pixelSize: Theme.fontLg
                font.bold: true
                font.family: Theme.fontFamily
                color: Theme.textPrimary
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Ölçek + Dönem Seçiciler
        Row {
            width: parent.width
            spacing: 10

            CustomComboBox {
                id: scaleCombo
                width: 100
                model: root.scaleModel
                currentIndex: root.scaleIndex
                onActivated: root.scaleActivated(currentIndex)

                // ComboBox kullanıcı seçiminde currentIndex'i doğrudan yazdığından
                // yukarıdaki deklaratif binding kopar; root.scaleIndex programatik
                // olarak değiştiğinde (ör. dışarıdan reset) senkronu elle geri kurar.
                Connections {
                    target: root
                    function onScaleIndexChanged() { scaleCombo.currentIndex = root.scaleIndex }
                }
            }

            CustomComboBox {
                id: periodCombo
                width: parent.width - scaleCombo.width - 10
                model: root.periodsModel
                currentIndex: root.periodIndex
                onActivated: root.periodActivated(currentIndex)

                Connections {
                    target: root
                    function onPeriodIndexChanged() { periodCombo.currentIndex = root.periodIndex }
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.borderSubtle
        }

        // Tür Kolonlu Tablo — her kolon o türe ait faaliyetleri alt alta listeler;
        // en çok veriye sahip tür kaç satırsa tablo o kadar yükselir.
        Flickable {
            id: tableFlick
            width: parent.width
            height: colsRow.implicitHeight
            contentWidth: colsRow.implicitWidth
            contentHeight: colsRow.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            visible: root.periodsModel.length > 0
            ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

            Row {
                id: colsRow
                spacing: root.colSpacing

                Repeater {
                    model: root.columns

                    Column {
                        id: colItem
                        width: root.colWidth
                        spacing: 6
                        property int colIndex: index

                        Rectangle {
                            width: parent.width
                            height: 28
                            radius: Theme.radiusSm
                            color: Theme.bgInput

                            Text {
                                anchors.centerIn: parent
                                width: parent.width - 8
                                text: modelData.name
                                font.pixelSize: Theme.fontXs
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: modelData.color
                                elide: Text.ElideRight
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }

                        Column {
                            width: parent.width
                            spacing: 4

                            Repeater {
                                model: colItem.colIndex < root.itemsData.length ? root.itemsData[colItem.colIndex] : []

                                Rectangle {
                                    width: colItem.width
                                    height: 26
                                    radius: Theme.radiusSm
                                    color: Theme.bgSidebar
                                    border.color: Theme.borderSubtle
                                    border.width: 1

                                    Text {
                                        id: itemNameText
                                        anchors.fill: parent
                                        anchors.leftMargin: 6
                                        anchors.rightMargin: 6
                                        verticalAlignment: Text.AlignVCenter
                                        horizontalAlignment: Text.AlignHCenter
                                        text: modelData
                                        font.pixelSize: Theme.fontXs
                                        font.family: Theme.fontFamily
                                        color: Theme.textPrimary
                                        elide: Text.ElideRight
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.ArrowCursor
                                        ToolTip.visible: containsMouse && itemNameText.truncated
                                        ToolTip.text: modelData
                                        ToolTip.delay: 400
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Text {
            width: parent.width
            visible: root.periodsModel.length === 0
            text: "Bu dönemde veri yok."
            font.pixelSize: Theme.fontSm
            font.family: Theme.fontFamily
            color: Theme.textMuted
            horizontalAlignment: Text.AlignHCenter
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.borderSubtle
        }

        // Toplam
        Text {
            width: parent.width
            text: "TOPLAM: " + root.total
            font.pixelSize: Theme.fontMd
            font.bold: true
            font.family: Theme.fontFamily
            color: root.accentColor
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
