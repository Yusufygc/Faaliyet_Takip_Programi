// qml/modals/PlanFormModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property bool isEdit: false
    property int editId: 0

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openAdd(defaultFolderId) {
        isEdit = false
        editId = 0
        titleField.text = ""
        descField.text = ""
        scopeCombo.currentIndex = 0 // Aylık
        
        var d = new Date()
        yearField.text = String(d.getFullYear())
        monthCombo.currentIndex = d.getMonth()
        priorityCombo.currentIndex = 1 // Orta
        
        // Klasör seçimi
        var fIndex = 0
        if (defaultFolderId && defaultFolderId > 0) {
            for (var i = 0; i < planBridge.folders.length; i++) {
                if (planBridge.folders[i].id === defaultFolderId) {
                    fIndex = i
                    break
                }
            }
        }
        folderCombo.currentIndex = fIndex
        progressSlider.value = 0

        opacity = 1.0
        titleField.inputItem.forceActiveFocus()
    }

    function openEdit(planId) {
        var data = planBridge.getPlanById(planId)
        if (!data || !data.id) return

        isEdit = true
        editId = planId
        titleField.text = data.title || ""
        descField.text = data.description || ""
        scopeCombo.currentIndex = data.scope === "yearly" ? 1 : 0
        yearField.text = String(data.year || new Date().getFullYear())
        monthCombo.currentIndex = Math.max(0, (data.month || 1) - 1)
        
        var pIdx = 1
        if (data.priority === "high") pIdx = 2
        else if (data.priority === "low") pIdx = 0
        priorityCombo.currentIndex = pIdx

        var fIndex = 0
        for (var i = 0; i < planBridge.folders.length; i++) {
            if (planBridge.folders[i].id === data.folderId) {
                fIndex = i
                break
            }
        }
        folderCombo.currentIndex = fIndex
        progressSlider.value = data.progress || 0

        opacity = 1.0
        titleField.inputItem.forceActiveFocus()
    }

    function close() {
        opacity = 0.0
    }

    function save() {
        var t = titleField.text.trim()
        var d = descField.text.trim()
        var sc = scopeCombo.currentIndex === 1 ? "yearly" : "monthly"
        var yr = parseInt(yearField.text) || new Date().getFullYear()
        var mn = sc === "monthly" ? (monthCombo.currentIndex + 1) : 0
        
        var pr = "medium"
        if (priorityCombo.currentIndex === 0) pr = "low"
        else if (priorityCombo.currentIndex === 2) pr = "high"

        var selFolder = planBridge.folders[folderCombo.currentIndex]
        var fid = selFolder ? selFolder.id : 0
        var prog = Math.round(progressSlider.value)

        if (!t) {
            appBridge.showToast("warning", "Uyarı", "Lütfen bir plan başlığı giriniz.")
            return
        }

        var success = false
        if (isEdit) {
            var st = prog >= 100 ? "completed" : (prog > 0 ? "in_progress" : "planned")
            success = planBridge.updatePlan(editId, t, d, st, prog, pr, fid)
        } else {
            success = planBridge.addPlan(t, d, sc, yr, mn, pr, fid)
        }

        if (success) {
            root.close()
        }
    }

    // Modal Pencere Kartı
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 500)
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
            spacing: 14

            Row {
                width: parent.width

                Column {
                    width: parent.width - 40
                    spacing: 4

                    Text {
                        text: root.isEdit ? "HEDEFİ / PLANI DÜZENLE" : "YENİ HEDEF & PLAN OLUŞTUR"
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "Kendinize bir aylık veya yıllık hedef belirleyin"
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

            // Plan Başlığı
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Plan Başlığı"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                CustomTextField {
                    id: titleField
                    width: parent.width
                    placeholderText: "Örn: 10 Kitap Bitir, Python Kursunu Tamamla..."
                    iconText: "🎯"
                }
            }

            // Kapsam, Yıl & Ay
            Row {
                width: parent.width
                spacing: 10

                Column {
                    width: (parent.width - 20) / 3
                    spacing: 6

                    Text {
                        text: "Kapsam"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomComboBox {
                        id: scopeCombo
                        width: parent.width
                        model: ["Aylık Plan", "Yıllık Plan"]
                    }
                }

                Column {
                    width: (parent.width - 20) / 3
                    spacing: 6

                    Text {
                        text: "Yıl"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomTextField {
                        id: yearField
                        width: parent.width
                        placeholderText: "2026"
                        iconText: "📅"
                    }
                }

                Column {
                    width: (parent.width - 20) / 3
                    spacing: 6
                    visible: scopeCombo.currentIndex === 0

                    Text {
                        text: "Ay"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomComboBox {
                        id: monthCombo
                        width: parent.width
                        model: ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                    }
                }
            }

            // Öncelik & Klasör
            Row {
                width: parent.width
                spacing: 12

                Column {
                    width: (parent.width - 12) / 2
                    spacing: 6

                    Text {
                        text: "Öncelik Seviyesi"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomComboBox {
                        id: priorityCombo
                        width: parent.width
                        model: ["🟢 Düşük", "🟡 Orta", "🔴 Yüksek"]
                    }
                }

                Column {
                    width: (parent.width - 12) / 2
                    spacing: 6

                    Text {
                        text: "Proje / Klasör"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomComboBox {
                        id: folderCombo
                        width: parent.width
                        textRole: "name"
                        model: planBridge.folders
                    }
                }
            }

            // İlerleme Çubuğu (Düzenleme Modunda)
            Column {
                width: parent.width
                spacing: 6
                visible: root.isEdit

                Item {
                    width: parent.width
                    height: 16

                    Text {
                        text: "Tamamlanma İlerlemesi"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: "%" + Math.round(progressSlider.value)
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.primaryLight
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                Slider {
                    id: progressSlider
                    width: parent.width
                    from: 0
                    to: 100
                    stepSize: 5
                }
            }

            // Açıklama
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Açıklama / Alt Hedefler"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                Rectangle {
                    width: parent.width
                    height: 60
                    radius: Theme.radiusMd
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 8

                        TextArea {
                            id: descField
                            placeholderText: "Planla ilgili detaylar ve notlar..."
                            placeholderTextColor: Theme.textMuted
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontSm
                            font.family: Theme.fontFamily
                            wrapMode: TextArea.Wrap
                            background: Item {}
                        }
                    }
                }
            }

            // Butonlar
            Row {
                anchors.right: parent.right
                spacing: 12
                topPadding: 6

                CustomButton {
                    text: "İptal"
                    variant: "ghost"
                    onClicked: root.close()
                }

                CustomButton {
                    text: root.isEdit ? "💾 Kaydet" : "＋ Planı Ekle"
                    variant: "primary"
                    onClicked: root.save()
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
