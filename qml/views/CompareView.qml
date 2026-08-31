// qml/views/CompareView.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    color: Theme.bgApp

    Component.onCompleted: {
        var periods = compareBridge.getAvailablePeriods("month")
        if (periods && periods.length >= 2) {
            periodACombo.model = periods
            periodBCombo.model = periods
            periodACombo.currentIndex = 0
            periodBCombo.currentIndex = 1
            compareBridge.compare(periods[0], periods[1])
        } else if (periods && periods.length === 1) {
            periodACombo.model = periods
            periodBCombo.model = periods
            compareBridge.compare(periods[0], periods[0])
        }
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
                    text: "İki farklı dönemin faaliyet sayılarını ve kategori dağılımlarını kıyaslayın"
                    font.pixelSize: Theme.fontSm
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            // --- 2. Dönem Seçici Çubuğu ---
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
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: 16

                    // Tür Seçimi (Aylık / Yıllık)
                    Row {
                        spacing: 8
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            text: "Ölçek:"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        CustomComboBox {
                            width: 110
                            model: ["Aylık", "Yıllık"]
                            onActivated: {
                                var pType = currentIndex === 0 ? "month" : "year"
                                var periods = compareBridge.getAvailablePeriods(pType)
                                periodACombo.model = periods
                                periodBCombo.model = periods
                                if (periods.length >= 2) {
                                    periodACombo.currentIndex = 0
                                    periodBCombo.currentIndex = 1
                                    compareBridge.compare(periods[0], periods[1])
                                }
                            }
                        }
                    }

                    // 1. Dönem
                    Row {
                        spacing: 8
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            text: "1. Dönem:"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.primaryLight
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        CustomComboBox {
                            id: periodACombo
                            width: 140
                        }
                    }

                    Text {
                        text: "VS"
                        font.pixelSize: Theme.fontMd
                        font.bold: true
                        color: Theme.accent
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // 2. Dönem
                    Row {
                        spacing: 8
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            text: "2. Dönem:"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.warning
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        CustomComboBox {
                            id: periodBCombo
                            width: 140
                        }
                    }

                    Item { width: 1; height: 1 }

                    CustomButton {
                        text: "Karşılaştır"
                        icon: Icons.nav_compare
                        variant: "primary"
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: {
                            if (periodACombo.currentText && periodBCombo.currentText) {
                                compareBridge.compare(periodACombo.currentText, periodBCombo.currentText)
                            }
                        }
                    }
                }
            }

            // --- 3. Karşılaştırma KPI Kartları ---
            Row {
                width: parent.width
                spacing: 16

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "1. DÖNEM TOPLAM (" + compareBridge.periodA + ")"
                    value: String(compareBridge.totalA)
                    subtitle: "Faaliyet adedi"
                    icon: Icons.calendar
                    accentColor: Theme.primary
                }

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "2. DÖNEM TOPLAM (" + compareBridge.periodB + ")"
                    value: String(compareBridge.totalB)
                    subtitle: "Faaliyet adedi"
                    icon: Icons.calendar
                    accentColor: Theme.warning
                }

                StatCard {
                    width: (parent.width - 32) / 3
                    title: "FARK (DEĞİŞİM)"
                    value: (compareBridge.diffCount > 0 ? ("+" + compareBridge.diffCount) : String(compareBridge.diffCount))
                    subtitle: compareBridge.diffCount > 0 ? "1. döneme göre artış" : (compareBridge.diffCount < 0 ? "1. döneme göre azalış" : "Değişim yok")
                    icon: Icons.nav_compare
                    accentColor: compareBridge.diffCount >= 0 ? Theme.success : Theme.danger
                }
            }

            // --- 4. Kategori Kıyaslama Tablosu ---
            Rectangle {
                width: parent.width
                implicitHeight: compCol.implicitHeight + 36
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: compCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Text {
                        text: "Kategori Bazlı Karşılaştırma Tablosu"
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    // Başlık Satırı
                    Rectangle {
                        width: parent.width
                        height: 38
                        radius: Theme.radiusSm
                        color: Theme.bgInput

                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16

                            Text {
                                text: "Kategori"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.textSecondary
                                width: 140
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: compareBridge.periodA + " (1. Dönem)"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.primaryLight
                                width: 180
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: compareBridge.periodB + " (2. Dönem)"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.warning
                                width: 180
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: "Fark"
                                font.pixelSize: Theme.fontSm
                                font.bold: true
                                color: Theme.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }

                    // Kategori Karşılaştırma Satırları
                    ListView {
                        id: compListView
                        width: parent.width
                        implicitHeight: contentHeight
                        clip: true
                        model: compareBridge.categoryComparison
                        spacing: 8

                        delegate: Rectangle {
                            width: compListView.width
                            height: 48
                            radius: Theme.radiusSm
                            color: Theme.bgSidebar
                            border.color: Theme.borderSubtle
                            border.width: 1

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 16

                                Badge {
                                    text: modelData.type
                                    badgeColor: modelData.color
                                    width: 120
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.countA + " Kayıt"
                                    font.pixelSize: Theme.fontSm
                                    font.bold: true
                                    color: Theme.textPrimary
                                    width: 180
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.countB + " Kayıt"
                                    font.pixelSize: Theme.fontSm
                                    font.bold: true
                                    color: Theme.textPrimary
                                    width: 180
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Badge {
                                    text: modelData.diffText
                                    badgeColor: modelData.difference > 0 ? Theme.success : (modelData.difference < 0 ? Theme.danger : Theme.textMuted)
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }
                    }

                    Text {
                        text: "Karşılaştırma yapılacak veri bulunamadı."
                        font.pixelSize: Theme.fontSm
                        color: Theme.textMuted
                        visible: compareBridge.categoryComparison.length === 0
                    }
                }
            }
        }
    }
}
