# main.py
from database import init_db
from gui import run_gui

def main():
    init_db()
    run_gui()

if __name__ == "__main__":
    main()
