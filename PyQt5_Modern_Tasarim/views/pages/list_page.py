# views/pages/list_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
                             QMenu, QDialog, QGridLayout) # QGridLayout eklendi
from PyQt5.QtCore import Qt, QTimer
import math

from constants import LIST_PAGE_FILTRE_SECENEKLERI
from views.widgets import MonthYearWidget
from views.pages.edit_dialog import EditDialog

class ListPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Sayfalama Değişkenleri
        self.current_page = 1
        self.items_per_page = 15 # Varsayılan gösterim sayısı
        self.total_pages = 1
        
        # Arama Gecikmesi (Debounce) için Zamanlayıcı
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.interval = 300 # 300ms bekleme
        self.search_timer.timeout.connect(self.on_filter_changed)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Üst Başlık ve Toplam Kayıt Sayısı ---
        header_layout = QHBoxLayout()
        title = QLabel("Faaliyet Listesi")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        
        self.lbl_total_count = QLabel("Toplam: 0")
        self.lbl_total_count.setStyleSheet("color: #666; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_total_count)
        layout.addLayout(header_layout)

        # --- Filtre Alanı (Modern Tasarım) ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
            }
            QLabel { border: none; font-weight: bold; color: #555; }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Tür Filtresi
        filter_layout.addWidget(QLabel("Tür:"))
        self.combo_filter_type = QComboBox()
        self.combo_filter_type.addItems(LIST_PAGE_FILTRE_SECENEKLERI)
        self.combo_filter_type.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.combo_filter_type)

        # 2. Tarih Filtresi (Widget)
        filter_layout.addWidget(QLabel("Tarih:"))
        self.date_widget = MonthYearWidget()
        self.date_widget.dateChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.date_widget)

        # 3. İsim Arama
        filter_layout.addWidget(QLabel("Ara:"))
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Faaliyet adı yazın...")
        self.input_search.setClearButtonEnabled(True)
        # Her tuşa basıldığında sayacı yeniden başlat
        self.input_search.textChanged.connect(lambda: self.search_timer.start())
        filter_layout.addWidget(self.input_search)

        # 4. Temizle Butonu
        btn_clear = QPushButton("Temizle")
        btn_clear.setFixedWidth(80)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE; color: #D32F2F; border: none; border-radius: 4px; padding: 5px;
            }
            QPushButton:hover { background-color: #FFCDD2; }
        """)
        btn_clear.clicked.connect(self.reset_filters)
        filter_layout.addWidget(btn_clear)
        
        layout.addWidget(filter_frame)

        # --- Tablo (Liste) ---
        self.table = QTableWidget()
        
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tür", "Ad", "Tarih", "Yorum", "Puan"])
        
        # Tablo Görünüm Ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Tür sütunu dar
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Puan sütunu dar
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # Satır seçimi
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Düzenleme kapalı
        self.table.setSortingEnabled(True) # Sütun başlığına tıklayarak sıralama
        self.table.setAlternatingRowColors(True) # Okunabilirlik için
        self.table.setShowGrid(False) # Izgara çizgilerini gizle
        self.table.setStyleSheet("QTableWidget { border: none; selection-background-color: #E3F2FD; selection-color: black; }")
        
        # Tablo Olayları
        self.table.doubleClicked.connect(self.open_edit_dialog) # Çift tıkla düzenle
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu) # Sağ tık menüsü
        
        layout.addWidget(self.table)

        # --- Sayfalama (Pagination) Alanı - GÜNCELLENDİ (Grid Layout) ---
        pagination_widget = QWidget()
        pagination_layout = QGridLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 10, 0, 0) # Üstten biraz boşluk
        
        # 1. SOL PARÇA: Sayfa Başına Gösterim (Kendi içinde yatay layout)
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("Sayfa başına:"))
        self.combo_per_page = QComboBox()
        self.combo_per_page.addItems(["15", "30", "50", "100"])
        self.combo_per_page.currentTextChanged.connect(self.on_per_page_changed)
        left_layout.addWidget(self.combo_per_page)
        
        # 2. ORTA PARÇA: Navigasyon Butonları (Kendi içinde yatay layout)
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_prev = QPushButton("◄ Önceki")
        self.btn_prev.clicked.connect(self.prev_page)
        center_layout.addWidget(self.btn_prev)

        self.lbl_page_info = QLabel("Sayfa 1 / 1")
        self.lbl_page_info.setStyleSheet("font-weight: bold; margin: 0 10px;")
        center_layout.addWidget(self.lbl_page_info)

        self.btn_next = QPushButton("Sonraki ►")
        self.btn_next.clicked.connect(self.next_page)
        center_layout.addWidget(self.btn_next)

        # 3. GRİD YERLEŞİMİ (3 Sütunlu Mantık)
        # (Widget, Satır, Sütun, Hizalama)
        pagination_layout.addWidget(left_container, 0, 0, Qt.AlignLeft)   # Sol: Sola yasla
        pagination_layout.addWidget(center_container, 0, 1, Qt.AlignCenter) # Orta: Ortaya yasla
        pagination_layout.addWidget(QWidget(), 0, 2)                      # Sağ: Boş widget (Denge için)

        # Sütun Genişlik Ayarları (Sol ve Sağ eşit esneyerek ortayı sıkıştırır ve ortalar)
        pagination_layout.setColumnStretch(0, 1) # Sol taraf esnesin
        pagination_layout.setColumnStretch(1, 0) # Orta taraf sadece içeriği kadar olsun
        pagination_layout.setColumnStretch(2, 1) # Sağ taraf esnesin (Soldaki kadar)

        layout.addWidget(pagination_widget)

        # İlk Yükleme
        self.refresh_data()

    def on_filter_changed(self):
        """Filtre değiştiğinde (veya arama yapıldığında) sayfayı 1'e al ve yenile."""
        self.current_page = 1
        self.refresh_data()

    def on_per_page_changed(self, text):
        """Sayfa başına öğe sayısı değiştiğinde."""
        self.items_per_page = int(text)
        self.current_page = 1
        self.refresh_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_data()

    def refresh_data(self):
        """Verileri Controller'dan çeker, tabloyu ve sayfalama bilgisini günceller."""
        # Veri yüklerken sıralamayı geçici kapat (Titremeyi önler)
        self.table.setSortingEnabled(False)
        
        # Filtre değerlerini al
        type_filter = self.combo_filter_type.currentText()
        search_term = self.input_search.text()
        date_filter = self.date_widget.get_date_str()

        # Controller'dan veriyi ve toplam sayıyı al (Pagination destekli metod)
        activities, total_count = self.controller.get_all_activities(
            type_filter, search_term, date_filter, 
            page=self.current_page, 
            items_per_page=self.items_per_page
        )
        
        # Toplam Kayıt Bilgisini Güncelle
        self.lbl_total_count.setText(f"Toplam: {total_count}")
        
        # Sayfa Sayısını Hesapla
        self.total_pages = math.ceil(total_count / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        
        # Sayfa Bilgisini Güncelle
        self.lbl_page_info.setText(f"Sayfa {self.current_page} / {self.total_pages}")
        
        # Butonları Aktif/Pasif Yap
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

        # Tabloyu Doldur
        self.table.setRowCount(0)
        for row_idx, activity in enumerate(activities):
            self.table.insertRow(row_idx)
            
            # 1. TÜR SÜTUNU
            # Baş harfi büyüt (dizi -> Dizi)
            type_text = activity.type.title() if activity.type else ""
            item_type = QTableWidgetItem(type_text)
            # ID'yi bu hücreye GİZLİ VERİ (UserRole) olarak saklıyoruz
            item_type.setData(Qt.UserRole, activity.id)
            self.table.setItem(row_idx, 0, item_type)
            
            # 2. AD SÜTUNU (Ortalı)
            item_name = QTableWidgetItem(activity.name)
            item_name.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_name)
            
            # 3. TARİH SÜTUNU (Ortalı)
            item_date = QTableWidgetItem(activity.date)
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, item_date)
            
            # 4. YORUM SÜTUNU
            self.table.setItem(row_idx, 3, QTableWidgetItem(activity.comment))
            
            # 5. PUAN SÜTUNU (Ortalı)
            rating_display = str(activity.rating) if activity.rating > 0 else "-"
            rating_item = QTableWidgetItem(rating_display)
            rating_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, rating_item)

        # Sıralamayı tekrar aç
        self.table.setSortingEnabled(True)

    def reset_filters(self):
        """Filtreleri varsayılan değerlere döndürür."""
        self.combo_filter_type.setCurrentIndex(0)
        self.input_search.clear()
        self.date_widget.clear_filters() # Widgets.py'de eklediğimiz metod
        self.current_page = 1
        # resetlenen widget'lar sinyal gönderdiği için refresh_data otomatik çalışır.
    
    def open_edit_dialog(self):
        """Seçili satırı düzenlemek için pencere açar."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return

        row_index = selected_rows[0].row()
        
        # ID'yi GİZLİ VERİ (UserRole)'den çekiyoruz (0. Sütundan)
        activity_id = self.table.item(row_index, 0).data(Qt.UserRole)

        # Güncel veriyi çek
        activity = self.controller.get_activity(activity_id)
        
        if activity:
            dialog = EditDialog(self.controller, activity, self)
            if dialog.exec_() == QDialog.Accepted:
                # Düzenleme bittiyse listeyi yenile
                self.refresh_data()
                
                # Status bar güncellemesi
                if self.window().statusBar():
                    self.window().statusBar().showMessage(f"✏️ Kayıt güncellendi: {activity.name}", 3000)

    def open_context_menu(self, position):
        """Sağ tık menüsünü açar."""
        menu = QMenu()
        edit_action = menu.addAction("✏️ Düzenle")
        delete_action = menu.addAction("🗑️ Sil")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == delete_action:
            self.delete_selected_row()
        elif action == edit_action:
            self.open_edit_dialog()

    def delete_selected_row(self):
        """Seçili satırı siler."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir satır seçin.")
            return

        row_index = selected_rows[0].row()
        
        # ID'yi GİZLİ VERİ (UserRole)'den çekiyoruz
        activity_id = self.table.item(row_index, 0).data(Qt.UserRole)

        confirm = QMessageBox.question(self, "Onay", "Bu kaydı silmek istediğinize emin misiniz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = self.controller.delete_activity(activity_id)
            if success:
                if self.window().statusBar():
                    self.window().statusBar().showMessage(f"🗑️ {msg}", 3000)
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Hata", msg)