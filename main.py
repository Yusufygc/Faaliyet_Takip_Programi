# main.py
import sys
import os
import traceback

# --- PySide6 / Qt6 Platform Eklentisi & OpenSSL DLL Yolu Yapılandırması ---
if sys.platform == "win32":
    # 1. Conda OpenSSL (Library/bin) önceliği ayarla
    env_dir = sys.prefix
    lib_bin = os.path.join(env_dir, "Library", "bin")
    if os.path.exists(lib_bin):
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(lib_bin)
            except Exception:
                pass
        # Library/bin'i PATH'in en başına al ve mingw64 çakışmalarını önle
        raw_paths = os.environ.get("PATH", "").split(os.pathsep)
        clean_paths = [p for p in raw_paths if "mingw64" not in p.lower()]
        os.environ["PATH"] = os.pathsep.join([lib_bin] + clean_paths)

import PySide6
pyside_dir = os.path.dirname(PySide6.__file__)
plugins_dir = os.path.join(pyside_dir, "plugins")
platforms_dir = os.path.join(plugins_dir, "platforms")

os.environ["QT_PLUGIN_PATH"] = plugins_dir
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platforms_dir

if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(pyside_dir)
        if os.path.exists(platforms_dir):
            os.add_dll_directory(platforms_dir)
    except Exception:
        pass

from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtCore import QUrl, Qt


from constants import APP_NAME, APP_TITLE, VERSION, DATA_DIR_NAME
from database.connection import init_db
from database.repository import ActivityRepository
from utils import get_resource_path
from logger_setup import logger
import bridges


def _get_crash_log_path():
    if sys.platform == "win32":
        base = os.environ.get('LOCALAPPDATA') or os.path.expanduser("~")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
    log_dir = os.path.join(base, DATA_DIR_NAME)
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "crash_log.txt")


def log_error(msg):
    try:
        with open(_get_crash_log_path(), "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def main():
    try:
        # High DPI ölçekleme desteği
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        QQuickStyle.setStyle("Basic")

        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationDisplayName(APP_TITLE)
        app.setApplicationVersion(VERSION)
        app.setOrganizationName("MYY Yazilim")

        # Uygulama İkonu
        icon_path = get_resource_path(os.path.join("icons", "icon.ico"))
        if not os.path.exists(icon_path):
            icon_path = get_resource_path(os.path.join("icons", "icon.png"))
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # Veritabanı ve Şema Migration Başlatma
        init_db()
        repo = ActivityRepository()
        repo.check_and_migrate_schema()

        # QML Engine ve Köprülerin Başlatılması
        engine = QQmlApplicationEngine()

        qml_dir = get_resource_path("qml")
        engine.addImportPath(qml_dir)

        # Bridge Nesneleri
        activity_bridge = bridges.ActivityBridge()
        stats_bridge = bridges.StatsBridge()
        plan_bridge = bridges.PlanBridge()
        discover_bridge = bridges.DiscoverBridge()
        settings_bridge = bridges.SettingsBridge()
        compare_bridge = bridges.CompareBridge()
        app_bridge = bridges.AppBridge()

        # QML Context Enjeksiyonu
        ctx = engine.rootContext()
        ctx.setContextProperty("activityBridge", activity_bridge)
        ctx.setContextProperty("statsBridge", stats_bridge)
        ctx.setContextProperty("planBridge", plan_bridge)
        ctx.setContextProperty("discoverBridge", discover_bridge)
        ctx.setContextProperty("settingsBridge", settings_bridge)
        ctx.setContextProperty("compareBridge", compare_bridge)
        ctx.setContextProperty("appBridge", app_bridge)

        # Main QML Dosyasını Yükle
        main_qml_path = os.path.join(qml_dir, "Main.qml")
        engine.load(QUrl.fromLocalFile(main_qml_path))

        if not engine.rootObjects():
            logger.error("QML root objects oluşturulamadı. Main.qml yüklenemedi.")
            sys.exit(-1)

        logger.info(f"{APP_NAME} v{VERSION} (PySide6 + QML) başarıyla başlatıldı.")
        sys.exit(app.exec())

    except Exception as e:
        err = f"Fatal Startup Error: {traceback.format_exc()}"
        logger.error(err)
        log_error(err)
        if sys.stderr is not None:
            print(err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()