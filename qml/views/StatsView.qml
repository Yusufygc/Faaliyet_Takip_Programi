// qml/views/StatsView.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"
import "../modals"

Rectangle {
    id: root

    color: Theme.bgApp

    Component.onCompleted: {
        var now = new Date()
        var year = now.getFullYear()
        var month = String(now.getMonth() + 1).padStart(2, '0')
        var defaultPrefix = year + "-" + month
        dateInput.text = defaultPrefix
        statsBridge.loadStats(defaultPrefix, false, false)
        statsBridge.loadTrend(year, "Hepsi")
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

            // --- 1. Başlık & Aksiyon Alanı ---
            Item {
                width: parent.width
                height: 44

                Column {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4

                    Text {
                        text: "İstatistik & Trend Paneli"
                        font.pixelSize: Theme.fontTitle
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "Aktivite dağılımlarınız, pasta grafiği, puan ortalamalarınız ve zaman serisi trendleri"
                        font.pixelSize: Theme.fontSm
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }
                }

                // PDF Rapor Butonu
                CustomButton {
                    text: "PDF Raporu Oluştur"
                    icon: Icons.pdf
                    variant: "success"
                    fontSize: Theme.fontSm + 1
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    busy: statsBridge.isExportingPdf
                    onClicked: {
                        pdfExportModal.openExport(
                            statsBridge.datePrefix,
                            statsBridge.isYearOnly,
                            statsBridge.isAllTime
                        )
                    }
                }
            }

            // --- 2. Dönem Filtre Çubuğu (Ferah ve Şık Kutucuklar) ---
            Rectangle {
                width: parent.width
                height: 60
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Row {
                    anchors.fill: parent
                    anchors.margins: 10
                    anchors.leftMargin: 18
                    anchors.rightMargin: 18
                    spacing: 20

                    Text {
                        text: "Rapor Dönemi:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Tarih Girişi (Genişletilmiş ve Vektör İkonlu)
                    CustomTextField {
                        id: dateInput
                        width: 145
                        placeholderText: "YYYY-MM"
                        icon: Icons.calendar
                        enabled: !allTimeCheck.checked
                        onAccepted: statsBridge.loadStats(text, yearOnlyCheck.checked, allTimeCheck.checked)
                    }

                    // Şık Sadece Yıl Seçeneği
                    CustomCheckBox {
                        id: yearOnlyCheck
                        text: "Sadece Yıl Bazında"
                        enabled: !allTimeCheck.checked
                        anchors.verticalCenter: parent.verticalCenter
                        onToggled: function(isChecked) {
                            if (isChecked) {
                                if (dateInput.text.length >= 4) {
                                    statsBridge.loadStats(dateInput.text.substring(0, 4), true, false)
                                }
                            } else {
                                statsBridge.loadStats(dateInput.text, false, false)
                            }
                        }
                    }

                    // Şık Tüm Zamanlar Seçeneği
                    CustomCheckBox {
                        id: allTimeCheck
                        text: "Tüm Zamanlar"
                        anchors.verticalCenter: parent.verticalCenter
                        onToggled: function(isChecked) {
                            if (isChecked) {
                                statsBridge.loadStats("", false, true)
                            } else {
                                statsBridge.loadStats(dateInput.text, yearOnlyCheck.checked, false)
                            }
                        }
                    }

                    Item { width: 1; height: 1 }

                    CustomButton {
                        text: "Yenile"
                        icon: Icons.refresh
                        variant: "secondary"
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: statsBridge.loadStats(dateInput.text, yearOnlyCheck.checked, allTimeCheck.checked)
                    }
                }
            }

            // --- 3. KPI Özet Kartları (Vektör İkon Rozetleri) ---
            Row {
                width: parent.width
                spacing: 16

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "TOPLAM FAALİYET"
                    value: String(statsBridge.kpiTotal)
                    subtitle: statsBridge.isAllTime ? "Tüm zamanlar toplamı" : (statsBridge.isYearOnly ? "Yıllık toplam aktivite" : "Aylık toplam aktivite")
                    icon: Icons.nav_list
                    accentColor: Theme.primary
                }

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "GENEL ORTALAMA PUAN"
                    value: statsBridge.kpiAvgRating > 0 ? statsBridge.kpiAvgRating.toFixed(1) + " ★" : "-"
                    subtitle: "Değerlendirilen faaliyetler üzerinden"
                    icon: Icons.star
                    accentColor: Theme.warning
                }

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "EN AKTİF KATEGORİ"
                    value: statsBridge.kpiTopCategory
                    subtitle: statsBridge.kpiTopCategoryCount > 0 ? (statsBridge.kpiTopCategoryCount + " faaliyet ile lider") : "Veri bulunmuyor"
                    icon: Icons.trophy
                    accentColor: Theme.categoryColor(statsBridge.kpiTopCategory)
                }
            }

            // --- 4. BÖLÜM: Kategori Dağılımı & Pasta/Donut Grafiği ---
            Rectangle {
                width: parent.width
                implicitHeight: pieSectionCol.implicitHeight + 40
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: pieSectionCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Item {
                        width: parent.width
                        height: 28

                        Row {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 8

                            Icon {
                                name: Icons.app_logo
                                size: 16
                                color: Theme.primary
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: "Kategori Dağılımı (Pasta & Detay)"
                                font.pixelSize: Theme.fontLg
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        Text {
                            text: "Detayları görmek için pasta dilimine veya kategoriye tıklayın"
                            font.pixelSize: Theme.fontXs
                            font.family: Theme.fontFamily
                            color: Theme.textMuted
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    // Pasta Grafiği, Bar Grafiği ve Liste Tablosu Yan Yana
                    RowLayout {
                        width: parent.width
                        spacing: 24

                        // Sol: İnteraktif Pasta/Donut Grafiği
                        CategoryPieChart {
                            id: pieChart
                            Layout.preferredWidth: 280
                            Layout.preferredHeight: 280
                            dataModel: statsBridge.categoryDistribution
                            totalCount: statsBridge.kpiTotal
                            onCategoryClicked: function(catName) {
                                categoryDetailModal.openCategory(catName)
                            }
                        }

                        // Orta: Zamana Göre Kategori Payı
                        CategoryTimelineChart {
                            id: timelineChart
                            Layout.preferredWidth: 240
                            Layout.preferredHeight: 280
                            dataModel: statsBridge.monthlyCategoryDistribution
                        }

                        // Sağ: Kategori Dağılım Listesi
                        ListView {
                            id: catListView
                            Layout.fillWidth: true
                            Layout.minimumWidth: 260
                            Layout.maximumWidth: 340
                            implicitHeight: Math.max(260, contentHeight)
                            clip: true
                            model: statsBridge.categoryDistribution
                            spacing: 8

                            delegate: Rectangle {
                                id: catItem
                                width: catListView.width
                                height: 48
                                radius: Theme.radiusMd
                                color: catMouse.containsMouse ? Theme.bgCardElevated : Theme.bgInput
                                border.color: catMouse.containsMouse ? modelData.color : "transparent"
                                border.width: 1

                                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                                Item {
                                    anchors.fill: parent
                                    anchors.leftMargin: 14
                                    anchors.rightMargin: 14

                                    Row {
                                        anchors.left: parent.left
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 10

                                        Badge {
                                            text: modelData.type
                                            badgeColor: modelData.color
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Text {
                                            text: modelData.count + " Adet"
                                            font.pixelSize: Theme.fontSm
                                            font.bold: true
                                            color: Theme.textPrimary
                                            anchors.verticalCenter: parent.verticalCenter
                                        }
                                    }

                                    Row {
                                        anchors.right: parent.right
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 8

                                        // İlerleme Yüzde Barı
                                        Rectangle {
                                            width: 50
                                            height: 6
                                            radius: 3
                                            color: Theme.borderSubtle
                                            anchors.verticalCenter: parent.verticalCenter

                                            Rectangle {
                                                width: Math.max(4, parent.width * (modelData.percent / 100))
                                                height: parent.height
                                                radius: 3
                                                color: modelData.color
                                            }
                                        }

                                        Text {
                                            text: modelData.avgRating > 0 ? (modelData.avgRating.toFixed(1) + " ★") : "-"
                                            font.pixelSize: Theme.fontXs
                                            font.bold: true
                                            color: Theme.textSecondary
                                            anchors.verticalCenter: parent.verticalCenter
                                        }
                                    }
                                }

                                MouseArea {
                                    id: catMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: categoryDetailModal.openCategory(modelData.type)
                                }
                            }
                        }
                    }
                }
            }

            // --- 5. BÖLÜM: Zaman Serisi ve Trend Analizi ---
            Rectangle {
                width: parent.width
                implicitHeight: trendCol.implicitHeight + 40
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: trendCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    // Başlık ve Filtreler (Vektör İkonlu)
                    Item {
                        width: parent.width
                        height: 38

                        Row {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 8

                            Icon {
                                name: Icons.nav_stats
                                size: 17
                                color: Theme.primary
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: "Zaman Serisi & Trend Analizi"
                                font.pixelSize: Theme.fontLg
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        // Yıl ve Kategori Seçici
                        Row {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 10

                            Text {
                                text: "Yıl:"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            CustomComboBox {
                                id: trendYearCombo
                                width: 90
                                model: statsBridge.availableYears
                                currentIndex: 4 // Mevcut yıl
                                onActivated: {
                                    statsBridge.loadTrend(parseInt(currentText), trendCatCombo.currentText)
                                }
                            }

                            Text {
                                text: "Kategori:"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            CustomComboBox {
                                id: trendCatCombo
                                width: 130
                                model: ["Hepsi"].concat(settingsBridge.typesList)
                                onActivated: {
                                    statsBridge.loadTrend(parseInt(trendYearCombo.currentText), currentText)
                                }
                            }
                        }
                    }

                    // Trend Özet Mini Kartları (Vektör İkonlu)
                    Row {
                        width: parent.width
                        spacing: 16

                        Rectangle {
                            width: (parent.width - 32) / 3
                            height: 68
                            radius: Theme.radiusMd
                            color: Theme.bgInput

                            Column {
                                anchors.centerIn: parent
                                spacing: 4

                                Row {
                                    spacing: 6
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    Icon {
                                        name: Icons.calendar
                                        size: 11
                                        color: Theme.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Text {
                                        text: "YILLIK TOPLAM (" + statsBridge.trendYear + ")"
                                        font.pixelSize: Theme.fontXs - 1
                                        font.bold: true
                                        color: Theme.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }

                                Text {
                                    text: statsBridge.trendTotal + " Aktivite"
                                    font.pixelSize: Theme.fontLg
                                    font.bold: true
                                    color: Theme.primaryLight
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }

                        Rectangle {
                            width: (parent.width - 32) / 3
                            height: 68
                            radius: Theme.radiusMd
                            color: Theme.bgInput

                            Column {
                                anchors.centerIn: parent
                                spacing: 4

                                Row {
                                    spacing: 6
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    Icon {
                                        name: Icons.nav_stats
                                        size: 11
                                        color: Theme.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Text {
                                        text: "AYLIK ORTALAMA"
                                        font.pixelSize: Theme.fontXs - 1
                                        font.bold: true
                                        color: Theme.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }

                                Text {
                                    text: statsBridge.trendMonthlyAvg.toFixed(1) + " / Ay"
                                    font.pixelSize: Theme.fontLg
                                    font.bold: true
                                    color: Theme.success
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }

                        Rectangle {
                            width: (parent.width - 32) / 3
                            height: 68
                            radius: Theme.radiusMd
                            color: Theme.bgInput

                            Column {
                                anchors.centerIn: parent
                                spacing: 4

                                Row {
                                    spacing: 6
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    Icon {
                                        name: Icons.trophy
                                        size: 11
                                        color: Theme.warning
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Text {
                                        text: "EN AKTİF AY (ZİRVE)"
                                        font.pixelSize: Theme.fontXs - 1
                                        font.bold: true
                                        color: Theme.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }

                                Text {
                                    text: statsBridge.trendPeakMonthName + " (" + statsBridge.trendPeakMonthCount + " Kayıt)"
                                    font.pixelSize: Theme.fontLg
                                    font.bold: true
                                    color: Theme.warning
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                    }

                    // İnteraktif Trend Çizgi / Alan Grafiği
                    TrendLineChart {
                        id: trendChart
                        width: parent.width
                        height: 270
                        dataModel: statsBridge.trendData
                        lineColor: Theme.categoryColor(statsBridge.trendCategory)
                        onMonthClicked: function(prefix, mName, count) {
                            if (count > 0) {
                                monthDetailModal.openMonth(prefix, mName, statsBridge.trendCategory)
                            }
                        }
                    }
                }
            }
        }
    }

    // ✨ MODALLAR ✨
    PdfExportModal {
        id: pdfExportModal
    }

    CategoryDetailModal {
        id: categoryDetailModal
    }

    CategoryDetailModal {
        id: monthDetailModal
    }
}
