# views/pages/list_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
                             QMenu, QDialog, QGridLayout, QGraphicsDropShadowEffect, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QIcon, QBrush
import math

from views.widgets import MonthYearWidget
from views.dialogs.edit_dialog import EditDialog
# ═══════════════════════════════════════════════════════════════════════════════
# STYLE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'bg_main':       '#F8FAFC',  # C_BG_LIGHT
    'bg_card':       '#FFFFFF',  # C_BG_WHITE
    'text_main':     '#1E293B',  # C_TEXT_DARK
    'text_sub':      '#64748B',  # C_TEXT_LIGHT
    'primary':       '#3B82F6',  # C_PRIMARY
    'primary_light': '#EFF6FF',
    'border':        '#E2E8F0',  # C_BORDER
    'table_header':  '#F1F5F9',  # C_BG_SUBTLE
    'table_alt_row': '#F8FAFC',  # C_BG_LIGHT
}

class ListPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Sayfalama Değişkenleri
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.interval = 300
        self.search_timer.timeout.connect(self.on_filter_changed)

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self._build_header(layout)
        self._build_filter(layout)
        self._build_table(layout)
        self._build_pagination(layout)
        self.load_types()
        self.refresh_data()

    def _build_header(self, layout):
        header_layout = QHBoxLayout()
        title = QLabel("Faaliyet Listesi")
        title.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {COLORS['text_main']}; letter-spacing: 0.5px;")

        self.badge_total = QLabel("0 Kayıt")
        self.badge_total.setStyleSheet(f"""
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary']};
            font-weight: bold;
            padding: 6px 15px;
            border-radius: 16px;
            font-size: 14px;
        """)

        header_layout.addWidget(title)
        header_layout.addSpacing(15)
        header_layout.addWidget(self.badge_total)
        header_layout.addStretch()
        layout.addLayout(header_layout)

    def _build_filter(self, layout):
        filter_frame = QFrame()
        filter_frame.setObjectName("filter_frame")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 5)
        filter_frame.setGraphicsEffect(shadow)

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(20)

        lbl_type = QLabel("Tür:")
        lbl_type.setStyleSheet(f"font-weight: 700; color: {COLORS['text_sub']}; font-size: 14px; border: none;")
        self.combo_filter_type = QComboBox()
        self.combo_filter_type.addItem("Hepsi")
        self.combo_filter_type.setStyleSheet(self._get_combo_style())
        self.combo_filter_type.currentIndexChanged.connect(self.on_filter_changed)

        lbl_date = QLabel("Tarih:")
        lbl_date.setStyleSheet(f"font-weight: 700; color: {COLORS['text_sub']}; font-size: 14px; border: none;")
        self.date_widget = MonthYearWidget()
        self.date_widget.setStyleSheet(self._get_combo_style())
        self.date_widget.dateChanged.connect(self.on_filter_changed)

        lbl_search = QLabel("Ara:")
        lbl_search.setStyleSheet(f"font-weight: 700; color: {COLORS['text_sub']}; font-size: 14px; border: none;")
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Faaliyet adı ile ara...")
        self.input_search.setClearButtonEnabled(True)
        self.input_search.textChanged.connect(lambda: self.search_timer.start())

        btn_clear = QPushButton("Temizle")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setFixedWidth(100)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: #FDEDEC; color: #E74C3C; border: none; border-radius: 8px;
                padding: 10px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #FADBD8; }}
        """)
        btn_clear.clicked.connect(self.reset_filters)

        def _divider():
            line = QFrame()
            line.setFixedWidth(1)
            line.setFixedHeight(20)
            line.setStyleSheet(f"background: {COLORS['border']};")
            return line

        filter_layout.addWidget(lbl_type)
        filter_layout.addWidget(self.combo_filter_type)
        filter_layout.addSpacing(15)
        filter_layout.addWidget(_divider())
        filter_layout.addSpacing(5)
        filter_layout.addWidget(lbl_date)
        filter_layout.addWidget(self.date_widget)
        filter_layout.addSpacing(15)
        filter_layout.addWidget(_divider())
        filter_layout.addSpacing(5)
        filter_layout.addWidget(lbl_search)
        filter_layout.addWidget(self.input_search, 1)
        filter_layout.addWidget(btn_clear)

        layout.addWidget(filter_frame)

    def _build_table(self, layout):
        table_container = QFrame()
        table_container.setObjectName("card")
        t_shadow = QGraphicsDropShadowEffect()
        t_shadow.setBlurRadius(20)
        t_shadow.setColor(QColor(0, 0, 0, 8))
        t_shadow.setOffset(0, 4)
        table_container.setGraphicsEffect(t_shadow)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["TÜR", "FAALİYET ADI", "TARİH", "YORUM", "PUAN"])
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                border-radius: 12px;
                padding: 10px;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_main']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS['table_alt_row']};
            }}
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {COLORS['table_header']};
                color: {COLORS['text_sub']};
                padding: 0 10px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: 800;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        self.table.verticalHeader().setVisible(False)

        self.table.doubleClicked.connect(self.open_edit_dialog)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

    def _build_pagination(self, layout):
        pagination_widget = QWidget()
        pagination_layout = QGridLayout(pagination_widget)
        pagination_layout.setContentsMargins(10, 5, 10, 0)

        left_box = QHBoxLayout()
        lbl_pp = QLabel("Sayfa başına:")
        lbl_pp.setStyleSheet(f"color: {COLORS['text_sub']}; font-weight: bold; font-size: 13px;")
        self.combo_per_page = QComboBox()
        self.combo_per_page.addItems(["15", "30", "50", "100"])
        self.combo_per_page.setStyleSheet(self._get_combo_style())
        self.combo_per_page.setFixedWidth(70)
        self.combo_per_page.currentTextChanged.connect(self.on_per_page_changed)
        left_box.addWidget(lbl_pp)
        left_box.addWidget(self.combo_per_page)

        center_box = QHBoxLayout()

        def create_nav_btn(text, callback):
            btn = QPushButton(text)
            btn.setObjectName("btn_nav")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            return btn

        self.btn_prev = create_nav_btn("◄ Önceki", self.prev_page)
        self.btn_next = create_nav_btn("Sonraki ►", self.next_page)

        self.lbl_page_info = QLabel("Sayfa 1 / 1")
        self.lbl_page_info.setStyleSheet(f"font-weight: 800; color: {COLORS['text_main']}; margin: 0 20px; font-size: 14px;")

        center_box.addWidget(self.btn_prev)
        center_box.addWidget(self.lbl_page_info)
        center_box.addWidget(self.btn_next)

        pagination_layout.addLayout(left_box, 0, 0, Qt.AlignLeft)
        pagination_layout.addLayout(center_box, 0, 1, Qt.AlignCenter)
        pagination_layout.addWidget(QWidget(), 0, 2)

        layout.addWidget(pagination_widget)

    def _get_combo_style(self):
        """Minimal Combobox: Buton ve ok yok, sadece metin."""
        return f"""
            QComboBox {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                color: {COLORS['text_main']};
                font-weight: 700;
                font-size: 14px;
                min-width: 60px;
            }}
            /* Üzerine gelince belirginleşsin */
            QComboBox:hover {{ 
                background-color: #F0F2F5; 
                color: {COLORS['primary']};
            }}
            
            /* Dropdown butonunu ve oku tamamen gizle */
            QComboBox::drop-down {{
                width: 0px;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            
            /* Açılan Liste */
            QComboBox QAbstractItemView {{
                background-color: white; 
                border: 1px solid {COLORS['border']}; 
                border-radius: 12px; 
                padding: 8px; 
                outline: none;
                min-width: 140px;
            }}
            QComboBox QAbstractItemView::item {{
                height: 36px; 
                padding-left: 15px; 
                color: {COLORS['text_main']};
                font-size: 14px;
                border-radius: 6px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary_light']}; 
                color: {COLORS['primary']};
                font-weight: bold;
            }}
        """

    def load_types(self):
        if hasattr(self.controller, 'get_all_activity_types'):
            self.controller.get_all_activity_types(self.on_types_loaded)

    def on_types_loaded(self, types):
        current_text = self.combo_filter_type.currentText()
        self.combo_filter_type.blockSignals(True)
        self.combo_filter_type.clear()
        self.combo_filter_type.addItem("Hepsi")
        if types:
            self.combo_filter_type.addItems(types)
        
        index = self.combo_filter_type.findText(current_text)
        if index >= 0: self.combo_filter_type.setCurrentIndex(index)
        self.combo_filter_type.blockSignals(False)

    def on_filter_changed(self):
        self.current_page = 1
        self.refresh_data()

    def on_per_page_changed(self, text):
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
        self.table.setSortingEnabled(False)
        
        type_filter = self.combo_filter_type.currentText()
        search_term = self.input_search.text()
        date_filter = self.date_widget.get_date_str()

        self.load_types()
        self.controller.get_all_activities(
            self.on_data_loaded,
            type_filter, search_term, date_filter, 
            page=self.current_page, 
            items_per_page=self.items_per_page
        )

    def on_data_loaded(self, result):
        if not result: return

        activities, total_count = result
        self.badge_total.setText(f"{total_count} Kayıt")
        
        self.total_pages = math.ceil(total_count / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        
        self.lbl_page_info.setText(f"Sayfa {self.current_page} / {self.total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

        self.table.setRowCount(0)
        for row_idx, activity in enumerate(activities):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 60) # Satır yüksekliği arttırıldı
            
            # 1. Tür (Badge Görünümü) - ORTALI
            type_text = activity.type.title() if activity.type else "-"
            item_type = QTableWidgetItem(type_text)
            item_type.setData(Qt.UserRole, activity.id)
            item_type.setTextAlignment(Qt.AlignCenter) # Ortala
            item_type.setFont(QFont("Segoe UI", 10, QFont.Bold)) # Font Büyüt
            item_type.setForeground(QBrush(QColor(COLORS['primary'])))
            self.table.setItem(row_idx, 0, item_type)
            
            # 2. Ad - ORTALI
            item_name = QTableWidgetItem(activity.name)
            item_name.setTextAlignment(Qt.AlignCenter) # Ortala
            item_name.setFont(QFont("Segoe UI", 10, QFont.DemiBold)) # Font Büyüt
            self.table.setItem(row_idx, 1, item_name)
            
            # 3. Tarih - ORTALI
            date_display = activity.date
            if activity.end_date:
                date_display = f"{activity.date}  ➜  {activity.end_date}"
            item_date = QTableWidgetItem(date_display)
            item_date.setTextAlignment(Qt.AlignCenter) # Ortala
            item_date.setFont(QFont("Segoe UI", 10)) # Font Büyüt
            item_date.setForeground(QBrush(QColor(COLORS['text_sub'])))
            self.table.setItem(row_idx, 2, item_date)
            
            # 4. Yorum - ORTALI (İsteğe bağlı, uzunsa sola yaslanabilir ama istek üzerine ortalandı)
            item_comment = QTableWidgetItem(activity.comment)
            item_comment.setTextAlignment(Qt.AlignCenter) # Ortala
            item_comment.setFont(QFont("Segoe UI", 10))
            item_comment.setForeground(QBrush(QColor(COLORS['text_sub'])))
            self.table.setItem(row_idx, 3, item_comment)
            
            # 5. Puan (Renkli) - ORTALI
            rating_display = str(activity.rating) if activity.rating > 0 else "-"
            rating_item = QTableWidgetItem(rating_display)
            rating_item.setTextAlignment(Qt.AlignCenter) # Ortala
            rating_item.setFont(QFont("Segoe UI", 11, QFont.Bold)) # Font Büyüt
            
            # Puan Renklendirme
            if activity.rating >= 8:
                rating_item.setForeground(QBrush(QColor("#27AE60"))) # Yeşil
            elif activity.rating >= 5:
                rating_item.setForeground(QBrush(QColor("#F39C12"))) # Turuncu
            elif activity.rating > 0:
                rating_item.setForeground(QBrush(QColor("#E74C3C"))) # Kırmızı
                
            self.table.setItem(row_idx, 4, rating_item)

        self.table.setSortingEnabled(True)

    def reset_filters(self):
        self.combo_filter_type.setCurrentIndex(0)
        self.input_search.clear()
        self.date_widget.clear_filters()
        self.current_page = 1
    
    def open_edit_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        activity_id = self.table.item(row_index, 0).data(Qt.UserRole)
        self.controller.get_activity(activity_id, self.on_activity_loaded_for_edit)

    def on_activity_loaded_for_edit(self, activity):
        if activity:
            dialog = EditDialog(self.controller, activity, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_data()

    def open_context_menu(self, position):
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{ background-color: white; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 5px; }}
            QMenu::item {{ padding: 8px 20px; font-size: 13px; color: {COLORS['text_main']}; }}
            QMenu::item:selected {{ background-color: {COLORS['primary_light']}; color: {COLORS['primary']}; border-radius: 4px; }}
        """)
        edit_action = menu.addAction("✏️ Düzenle")
        delete_action = menu.addAction("🗑️ Sil")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == delete_action:
            self.delete_selected_row()
        elif action == edit_action:
            self.open_edit_dialog()

    def delete_selected_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir satır seçin.")
            return

        row_index = selected_rows[0].row()
        activity_id = self.table.item(row_index, 0).data(Qt.UserRole)

        confirm = QMessageBox.question(self, "Onay", "Bu kaydı silmek istediğinize emin misiniz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.controller.delete_activity(activity_id, self.on_delete_finished)

    def on_delete_finished(self, result):
        success, msg = result
        if success:
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Hata", msg)