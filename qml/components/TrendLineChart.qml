// qml/components/TrendLineChart.qml
import QtQuick
import "../theme"

Item {
    id: root

    property var dataModel: []
    property color lineColor: Theme.primary
    property int hoveredMonthIndex: -1
    signal monthClicked(string datePrefix, string monthName, int count)

    implicitWidth: 600
    implicitHeight: 280

    onDataModelChanged: canvas.requestPaint()
    onHoveredMonthIndexChanged: canvas.requestPaint()

    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.Image
        renderStrategy: Canvas.Threaded

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.clearRect(0, 0, width, height)

            var padLeft = 40
            var padRight = 30
            var padTop = 25
            var padBottom = 40
            var chartW = width - padLeft - padRight
            var chartH = height - padTop - padBottom

            if (!root.dataModel || root.dataModel.length === 0) return

            // Maksimum değeri bul
            var maxVal = 1
            for (var i = 0; i < root.dataModel.length; i++) {
                if (root.dataModel[i].count > maxVal) maxVal = root.dataModel[i].count
            }
            // Yuvarla (en az 4 grid çizgisi)
            var gridMax = Math.ceil(maxVal * 1.25)
            if (gridMax < 4) gridMax = 4

            // 1. Yatay Izgara Çizgileri & Y-Eksen Etiketleri
            var numGridLines = 4
            ctx.lineWidth = 1
            ctx.strokeStyle = "#1E293B"
            ctx.font = "10px " + Theme.fontFamily
            ctx.fillStyle = "#64748B"
            ctx.textAlign = "right"
            ctx.textBaseline = "middle"

            for (var g = 0; g <= numGridLines; g++) {
                var yVal = Math.round((gridMax / numGridLines) * g)
                var yPos = padTop + chartH - (g / numGridLines) * chartH

                ctx.beginPath()
                ctx.moveTo(padLeft, yPos)
                ctx.lineTo(padLeft + chartW, yPos)
                ctx.stroke()

                ctx.fillText(String(yVal), padLeft - 8, yPos)
            }

            // 2. Nokta Koordinatlarını Hesapla
            var points = []
            var stepX = chartW / (root.dataModel.length - 1)

            for (var i = 0; i < root.dataModel.length; i++) {
                var item = root.dataModel[i]
                var px = padLeft + (i * stepX)
                var py = padTop + chartH - ((item.count / gridMax) * chartH)
                points.push({ x: px, y: py, item: item, index: i })
            }

            // 3. Alan Gradyan Dolgusu (Area Gradient)
            if (points.length > 0) {
                var grad = ctx.createLinearGradient(0, padTop, 0, padTop + chartH)
                grad.addColorStop(0.0, Qt.rgba(root.lineColor.r, root.lineColor.g, root.lineColor.b, 0.40))
                grad.addColorStop(1.0, Qt.rgba(root.lineColor.r, root.lineColor.g, root.lineColor.b, 0.02))

                ctx.beginPath()
                ctx.moveTo(points[0].x, padTop + chartH)
                ctx.lineTo(points[0].x, points[0].y)

                for (var i = 0; i < points.length - 1; i++) {
                    var p0 = points[i]
                    var p1 = points[i + 1]
                    var mx = (p0.x + p1.x) / 2
                    ctx.bezierCurveTo(mx, p0.y, mx, p1.y, p1.x, p1.y)
                }

                ctx.lineTo(points[points.length - 1].x, padTop + chartH)
                ctx.closePath()
                ctx.fillStyle = grad
                ctx.fill()
            }

            // 4. Çizgi Çizimi (Smooth Line Curve)
            if (points.length > 0) {
                ctx.beginPath()
                ctx.moveTo(points[0].x, points[0].y)

                for (var i = 0; i < points.length - 1; i++) {
                    var p0 = points[i]
                    var p1 = points[i + 1]
                    var mx = (p0.x + p1.x) / 2
                    ctx.bezierCurveTo(mx, p0.y, mx, p1.y, p1.x, p1.y)
                }

                ctx.strokeStyle = root.lineColor
                ctx.lineWidth = 3
                ctx.stroke()
            }

            // 5. Ay İsimleri (X-Eksen) & Veri Noktaları
            ctx.textAlign = "center"
            ctx.textBaseline = "top"
            ctx.font = "11px " + Theme.fontFamily

            for (var i = 0; i < points.length; i++) {
                var pt = points[i]
                var isHovered = (root.hoveredMonthIndex === i)

                // Ay Etiketi
                ctx.fillStyle = isHovered ? Theme.primaryLight : "#94A3B8"
                ctx.fillText(pt.item.monthName || String(i + 1), pt.x, padTop + chartH + 10)

                // Dış Halka (Hover ise parlama)
                if (isHovered) {
                    ctx.beginPath()
                    ctx.arc(pt.x, pt.y, 8, 0, 2 * Math.PI)
                    ctx.fillStyle = Qt.rgba(root.lineColor.r, root.lineColor.g, root.lineColor.b, 0.35)
                    ctx.fill()
                }

                // Veri Noktası Dairesi
                ctx.beginPath()
                ctx.arc(pt.x, pt.y, isHovered ? 5 : 3.5, 0, 2 * Math.PI)
                ctx.fillStyle = isHovered ? "#FFFFFF" : root.lineColor
                ctx.fill()
                ctx.strokeStyle = root.lineColor
                ctx.lineWidth = 2
                ctx.stroke()
            }
        }
    }

    // Yüzen Tooltip Balonu
    Rectangle {
        id: tooltipBox
        visible: root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < root.dataModel.length
        width: 100
        height: 38
        radius: Theme.radiusSm
        color: Qt.rgba(15, 23, 42, 0.92)
        border.color: root.lineColor
        border.width: 1
        z: 10

        Column {
            anchors.centerIn: parent
            spacing: 1

            Text {
                text: (root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < root.dataModel.length)
                      ? root.dataModel[root.hoveredMonthIndex].monthName + " " + root.dataModel[root.hoveredMonthIndex].year
                      : ""
                font.pixelSize: Theme.fontXs - 1
                font.family: Theme.fontFamily
                color: Theme.textMuted
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: (root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < root.dataModel.length)
                      ? root.dataModel[root.hoveredMonthIndex].count + " Aktivite"
                      : ""
                font.pixelSize: Theme.fontXs
                font.bold: true
                font.family: Theme.fontFamily
                color: root.lineColor
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // Mouse Etkileşim Alanı
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.hoveredMonthIndex >= 0 ? Qt.PointingHandCursor : Qt.ArrowCursor

        onPositionChanged: function(mouse) {
            var padLeft = 40
            var padRight = 30
            var chartW = width - padLeft - padRight

            if (!root.dataModel || root.dataModel.length === 0) return

            var stepX = chartW / (root.dataModel.length - 1)
            var relX = mouse.x - padLeft
            var idx = Math.round(relX / stepX)

            if (idx >= 0 && idx < root.dataModel.length) {
                root.hoveredMonthIndex = idx
                var ptX = padLeft + (idx * stepX)
                tooltipBox.x = Math.max(10, Math.min(width - tooltipBox.width - 10, ptX - (tooltipBox.width / 2)))
                tooltipBox.y = Math.max(5, mouse.y - tooltipBox.height - 12)
            } else {
                root.hoveredMonthIndex = -1
            }
        }

        onExited: {
            root.hoveredMonthIndex = -1
        }

        onClicked: {
            if (root.hoveredMonthIndex >= 0 && root.hoveredMonthIndex < root.dataModel.length) {
                var item = root.dataModel[root.hoveredMonthIndex]
                root.monthClicked(item.datePrefix, item.monthName, item.count)
            }
        }
    }
}
