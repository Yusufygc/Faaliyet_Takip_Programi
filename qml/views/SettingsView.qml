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

            // --- 2. BÖLÜM: Özel Faaliyet Türleri ---
            Rectangle {
                width: parent.width
                implicitHeight: typesCol.implicitHeight + 40
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: typesCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Row {
                        spacing: 10
                        Icon {
                            name: Icons.folder
                            size: 18
                            color: Theme.primary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Faaliyet Türleri Yönetimi"
                            font.pixelSize: Theme.fontLg
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: "Faaliyetlerinizi gruplamak için özel kategoriler (ör. Podcast, Tiyatro, Belgesel) ekleyebilirsiniz."
                        font.pixelSize: Theme.fontXs
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }

                    // Yeni Tür Ekleme Formu
                    Row {
                        width: parent.width
                        spacing: 10

                        CustomTextField {
                            id: newTypeInput
                            width: 280
                            placeholderText: "Yeni tür adı (Örn: Tiyatro)..."
                            icon: Icons.add
                            onAccepted: addTypeBtn.clicked()
                        }

                        CustomButton {
                            id: addTypeBtn
                            text: "Kategori Ekle"
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
                        spacing: 10

                        Repeater {
                            model: settingsBridge.typesList

                            Rectangle {
                                height: 36
                                implicitWidth: typeBadgeRow.implicitWidth + 24
                                radius: Theme.radiusSm
                                color: Theme.bgInput
                                border.color: Theme.borderLight
                                border.width: 1

                                Row {
                                    id: typeBadgeRow
                                    anchors.centerIn: parent
                                    spacing: 8

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

            // --- 3. BÖLÜM: Harici API Anahtarları (Keyring) ---
            Rectangle {
                width: parent.width
                implicitHeight: apiCol.implicitHeight + 40
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: apiCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 18

                    Row {
                        spacing: 10
                        Icon {
                            name: Icons.key
                            size: 18
                            color: Theme.warning
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Keşfet & Öneriler API Anahtarları"
                            font.pixelSize: Theme.fontLg
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: "API anahtarlarınız işletim sistemi kasasında (Keyring) şifreli ve güvenli olarak saklanır."
                        font.pixelSize: Theme.fontXs
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }

                    // 1. TMDB API Key
                    Column {
                        width: parent.width
                        spacing: 6

                        Text {
                            text: "The Movie Database (TMDB) API Key — Film & Dizi İçerikleri"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.primaryLight
                        }

                        Row {
                            width: parent.width
                            spacing: 10

                            CustomTextField {
                                id: tmdbInput
                                width: parent.width - 120
                                text: settingsBridge.tmdbKey
                                echoMode: TextInput.Password
                                placeholderText: "TMDB API v3 Key (32 karakterlik anahtar)..."
                                icon: Icons.film
                            }

                            CustomButton {
                                text: "Kaydet"
                                icon: Icons.save
                                variant: "primary"
                                onClicked: settingsBridge.saveApiKey("tmdb", tmdbInput.text)
                            }
                        }
                    }

                    // 2. RAWG API Key
                    Column {
                        width: parent.width
                        spacing: 6

                        Text {
                            text: "RAWG Video Games Database API Key — Video Oyunları"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.success
                        }

                        Row {
                            width: parent.width
                            spacing: 10

                            CustomTextField {
                                id: rawgInput
                                width: parent.width - 120
                                text: settingsBridge.rawgKey
                                echoMode: TextInput.Password
                                placeholderText: "RAWG API Key..."
                                icon: Icons.game
                            }

                            CustomButton {
                                text: "Kaydet"
                                icon: Icons.save
                                variant: "primary"
                                onClicked: settingsBridge.saveApiKey("rawg", rawgInput.text)
                            }
                        }
                    }

                    // 3. Google Books API Key
                    Column {
                        width: parent.width
                        spacing: 6

                        Text {
                            text: "Google Books API Key — Kitap İçerikleri (İsteğe Bağlı)"
                            font.pixelSize: Theme.fontSm
                            font.bold: true
                            color: Theme.warning
                        }

                        Row {
                            width: parent.width
                            spacing: 10

                            CustomTextField {
                                id: booksInput
                                width: parent.width - 120
                                text: settingsBridge.googleBooksKey
                                echoMode: TextInput.Password
                                placeholderText: "Google Books API Key..."
                                icon: Icons.book
                            }

                            CustomButton {
                                text: "Kaydet"
                                icon: Icons.save
                                variant: "primary"
                                onClicked: settingsBridge.saveApiKey("google_books", booksInput.text)
                            }
                        }
                    }
                }
            }

            // --- 4. BÖLÜM: Uygulama & Sistem Hakkında ---
            Rectangle {
                width: parent.width
                implicitHeight: sysCol.implicitHeight + 36
                radius: Theme.radiusLg
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Column {
                    id: sysCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 12

                    Row {
                        spacing: 8
                        Icon {
                            name: Icons.app_logo
                            size: 16
                            color: Theme.primary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Uygulama Bilgileri"
                            font.pixelSize: Theme.fontMd
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Row {
                        spacing: 24

                        Column {
                            spacing: 4
                            Text { text: "Sürüm"; font.pixelSize: Theme.fontXs; color: Theme.textMuted }
                            Text { text: appBridge.appVersion + " (PySide6 + QML)"; font.pixelSize: Theme.fontSm; font.bold: true; color: Theme.textPrimary }
                        }

                        Column {
                            spacing: 4
                            Text { text: "Mimari"; font.pixelSize: Theme.fontXs; color: Theme.textMuted }
                            Text { text: "Qt 6 Quick MVVM"; font.pixelSize: Theme.fontSm; font.bold: true; color: Theme.textPrimary }
                        }

                        Column {
                            spacing: 4
                            Text { text: "Veritabanı"; font.pixelSize: Theme.fontXs; color: Theme.textMuted }
                            Text { text: "SQLite 3 Local"; font.pixelSize: Theme.fontSm; font.bold: true; color: Theme.textPrimary }
                        }
                    }
                }
            }
        }
    }
}
