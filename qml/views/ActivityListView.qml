// qml/views/ActivityListView.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"
import "../modals"

Rectangle {
    id: root

    color: Theme.bgApp

    property string viewMode: "list" // "list" veya "grid"
    property int pendingDeleteId: 0

    Column {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 20

        // --- 1. Üst Başlık & Aksiyon Alanı ---
        Item {
            width: parent.width
            height: 42

            Row {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: 12

                Text {
                    text: "Faaliyet Listesi"
                    font.pixelSize: Theme.fontTitle
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                    anchors.verticalCenter: parent.verticalCenter
                }

                Badge {
                    text: activityBridge.totalCount + " Kayıt"
                    badgeColor: Theme.primary
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // Sağ Taraf: Görünüm Butonları & ✨ YENİ FAALİYET EKLE BUTONU ✨
            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                // Liste / Grid Geçişi
                Rectangle {
                    width: 76
                    height: 38
                    radius: Theme.radiusMd
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Row {
                        anchors.fill: parent

                        Rectangle {
                            width: 38
                            height: 38
                            radius: Theme.radiusMd
                            color: root.viewMode === "list" ? Theme.primary : "transparent"

                            Icon {
                                anchors.centerIn: parent
                                name: Icons.list_view
                                size: 14
                                color: root.viewMode === "list" ? "#FFFFFF" : Theme.textSecondary
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.viewMode = "list"
                            }
                        }

                        Rectangle {
                            width: 38
                            height: 38
                            radius: Theme.radiusMd
                            color: root.viewMode === "grid" ? Theme.primary : "transparent"

                            Icon {
                                anchors.centerIn: parent
                                name: Icons.grid_view
                                size: 14
                                color: root.viewMode === "grid" ? "#FFFFFF" : Theme.textSecondary
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.viewMode = "grid"
                            }
                        }
                    }
                }

                // ✨ 1. UX Değişikliği: Liste Sayfasında Odaklı Modal Ekleme Butonu ✨
                CustomButton {
                    text: "Yeni Faaliyet Ekle"
                    icon: Icons.add
                    variant: "primary"
                    fontSize: Theme.fontSm + 1
                    onClicked: activityFormModal.openAdd()
                }
            }
        }

        // --- 2. Filtre ve Arama Çubuğu ---
        Rectangle {
            width: parent.width
            height: 60
            radius: Theme.radiusLg
            color: Theme.bgCard
            border.color: Theme.borderSubtle
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 14

                // Arama Çubuğu
                CustomTextField {
                    id: searchInput
                    Layout.fillWidth: true
                    Layout.minimumWidth: 140
                    Layout.preferredWidth: 280
                    placeholderText: "Faaliyet adı ile ara..."
                    iconText: "🔍"
                    onTextEdited: function(txt) {
                        searchDebounceTimer.restart()
                    }
                }

                Timer {
                    id: searchDebounceTimer
                    interval: 300
                    onTriggered: activityBridge.setSearchTerm(searchInput.text)
                }

                // Tür Filtresi
                Row {
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter

                    Text {
                        text: "Tür:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        id: typeFilterCombo
                        width: 150
                        model: activityBridge.availableTypes
                        onActivated: activityBridge.setTypeFilter(currentText)
                    }
                }

                // Tarih Filtresi (YYYY-MM)
                Row {
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter

                    Text {
                        text: "Dönem:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomTextField {
                        id: dateFilterInput
                        width: 130
                        placeholderText: "YYYY-MM"
                        iconText: "📅"
                        onAccepted: activityBridge.setDateFilter(text)
                        onTextEdited: function(txt) {
                            if (txt.length === 0 || txt.length === 4 || txt.length === 7) {
                                activityBridge.setDateFilter(txt)
                            }
                        }
                    }
                }

                // Sayfa Başına Veri Adedi (15 - 30 - 50 - 100)
                Row {
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter

                    Text {
                        text: "Sayfa Başına:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        id: pageSizeCombo
                        width: 80
                        model: ["15", "30", "50", "100"]
                        currentIndex: 0
                        onActivated: {
                            activityBridge.setItemsPerPage(parseInt(currentText))
                        }
                    }
                }

                Item { width: 1; height: 1 }

                // Filtreleri Temizle Butonu
                CustomButton {
                    visible: searchInput.text !== "" || typeFilterCombo.currentIndex !== 0 || dateFilterInput.text !== ""
                    text: "Filtreleri Sıfırla"
                    variant: "ghost"
                    Layout.alignment: Qt.AlignVCenter
                    onClicked: {
                        searchInput.text = ""
                        typeFilterCombo.currentIndex = 0
                        dateFilterInput.text = ""
                        activityBridge.setSearchTerm("")
                        activityBridge.setTypeFilter("Hepsi")
                        activityBridge.setDateFilter("")
                    }
                }
            }
        }

        // --- 3. İçerik Alanı (Tablo / Liste veya Kart Grid) ---
        Item {
            width: parent.width
            height: parent.height - 180
            clip: true

            // Boş Durum
            EmptyState {
                anchors.centerIn: parent
                visible: activityBridge.totalCount === 0 && !activityBridge.isLoading
                title: "Henüz Kayıt Bulunmuyor"
                description: searchInput.text !== "" ? "Arama kriterlerinize uyan faaliyet bulunamadı." : "Yeni bir film, dizi, oyun veya kitap ekleyerek takibe başlayın."
                actionText: "＋ İlk Faaliyetini Ekle"
                onActionClicked: activityFormModal.openAdd()
            }

            // Yükleniyor Spinner
            BusyIndicator {
                anchors.centerIn: parent
                running: activityBridge.isLoading
                visible: activityBridge.isLoading
            }

            // GÖRÜNÜM 1: LİSTE / TABLO GÖRÜNÜMÜ
            ListView {
                id: activityListView
                anchors.fill: parent
                visible: root.viewMode === "list" && activityBridge.totalCount > 0
                clip: true
                model: activityBridge.model
                spacing: 8

                delegate: Rectangle {
                    id: listRow
                    width: activityListView.width
                    height: 64
                    radius: Theme.radiusMd
                    color: rowMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard
                    border.color: rowMouse.containsMouse ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.4) : Theme.borderSubtle
                    border.width: 1

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

                    // Sol Renk Çubuğu
                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: 4
                        radius: Theme.radiusSm
                        color: typeColor
                    }

                    Item {
                        anchors.fill: parent
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16

                        // Sol: Kategori Rozeti
                        Badge {
                            id: catBadge
                            text: activityType
                            badgeColor: typeColor
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        // Sağ Kısım: Tarih + Puan + Aksiyon Butonları (Sabit hizalı, asla taşmaz!)
                        Row {
                            id: rightSection
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 16

                            // Tarih Alanı (Sabit 200px genişlik ve elide)
                            Row {
                                spacing: 6
                                width: 200
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "📅"
                                    font.pixelSize: 13
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: displayDate
                                    font.pixelSize: Theme.fontSm
                                    font.family: Theme.fontFamily
                                    color: Theme.textSecondary
                                    elide: Text.ElideRight
                                    width: parent.width - 24
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            // Puan Rozeti
                            Rectangle {
                                width: 52
                                height: 30
                                radius: 15
                                color: activityRating > 0 ? Qt.rgba(Theme.warning.r, Theme.warning.g, Theme.warning.b, 0.15) : "transparent"
                                border.color: activityRating > 0 ? Theme.warning : "transparent"
                                border.width: 1
                                anchors.verticalCenter: parent.verticalCenter

                                Row {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Text {
                                        text: "★"
                                        font.pixelSize: 12
                                        color: Theme.warning
                                        visible: activityRating > 0
                                    }

                                    Text {
                                        text: scoreBadge
                                        font.pixelSize: Theme.fontSm
                                        font.bold: true
                                        color: activityRating > 0 ? Theme.warning : Theme.textMuted
                                    }
                                }
                            }

                            // Aksiyon Butonları (Düzenle & Sil)
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 6

                                // Düzenle
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: Theme.radiusSm
                                    color: editHover.containsMouse ? Theme.bgCardElevated : "transparent"
                                    border.color: editHover.containsMouse ? Theme.primary : "transparent"
                                    border.width: 1

                                    Icon {
                                        name: Icons.edit
                                        size: 13
                                        color: editHover.containsMouse ? Theme.primaryLight : Theme.textSecondary
                                        anchors.centerIn: parent
                                    }

                                    MouseArea {
                                        id: editHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: activityFormModal.openEdit(activityId)
                                    }
                                }

                                // Sil
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: Theme.radiusSm
                                    color: delHover.containsMouse ? Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2) : "transparent"
                                    border.color: delHover.containsMouse ? Theme.danger : "transparent"
                                    border.width: 1

                                    Icon {
                                        name: Icons.delete_icon
                                        size: 13
                                        color: delHover.containsMouse ? Theme.danger : Theme.textSecondary
                                        anchors.centerIn: parent
                                    }

                                    MouseArea {
                                        id: delHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.pendingDeleteId = activityId
                                            confirmDeleteModal.message = "'" + activityName + "' faaliyetini silmek istediğinize emin misiniz?"
                                            confirmDeleteModal.open()
                                        }
                                    }
                                }
                            }
                        }

                        // Orta: Faaliyet Adı & Yorum Özeti
                        Column {
                            anchors.left: catBadge.right
                            anchors.right: rightSection.left
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 3

                            Text {
                                text: activityName
                                font.pixelSize: Theme.fontMd
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                width: parent.width
                            }

                            Text {
                                text: activityComment !== "" ? activityComment : "Yorum girilmedi"
                                font.pixelSize: Theme.fontXs
                                font.family: Theme.fontFamily
                                color: activityComment !== "" ? Theme.textSecondary : Theme.textMuted
                                elide: Text.ElideRight
                                width: parent.width
                            }
                        }
                    }

                    // Çift Tıklama ile Düzenleme
                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        z: -1
                        onDoubleClicked: activityFormModal.openEdit(activityId)
                    }
                }
            }

            // ==========================================
            // GÖRÜNÜM B: Grid Görünümü (Dikey Poster Formatında Kartlar)
            // ==========================================
            GridView {
                id: activityGridView
                anchors.fill: parent
                visible: root.viewMode === "grid" && activityBridge.totalCount > 0
                clip: true
                cellWidth: 235
                cellHeight: 448
                model: activityBridge.model

                delegate: Rectangle {
                    width: 215
                    height: 428
                    radius: Theme.radiusLg
                    color: gridMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard
                    border.color: gridMouse.containsMouse ? typeColor : Theme.borderSubtle
                    border.width: 1
                    clip: true

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }

                    Column {
                        anchors.fill: parent
                        spacing: 0

                        // 1. Kapak / Afiş Görseli Alanı (Dikey Poster Oranı 2:3)
                        Rectangle {
                            id: coverArea
                            width: parent.width
                            height: Math.round(width * 1.5)
                            color: Theme.bgInput
                            clip: true

                            // Renk Gradyanı (Resim yüklenirken veya yokken)
                            Rectangle {
                                anchors.fill: parent
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: typeColor }
                                    GradientStop { position: 1.0; color: Qt.darker(typeColor, 2.2) }
                                }
                                opacity: cardCover.status === Image.Ready ? 0 : 0.65
                                Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }
                            }

                            // Kategori İkonu (Resim yokken)
                            Text {
                                anchors.centerIn: parent
                                text: activityType === "Film" ? "🎬" : (activityType === "Dizi" ? "📺" : (activityType === "Oyun" ? "🎮" : (activityType === "Kitap" ? "📚" : (activityType === "Kurs" ? "🎓" : "📍"))))
                                font.pixelSize: 46
                                opacity: 0.85
                                visible: cardCover.status !== Image.Ready
                            }

                            // Kapak Resmi
                            Image {
                                id: cardCover
                                anchors.fill: parent
                                source: activityBridge.getCover(activityName, activityType) || ""
                                fillMode: Image.PreserveAspectFit
                                asynchronous: true
                            }

                            // Kategori Rozeti (Sol Üst)
                            Badge {
                                anchors.top: parent.top
                                anchors.left: parent.left
                                anchors.margins: 8
                                text: activityType
                                badgeColor: typeColor
                            }

                            // Puan Rozeti (Sağ Üst)
                            Rectangle {
                                anchors.top: parent.top
                                anchors.right: parent.right
                                anchors.margins: 8
                                width: 44
                                height: 24
                                radius: Theme.radiusSm
                                color: Qt.rgba(0, 0, 0, 0.75)
                                visible: activityRating > 0

                                Row {
                                    anchors.centerIn: parent
                                    spacing: 3

                                    Text {
                                        text: "★"
                                        font.pixelSize: 11
                                        color: Theme.warning
                                    }

                                    Text {
                                        text: scoreBadge
                                        font.pixelSize: Theme.fontXs
                                        font.bold: true
                                        color: "#FFFFFF"
                                    }
                                }
                            }

                            // Asenkron Kapak Dinleyicisi
                            Connections {
                                target: activityBridge
                                function onCoverLoaded(name, url) {
                                    if (name === activityName && url) {
                                        cardCover.source = url
                                    }
                                }
                            }

                            Component.onCompleted: {
                                activityBridge.requestCover(activityName, activityType)
                            }
                        }

                        // 2. Alt Bilgi Alanı
                        Column {
                            width: parent.width
                            height: 105
                            padding: 10
                            spacing: 4

                            Text {
                                text: activityName
                                font.pixelSize: Theme.fontSm + 1
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                width: parent.width - 20
                            }

                            Text {
                                text: activityComment !== "" ? activityComment : "Not eklenmedi."
                                font.pixelSize: Theme.fontXs
                                font.family: Theme.fontFamily
                                color: Theme.textSecondary
                                elide: Text.ElideRight
                                maximumLineCount: 1
                                width: parent.width - 20
                            }

                            Item { width: 1; height: 1 }

                            Item {
                                width: parent.width - 20
                                height: 28

                                Text {
                                    text: "📅 " + displayDate
                                    font.pixelSize: Theme.fontXs - 1
                                    color: Theme.textMuted
                                    anchors.left: parent.left
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 66
                                    elide: Text.ElideRight
                                }

                                Row {
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 6

                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: gridEditHover.containsMouse ? Theme.primaryGlow : "transparent"

                                        Icon {
                                            name: Icons.edit
                                            size: 12
                                            color: gridEditHover.containsMouse ? Theme.primaryLight : Theme.textSecondary
                                            anchors.centerIn: parent
                                        }

                                        MouseArea {
                                            id: gridEditHover
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: activityFormModal.openEdit(activityId)
                                        }
                                    }

                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: gridDelHover.containsMouse ? Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2) : "transparent"

                                        Icon {
                                            name: Icons.delete_icon
                                            size: 12
                                            color: gridDelHover.containsMouse ? Theme.danger : Theme.textSecondary
                                            anchors.centerIn: parent
                                        }

                                        MouseArea {
                                            id: gridDelHover
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                root.pendingDeleteId = activityId
                                                confirmDeleteModal.message = "'" + activityName + "' faaliyetini silmek istediğinize emin misiniz?"
                                                confirmDeleteModal.open()
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    MouseArea {
                        id: gridMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        z: -1
                        onDoubleClicked: activityFormModal.openEdit(activityId)
                    }
                }
            }
        }

        // --- 4. Sayfalama Kontrolleri & Sayfa Başına Veri Seçici ---
        Item {
            width: parent.width
            height: 40
            visible: activityBridge.totalCount > 0

            // Sol: Toplam Veri Bilgisi
            Text {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: "Toplam " + activityBridge.totalCount + " kayıt listeleniyor"
                font.pixelSize: Theme.fontSm
                font.family: Theme.fontFamily
                color: Theme.textMuted
            }

            // Orta: Sayfa Geçiş Butonları
            Row {
                anchors.centerIn: parent
                spacing: 14

                CustomButton {
                    text: "‹ Önceki"
                    variant: "secondary"
                    enabled: activityBridge.currentPage > 1
                    onClicked: activityBridge.prevPage()
                }

                Text {
                    text: "Sayfa " + activityBridge.currentPage + " / " + activityBridge.totalPages
                    font.pixelSize: Theme.fontSm
                    font.bold: true
                    color: Theme.textSecondary
                    anchors.verticalCenter: parent.verticalCenter
                }

                CustomButton {
                    text: "Sonraki ›"
                    variant: "secondary"
                    enabled: activityBridge.currentPage < activityBridge.totalPages
                    onClicked: activityBridge.nextPage()
                }
            }
        }
    }

    // ✨ MODAL DIALOGLAR ✨
    ActivityFormModal {
        id: activityFormModal
    }

    ConfirmationModal {
        id: confirmDeleteModal
        title: "Faaliyeti Sil"
        confirmText: "Sil"
        isDanger: true
        onConfirmed: {
            if (root.pendingDeleteId > 0) {
                activityBridge.deleteActivity(root.pendingDeleteId)
                root.pendingDeleteId = 0
            }
        }
    }
}

