// qml/Main.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"
import "views"
import "modals"

ApplicationWindow {
    id: mainWindow

    visible: true
    width: 1200
    height: 800
    minimumWidth: 1060
    minimumHeight: 700
    title: appBridge.appName

    flags: Qt.Window | Qt.FramelessWindowHint
    color: Theme.bgApp

    // --- Tema Durumu (Python <-> QML) ---
    Binding {
        target: Theme
        property: "isDark"
        value: settingsBridge.isDarkTheme
    }

    // --- Klavye Kısayolları ---
    Shortcut {
        sequence: "Ctrl+N"
        onActivated: {
            sidebar.activeIndex = 0
            viewStack.currentIndex = 0
            activityView.openAddModal()
        }
    }

    Shortcut {
        sequence: "Ctrl+1"
        onActivated: sidebar.activeIndex = 0
    }

    Shortcut {
        sequence: "Ctrl+2"
        onActivated: sidebar.activeIndex = 1
    }

    Shortcut {
        sequence: "Ctrl+3"
        onActivated: sidebar.activeIndex = 2
    }

    Shortcut {
        sequence: "Ctrl+4"
        onActivated: sidebar.activeIndex = 3
    }

    Shortcut {
        sequence: "Ctrl+5"
        onActivated: sidebar.activeIndex = 4
    }

    Shortcut {
        sequence: "Ctrl+6"
        onActivated: sidebar.activeIndex = 5
    }

    // --- Ana Düzen ---
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 1. Özel Pencere Başlık Çubuğu
        TitleBar {
            id: titleBar
            Layout.fillWidth: true
            Layout.preferredHeight: 38
            targetWindow: mainWindow
            title: appBridge.appName + " — Faaliyet & Planlama Sistemi"
        }

        // 2. Gövde (Sol Menü + Sayfa İçerik Alanı)
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Sol Menü
            Sidebar {
                id: sidebar
                Layout.preferredWidth: sidebar.implicitWidth
                Layout.fillHeight: true
                onNavigate: function(index, route) {
                    viewStack.currentIndex = index
                }
            }

            // Sayfa Stack Alanı
            StackLayout {
                id: viewStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: sidebar.activeIndex

                // 0: Faaliyetler Listesi
                ActivityListView {
                    id: activityView
                    function openAddModal() {
                        // ActivityListView içindeki activityFormModal'ı aç
                        for (var i = 0; i < children.length; i++) {
                            if (children[i].openAdd !== undefined) {
                                children[i].openAdd()
                                break
                            }
                        }
                    }
                }

                // 1: İstatistikler & PDF
                StatsView {
                    id: statsView
                }

                // 2: Hedefler & Planlar
                PlansView {
                    id: plansView
                }

                // 3: Keşfet & Öneriler
                DiscoverView {
                    id: discoverView
                    onQuickAddActivity: function(cat, title, rating) {
                        sidebar.activeIndex = 0
                        viewStack.currentIndex = 0
                        // ActivityListView modalını önceden doldurarak aç
                        for (var i = 0; i < activityView.children.length; i++) {
                            if (activityView.children[i].openAdd !== undefined) {
                                activityView.children[i].openAdd(cat, title, rating)
                                break
                            }
                        }
                    }
                }

                // 4: Dönem Karşılaştırma
                CompareView {
                    id: compareView
                }

                // 5: Ayarlar & Tür Yönetimi
                SettingsView {
                    id: settingsView
                }
            }
        }
    }

    // --- Sağ Alt Toast Bildirim Balonu ---
    ToastNotification {
        id: globalToast
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 24
        z: 9999
    }

    // --- Backend Sinyal Bağlantıları & Toast Yönlendirmeleri ---
    Connections {
        target: appBridge
        function onToastRequested(type, title, msg) {
            globalToast.show(type, title, msg)
        }
    }

    Connections {
        target: activityBridge
        function onActivitySaved(success, msg, actId) {
            globalToast.show(success ? "success" : "error", success ? "Başarılı" : "Hata", msg)
            if (success) {
                statsBridge.loadStats(statsBridge.datePrefix, statsBridge.isYearOnly, statsBridge.isAllTime)
            }
        }
        function onActivityDeleted(success, msg) {
            globalToast.show(success ? "success" : "error", success ? "Silindi" : "Hata", msg)
            if (success) {
                statsBridge.loadStats(statsBridge.datePrefix, statsBridge.isYearOnly, statsBridge.isAllTime)
            }
        }
        function onErrorOccurred(err) {
            globalToast.show("error", "Hata", err)
        }
    }

    Connections {
        target: statsBridge
        function onPdfExportResult(success, msg, filePath) {
            globalToast.show(
                success ? "success" : "error",
                success ? "PDF Hazırlandı" : "PDF Hatası",
                msg
            )
            if (success && filePath) {
                appBridge.openFile(filePath)
            }
        }
    }

    Connections {
        target: planBridge
        function onPlanSaved(success, msg) {
            globalToast.show(success ? "success" : "error", success ? "Kaydedildi" : "Hata", msg)
        }
        function onFolderSaved(success, msg) {
            globalToast.show(success ? "success" : "error", success ? "Klasör İşlemi" : "Hata", msg)
        }
    }

    Connections {
        target: settingsBridge
        function onNotification(type, title, msg) {
            globalToast.show(type, title, msg)
        }
    }

    Connections {
        target: discoverBridge
        function onErrorOccurred(err) {
            globalToast.show("warning", "Bilgi", err)
        }
    }
}
