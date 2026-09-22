// qml/views/SettingsView.qml
import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Rectangle {
    id: root

    color: Theme.bgApp

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
                    text: "Uygulama Ayarları"
                    font.pixelSize: Theme.fontTitle
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }

                Text {
                    text: "Özel faaliyet kategorilerinizi ve harici API anahtarlarınızı yönetin"
                    font.pixelSize: Theme.fontSm
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            // --- 2. BÖLÜM: Özel Faaliyet Türleri + API Anahtarları (yan yana) ---
            Row {
                width: parent.width
                spacing: 20

                // Faaliyet Türleri Yönetimi
                Rectangle {
                    width: (parent.width - 20) / 2
                    height: Math.max(typesCol.implicitHeight, apiCol.implicitHeight) + 32
                    radius: Theme.radiusLg
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Column {
                        id: typesCol
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        Row {
                            spacing: 8
                            Icon {
                                name: Icons.folder
                                size: 16
                                color: Theme.primary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "Tür Yönetimi"
                                font.pixelSize: Theme.fontMd
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        Text {
                            width: parent.width
                            text: "Faaliyetlerinizi gruplamak için özel kategoriler ekleyebilirsiniz."
                            font.pixelSize: Theme.fontXs
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                        }

                        // Yeni Tür Ekleme Formu
                        Row {
                            width: parent.width
                            spacing: 8

                            CustomTextField {
                                id: newTypeInput
                                width: parent.width - addTypeBtn.implicitWidth - 8
                                placeholderText: "Yeni tür adı..."
                                icon: Icons.add
                                onAccepted: addTypeBtn.clicked()
                            }

                            CustomButton {
                                id: addTypeBtn
                                text: "Ekle"
                                icon: Icons.add
                                variant: "primary"
                                onClicked: {
                                    var val = newTypeInput.text.trim()
                                    if (val) {
                                        settingsBridge.addType(val)
                                        newTypeInput.text = ""
                                        activityBridge.syncTypes()
                                    }
                                }
                            }
                        }

                        // Mevcut Tür Rozetleri
                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: settingsBridge.typesList

                                Rectangle {
                                    height: 32
                                    implicitWidth: typeBadgeRow.implicitWidth + 20
                                    radius: Theme.radiusSm
                                    color: Theme.bgInput
                                    border.color: Theme.borderLight
                                    border.width: 1

                                    Row {
                                        id: typeBadgeRow
                                        anchors.centerIn: parent
                                        spacing: 6

                                        Badge {
                                            text: modelData
                                            badgeColor: Theme.categoryColor(modelData)
                                        }

                                        // Silme İkonu
                                        Text {
                                            text: "✕"
                                            font.pixelSize: 11
                                            color: delTypeHover.containsMouse ? Theme.danger : Theme.textMuted
                                            anchors.verticalCenter: parent.verticalCenter

                                            MouseArea {
                                                id: delTypeHover
                                                anchors.fill: parent
                                                anchors.margins: -4
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    settingsBridge.deleteType(modelData)
                                                    activityBridge.syncTypes()
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Harici API Anahtarları (Keyring)
                Rectangle {
                    width: (parent.width - 20) / 2
                    height: Math.max(typesCol.implicitHeight, apiCol.implicitHeight) + 32
                    radius: Theme.radiusLg
                    color: Theme.bgCard
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Column {
                        id: apiCol
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 14

                        Row {
                            spacing: 8
                            Icon {
                                name: Icons.key
                                size: 16
                                color: Theme.warning
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "API Anahtarları"
                                font.pixelSize: Theme.fontMd
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        Text {
                            width: parent.width
                            text: "Anahtarlarınız işletim sistemi kasasında (Keyring) şifreli saklanır."
                            font.pixelSize: Theme.fontXs
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                        }

                        // 1. TMDB API Key
                        Column {
                            width: parent.width
                            spacing: 6

                            Row {
                                spacing: 6
                                Text {
                                    text: "TMDB — Film & Dizi"
                                    font.pixelSize: Theme.fontSm
                                    font.bold: true
                                    color: Theme.primaryLight
                                }
                                Icon {
                                    visible: settingsBridge.hasTmdbKey
                                    name: Icons.check
                                    size: 13
                                    color: Theme.success
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            Row {
                                width: parent.width
                                spacing: 8

                                CustomTextField {
                                    id: tmdbInput
                                    width: parent.width - tmdbSaveBtn.implicitWidth - 8
                                    echoMode: TextInput.Password
                                    placeholderText: settingsBridge.hasTmdbKey ? "•••••••• (Kayıtlı — değiştirmek için yeni anahtar girin)" : "TMDB API Key..."
                                    icon: Icons.film
                                }

                                CustomButton {
                                    id: tmdbSaveBtn
                                    text: "Kaydet"
                                    icon: Icons.save
                                    variant: "primary"
                                    onClicked: {
                                        if (tmdbInput.text.length > 0) {
                                            settingsBridge.saveApiKey("tmdb", tmdbInput.text)
                                            tmdbInput.text = ""
                                        }
                                    }
                                }
                            }
                        }

                        // 2. RAWG API Key
                        Column {
                            width: parent.width
                            spacing: 6

                            Row {
                                spacing: 6
                                Text {
                                    text: "RAWG — Video Oyunları"
                                    font.pixelSize: Theme.fontSm
                                    font.bold: true
                                    color: Theme.success
                                }
                                Icon {
                                    visible: settingsBridge.hasRawgKey
                                    name: Icons.check
                                    size: 13
                                    color: Theme.success
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            Row {
                                width: parent.width
                                spacing: 8

                                CustomTextField {
                                    id: rawgInput
                                    width: parent.width - rawgSaveBtn.implicitWidth - 8
                                    echoMode: TextInput.Password
                                    placeholderText: settingsBridge.hasRawgKey ? "•••••••• (Kayıtlı — değiştirmek için yeni anahtar girin)" : "RAWG API Key..."
                                    icon: Icons.game
                                }

                                CustomButton {
                                    id: rawgSaveBtn
                                    text: "Kaydet"
                                    icon: Icons.save
                                    variant: "primary"
                                    onClicked: {
                                        if (rawgInput.text.length > 0) {
                                            settingsBridge.saveApiKey("rawg", rawgInput.text)
                                            rawgInput.text = ""
                                        }
                                    }
                                }
                            }
                        }

                        // 3. Google Books API Key
                        Column {
                            width: parent.width
                            spacing: 6

                            Row {
                                spacing: 6
                                Text {
                                    text: "Google Books — Kitap (İsteğe Bağlı)"
                                    font.pixelSize: Theme.fontSm
                                    font.bold: true
                                    color: Theme.warning
                                }
                                Icon {
                                    visible: settingsBridge.hasGoogleBooksKey
                                    name: Icons.check
                                    size: 13
                                    color: Theme.success
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            Row {
                                width: parent.width
                                spacing: 8

                                CustomTextField {
                                    id: booksInput
                                    width: parent.width - booksSaveBtn.implicitWidth - 8
                                    echoMode: TextInput.Password
                                    placeholderText: settingsBridge.hasGoogleBooksKey ? "•••••••• (Kayıtlı — değiştirmek için yeni anahtar girin)" : "Google Books API Key..."
                                    icon: Icons.book
                                }

                                CustomButton {
                                    id: booksSaveBtn
                                    text: "Kaydet"
                                    icon: Icons.save
                                    variant: "primary"
                                    onClicked: {
                                        if (booksInput.text.length > 0) {
                                            settingsBridge.saveApiKey("google_books", booksInput.text)
                                            booksInput.text = ""
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
