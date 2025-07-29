# main.py
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'
from database import init_db
from gui import run_gui

def main():
    init_db()
    run_gui()

if __name__ == "__main__":
    main()
