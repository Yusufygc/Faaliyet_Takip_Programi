// qml/components/CategoryMonthHeatmap.qml
import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root

    // [{ month, monthName, total, categories: [{ type, count, color }, ...] }, ...] (12 ay)
    property var dataModel: []

    readonly property var categoryRows: (dataModel && dataModel.length === 12 && dataModel[0].categories) ? dataModel[0].categories : []
    readonly property int rowCount: categoryRows.length

    readonly property int labelWidth: 96
    readonly property int rowHeight: 30
    readonly property int rowSpacing: 6
    readonly property int cellSpacing: 4
    readonly property real cellWidth: Math.max(24, (width - labelWidth - cellSpacing * 11) / 12)

    implicitWidth: 400
    implicitHeight: mainCol.implicitHeight

    function countFor(catIndex, monthIndex) {
        var m = root.dataModel[monthIndex]
        if (!m || !m.categories || !m.categories[catIndex]) return 0
        return m.categories[catIndex].count
    }

    function rowMax(catIndex) {
        var mx = 1
        for (var i = 0; i < 12; i++) mx = Math.max(mx, countFor(catIndex, i))
        return mx
    }

    Column {
        id: mainCol
        width: parent.width
        spacing: 10

        // Ay Başlıkları
        Row {
            spacing: root.cellSpacing

            Item { width: root.labelWidth; height: 18 }

            Repeater {
                model: 12

                Text {
                    width: root.cellWidth
                    text: root.dataModel.length === 12 ? root.dataModel[index].monthName : ""
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: Theme.fontXs
                    font.family: Theme.fontFamily
                    color: Theme.textMuted
                }
            }
        }

        Text {
            visible: root.rowCount === 0
            text: "Yeterli veri yok"
            font.pixelSize: Theme.fontSm
            font.family: Theme.fontFamily
            color: Theme.textMuted
        }

        // Tür Satırları
        Column {
            width: parent.width
            spacing: root.rowSpacing

            Repeater {
                model: root.categoryRows

                Row {
                    id: catRow
                    spacing: root.cellSpacing
                    property int catIndex: index
                    property color rowColor: modelData.color
                    property string rowType: modelData.type

                    Text {
                        width: root.labelWidth
                        height: root.rowHeight
                        text: catRow.rowType
                        elide: Text.ElideRight
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: catRow.rowColor
                        verticalAlignment: Text.AlignVCenter
                    }

                    Repeater {
                        model: 12

                        Rectangle {
                            id: cell
                            width: root.cellWidth
                            height: root.rowHeight
                            radius: 4
                            border.color: Theme.borderSubtle
                            border.width: 1

                            property int monthIdx: index
                            property int cnt: root.countFor(catRow.catIndex, monthIdx)
                            property real intensity: cnt > 0 ? Math.min(1, cnt / root.rowMax(catRow.catIndex)) : 0

                            color: cnt > 0
                                ? Qt.rgba(catRow.rowColor.r, catRow.rowColor.g, catRow.rowColor.b, 0.15 + 0.75 * intensity)
                                : Theme.bgInput

                            Text {
                                anchors.centerIn: parent
                                visible: cell.cnt > 0
                                text: cell.cnt
                                font.pixelSize: Theme.fontXs - 1
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: cell.intensity > 0.55 ? "#FFFFFF" : Theme.textPrimary
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor
                                ToolTip.visible: containsMouse
                                ToolTip.delay: 300
                                ToolTip.text: catRow.rowType + " · " + (root.dataModel.length === 12 ? root.dataModel[cell.monthIdx].monthName : "") + ": " + cell.cnt + " faaliyet"
                            }
                        }
                    }
                }
            }
        }

        Text {
            visible: root.rowCount > 0
            text: "Koyu = o türün kendi içinde görece yoğun ay, açık = az"
            font.pixelSize: Theme.fontXs - 1
            font.family: Theme.fontFamily
            color: Theme.textMuted
        }
    }
}
