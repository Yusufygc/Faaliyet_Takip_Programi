# main.py
import customtkinter as ctk
from database import init_db
from gui import run_gui
import traceback
import sys
import os

def main():
    """
    Ana uygulama akışını başlatır.
    Veritabanını başlatır ve GUI'yi çalıştırır.
    """
    init_db()
    run_gui()

if __name__ == "__main__":
    # Hataları bir dosyaya yönlendirmek için try-except bloğu ekle
    log_file_path = os.path.join(os.path.dirname(sys.executable), "error.log")
    
    # pyinstaller ile paketlenmiş uygulamalar için
    if getattr(sys, 'frozen', False):
        try:
            main()
        except Exception as e:
            with open(log_file_path, "w") as f:
                f.write(f"Uygulama Hatası: {e}\n\n")
                f.write("Hata İzlemi:\n")
                traceback.print_exc(file=f)
    else:
        # Geliştirme ortamı
        main()