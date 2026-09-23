// qml/views/PlansView.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../modals"

Rectangle {
    id: root

    color: Theme.bgApp

    property int pendingDeletePlanId: 0

    Column {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 20

        // --- 1. Üst Başlık & Butonlar ---
        Item {
            width: parent.width
            height: 42

            Column {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4

                Text {
                    text: "Hedefler & Planlar"
                    font.pixelSize: Theme.fontTitle
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }

                Text {
                    text: "Aylık ve yıllık hedeflerinizi belirleyin, ilerlemenizi takip edin"
                    font.pixelSize: Theme.fontSm
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                CustomButton {
                    text: "Klasörleri Yönet"
                    icon: Icons.folder
                    variant: "secondary"
                    onClicked: folderManageModal.open()
                }

                CustomButton {
                    text: "Yeni Hedef / Plan"
                    icon: Icons.add
                    variant: "primary"
                    onClicked: planFormModal.openAdd(planBridge.activeFolderId)
                }
            }
        }

        // --- 2. Klasör Sekmeleri ---
        ScrollView {
            width: parent.width
            height: 44
            contentWidth: folderRow.width
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            clip: true

            Row {
                id: folderRow
                spacing: 8

                Repeater {
                    model: planBridge.folders

                    Rectangle {
                        height: 38
                        implicitWidth: folderRow.implicitWidth + 24
                        radius: Theme.radiusMd
                        color: planBridge.activeFolderId === modelData.id ? Theme.primary : (folderMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard)
                        border.color: planBridge.activeFolderId === modelData.id ? "transparent" : Theme.borderSubtle
                        border.width: 1

                        Row {
                            id: folderRow
                            anchors.centerIn: parent
                            spacing: 8

                            Icon {
                                name: modelData.id === 0 ? Icons.folder_open : Icons.folder
                                size: 13
                                color: planBridge.activeFolderId === modelData.id ? "#FFFFFF" : Theme.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.name
                                font.pixelSize: Theme.fontSm
                                font.bold: planBridge.activeFolderId === modelData.id
                                font.family: Theme.fontFamily
                                color: planBridge.activeFolderId === modelData.id ? "#FFFFFF" : Theme.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        MouseArea {
                            id: folderMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: planBridge.setActiveFolder(modelData.id)
                        }
                    }
                }
            }
        }

        // --- 3. Filtre Çubuğu ---
        Rectangle {
            width: parent.width
            height: 52
            radius: Theme.radiusLg
            color: Theme.bgCard
            border.color: Theme.borderSubtle
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 8
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 14

                Row {
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "Kapsam:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        width: 130
                        model: ["Tümü", "Aylık", "Yıllık"]
                        onActivated: {
                            var val = "all"
                            if (currentIndex === 1) val = "monthly"
                            else if (currentIndex === 2) val = "yearly"
                            planBridge.setScopeFilter(val)
                        }
                    }
                }

                Row {
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "Durum:"
                        font.pixelSize: Theme.fontSm
                        font.bold: true
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    CustomComboBox {
                        width: 150
                        model: ["Tümü", "Planlandı", "Devam Eden", "Tamamlanan"]
                        onActivated: {
                            var val = "all"
                            if (currentIndex === 1) val = "planned"
                            else if (currentIndex === 2) val = "in_progress"
                            else if (currentIndex === 3) val = "completed"
                            planBridge.setStatusFilter(val)
                        }
                    }
                }

                Item { width: 1; height: 1 }

                // Özet Bilgiler
                Row {
                    spacing: 10
                    anchors.verticalCenter: parent.verticalCenter

                    Badge {
                        text: "Toplam: " + planBridge.totalPlansCount
                        badgeColor: Theme.primary
                    }

                    Badge {
                        text: "Devam Eden: " + planBridge.inProgressPlansCount
                        badgeColor: Theme.warning
                    }

                    Badge {
                        text: "Tamamlanan: " + planBridge.completedPlansCount
                        badgeColor: Theme.success
                    }
                }
            }
        }

        // --- 4. Plan Kartları Grid Görünümü ---
        Item {
            width: parent.width
            height: parent.height - 200
            clip: true

            EmptyState {
                anchors.centerIn: parent
                visible: planBridge.totalPlansCount === 0
                iconText: "🎯"
                title: "Henüz Plan Eklenmedi"
                description: "Yeni bir hedef veya plan belirleyerek kendinizi motive edin."
                actionText: "＋ İlk Hedefini Oluştur"
                onActionClicked: planFormModal.openAdd(planBridge.activeFolderId)
            }

            GridView {
                id: planGrid
                anchors.fill: parent
                clip: true
                cellWidth: 320
                cellHeight: 220
                model: planBridge.model

                delegate: Item {
                    width: planGrid.cellWidth
                    height: planGrid.cellHeight

                Rectangle {
                    id: planCard
                    width: 300
                    height: 200
                    anchors.centerIn: parent
                    radius: Theme.radiusLg
                    color: planCardMouse.containsMouse ? Theme.bgCardElevated : Theme.bgCard
                    border.color: statusColor
                    border.width: 1

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Behavior on scale { NumberAnimation { duration: Theme.animFast } }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        // Rozetler
                        Row {
                            width: parent.width
                            spacing: 8

                            Badge {
                                text: periodText
                                badgeColor: Theme.primary
                            }

                            Badge {
                                text: planFolderName
                                badgeColor: Theme.textMuted
                            }

                            Badge {
                                text: planPriority === "high" ? "Yüksek" : (planPriority === "low" ? "Düşük" : "Orta")
                                badgeColor: priorityColor
                                dotColor: priorityColor
                            }
                        }

                        // Başlık
                        Text {
                            text: planTitle
                            font.pixelSize: Theme.fontMd
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            elide: Text.ElideRight
                            width: parent.width
                        }

                        // Açıklama
                        Text {
                            text: planDescription
                            visible: planDescription !== ""
                            font.pixelSize: Theme.fontXs
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                            elide: Text.ElideRight
                            maximumLineCount: 2
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Item { width: 1; height: 1 }

                        // Aksiyon Butonları & Durum
                        Row {
                            width: parent.width

                            // Hızlı Durum Butonu
                            Rectangle {
                                height: 26
                                implicitWidth: statusBtnText.implicitWidth + 16
                                radius: Theme.radiusSm
                                color: Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.15)
                                border.color: statusColor
                                border.width: 1

                                Text {
                                    id: statusBtnText
                                    anchors.centerIn: parent
                                    text: planStatus === "completed" ? "✓ Tamamlandı" : (planStatus === "in_progress" ? "▶ Devam Ediyor" : "⏳ Planlandı")
                                    font.pixelSize: Theme.fontXs - 1
                                    font.bold: true
                                    color: statusColor
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        var nextStatus = "in_progress"
                                        if (planStatus === "planned") nextStatus = "in_progress"
                                        else if (planStatus === "in_progress") nextStatus = "completed"
                                        else if (planStatus === "completed") nextStatus = "planned"
                                        planBridge.updateStatus(planId, nextStatus)
                                    }
                                }
                            }

                            Item { width: 1; height: 1 }

                            Row {
                                spacing: 6

                                Rectangle {
                                    width: 26
                                    height: 26
                                    radius: 13
                                    color: pEditHover.containsMouse ? Theme.primaryGlow : "transparent"

                                    Icon {
                                        name: Icons.edit
                                        size: 12
                                        color: pEditHover.containsMouse ? Theme.primaryLight : Theme.textSecondary
                                        anchors.centerIn: parent
                                    }

                                    MouseArea {
                                        id: pEditHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: planFormModal.openEdit(planId)
                                    }
                                }

                                Rectangle {
                                    width: 26
                                    height: 26
                                    radius: 13
                                    color: pDelHover.containsMouse ? Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2) : "transparent"

                                    Icon {
                                        name: Icons.delete_icon
                                        size: 12
                                        color: pDelHover.containsMouse ? Theme.danger : Theme.textSecondary
                                        anchors.centerIn: parent
                                    }

                                    MouseArea {
                                        id: pDelHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.pendingDeletePlanId = planId
                                            confirmDeletePlanModal.message = "'" + planTitle + "' hedefini silmek istediğinize emin misiniz?"
                                            confirmDeletePlanModal.open()
                                        }
                                    }
                                }
                            }
                        }
                    }

                    MouseArea {
                        id: planCardMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        z: -1
                        onEntered: planCard.scale = 1.02
                        onExited: planCard.scale = 1.0
                        onDoubleClicked: planFormModal.openEdit(planId)
                    }
                }
                }
            }
        }
    }

    // ✨ MODALLAR ✨
    PlanFormModal {
        id: planFormModal
    }

    FolderManageModal {
        id: folderManageModal
    }

    ConfirmationModal {
        id: confirmDeletePlanModal
        title: "Hedefi Sil"
        confirmText: "Sil"
        isDanger: true
        onConfirmed: {
            if (root.pendingDeletePlanId > 0) {
                planBridge.deletePlan(root.pendingDeletePlanId)
                root.pendingDeletePlanId = 0
            }
        }
    }
}
