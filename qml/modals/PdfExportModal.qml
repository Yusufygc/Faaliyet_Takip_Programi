// qml/modals/PdfExportModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property string currentPeriod: ""
    property bool isYearOnly: false
    property bool isAllTime: false

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openExport(periodPrefix, yearOnly, allTime) {
        currentPeriod = periodPrefix || ""
        isYearOnly = yearOnly || false
        isAllTime = allTime || false

        var defaultPrefix = isAllTime ? "" : (isYearOnly ? currentPeriod.substring(0, 4) : currentPeriod)
        var suggestedPath = statsBridge.getDefaultPdfPath(defaultPrefix)
        pathField.text = suggestedPath

        var titleStr = defaultPrefix ? (defaultPrefix + " Faaliyet Raporu") : "Tüm Zamanlar Faaliyet Raporu"
        titleField.text = titleStr

        opacity = 1.0
    }

    function close() {
        opacity = 0.0
    }

    function startExport() {
        var prefix = isAllTime ? "" : (isYearOnly ? currentPeriod.substring(0, 4) : currentPeriod)
        var savePath = pathField.text.trim()
        var reportTitle = titleField.text.trim()

        if (!savePath) {
            appBridge.showToast("warning", "Uyarı", "Lütfen bir kayıt dosyası yolu belirtiniz.")
            return
        }

        statsBridge.exportPdf(prefix, savePath, reportTitle)
        root.close()
    }

    // Modal Pencere Kartı
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 480)
        implicitHeight: contentCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.borderLight
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
            id: contentCol
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            // Başlık & Kapat
            Row {
                width: parent.width

                Column {
                    width: parent.width - 40
                    spacing: 4

                    Text {
                        text: "📄 PDF RAPORU OLUŞTUR"
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "İstatistikler ve faaliyet listesini PDF formatında dışa aktarın"
                        font.pixelSize: Theme.fontXs
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }
                }

                Rectangle {
                    width: 32
                    height: 32
                    radius: 16
                    color: closeHover.containsMouse ? Theme.bgCardElevated : "transparent"

                    Text {
                        text: "✕"
                        font.pixelSize: 14
                        color: Theme.textSecondary
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        id: closeHover
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.borderSubtle
            }

            // Dönem Özeti
            Rectangle {
                width: parent.width
                height: 50
                radius: Theme.radiusMd
                color: Theme.primaryGlow
                border.color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.4)
                border.width: 1

                Row {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    Text {
                        text: "📅"
                        font.pixelSize: 16
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: "Rapor Dönemi: " + (root.isAllTime ? "Tüm Zamanlar" : (root.isYearOnly ? (root.currentPeriod.substring(0, 4) + " Yılı (Yıllık)") : (root.currentPeriod + " (Aylık)")))
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.primaryLight
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            // Rapor Başlığı
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Rapor Başlığı"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                CustomTextField {
                    id: titleField
                    width: parent.width
                    iconText: "📝"
                }
            }

            // Kayıt Konumu
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Kayıt Edilecek Dosya Yolu"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                CustomTextField {
                    id: pathField
                    width: parent.width
                    iconText: "💾"
                }
            }

            Item { width: 1; height: 6 }

            // Aksiyon Butonları
            Row {
                anchors.right: parent.right
                spacing: 12

                CustomButton {
                    text: "İptal"
                    variant: "ghost"
                    onClicked: root.close()
                }

                CustomButton {
                    text: "📄 Raporu Kaydet & Oluştur"
                    variant: "success"
                    busy: statsBridge.isExportingPdf
                    onClicked: root.startExport()
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        z: -1
        onClicked: root.close()
    }
}
