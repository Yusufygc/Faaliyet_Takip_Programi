# main_window.py
import customtkinter as ctk
from gui.add_page import AddPage
from gui.list_page import ListPage
from gui.edit_page import EditPage
from gui.stats_page import StatsPage

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Faaliyet Takip Sistemi")
        self.minsize(1024, 600)
        self.geometry("1200x700")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tema Ayarı
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Navigasyon Alanı
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        nav_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(nav_frame, text="➕ Ekle", command=self.show_add_page).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(nav_frame, text="📋 Listele", command=self.show_list_page).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(nav_frame, text="📊 İstatistik", command=self.show_stats_page).grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkButton(nav_frame, text="❌ Çıkış", command=self.destroy).grid(row=0, column=3, padx=5, sticky="ew")

        # Sayfa Alanı
        self.page_container = ctk.CTkFrame(self)
        self.page_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "add": AddPage(self.page_container, self),
            "list": ListPage(self.page_container, self),
            "stats": StatsPage(self.page_container, self),
            "edit": EditPage(self.page_container, self)
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_list_page()

    def show_add_page(self):
        self.pages["add"].tkraise()

    def show_list_page(self):
        self.pages["list"].tkraise()

    def show_stats_page(self):
        self.pages["stats"].tkraise()

    def show_edit_page(self, activity):
        self.pages["edit"].load_activity(activity)
        self.pages["edit"].tkraise()

def run_gui():
    app = MainWindow()
    app.mainloop()
