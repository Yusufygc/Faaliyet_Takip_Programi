import sys
import os
import ctypes
import matplotlib
import traceback

# Matplotlib Backend Ayarı - CRASH FIX
try:
    matplotlib.use('Qt5Agg')
except:
    pass

def log_error(msg):
    with open("crash_log.txt", "a") as f:
        f.write(msg + "\n")

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtGui import QIcon
    from controllers.main_controller import MainController
    from views.main_window import MainWindow
    from views.styles import STYLESHEET
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
    except:
        pass

    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion") 
        
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