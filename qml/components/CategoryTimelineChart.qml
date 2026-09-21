// qml/components/CategoryTimelineChart.qml
import QtQuick
import "../theme"

Item {
    id: root

    // [{ month, monthName, total, categories: [{ type, count, color }, ...] }, ...] (12 ay)
    property var dataModel: []
    property int hoveredMonthIndex: -1

    implicitWidth: 240
    implicitHeight: 280

    onDataModelChanged: canvas.requestPaint()
    onHoveredMonthIndexChanged: canvas.requestPaint()

    Connections {
        target: Theme
        function onIsDarkChanged() { canvas.requestPaint() }
    }

    Text {
        id: title
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        text: "Zamana Göre Kategori Payı"
        font.pixelSize: Theme.fontXs
        font.bold: true
        font.family: Theme.fontFamily
        color: Theme.textMuted
        wrapMode: Text.WordWrap
    }

    Canvas {
        id: canvas
        anchors.top: title.bottom
        anchors.topMargin: 14
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        renderTarget: Canvas.Image
        renderStrategy: Canvas.Threaded

        property int padTop: 18
        property int padBottom: 16

        function xForMonth(i) {
            return (i / 11) * width
        }

        function buildCumulative() {
            var months = root.dataModel
            var result = []
            if (!months || months.length !== 12) return result

            var numCats = months[0].categories ? months[0].categories.length : 0
            for (var i = 0; i < 12; i++) {
                var cum = [0]
                var cats = months[i].categories || []
                for (var k = 0; k < numCats; k++) {
                    cum.push(cum[k] + (cats[k] ? cats[k].count : 0))
                }
                result.push(cum)
            }
            return result
        }

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.clearRect(0, 0, width, height)

            var months = root.dataModel
            if (!months || months.length !== 12) {
                ctx.font = "12px " + Theme.fontFamily
                ctx.fillStyle = Theme.textMuted
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                ctx.fillText("Veri bulunmuyor", width / 2, height / 2)
                return
            }

            var numCats = months[0].categories ? months[0].categories.length : 0
            var maxTotal = 1
            for (var i = 0; i < 12; i++) {
                maxTotal = Math.max(maxTotal, months[i].total)
            }

            var chartH = height - padTop - padBottom

            function yFor(v) {
                return padTop + chartH - (v / maxTotal) * chartH
            }

            var cumulative = buildCumulative()

            if (numCats === 0 || maxTotal <= 1) {
                ctx.font = "11px " + Theme.fontFamily
                ctx.fillStyle = Theme.textMuted
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                ctx.fillText("Yeterli veri yok", width / 2, padTop + chartH / 2)
            } else {
                // Kategori bantlarını çiz (alttan üste yığılmış)
                for (var k = 0; k < numCats; k++) {
                    var color = months[0].categories[k].color || Theme.primary

                    ctx.beginPath()
                    for (var m = 0; m < 12; m++) {
                        var x = xForMonth(m)
                        var yTop = yFor(cumulative[m][k + 1])
                        if (m === 0) ctx.moveTo(x, yTop)
                        else ctx.lineTo(x, yTop)
                    }
                    for (var m2 = 11; m2 >= 0; m2--) {
                        var x2 = xForMonth(m2)
                        var yBottom = yFor(cumulative[m2][k])
                        ctx.lineTo(x2, yBottom)
                    }
                    ctx.closePath()
                    ctx.fillStyle = Qt.rgba(color.r, color.g, color.b, 0.7)
                    ctx.fill()

                    // Üst kenar çizgisi (banda belirginlik katmak için)
                    ctx.beginPath()
                    for (var m3 = 0; m3 < 12; m3++) {
                        var x3 = xForMonth(m3)
                        var yTop3 = yFor(cumulative[m3][k + 1])
                        if (m3 === 0) ctx.moveTo(x3, yTop3)
                        else ctx.lineTo(x3, yTop3)
                    }
                    ctx.strokeStyle = color
                    ctx.lineWidth = 1
                    ctx.stroke()
                }
            }

            // Hover: dikey kılavuz çizgisi
            if (root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < 12) {
                var hx = xForMonth(root.hoveredMonthIndex)
                ctx.strokeStyle = Theme.textMuted
                ctx.lineWidth = 1
                ctx.beginPath()
                ctx.moveTo(hx, padTop)
                ctx.lineTo(hx, padTop + chartH)
                ctx.stroke()
            }

            // Ay Etiketleri (çeyreklik: Oca, Nis, Tem, Eki)
            ctx.font = "9px " + Theme.fontFamily
            ctx.fillStyle = Theme.textMuted
            ctx.textAlign = "center"
            ctx.textBaseline = "top"
            var labelMonths = [0, 3, 6, 9]
            for (var lm = 0; lm < labelMonths.length; lm++) {
                var idx = labelMonths[lm]
                ctx.fillText(months[idx].monthName, xForMonth(idx), padTop + chartH + 4)
            }

            // Hover Detay Metni (üstte)
            if (root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < 12) {
                var hovered = months[root.hoveredMonthIndex]
                ctx.font = "bold 10px " + Theme.fontFamily
                ctx.fillStyle = Theme.textPrimary
                ctx.textAlign = "center"
                ctx.textBaseline = "top"
                ctx.fillText(hovered.monthName + " · " + hovered.total + " Faaliyet", width / 2, 0)
            }
        }
    }

    MouseArea {
        anchors.fill: canvas
        hoverEnabled: true

        onPositionChanged: function(mouse) {
            if (!root.dataModel || root.dataModel.length !== 12) {
                root.hoveredMonthIndex = -1
                return
            }
            var idx = Math.round((mouse.x / canvas.width) * 11)
            root.hoveredMonthIndex = Math.max(0, Math.min(11, idx))
        }

        onExited: root.hoveredMonthIndex = -1
    }
}
