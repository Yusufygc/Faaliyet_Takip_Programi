import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

# FAALIYET_TURLERI listesine "Hepsi" eklendi
FAALIYET_TURLERI = ["Hepsi", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ActivityDetailDialog(ctk.CTkToplevel):
    """
    Seçilen faaliyetin detaylarını gösteren ve düzenleme/silme işlemleri sunan diyalog penceresi.
    """
    def __init__(self, parent, controller, activity: Activity, refresh_list_callback):
        super().__init__(parent)
        self.controller = controller
        self.activity = activity
        self.refresh_list_callback = refresh_list_callback
        self.parent_list_page = parent # list_page instance'ına erişim için

        self.title(f"Faaliyet Detayları: {self.activity.name}")
        self.geometry("500x500") # ID kaldırıldığı için biraz küçültüldü
        self.transient(parent)  # Ana pencereye bağımlı yap
        self.grab_set()         # Ana pencere etkileşimini engelle
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # main_frame'in dikeyde ortalanması için

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1) # İkinci sütunun genişlemesi için

        ctk.CTkLabel(main_frame, text="Faaliyet Detayları", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Detayları göster (ID gösterilmiyor)
        row_idx = 1
        details = [
            ("Tür:", self.activity.type),
            ("Ad:", self.activity.name),
            ("Tarih:", self.activity.date),
            ("Yorum:", self.activity.comment),
            ("Puan:", self.activity.rating if self.activity.rating is not None else "Yok")
        ]

        for label_text, value_text in details:
            ctk.CTkLabel(main_frame, text=label_text).grid(row=row_idx, column=0, sticky="e", padx=10, pady=5)
            ctk.CTkLabel(main_frame, text=str(value_text), wraplength=300, justify="left").grid(row=row_idx, column=1, sticky="w", padx=10, pady=5)
            row_idx += 1
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=row_idx, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1) # Butonların eşit genişlemesi için

        ctk.CTkButton(button_frame, text="Düzenle", command=self._edit_activity).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(button_frame, text="Sil", command=self._delete_activity).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(button_frame, text="Kapat", command=self.destroy).grid(row=0, column=2, padx=5, sticky="ew")

    def _edit_activity(self):
        self.destroy() # Diyalogu kapat
        self.controller.show_edit_page(self.activity) # Düzenleme sayfasına yönlendir

    def _delete_activity(self):
        confirm = messagebox.askyesno("Onay", f"'{self.activity.name}' faaliyetini silmek istediğinizden emin misiniz?")
        if confirm:
            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM activities WHERE id = ?", (self.activity.id,))
                conn.commit()
                messagebox.showinfo("Başarılı", "Kayıt başarıyla silindi.")
                self.destroy() # Diyalogu kapat
                self.refresh_list_callback() # Listeyi yenile
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt silinirken bir hata oluştu: {e}")
            finally:
                if conn:
                    conn.close()


class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_page = 1
        self.items_per_page = 10 # Sayfa başına gösterilecek öğe sayısı
        self.total_pages = 1

        self.grid_rowconfigure(2, weight=1) # Tablo için
        self.grid_columnconfigure(0, weight=1)

        # Başlık
        ctk.CTkLabel(self, text="Faaliyetleri Listele", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=15)

        # Filtre ve Arama Alanı
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        # Filtre çerçevesindeki sütunları orantılı olacak şekilde ayarla
        filter_frame.grid_columnconfigure(0, weight=0, minsize=40) # Etiket sabit
        filter_frame.grid_columnconfigure(1, weight=1, minsize=120) # Tür menüsü orantılı genişlesin
        filter_frame.grid_columnconfigure(2, weight=0, minsize=40) # Etiket sabit
        filter_frame.grid_columnconfigure(3, weight=2, minsize=150) # Arama alanı en geniş
        filter_frame.grid_columnconfigure(4, weight=0, minsize=50) # Etiket sabit
        filter_frame.grid_columnconfigure(5, weight=1, minsize=120) # Tarih seçici orantılı genişlesin
        filter_frame.grid_columnconfigure(6, weight=1, minsize=100) # Filtrele butonu orantılı genişlesin
        filter_frame.grid_columnconfigure(7, weight=1, minsize=100) # Sıfırla butonu orantılı genişlesin

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.type_var = ctk.StringVar(value=FAALIYET_TURLERI[0])
        self.type_menu = ctk.CTkOptionMenu(filter_frame, variable=self.type_var, values=FAALIYET_TURLERI, 
                                          command=self.list_filtered_activities)
        self.type_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Ara:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Faaliyet adı...")
        self.search_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda event: self.list_filtered_activities())

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(filter_frame, text="Tarihe Göre Filtrele", command=self.list_filtered_activities).grid(row=0, column=6, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(filter_frame, text="Tarihi Sıfırla", command=self.reset_date_filter).grid(row=0, column=7, padx=5, pady=5, sticky="ew")

        # Faaliyet Listesi (Treeview) - ID sütunu kaldırıldı
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings")
        
        # Style for Treeview (for better appearance)
        style = ttk.Style()
        style.theme_use("default") # Use default theme as a base
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        style.map("Treeview", 
                  background=[('selected', '#3A7EBf')], # CustomTkinter blue
                  foreground=[('selected', 'white')])

        self.tree.heading("Tür", text="Tür")
        self.tree.heading("Ad", text="Ad")
        self.tree.heading("Tarih", text="Tarih")
        self.tree.heading("Yorum", text="Yorum")
        self.tree.heading("Puan", text="Puan")

        self.tree.column("Tür", width=80, anchor="center")
        self.tree.column("Ad", width=200, anchor="w")
        self.tree.column("Tarih", width=80, anchor="center")
        self.tree.column("Yorum", width=250, anchor="w")
        self.tree.column("Puan", width=60, stretch=False, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # İyileştirilmiş "Veri Yok" etiketi - Tam ortalanmış ve sade görünüm
        self.no_data_label = ctk.CTkLabel(
            table_frame, 
            text="Listelenecek herhangi bir faaliyet bulunamadı.\nLütfen önce 'Ekle' sayfasından yeni faaliyetler ekleyin.", 
            font=ctk.CTkFont(size=18, slant="italic"),  # Daha küçük font ve italik
            text_color="#999999",  # Sade gri ton
            wraplength=500,  # Uygun genişlik
            justify="center"  # Metin ortalanmış
        )
        
        # Etiketi table_frame'in tam ortasına yerleştir
        # place() kullanarak tam ortalama sağlayalım
        self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")
        self.no_data_label.place_forget()  # Başlangıçta gizli tut

        self.tree.bind("<Double-1>", self.open_detail_dialog) # Çift tıklama olayı

        # Sayfalama Bölümü - Tamamen yeniden düzenlendi
        pagination_container = ctk.CTkFrame(self)
        pagination_container.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        pagination_container.grid_columnconfigure(0, weight=1)  # Ana kapsayıcının tamamını genişlet
        pagination_container.grid_rowconfigure(0, weight=1)

        # 1. TAMAMEN BAĞIMSIZ: Sayfa geçiş kontrolleri - Pencerenin tam genişliğine göre ortalanmış
        navigation_container = ctk.CTkFrame(pagination_container, fg_color="transparent")
        navigation_container.grid(row=0, column=0, sticky="ew")  # Tam genişlikte yerleş
        navigation_container.grid_columnconfigure(0, weight=1)  # Sol boş alan
        navigation_container.grid_columnconfigure(1, weight=0)  # Navigation grubu (sabit genişlik)
        navigation_container.grid_columnconfigure(2, weight=1)  # Sağ boş alan

        # Sayfa geçiş butonları grubu - Tam ortada
        navigation_frame = ctk.CTkFrame(navigation_container, fg_color="transparent")
        navigation_frame.grid(row=0, column=1, sticky="")  # Orta sütunda, ortalanmış
        navigation_frame.grid_columnconfigure(0, weight=0)  # Önceki butonu
        navigation_frame.grid_columnconfigure(1, weight=0)  # Sayfa etiketi
        navigation_frame.grid_columnconfigure(2, weight=0)  # Sonraki butonu

        self.prev_button = ctk.CTkButton(navigation_frame, text="Önceki", command=self.prev_page, width=100)
        self.prev_button.grid(row=0, column=0, padx=(0, 10))

        self.page_label = ctk.CTkLabel(navigation_frame, text=f"Sayfa {self.current_page}/{self.total_pages}", 
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.page_label.grid(row=0, column=1, padx=20)

        self.next_button = ctk.CTkButton(navigation_frame, text="Sonraki", command=self.next_page, width=100)
        self.next_button.grid(row=0, column=2, padx=(10, 0))

        # 2. TAMAMEN BAĞIMSIZ: "Sayfa Başına Gösterilecek Veri" kontrolleri - Sağ alt köşe
        items_per_page_container = ctk.CTkFrame(pagination_container, fg_color="transparent")
        items_per_page_container.grid(row=0, column=0, sticky="se", padx=(0, 0), pady=(0, 0))  # Sağ alt köşeye yapış
        items_per_page_container.grid_columnconfigure(0, weight=0)
        items_per_page_container.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(items_per_page_container, text="Sayfa Başına Gösterilecek Veri:").grid(row=0, column=0, padx=(0, 5))
        self.items_per_page_var = ctk.StringVar(value=str(self.items_per_page))
        self.items_per_page_menu = ctk.CTkOptionMenu(
            items_per_page_container, 
            variable=self.items_per_page_var, 
            values=["5", "10", "20", "50"], 
            command=self.change_items_per_page, 
            width=60
        )
        self.items_per_page_menu.grid(row=0, column=1)

        self.list_filtered_activities() # İlk yüklemede listeyi göster

    def reset_date_filter(self):
        """Tarih filtresini sıfırlar ve diğer filtrelere göre veri getirir."""
        # Tarih picker'ı sıfırla (year ve month değerlerini boş yap)
        if hasattr(self.date_picker, 'year_var'):
            self.date_picker.year_var.set("")
        if hasattr(self.date_picker, 'month_var'):
            self.date_picker.month_var.set("")
        
        # Listeyi yenile (tarih filtresi olmadan)
        self.list_filtered_activities()

    def fetch_activities(self, activity_type_filter="Hepsi", search_term="", date_filter=""):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, type, name, date, comment, rating FROM activities WHERE 1=1"
        params = []

        if activity_type_filter != "Hepsi":
            query += " AND type = ?"
            params.append(activity_type_filter)

        if search_term:
            query += " AND name LIKE ?"
            params.append(f"%{search_term}%")

        if date_filter:
            if is_valid_yyyymm(date_filter):
                query += " AND date = ?"
                params.append(date_filter)
            elif is_valid_yyyy(date_filter):
                query += " AND date LIKE ?"
                params.append(f"{date_filter}%")
            else:
                # Geçersiz tarih filtresi durumunda uyarı verilebilir veya yoksayılabilir
                pass

        query += " ORDER BY date DESC, id DESC" # Tarihe göre azalan, sonra ID'ye göre azalan

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Activity.from_row(row) for row in rows]

    def list_filtered_activities(self, *args): # *args, OptionMenu'den gelen event argümanını yakalamak için
        selected_type = self.type_var.get()
        search_term = self.search_entry.get().strip()
        selected_date = get_formatted_date_from_picker(self.date_picker)

        all_activities = self.fetch_activities(selected_type, search_term, selected_date)
        
        self.total_pages = (len(all_activities) + self.items_per_page - 1) // self.items_per_page
        if self.total_pages == 0: # Hiç aktivite yoksa sayfa sayısı 1 değil 0 olmalı
            self.total_pages = 1
            self.current_page = 1 # Sayfa 1'e sıfırla

        # Eğer mevcut sayfa toplam sayfa sayısından büyükse, mevcut sayfayı ayarla
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1: # En az 1. sayfada olmalı
            self.current_page = 1

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_activities = all_activities[start_index:end_index]

        self.update_treeview(paginated_activities)
        self.update_pagination_buttons()

    def update_treeview(self, activities):
        # Mevcut öğeleri temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not activities: # Eğer aktiviteler boşsa
            self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")  # Etiketi tam ortada göster
        else:
            self.no_data_label.place_forget()  # Etiketi gizle
            
            # Yeni öğeleri ekle (ID gösterilmiyor, ancak dahili olarak saklanıyor)
            for activity in activities:
                # Yorum sütunu eklendi
                comment_display = activity.comment[:50] + "..." if activity.comment and len(activity.comment) > 50 else (activity.comment or "")
                self.tree.insert("", "end", iid=str(activity.id), 
                               values=(activity.type, activity.name, activity.date, comment_display, activity.rating))

    def update_pagination_buttons(self):
        self.page_label.configure(text=f"Sayfa {self.current_page}/{self.total_pages}")
        self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.list_filtered_activities()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.list_filtered_activities()

    def change_items_per_page(self, new_value):
        self.items_per_page = int(new_value)
        self.current_page = 1 # Sayfa başına öğe değiştiğinde ilk sayfaya dön
        self.list_filtered_activities()

    def open_detail_dialog(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen detaylarını görmek istediğiniz bir faaliyet seçiniz.")
            return

        # ID'yi item'ın iid'sinden al
        activity_id = selected_item

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, name, date, comment, rating FROM activities WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            activity = Activity.from_row(row)
            # ActivityDetailDialog'a refresh_list_callback gönder
            ActivityDetailDialog(self, self.controller, activity, self.list_filtered_activities)
        else:
            messagebox.showerror("Hata", "Seçilen faaliyet bulunamadı.")

    # Bu metotlar artık alt kısımdaki butonlardan çağrılmayacak
    # Ancak _get_selected_activity_from_tree fonksiyonunu kullandıkları için bırakıldı.
    # Eğer bu metotlar başka bir yerden de çağrılmıyorsa tamamen kaldırılabilir.
    def _delete_selected_from_list_page(self):
        """ListPage üzerindeki butondan seçili kaydı siler."""
        activity = self._get_selected_activity_from_tree()
        if not activity:
            return # Zaten uyarı verildi

        confirm = messagebox.askyesno("Onay", f"'{activity.name}' faaliyetini silmek istediğinizden emin misiniz?")
        if not confirm:
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activities WHERE id = ?", (activity.id,))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt başarıyla silindi.")
            self.list_filtered_activities() # Mevcut filtrelerle listeyi yenile
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt silinirken bir hata oluştu: {e}")
        finally:
            if conn:
                conn.close()

    def _edit_selected_from_list_page(self):
        """ListPage üzerindeki butondan seçili kaydı düzenleme sayfasına yönlendirir."""
        activity = self._get_selected_activity_from_tree()
        if not activity:
            return # Zaten uyarı verildi
        self.controller.show_edit_page(activity)

    def _get_selected_activity_from_tree(self):
        """Treeview'dan seçili aktiviteyi döndürür."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir faaliyet seçiniz.")
            return None
        
        # ID'yi item'ın iid'sinden al
        activity_id = selected_item

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, name, date, comment, rating FROM activities WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Activity.from_row(row)
        else:
            messagebox.showerror("Hata", "Seçilen faaliyet veritabanında bulunamadı.")
            return None