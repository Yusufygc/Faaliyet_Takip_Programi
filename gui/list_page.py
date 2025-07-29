import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker
from datetime import datetime

# FAALIYET_TURLERI listesine "Hepsi" eklendi
FAALIYET_TURLERI = ["Hepsi", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=False)
        self.current_page = 1
        self.items_per_page = 15  # Her sayfada gösterilecek öğe sayısı

        # Ana çerçevenin grid yapılandırması
        self.grid_rowconfigure(1, weight=1) # Treeview'in dikeyde genişlemesi için
        self.grid_columnconfigure(0, weight=1) # Tek sütunun yatayda genişlemesi için
        self.grid_rowconfigure(2, weight=0) # Kontrol butonları satırı dikeyde genişlemesin

        # Genel boşluk değeri
        padding_value = 12 # Tüm butonlar ve öğeler arası boşluk için

        # --- Filtreleme Çerçevesi ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=padding_value/2)
        # Varsayılan değer "Hepsi" olarak ayarlandı
        self.filter_type_var = ctk.StringVar(value="Hepsi") 
        filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_type_var, values=FAALIYET_TURLERI)
        filter_type_dropdown.grid(row=0, column=1, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=2, padx=padding_value/2)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=3, padx=padding_value/2)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=4, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=5, padx=padding_value/2)
        self.filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
        self.filter_name_entry.grid(row=0, column=6, padx=padding_value/2)

        # Filtrele butonu
        ctk.CTkButton(filter_frame, text="Filtrele", command=self.list_filtered_activities).grid(row=0, column=7, padx=padding_value/2)
        # Yeni Yenile butonu
        ctk.CTkButton(filter_frame, text="Yenile", command=self.refresh_all).grid(row=0, column=8, padx=padding_value/2)


        # --- Treeview ---
        self.tree = ttk.Treeview(self, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=self.items_per_page)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Ana Kontrol Butonları Çerçevesi ---
        main_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_control_frame.grid(row=2, column=0, pady=padding_value, padx=padding_value, sticky="ew")
        
        main_control_frame.grid_columnconfigure(0, weight=1) 
        main_control_frame.grid_columnconfigure(1, weight=0)
        main_control_frame.grid_columnconfigure(2, weight=1)

        button_group_frame = ctk.CTkFrame(main_control_frame, fg_color="transparent")
        button_group_frame.grid(row=0, column=1, sticky="nsew")
        
        button_group_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Sol Dikey Blok: Seçili Kaydı Sil ve Önceki ---
        left_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        left_block_frame.grid(row=0, column=0, sticky="ew", padx=padding_value/2)
        left_block_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkButton(left_block_frame, text="Seçili Kaydı Sil", command=self.delete_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.prev_button = ctk.CTkButton(left_block_frame, text="Önceki", command=self.go_to_previous_page)
        self.prev_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)

        # --- Orta Dikey Blok: Düzenle ve Sayfa Sayısı ---
        middle_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        middle_block_frame.grid(row=0, column=1, sticky="ew", padx=padding_value/2)
        middle_block_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(middle_block_frame, text="Düzenle", command=self.edit_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.page_info_label = ctk.CTkLabel(middle_block_frame, text="Sayfa 1/1", font=ctk.CTkFont(size=14, weight="bold"))
        self.page_info_label.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # --- Sağ Dikey Blok: Yenile (alt) ve Sonraki ---
        right_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        right_block_frame.grid(row=0, column=2, sticky="ew", padx=padding_value/2)
        right_block_frame.grid_columnconfigure(0, weight=1)

        # Yenile butonu (bu, daha önce alt kısımda olan Yenile butonu)
        ctk.CTkButton(right_block_frame, text="Yenile", command=self.refresh_all).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.next_button = ctk.CTkButton(right_block_frame, text="Sonraki", command=self.go_to_next_page)
        self.next_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # Minimum pencere boyutu
        self.controller.wm_minsize(800, 600)

        self.refresh_all()

    def refresh_all(self):
        """Tüm filtreleri temizler ve listeyi ilk sayfadan (tüm verileri göstererek) yeniden yükler."""
        # Filtre girişlerini varsayılan hallerine getir
        self.filter_type_var.set("Hepsi") # Türü "Hepsi" yap
        
        # Tarih seçiciyi boşalt
        self.date_picker.year_var.set("") 
        self.date_picker.month_var.set("")
        self.selected_year_only.set(False)
        self.filter_name_entry.delete(0, ctk.END)

        self.current_page = 1
        # Tüm filtreleri yok sayarak listeyi yenile
        self.list_filtered_activities(ignore_filters=True)


    def list_filtered_activities(self, ignore_filters=False):
        conn = get_connection()
        cursor = conn.cursor()

        where_clauses = ["1=1"]
        params = []
        
        filter_details = [] # Bildirim için uygulanan filtreleri sakla

        if not ignore_filters:
            applied_type = self.filter_type_var.get()
            # "Hepsi" seçeneği seçildiğinde tür filtresini uygulama
            if applied_type and applied_type != "Hepsi": 
                where_clauses.append("type = ?")
                params.append(applied_type)
                filter_details.append(f"Tür: '{applied_type}'")

            selected_year = self.date_picker.year_var.get()
            selected_month = self.date_picker.month_var.get()
            is_year_only = self.selected_year_only.get()

            # Tarih filtreleme mantığı güncellendi
            if is_year_only and selected_year: # Sadece yıl seçiliyse ve yıl girilmişse
                if is_valid_yyyy(selected_year):
                    where_clauses.append("date LIKE ?")
                    params.append(selected_year + "%")
                    filter_details.append(f"Yıl: '{selected_year}'")
                else:
                    messagebox.showwarning("Geçersiz Yıl", "Lütfen geçerli bir yıl girin (YYYY).")
                    conn.close()
                    return
            elif not is_year_only and selected_year and selected_month: # Yıl ve ay seçiliyse (sadece yıla göre değilse)
                date_str = f"{selected_year}-{selected_month}"
                if is_valid_yyyymm(date_str):
                    where_clauses.append("date = ?")
                    params.append(date_str)
                    filter_details.append(f"Tarih: '{date_str}'")
                else:
                    messagebox.showwarning("Geçersiz Tarih", "Lütfen geçerli bir tarih girin (YYYY-MM).")
                    conn.close()
                    return
            # Aksi takdirde, yani yıl veya ay boşsa ya da sadece ay seçiliyse, tarih filtresi uygulanmaz.

            applied_name = self.filter_name_entry.get().strip()
            if applied_name:
                where_clauses.append("name LIKE ?")
                params.append(f"%{applied_name}%")
                filter_details.append(f"İsim: '{applied_name}'")

        full_where_clause = " WHERE " + " AND ".join(where_clauses)

        count_query = f"SELECT COUNT(*) FROM activities {full_where_clause}"
        cursor.execute(count_query, params)
        total_activities = cursor.fetchone()[0]
        self.total_pages = (total_activities + self.items_per_page - 1) // self.items_per_page

        offset = (self.current_page - 1) * self.items_per_page
        data_query = f"SELECT * FROM activities {full_where_clause} LIMIT ? OFFSET ?"
        data_params = params + [self.items_per_page, offset]

        cursor.execute(data_query, data_params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        if not rows:
            # Veri yoksa bildirim göster
            message_parts = ["Seçilen filtrelerle eşleşen kayıt bulunamadı."]
            if filter_details:
                message_parts.append("\nUygulanan filtreler:")
                for detail in filter_details:
                    message_parts.append(f"- {detail}")
            
            final_message = "\n".join(message_parts)
            messagebox.showinfo("Bilgi", final_message)

            self.tree.insert("", "end", values=("", "Gösterilecek veri bulunamadı.", "", "", ""), tags=("no_data",))
            self.page_info_label.configure(text="Sayfa 0/0")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
        else:
            for row in rows:
                activity = Activity.from_row(row)
                self.tree.insert("", "end", values=(activity.type, activity.name, activity.date, activity.comment, activity.rating), tags=(activity.id,))

            self.page_info_label.configure(text=f"Sayfa {self.current_page}/{self.total_pages}")
            self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")


    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.list_filtered_activities() # Mevcut filtreler korunarak sayfa geçişi
            self.reset_scroll_position()

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.list_filtered_activities() # Mevcut filtreler korunarak sayfa geçişi
            self.reset_scroll_position()

    def reset_scroll_position(self):
        self.tree.yview_moveto(0)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe silinemez.")
            return

        item = self.tree.item(selected[0])
        activity_id = item["tags"][0]


        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Başarılı", "Kayıt silindi.")
        # Silme sonrası sayfa sayısı değişebileceğinden, mevcut sayfayı kontrol et
        # ve gerekirse önceki sayfaya dön veya mevcut filtrelerle yeniden listele
        # Daha doğru bir davranış için, silme sonrası tüm filtreleri koruyarak listeyi yenilemek.
        self.list_filtered_activities()


    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe düzenlenemez.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        item_id = self.tree.item(selected[0], "tags")[0]

        activity = Activity(item_id, *values)
        self.controller.show_edit_page(activity)
"""import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=False)
        self.current_page = 1
        self.items_per_page = 15  # Her sayfada gösterilecek öğe sayısı

        # Ana çerçevenin grid yapılandırması
        self.grid_rowconfigure(1, weight=1) # Treeview'in dikeyde genişlemesi için
        self.grid_columnconfigure(0, weight=1) # Tek sütunun yatayda genişlemesi için
        self.grid_rowconfigure(2, weight=0) # Kontrol butonları satırı dikeyde genişlemesin

        # Genel boşluk değeri
        padding_value = 12 # Tüm butonlar ve öğeler arası boşluk için

        # --- Filtreleme Çerçevesi ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=padding_value/2)
        self.filter_type_var = ctk.StringVar()
        filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_type_var, values=FAALIYET_TURLERI)
        filter_type_dropdown.grid(row=0, column=1, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=2, padx=padding_value/2)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=3, padx=padding_value/2)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=4, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=5, padx=padding_value/2)
        self.filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
        self.filter_name_entry.grid(row=0, column=6, padx=padding_value/2)

        ctk.CTkButton(filter_frame, text="Filtrele", command=self.list_filtered_activities).grid(row=0, column=7, padx=padding_value)
        ctk.CTkButton(filter_frame, text="Yenile", command=self.refresh_all).grid(row=0, column=8, padx=padding_value/2)

        # --- Treeview ---
        self.tree = ttk.Treeview(self, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=self.items_per_page)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Ana Kontrol Butonları Çerçevesi ---
        main_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_control_frame.grid(row=2, column=0, pady=padding_value, padx=padding_value, sticky="ew")
        
        main_control_frame.grid_columnconfigure(0, weight=1) 
        main_control_frame.grid_columnconfigure(1, weight=0)
        main_control_frame.grid_columnconfigure(2, weight=1)

        button_group_frame = ctk.CTkFrame(main_control_frame, fg_color="transparent")
        button_group_frame.grid(row=0, column=1, sticky="nsew")
        
        button_group_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Sol Dikey Blok: Seçili Kaydı Sil ve Önceki ---
        left_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        left_block_frame.grid(row=0, column=0, sticky="ew", padx=padding_value/2)
        left_block_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkButton(left_block_frame, text="Seçili Kaydı Sil", command=self.delete_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.prev_button = ctk.CTkButton(left_block_frame, text="Önceki", command=self.go_to_previous_page)
        self.prev_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)

        # --- Orta Dikey Blok: Düzenle ve Sayfa Sayısı ---
        middle_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        middle_block_frame.grid(row=0, column=1, sticky="ew", padx=padding_value/2)
        middle_block_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(middle_block_frame, text="Düzenle", command=self.edit_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.page_info_label = ctk.CTkLabel(middle_block_frame, text="Sayfa 1/1", font=ctk.CTkFont(size=14, weight="bold"))
        self.page_info_label.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # --- Sağ Dikey Blok: Yenile ve Sonraki ---
        right_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        right_block_frame.grid(row=0, column=2, sticky="ew", padx=padding_value/2)
        right_block_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(right_block_frame, text="Yenile", command=self.refresh_all).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.next_button = ctk.CTkButton(right_block_frame, text="Sonraki", command=self.go_to_next_page)
        self.next_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # Minimum pencere boyutu
        self.controller.wm_minsize(800, 600)

        self.refresh_all()

    def refresh_all(self):
        self.current_page = 1
        self.list_filtered_activities(ignore_filters=True)

    def list_filtered_activities(self, ignore_filters=False):
        conn = get_connection()
        cursor = conn.cursor()

        where_clauses = ["1=1"]
        params = []
        
        filter_details = []

        if not ignore_filters:
            applied_type = self.filter_type_var.get()
            if applied_type:
                where_clauses.append("type = ?")
                params.append(applied_type)
                filter_details.append(f"Tür: '{applied_type}'")

            date_str = get_formatted_date_from_picker(self.date_picker)
            if self.selected_year_only.get():
                if is_valid_yyyy(date_str[:4]):
                    where_clauses.append("date LIKE ?")
                    params.append(date_str[:4] + "%")
                    filter_details.append(f"Yıl: '{date_str[:4]}'")
                else:
                    messagebox.showwarning("Geçersiz Yıl", "Lütfen geçerli bir yıl girin (YYYY).")
                    conn.close()
                    return
            else:
                if is_valid_yyyymm(date_str):
                    where_clauses.append("date = ?")
                    params.append(date_str)
                    filter_details.append(f"Tarih: '{date_str}'")
                else:
                    messagebox.showwarning("Geçersiz Tarih", "Lütfen geçerli bir tarih girin (YYYY-MM).")
                    conn.close()
                    return

            applied_name = self.filter_name_entry.get().strip()
            if applied_name:
                where_clauses.append("name LIKE ?")
                params.append(f"%{applied_name}%")
                filter_details.append(f"İsim: '{applied_name}'")

        full_where_clause = " WHERE " + " AND ".join(where_clauses)

        count_query = f"SELECT COUNT(*) FROM activities {full_where_clause}"
        cursor.execute(count_query, params)
        total_activities = cursor.fetchone()[0]
        self.total_pages = (total_activities + self.items_per_page - 1) // self.items_per_page

        offset = (self.current_page - 1) * self.items_per_page
        data_query = f"SELECT * FROM activities {full_where_clause} LIMIT ? OFFSET ?"
        data_params = params + [self.items_per_page, offset]

        cursor.execute(data_query, data_params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        if not rows:
            message_parts = ["Seçilen filtrelerle eşleşen kayıt bulunamadı."]
            if filter_details:
                message_parts.append("\nUygulanan filtreler:")
                for detail in filter_details:
                    message_parts.append(f"- {detail}")
            
            final_message = "\n".join(message_parts)
            messagebox.showinfo("Bilgi", final_message)

            self.tree.insert("", "end", values=("", "Gösterilecek veri bulunamadı.", "", "", ""), tags=("no_data",))
            self.page_info_label.configure(text="Sayfa 0/0")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
        else:
            for row in rows:
                activity = Activity.from_row(row)
                self.tree.insert("", "end", values=(activity.type, activity.name, activity.date, activity.comment, activity.rating), tags=(activity.id,))

            # Kullanıcı isteği üzerine bu bildirim kaldırıldı
            # if total_activities == 1:
            #     messagebox.showinfo("Bilgi", "Sadece 1 eşleşen kayıt bulundu.")

            self.page_info_label.configure(text=f"Sayfa {self.current_page}/{self.total_pages}")
            self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")


    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.list_filtered_activities()
            self.reset_scroll_position()

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.list_filtered_activities()
            self.reset_scroll_position()

    def reset_scroll_position(self):
        self.tree.yview_moveto(0)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe silinemez.")
            return

        item = self.tree.item(selected[0])
        activity_id = item["tags"][0]


        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Başarılı", "Kayıt silindi.")
        if self.current_page > self.total_pages and self.current_page > 1:
            self.current_page -= 1
        self.list_filtered_activities()


    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe düzenlenemez.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        item_id = self.tree.item(selected[0], "tags")[0]

        activity = Activity(item_id, *values)
        self.controller.show_edit_page(activity)
"""

"""import customtkinter as ctk
from tkinter import messagebox, ttk
from models import Activity
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy
from gui.widgets import build_month_year_picker, get_formatted_date_from_picker

FAALIYET_TURLERI = ["", "dizi", "film", "kitap", "oyun", "kurs", "şehir"]

class ListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_year_only = ctk.BooleanVar(value=False)
        self.current_page = 1
        self.items_per_page = 15  # Her sayfada gösterilecek öğe sayısı

        # Ana çerçevenin grid yapılandırması
        self.grid_rowconfigure(1, weight=1) # Treeview'in dikeyde genişlemesi için
        self.grid_columnconfigure(0, weight=1) # Tek sütunun yatayda genişlemesi için
        self.grid_rowconfigure(2, weight=0) # Kontrol butonları satırı dikeyde genişlemesin

        # Genel boşluk değeri
        padding_value = 12 # Tüm butonlar ve öğeler arası boşluk için

        # --- Filtreleme Çerçevesi ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Tür:").grid(row=0, column=0, padx=padding_value/2)
        self.filter_type_var = ctk.StringVar()
        filter_type_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_type_var, values=FAALIYET_TURLERI)
        filter_type_dropdown.grid(row=0, column=1, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="Tarih:").grid(row=0, column=2, padx=padding_value/2)
        self.date_picker = build_month_year_picker(filter_frame)
        self.date_picker.grid(row=0, column=3, padx=padding_value/2)

        self.year_only_checkbox = ctk.CTkCheckBox(filter_frame, text="Sadece yıla göre", variable=self.selected_year_only)
        self.year_only_checkbox.grid(row=0, column=4, padx=padding_value/2)

        ctk.CTkLabel(filter_frame, text="İsim:").grid(row=0, column=5, padx=padding_value/2)
        self.filter_name_entry = ctk.CTkEntry(filter_frame, width=120)
        self.filter_name_entry.grid(row=0, column=6, padx=padding_value/2)

        ctk.CTkButton(filter_frame, text="Filtrele", command=self.list_filtered_activities).grid(row=0, column=7, padx=padding_value)

        # --- Treeview ---
        self.tree = ttk.Treeview(self, columns=("Tür", "Ad", "Tarih", "Yorum", "Puan"), show="headings", height=self.items_per_page)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Ana Kontrol Butonları Çerçevesi (Yeni Birleştirilmiş) ---
        main_control_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_control_frame.grid(row=2, column=0, pady=padding_value, padx=padding_value, sticky="ew")
        
        # main_control_frame içindeki sütun yapılandırması
        # Ortadaki 'button_group_frame'i merkeze hizalamak için yan sütunlara ağırlık veriyoruz
        main_control_frame.grid_columnconfigure(0, weight=1) 
        main_control_frame.grid_columnconfigure(1, weight=0) # İçerik bloğunun bulunduğu sütun (ağırlık 0)
        main_control_frame.grid_columnconfigure(2, weight=1)

        # Buton gruplarını içeren ana çerçeve
        button_group_frame = ctk.CTkFrame(main_control_frame, fg_color="transparent")
        button_group_frame.grid(row=0, column=1, sticky="nsew") # main_control_frame'in ortasında
        
        # button_group_frame içindeki sütun yapılandırması (içeriklerin genişlemesi için)
        button_group_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Sol Dikey Blok: Seçili Kaydı Sil ve Önceki ---
        left_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        left_block_frame.grid(row=0, column=0, sticky="ew", padx=padding_value/2)
        left_block_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkButton(left_block_frame, text="Seçili Kaydı Sil", command=self.delete_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.prev_button = ctk.CTkButton(left_block_frame, text="Önceki", command=self.go_to_previous_page)
        self.prev_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)

        # --- Orta Dikey Blok: Düzenle ve Sayfa Sayısı ---
        middle_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        middle_block_frame.grid(row=0, column=1, sticky="ew", padx=padding_value/2)
        middle_block_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(middle_block_frame, text="Düzenle", command=self.edit_selected).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.page_info_label = ctk.CTkLabel(middle_block_frame, text="Sayfa 1/1", font=ctk.CTkFont(size=14, weight="bold"))
        self.page_info_label.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # --- Sağ Dikey Blok: Yenile ve Sonraki ---
        right_block_frame = ctk.CTkFrame(button_group_frame, fg_color="transparent")
        right_block_frame.grid(row=0, column=2, sticky="ew", padx=padding_value/2)
        right_block_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(right_block_frame, text="Yenile", command=self.refresh_all).grid(row=0, column=0, pady=(0, padding_value/2), padx=padding_value/2)
        self.next_button = ctk.CTkButton(right_block_frame, text="Sonraki", command=self.go_to_next_page)
        self.next_button.grid(row=1, column=0, pady=(padding_value/2, 0), padx=padding_value/2)


        # Minimum pencere boyutu
        self.controller.wm_minsize(800, 600)

        self.refresh_all()

    def refresh_all(self):
        self.current_page = 1
        self.list_filtered_activities(ignore_filters=True)

    def list_filtered_activities(self, ignore_filters=False):
        conn = get_connection()
        cursor = conn.cursor()

        where_clauses = ["1=1"]
        params = []

        if not ignore_filters:
            if self.filter_type_var.get():
                where_clauses.append("type = ?")
                params.append(self.filter_type_var.get())

            date_str = get_formatted_date_from_picker(self.date_picker)
            if self.selected_year_only.get():
                if is_valid_yyyy(date_str[:4]):
                    where_clauses.append("date LIKE ?")
                    params.append(date_str[:4] + "%")
                else:
                    messagebox.showwarning("Geçersiz Yıl", "Lütfen geçerli bir yıl girin (YYYY).")
                    conn.close()
                    return
            else:
                if is_valid_yyyymm(date_str):
                    where_clauses.append("date = ?")
                    params.append(date_str)
                else:
                    messagebox.showwarning("Geçersiz Tarih", "Lütfen geçerli bir tarih girin (YYYY-MM).")
                    conn.close()
                    return

            name = self.filter_name_entry.get().strip()
            if name:
                where_clauses.append("name LIKE ?")
                params.append(f"%{name}%")

        full_where_clause = " WHERE " + " AND ".join(where_clauses)

        count_query = f"SELECT COUNT(*) FROM activities {full_where_clause}"
        cursor.execute(count_query, params)
        total_activities = cursor.fetchone()[0]
        self.total_pages = (total_activities + self.items_per_page - 1) // self.items_per_page

        offset = (self.current_page - 1) * self.items_per_page
        data_query = f"SELECT * FROM activities {full_where_clause} LIMIT ? OFFSET ?"
        data_params = params + [self.items_per_page, offset]

        cursor.execute(data_query, data_params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        if not rows:
            self.tree.insert("", "end", values=("", "Gösterilecek veri bulunamadı.", "", "", ""), tags=("no_data",))
            self.page_info_label.configure(text="Sayfa 0/0")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
        else:
            for row in rows:
                activity = Activity.from_row(row)
                self.tree.insert("", "end", values=(activity.type, activity.name, activity.date, activity.comment, activity.rating), tags=(activity.id,))

            self.page_info_label.configure(text=f"Sayfa {self.current_page}/{self.total_pages}")
            self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")


    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.list_filtered_activities()
            self.reset_scroll_position()

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.list_filtered_activities()
            self.reset_scroll_position()

    def reset_scroll_position(self):
        self.tree.yview_moveto(0)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe silinemez.")
            return

        item = self.tree.item(selected[0])
        activity_id = item["tags"][0]


        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Başarılı", "Kayıt silindi.")
        if self.current_page > self.total_pages and self.current_page > 1:
            self.current_page -= 1
        self.list_filtered_activities()


    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kayıt seçin.")
            return
        
        item_tags = self.tree.item(selected[0], "tags")
        if "no_data" in item_tags:
            messagebox.showinfo("Bilgi", "Seçilen öğe düzenlenemez.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        item_id = self.tree.item(selected[0], "tags")[0]

        activity = Activity(item_id, *values)
        self.controller.show_edit_page(activity)
"""