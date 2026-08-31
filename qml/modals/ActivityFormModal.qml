// qml/modals/ActivityFormModal.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    property bool isEdit: false
    property int editId: 0
    property string currentTypeName: "Film"

    signal saved(bool success, string message)

    anchors.fill: parent
    color: Theme.bgModalOverlay
    visible: opacity > 0
    opacity: 0
    z: 999

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    function openAdd(defaultCategory, defaultTitle, defaultRating) {
        isEdit = false
        editId = 0
        currentTypeName = defaultCategory || (activityBridge.availableTypes.length > 1 ? activityBridge.availableTypes[1] : "Film")
        typeCombo.currentIndex = Math.max(0, activityBridge.availableTypes.slice(1).indexOf(currentTypeName))
        nameField.text = defaultTitle || ""
        
        var today = new Date()
        var yyyy = today.getFullYear()
        var mm = String(today.getMonth() + 1).padStart(2, '0')
        var dd = String(today.getDate()).padStart(2, '0')
        dateField.text = yyyy + "-" + mm + "-" + dd

        hasEndDateCheck.checked = false
        endDateField.text = ""
        ratingBar.rating = defaultRating || 0.0
        commentField.text = ""
        errorText.text = ""
        suggestionPopup.visible = false

        opacity = 1.0
        nameField.inputItem.forceActiveFocus()
    }

    function openEdit(actId) {
        var data = activityBridge.getActivityById(actId)
        if (!data || !data.id) return

        isEdit = true
        editId = actId
        currentTypeName = data.type || "Film"
        typeCombo.currentIndex = Math.max(0, activityBridge.availableTypes.slice(1).indexOf(currentTypeName))
        nameField.text = data.name || ""
        dateField.text = data.date || ""
        hasEndDateCheck.checked = Boolean(data.hasEndDate)
        endDateField.text = data.endDate || ""
        ratingBar.rating = data.rating || 0.0
        commentField.text = data.comment || ""
        errorText.text = ""
        suggestionPopup.visible = false

        opacity = 1.0
        nameField.inputItem.forceActiveFocus()
    }

    function close() {
        opacity = 0.0
        suggestionPopup.visible = false
    }

    function save() {
        var tName = typeCombo.currentText
        var nName = nameField.text.trim()
        var dVal = dateField.text.trim()
        var eVal = hasEndDateCheck.checked ? endDateField.text.trim() : ""
        var cVal = commentField.text.trim()
        var rVal = ratingBar.rating

        if (!nName) {
            errorText.text = "Lütfen faaliyet adını giriniz."
            return
        }

        if (!dVal) {
            errorText.text = "Lütfen başlangıç tarihini giriniz (YYYY-MM-DD)."
            return
        }

        var success = false
        if (isEdit) {
            success = activityBridge.updateActivity(editId, tName, nName, dVal, cVal, rVal, eVal)
        } else {
            success = activityBridge.addActivity(tName, nName, dVal, cVal, rVal, eVal)
        }

        if (success) {
            root.close()
        }
    }

    // Modal Kart Gövdesi
    Rectangle {
        id: modalCard
        width: Math.min(parent.width - 40, 520)
        implicitHeight: formCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: Theme.radiusLg
        color: Theme.bgSidebar
        border.color: Theme.borderLight
        border.width: 1
        scale: root.opacity

        Behavior on scale { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutBack } }

        Column {
            id: formCol
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            // Başlık & Kapat Butonu
            Row {
                width: parent.width

                Column {
                    width: parent.width - 40
                    spacing: 4

                    Text {
                        text: root.isEdit ? "FAALİYETİ DÜZENLE" : "YENİ FAALİYET EKLE"
                        font.pixelSize: Theme.fontLg
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: root.isEdit ? "Kayıt detaylarını güncelleyin" : "Listeye eklemek istediğiniz aktivite bilgilerini doldurun"
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

                    Icon {
                        name: Icons.close
                        size: 13
                        color: closeHover.containsMouse ? Theme.textPrimary : Theme.textSecondary
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

            // Hata Mesajı
            Text {
                id: errorText
                text: ""
                visible: text !== ""
                font.pixelSize: Theme.fontSm
                font.bold: true
                color: Theme.danger
            }

            // Form Satırı 1: Tür & Tarih
            Row {
                width: parent.width
                spacing: 12

                Column {
                    width: (parent.width - 12) / 2
                    spacing: 6

                    Text {
                        text: "Tür / Kategori"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomComboBox {
                        id: typeCombo
                        width: parent.width
                        model: activityBridge.availableTypes.filter(function(t) { return t !== "Hepsi" })
                    }
                }

                Column {
                    width: (parent.width - 12) / 2
                    spacing: 6

                    Text {
                        text: "Başlangıç Tarihi (YYYY-MM-DD)"
                        font.pixelSize: Theme.fontXs
                        font.bold: true
                        color: Theme.textSecondary
                    }

                    CustomTextField {
                        id: dateField
                        width: parent.width
                        placeholderText: "2026-08-31"
                        icon: Icons.calendar
                    }
                }
            }

            // Form Satırı 2: Bitiş Tarihi Seçeneği
            Row {
                width: parent.width
                spacing: 12

                CustomCheckBox {
                    id: hasEndDateCheck
                    text: "Bitiş Tarihi Belirt (Dizi/Kitap vb.)"
                    anchors.verticalCenter: parent.verticalCenter
                }

                CustomTextField {
                    id: endDateField
                    width: parent.width - 240
                    visible: hasEndDateCheck.checked
                    placeholderText: "2026-09-05"
                    icon: Icons.calendar
                }
            }

            // Form Satırı 3: Faaliyet Adı & Otomatik Tamamlama
            Column {
                width: parent.width
                spacing: 6
                z: 10

                Text {
                    text: "Faaliyet Adı"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                CustomTextField {
                    id: nameField
                    width: parent.width
                    placeholderText: "Örn: Inception, Breaking Bad, Suç ve Ceza..."
                    iconText: "🎬"

                    onTextEdited: function(txt) {
                        if (txt.length >= 2) {
                            var suggestions = activityBridge.getNameSuggestions(txt)
                            if (suggestions && suggestions.length > 0) {
                                suggestionList.model = suggestions
                                suggestionPopup.visible = true
                            } else {
                                suggestionPopup.visible = false
                            }
                        } else {
                            suggestionPopup.visible = false
                        }
                    }

                    onAccepted: root.save()
                }

                // Otomatik Tamamlama Açılır Listesi
                Rectangle {
                    id: suggestionPopup
                    visible: false
                    width: parent.width
                    height: Math.min(suggestionList.contentHeight + 8, 140)
                    color: Theme.bgCard
                    border.color: Theme.primary
                    border.width: 1
                    radius: Theme.radiusMd
                    z: 99

                    ListView {
                        id: suggestionList
                        anchors.fill: parent
                        anchors.margins: 4
                        clip: true

                        delegate: Rectangle {
                            width: suggestionList.width
                            height: 30
                            radius: Theme.radiusSm
                            color: sugMouse.containsMouse ? Theme.primaryGlow : "transparent"

                            Text {
                                text: modelData
                                font.pixelSize: Theme.fontSm
                                color: Theme.textPrimary
                                anchors.left: parent.left
                                anchors.leftMargin: 8
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            MouseArea {
                                id: sugMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    nameField.text = modelData
                                    suggestionPopup.visible = false
                                }
                            }
                        }
                    }
                }
            }

            // Form Satırı 4: Puanlama (1-10 Yıldız)
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Değerlendirme Puanı (1 - 10)"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                RatingStars {
                    id: ratingBar
                    starSize: 22
                }
            }

            // Form Satırı 5: Yorum & Notlar
            Column {
                width: parent.width
                spacing: 6

                Text {
                    text: "Yorum & Kişisel Notlar (İsteğe Bağlı)"
                    font.pixelSize: Theme.fontXs
                    font.bold: true
                    color: Theme.textSecondary
                }

                Rectangle {
                    width: parent.width
                    height: 70
                    radius: Theme.radiusMd
                    color: commentField.activeFocus ? Theme.bgInput : Theme.bgCard
                    border.color: commentField.activeFocus ? Theme.primary : Theme.borderSubtle
                    border.width: commentField.activeFocus ? 2 : 1

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 8

                        TextArea {
                            id: commentField
                            placeholderText: "Bu aktivite hakkında düşünceleriniz, bölüm notları..."
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

            // Alt Aksiyon Butonları
            Row {
                anchors.right: parent.right
                spacing: 12
                topPadding: 8

                CustomButton {
                    text: "İptal"
                    variant: "ghost"
                    onClicked: root.close()
                }

                CustomButton {
                    text: root.isEdit ? "Değişiklikleri Kaydet" : "Faaliyeti Ekle"
                    icon: root.isEdit ? Icons.save : Icons.add
                    variant: "primary"
                    onClicked: root.save()
                }
            }
        }
    }

    // Modal dışına tıklayınca kapat
    MouseArea {
        anchors.fill: parent
        z: -1
        onClicked: root.close()
    }
}
