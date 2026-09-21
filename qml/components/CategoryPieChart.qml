// qml/components/CategoryPieChart.qml
import QtQuick
import "../theme"

Item {
    id: root

    property var dataModel: []
    property int totalCount: 0
    property int hoveredIndex: -1
    signal categoryClicked(string category)

    implicitWidth: 320
    implicitHeight: 320

    onDataModelChanged: canvas.requestPaint()
    onHoveredIndexChanged: canvas.requestPaint()

    Connections {
        target: Theme
        function onIsDarkChanged() { canvas.requestPaint() }
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.Image
        renderStrategy: Canvas.Threaded

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.clearRect(0, 0, width, height)

            if (!root.dataModel || root.dataModel.length === 0 || root.totalCount <= 0) {
                // Boş durum halkası
                ctx.beginPath()
                ctx.arc(width / 2, height / 2, Math.min(width, height) / 2 - 20, 0, 2 * Math.PI)
                ctx.strokeStyle = Theme.borderSubtle
                ctx.lineWidth = 28
                ctx.stroke()
                return
            }

            var centerX = width / 2
            var centerY = height / 2
            var outerRadius = Math.min(width, height) / 2 - 16
            var innerRadius = outerRadius - 32
            var currentAngle = -0.5 * Math.PI

            for (var i = 0; i < root.dataModel.length; i++) {
                var item = root.dataModel[i]
                var sliceAngle = (item.count / root.totalCount) * (2 * Math.PI)
                var isHovered = (root.hoveredIndex === i)
                var rOuter = isHovered ? outerRadius + 6 : outerRadius

                ctx.beginPath()
                ctx.arc(centerX, centerY, rOuter, currentAngle, currentAngle + sliceAngle, false)
                ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true)
                ctx.closePath()

                ctx.fillStyle = item.color || "#3B82F6"
                ctx.fill()

                ctx.strokeStyle = Theme.bgCard
                ctx.lineWidth = 2
                ctx.stroke()

                currentAngle += sliceAngle
            }
        }
    }

    // Merkezdeki Özet Bilgi (Toplam veya Seçili Kategori)
    Column {
        anchors.centerIn: parent
        spacing: 2

        Text {
            text: root.hoveredIndex >= 0 && root.hoveredIndex < root.dataModel.length
                  ? root.dataModel[root.hoveredIndex].count + " Adet"
                  : String(root.totalCount)
            font.pixelSize: Theme.fontXl + 2
            font.bold: true
            font.family: Theme.fontFamily
            color: root.hoveredIndex >= 0 && root.hoveredIndex < root.dataModel.length
                   ? root.dataModel[root.hoveredIndex].color
                   : Theme.textPrimary
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: root.hoveredIndex >= 0 && root.hoveredIndex < root.dataModel.length
                  ? root.dataModel[root.hoveredIndex].type + " (%" + root.dataModel[root.hoveredIndex].percent + ")"
                  : "Toplam Aktivite"
            font.pixelSize: Theme.fontXs
            font.bold: true
            font.family: Theme.fontFamily
            color: Theme.textSecondary
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    // Dilim Hover ve Tıklama Tespiti
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.hoveredIndex >= 0 ? Qt.PointingHandCursor : Qt.ArrowCursor

        onPositionChanged: function(mouse) {
            var dx = mouse.x - (width / 2)
            var dy = mouse.y - (height / 2)
            var dist = Math.sqrt(dx * dx + dy * dy)
            var outerRadius = Math.min(width, height) / 2 - 10
            var innerRadius = outerRadius - 40

            if (dist >= innerRadius && dist <= outerRadius && root.totalCount > 0) {
                var angle = Math.atan2(dy, dx)
                // Normalize angle to start at top (-PI/2)
                var normAngle = angle + (0.5 * Math.PI)
                if (normAngle < 0) normAngle += 2 * Math.PI

                var curAngle = 0
                for (var i = 0; i < root.dataModel.length; i++) {
                    var slice = (root.dataModel[i].count / root.totalCount) * (2 * Math.PI)
                    if (normAngle >= curAngle && normAngle <= curAngle + slice) {
                        root.hoveredIndex = i
                        return
                    }
                    curAngle += slice
                }
            }
            root.hoveredIndex = -1
        }

        onExited: {
            root.hoveredIndex = -1
        }

        onClicked: {
            if (root.hoveredIndex >= 0 && root.hoveredIndex < root.dataModel.length) {
                root.categoryClicked(root.dataModel[root.hoveredIndex].type)
            }
        }
    }
}
