import sys
import os
import matplotlib
import traceback

# Matplotlib Backend Ayarı - CRASH FIX
try:
    matplotlib.use('Qt5Agg')
except:
    pass

# Logging Setup
startup_log = "startup_log.txt"
if getattr(sys, 'frozen', False):
    startup_log = os.path.join(os.path.dirname(sys.executable), "startup_log.txt")
else:
    startup_log = os.path.join(os.path.dirname(__file__), "startup_log.txt")

def log(msg):
    print(msg)
    try:
        with open(startup_log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass

with open(startup_log, "w", encoding="utf-8") as f:
    f.write("=== STARTUP LOG ===\n")
    f.write(f"sys.executable: {sys.executable}\n")
    f.write(f"sys.frozen: {getattr(sys, 'frozen', False)}\n")
    f.write(f"os.getcwd(): {os.getcwd()}\n\n")

try:
    log("Step 1: Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication, QMessageBox
    log("Step 1: OK")
    
    log("Step 2: Importing controllers...")
    from controllers.main_controller import MainController
    log("Step 2: OK")
    
    log("Step 3: Importing add_page...")
    from views.pages.add_page import AddPage
    log("Step 3: OK")
    
    log("Step 4: Importing list_page...")
    from views.pages.list_page import ListPage
    log("Step 4: OK")
    
    log("Step 5: Importing stats_page (Checking Matplotlib)...")
    from views.pages.stats_page import StatsPage
    log("Step 5: OK")
    
    log("Step 6: Importing compare_page...")
    from views.pages.compare_page import ComparePage
    log("Step 6: OK")
    
    log("Step 7: Importing pdf_page...")
    from views.pages.pdf_page import PdfPage
    log("Step 7: OK")
    
    log("Step 8: Importing settings_page...")
    from views.pages.settings_page import SettingsPage
    log("Step 8: OK")
    
    log("Step 9: Importing plans_page...")
    from views.pages.plans_page import PlansPage
    log("Step 9: OK")
    
    log("Step 10: Importing suggestion_page...")
    from views.pages.suggestion_page import SuggestionPage
    log("Step 10: OK")
    
    log("Step 11: Importing styles...")
    from views.styles import STYLESHEET
    log("Step 11: OK")
    
    log("Step 12: Importing MainWindow...")
    from views.main_window import MainWindow
    log("Step 12: OK")
    
except Exception as e:
    log(f"\nERROR: {e}")
    log(traceback.format_exc())
    input("Hata olustu. Enter'a basin...")
    sys.exit(1)

# PyInstaller için çalışma dizinini ayarla
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)

def main():
    log("\nStep 13: Creating QApplication...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    log("Step 13: OK")

    log("Step 14: Creating MainWindow...")
    window = MainWindow()
    log("Step 14: OK")
    
    log("Step 15: Showing window...")
    window.show()
    log("Step 15: OK - Entering event loop")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()