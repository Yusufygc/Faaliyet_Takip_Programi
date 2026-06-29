import sys
import os
import ctypes
import matplotlib
import traceback

# Matplotlib Backend Ayarı - CRASH FIX
try:
    matplotlib.use('Qt5Agg')
except Exception:
    pass

def _get_crash_log_path():
    from constants import DATA_DIR_NAME
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

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtGui import QIcon
    from controllers.main_controller import MainController
    from views.main_window import MainWindow
    from styles import load
except Exception as e:
    err_msg = f"Import Error: {traceback.format_exc()}"
    log_error(err_msg)
    # Konsol yoksa bile hata mesajini goster
    ctypes.windll.user32.MessageBoxW(0, f"Baslatma hatasi:\n{e}", "Kritik Hata", 0x10)
    sys.exit(1)


def main():
    # Gorev cubugu ikonu icin App ID ayarla
    try:
        myappid = 'myy.faaliyettakip.v1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setStyleSheet(load("global", "inputs", "buttons", "cards", "scrollbars", "tables"))
        
        # Uygulama genelinde ikon ayarla (Taskbar icini)
        from utils import get_resource_path
        icon_path = get_resource_path(os.path.join("icons", "icon.ico"))
        if os.path.exists(icon_path):
             app.setWindowIcon(QIcon(icon_path)) 

        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        err_msg = f"Runtime Error: {traceback.format_exc()}"
        log_error(err_msg)
        ctypes.windll.user32.MessageBoxW(0, f"Calisma hatasi:\n{e}", "Hata", 0x10)
        sys.exit(1)

if __name__ == "__main__":
    main()