# main.py
import customtkinter as ctk 
from database import init_db
from gui import run_gui

def main():
    """
    Ana uygulama akışını başlatır.
    Veritabanını başlatır ve GUI'yi çalıştırır.
    """
    init_db()
    run_gui()

if __name__ == "__main__":
    main()
