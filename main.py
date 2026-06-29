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


def patch_cursors():
    from PyQt5.QtWidgets import QPushButton, QToolButton, QCheckBox, QRadioButton, QComboBox, QTableWidget, QListWidget, QHeaderView
    from PyQt5.QtCore import Qt

    # 1. QPushButton
    orig_push = QPushButton.__init__
    def new_push(self, *args, **kwargs):
        orig_push(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QPushButton.__init__ = new_push

    # 2. QToolButton
    orig_tool = QToolButton.__init__
    def new_tool(self, *args, **kwargs):
        orig_tool(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QToolButton.__init__ = new_tool

    # 3. QCheckBox
    orig_check = QCheckBox.__init__
    def new_check(self, *args, **kwargs):
        orig_check(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QCheckBox.__init__ = new_check

    # 4. QRadioButton
    orig_radio = QRadioButton.__init__
    def new_radio(self, *args, **kwargs):
        orig_radio(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QRadioButton.__init__ = new_radio

    # 5. QComboBox
    orig_combo = QComboBox.__init__
    def new_combo(self, *args, **kwargs):
        orig_combo(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QComboBox.__init__ = new_combo

    # 6. QTableWidget (Viewport)
    orig_table = QTableWidget.__init__
    def new_table(self, *args, **kwargs):
        orig_table(self, *args, **kwargs)
        self.viewport().setCursor(Qt.PointingHandCursor)
    QTableWidget.__init__ = new_table

    # 7. QListWidget (Viewport)
    orig_list = QListWidget.__init__
    def new_list(self, *args, **kwargs):
        orig_list(self, *args, **kwargs)
        self.viewport().setCursor(Qt.PointingHandCursor)
    QListWidget.__init__ = new_list

    # 8. QHeaderView
    orig_header = QHeaderView.__init__
    def new_header(self, *args, **kwargs):
        orig_header(self, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
    QHeaderView.__init__ = new_header


def main():
    patch_cursors()
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