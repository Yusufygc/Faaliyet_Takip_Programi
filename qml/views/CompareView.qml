// qml/views/CompareView.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    color: Theme.bgApp

    property string scopeA: "month"
    property string scopeB: "month"
    property var periodsA: []
    property var periodsB: []
    property int periodIndexA: -1
    property int periodIndexB: -1

    function refreshPeriodsA() {
        periodsA = compareBridge.getAvailablePeriods(scopeA)
        periodIndexA = periodsA.length > 0 ? 0 : -1
    }

    function refreshPeriodsB() {
        periodsB = compareBridge.getAvailablePeriods(scopeB)
        periodIndexB = periodsB.length > 1 ? 1 : (periodsB.length > 0 ? 0 : -1)
    }

    function doCompare() {
        if (periodIndexA >= 0 && periodIndexB >= 0) {
            compareBridge.compare(scopeA, periodsA[periodIndexA], scopeB, periodsB[periodIndexB])
        }
    }

    Component.onCompleted: {
        refreshPeriodsA()
        refreshPeriodsB()
        doCompare()
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        Column {
            width: parent.width - 56
            anchors.horizontalCenter: parent.horizontalCenter
            topPadding: 28
            bottomPadding: 36
            spacing: 24

            // --- 1. Başlık ---
            Column {
                spacing: 4

                Text {
                    text: "Dönem Karşılaştırma"
                    font.pixelSize: Theme.fontTitle
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }

                Text {
                    text: "İki farklı ay veya yılın tür bazlı faaliyet sayılarını karşılaştırın"
                    font.pixelSize: Theme.fontSm
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            // --- 2. İki Panel (Yan Yana) ---
            Row {
                width: parent.width
                spacing: 20

                ComparePanel {
                    width: (parent.width - 20) / 2
                    sideTitle: "1. Dönem"
                    accentColor: Theme.primary
                    scaleIndex: root.scopeA === "year" ? 1 : 0
                    periodsModel: root.periodsA
                    periodIndex: root.periodIndexA
                    columns: compareBridge.columns
                    itemsData: compareBridge.itemsA
                    total: compareBridge.totalA

                    onScaleActivated: function(idx) {
                        root.scopeA = idx === 1 ? "year" : "month"
                        root.refreshPeriodsA()
                        root.doCompare()
                    }
                    onPeriodActivated: function(idx) {
                        root.periodIndexA = idx
                        root.doCompare()
                    }
                }

                ComparePanel {
                    width: (parent.width - 20) / 2
                    sideTitle: "2. Dönem"
                    accentColor: Theme.warning
                    scaleIndex: root.scopeB === "year" ? 1 : 0
                    periodsModel: root.periodsB
                    periodIndex: root.periodIndexB
                    columns: compareBridge.columns
                    itemsData: compareBridge.itemsB
                    total: compareBridge.totalB

                    onScaleActivated: function(idx) {
                        root.scopeB = idx === 1 ? "year" : "month"
                        root.refreshPeriodsB()
                        root.doCompare()
                    }
                    onPeriodActivated: function(idx) {
                        root.periodIndexB = idx
                        root.doCompare()
                    }
                }
            }
        }
    }
}
