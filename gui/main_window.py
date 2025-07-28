# main_window.py (güncellenmiş)
import customtkinter as ctk
from gui.add_page import AddPage
from gui.list_page import ListPage
from gui.edit_page import EditPage
from gui.stats_page import StatsPage

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Faaliyet Takip Uygulaması")
        self.geometry("800x700")

        self.pages = {}

        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(side="top", fill="x")

        ctk.CTkButton(nav_frame, text="Ekle", command=self.show_add_page).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(nav_frame, text="Listele", command=self.show_list_page).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(nav_frame, text="İstatistik", command=self.show_stats_page).pack(side="left", padx=5, pady=5)

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True)

        self.pages["add"] = AddPage(container, self)
        self.pages["list"] = ListPage(container, self)
        self.pages["edit"] = EditPage(container, self)
        self.pages["stats"] = StatsPage(container, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_add_page()

    def show_add_page(self):
        self.pages["add"].tkraise()

    def show_list_page(self):
        self.pages["list"].list_filtered_activities()
        self.pages["list"].tkraise()

    def show_edit_page(self, activity):
        self.pages["edit"].load_activity(activity)
        self.pages["edit"].tkraise()

    def show_stats_page(self):
        self.pages["stats"].tkraise()

def run_gui():
    app = MainWindow()
    app.mainloop()
