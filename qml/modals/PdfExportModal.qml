// qml/modals/PdfExportModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property string currentPeriod: ""
    // scopeIndex: 0 = Aylık, 1 = Yıllık, 2 = Tüm Zamanlar
    property int scopeIndex: 0

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function currentPrefix() {
        if (scopeIndex === 2) return ""
        if (scopeIndex === 1) return periodField.text.trim().substring(0, 4)
        return periodField.text.trim()
    }

    function refreshSuggestions() {
        var prefix = currentPrefix()
        pathField.text = statsBridge.getDefaultPdfPath(prefix)
        titleField.text = prefix ? (prefix + " Faaliyet Raporu") : "Tüm Zamanlar Faaliyet Raporu"
    }

    function openExport(periodPrefix, yearOnly, allTime) {
        currentPeriod = periodPrefix || ""
        scopeIndex = allTime ? 2 : (yearOnly ? 1 : 0)
        scopeCombo.currentIndex = scopeIndex
        periodField.text = allTime ? "" : (yearOnly ? currentPeriod.substring(0, 4) : currentPeriod)

        refreshSuggestions()
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
    }

    function startExport() {
        var prefix = currentPrefix()
        var savePath = pathField.text.trim()
        var reportTitle = titleField.text.trim()

        if (scopeIndex !== 2 && !prefix) {
            appBridge.showToast("warning", "Uyarı", "Lütfen bir dönem giriniz.")
            return
        }

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

            // Rapor Kapsamı Seçimi
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Rapor Kapsamı"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                Row {
                    width: parent.width
                    spacing: 10

                    CustomComboBox {
                        id: scopeCombo
                        width: 160
                        model: ["Aylık", "Yıllık", "Tüm Zamanlar"]
                        onActivated: function(index) {
                            root.scopeIndex = index
                            root.refreshSuggestions()
                        }
                    }

                    CustomTextField {
                        id: periodField
                        width: parent.width - scopeCombo.width - 10
                        visible: root.scopeIndex !== 2
                        placeholderText: root.scopeIndex === 1 ? "YYYY" : "YYYY-MM"
                        iconText: "📅"
                        onTextChanged: root.refreshSuggestions()
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
