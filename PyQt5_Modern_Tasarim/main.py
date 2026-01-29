import sys
import os
import matplotlib
import traceback

# Matplotlib Backend Ayarı - CRASH FIX
try:
    matplotlib.use('Qt5Agg')
except:
    pass

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from controllers.main_controller import MainController
    from views.main_window import MainWindow
    from views.styles import STYLESHEET
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
    input("Hata olustu. Enter'a basin...")
    sys.exit(1)

# PyInstaller için çalışma dizinini ayarla
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()