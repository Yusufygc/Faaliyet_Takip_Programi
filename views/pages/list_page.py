# views/pages/list_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
                             QMenu, QDialog, QGridLayout, QGraphicsDropShadowEffect,
                             QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QBrush, QPalette
import math

from views.widgets import MonthYearWidget
from views.widgets.styled_combo import StyledComboBox
from views.widgets.table_utils import configure_table
from views.widgets.empty_state import EmptyStateWidget
from views.widgets.html_delegate import HtmlDelegate
from views.widgets.media_card import MediaCard
from views.widgets.toast_notification import show_toast
from views.dialogs.edit_dialog import EditDialog
from utils_markdown import md_to_html


class ListPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self._view_mode = "list"
        self._last_activities = []

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.interval = 300
        self.search_timer.timeout.connect(self.on_filter_changed)

        self.init_ui()

    def init_ui(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#F8FAFC"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self._build_header(layout)
        self._build_filter(layout)
        self._build_content_area(layout)
        self._build_pagination(layout)

        self.load_types()
        self.refresh_data()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, layout):
        header_layout = QHBoxLayout()

        title = QLabel("Faaliyet Listesi")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #1E293B; letter-spacing: 0.5px;")

        self.badge_total = QLabel("0 Kayıt")
        self.badge_total.setStyleSheet("""
            background-color: #EFF6FF;
            color: #3B82F6;
            font-weight: bold;
            padding: 6px 15px;
            border-radius: 16px;
            font-size: 14px;
        """)

        self.btn_view_list = QPushButton("☰ Liste")
        self.btn_view_list.setCheckable(True)
        self.btn_view_list.setChecked(True)
        self.btn_view_list.setCursor(Qt.PointingHandCursor)
        self.btn_view_list.setFixedHeight(36)
        self.btn_view_list.clicked.connect(lambda: self._set_view("list"))

        self.btn_view_grid = QPushButton("⊞ Grid")
        self.btn_view_grid.setCheckable(True)
        self.btn_view_grid.setCursor(Qt.PointingHandCursor)
        self.btn_view_grid.setFixedHeight(36)
        self.btn_view_grid.clicked.connect(lambda: self._set_view("grid"))

        self._apply_toggle_styles()

        header_layout.addWidget(title)
        header_layout.addSpacing(15)
        header_layout.addWidget(self.badge_total)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_view_list)
        header_layout.addWidget(self.btn_view_grid)

        layout.addLayout(header_layout)

    def _apply_toggle_styles(self):
        active_style = """
            QPushButton {
                background: #3B82F6; color: white; border: none;
                border-radius: 8px; padding: 0 16px; font-weight: 700; font-size: 13px;
            }
        """
        inactive_style = """
            QPushButton {
                background: white; color: #64748B;
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 0 16px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #F8FAFC; }
        """
        self.btn_view_list.setStyleSheet(active_style if self._view_mode == "list" else inactive_style)
        self.btn_view_grid.setStyleSheet(active_style if self._view_mode == "grid" else inactive_style)

    # ── Filter ────────────────────────────────────────────────────────────────

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
        lbl_type.setStyleSheet("font-weight: 700; color: #64748B; font-size: 14px; border: none;")
        self.combo_filter_type = StyledComboBox()
        self.combo_filter_type.addItem("Hepsi")
        self.combo_filter_type.setMinimumWidth(140)
        self.combo_filter_type.currentIndexChanged.connect(self.on_filter_changed)

        lbl_date = QLabel("Tarih:")
        lbl_date.setStyleSheet("font-weight: 700; color: #64748B; font-size: 14px; border: none;")
        self.date_widget = MonthYearWidget()
        self.date_widget.dateChanged.connect(self.on_filter_changed)

        lbl_search = QLabel("Ara:")
        lbl_search.setStyleSheet("font-weight: 700; color: #64748B; font-size: 14px; border: none;")
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Faaliyet adı ile ara...")
        self.input_search.setClearButtonEnabled(True)
        self.input_search.textChanged.connect(lambda: self.search_timer.start())

        btn_clear = QPushButton("Temizle")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setFixedWidth(100)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #FDEDEC; color: #E74C3C; border: none; border-radius: 8px;
                padding: 10px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #FADBD8; }
        """)
        btn_clear.clicked.connect(self.reset_filters)

        def _divider():
            line = QFrame()
            line.setFixedWidth(1)
            line.setFixedHeight(20)
            line.setStyleSheet("background: #E2E8F0;")
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

    # ── Content area ──────────────────────────────────────────────────────────

    def _build_content_area(self, layout):
        # Empty state
        self.empty_state = EmptyStateWidget(
            icon_name="inbox",
            title="Henüz faaliyet bulunmuyor",
            description="Filtreyi değiştir veya yeni kayıt ekle.",
            action_text="Yeni Kayıt Ekle",
            action_page_index=0,
        )
        self.empty_state.hide()
        layout.addWidget(self.empty_state)

        # Table (list mode)
        self._build_table_container(layout)

        # Grid (grid mode)
        self._build_grid_container(layout)

    def _build_table_container(self, layout):
        self.table_container = QFrame()
        self.table_container.setObjectName("card")
        t_shadow = QGraphicsDropShadowEffect()
        t_shadow.setBlurRadius(20)
        t_shadow.setColor(QColor(0, 0, 0, 8))
        t_shadow.setOffset(0, 4)
        self.table_container.setGraphicsEffect(t_shadow)

        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["TÜR", "FAALİYET ADI", "TARİH", "YORUM", "PUAN"])
        configure_table(self.table, row_height=52, resize_to_contents_cols=[0, 4])

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setFixedHeight(50)

        # Markdown delegate for comment column
        self._html_delegate = HtmlDelegate(self.table, elide_lines=2)
        self.table.setItemDelegateForColumn(3, self._html_delegate)

        self.table.doubleClicked.connect(self.open_edit_dialog)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        table_layout.addWidget(self.table)
        layout.addWidget(self.table_container)

    def _build_grid_container(self, layout):
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_scroll.setFrameShape(QFrame.NoFrame)
        self.grid_scroll.setStyleSheet("QScrollArea { background: transparent; }")

        grid_inner = QWidget()
        grid_inner.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(grid_inner)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.grid_scroll.setWidget(grid_inner)
        self.grid_scroll.hide()
        layout.addWidget(self.grid_scroll)

    # ── Pagination ────────────────────────────────────────────────────────────

    def _build_pagination(self, layout):
        pagination_widget = QWidget()
        pagination_layout = QGridLayout(pagination_widget)
        pagination_layout.setContentsMargins(10, 5, 10, 0)

        left_box = QHBoxLayout()
        lbl_pp = QLabel("Sayfa başına:")
        lbl_pp.setStyleSheet("color: #64748B; font-weight: bold; font-size: 13px;")
        self.combo_per_page = StyledComboBox()
        self.combo_per_page.addItems(["15", "30", "50", "100"])
        self.combo_per_page.setProperty("variant", "flat")
        self.combo_per_page.setFixedWidth(85)
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
        self.lbl_page_info.setStyleSheet("font-weight: 800; color: #1E293B; margin: 0 20px; font-size: 14px;")

        center_box.addWidget(self.btn_prev)
        center_box.addWidget(self.lbl_page_info)
        center_box.addWidget(self.btn_next)

        pagination_layout.addLayout(left_box, 0, 0, Qt.AlignLeft)
        pagination_layout.addLayout(center_box, 0, 1, Qt.AlignCenter)
        pagination_layout.addWidget(QWidget(), 0, 2)

        layout.addWidget(pagination_widget)

    # ── View toggle ───────────────────────────────────────────────────────────

    def _set_view(self, mode: str):
        if mode == self._view_mode:
            return
        self._view_mode = mode
        self._apply_toggle_styles()
        has_data = self.table.rowCount() > 0

        if has_data:
            self.table_container.setVisible(mode == "list")
            self.grid_scroll.setVisible(mode == "grid")
            if mode == "grid":
                self._fill_grid(self._last_activities)

    # ── Type loading ──────────────────────────────────────────────────────────

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
        if index >= 0:
            self.combo_filter_type.setCurrentIndex(index)
        self.combo_filter_type.blockSignals(False)

    # ── Filters ───────────────────────────────────────────────────────────────

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
            items_per_page=self.items_per_page,
        )

    # ── Data loaded ───────────────────────────────────────────────────────────

    def on_data_loaded(self, result):
        if not result:
            return

        activities, total_count = result
        self._last_activities = activities

        self.badge_total.setText(f"{total_count} Kayıt")

        self.total_pages = math.ceil(total_count / self.items_per_page)
        if self.total_pages == 0:
            self.total_pages = 1

        self.lbl_page_info.setText(f"Sayfa {self.current_page} / {self.total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

        has_data = bool(activities)
        self.empty_state.setVisible(not has_data)
        self.table_container.setVisible(has_data and self._view_mode == "list")
        self.grid_scroll.setVisible(has_data and self._view_mode == "grid")

        if has_data:
            self._fill_table(activities)
            if self._view_mode == "grid":
                self._fill_grid(activities)

    def _fill_table(self, activities):
        self.table.setRowCount(0)
        for row_idx, activity in enumerate(activities):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 60)

            # Tür
            type_text = activity.type.title() if activity.type else "-"
            item_type = QTableWidgetItem(type_text)
            item_type.setData(Qt.UserRole, activity.id)
            item_type.setTextAlignment(Qt.AlignCenter)
            item_type.setFont(QFont("Segoe UI", 10, QFont.Bold))
            item_type.setForeground(QBrush(QColor("#3B82F6")))
            self.table.setItem(row_idx, 0, item_type)

            # Ad
            item_name = QTableWidgetItem(activity.name)
            item_name.setTextAlignment(Qt.AlignCenter)
            item_name.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
            self.table.setItem(row_idx, 1, item_name)

            # Tarih
            date_display = activity.date
            if activity.end_date:
                date_display = f"{activity.date}  ➜  {activity.end_date}"
            item_date = QTableWidgetItem(date_display)
            item_date.setTextAlignment(Qt.AlignCenter)
            item_date.setFont(QFont("Segoe UI", 10))
            item_date.setForeground(QBrush(QColor("#64748B")))
            self.table.setItem(row_idx, 2, item_date)

            # Yorum (HTML/Markdown)
            html = md_to_html(activity.comment or "")
            item_comment = QTableWidgetItem(html)
            item_comment.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row_idx, 3, item_comment)

            # Puan
            rating_display = str(activity.rating) if activity.rating > 0 else "-"
            rating_item = QTableWidgetItem(rating_display)
            rating_item.setTextAlignment(Qt.AlignCenter)
            rating_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            if activity.rating >= 8:
                rating_item.setForeground(QBrush(QColor("#27AE60")))
            elif activity.rating >= 5:
                rating_item.setForeground(QBrush(QColor("#F39C12")))
            elif activity.rating > 0:
                rating_item.setForeground(QBrush(QColor("#E74C3C")))
            self.table.setItem(row_idx, 4, rating_item)

        self.table.setSortingEnabled(True)

    def _fill_grid(self, activities):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 4
        for idx, activity in enumerate(activities):
            card = MediaCard(activity, self)
            card.edit_requested.connect(self._open_edit_by_id)
            self.grid_layout.addWidget(card, idx // cols, idx % cols)

    # ── Edit / Delete ─────────────────────────────────────────────────────────

    def reset_filters(self):
        self.combo_filter_type.setCurrentIndex(0)
        self.input_search.clear()
        self.date_widget.clear_filters()
        self.current_page = 1

    def _open_edit_by_id(self, activity_id: int):
        self.controller.get_activity(activity_id, self.on_activity_loaded_for_edit)

    def open_edit_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
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
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 5px; }
            QMenu::item { padding: 8px 20px; font-size: 13px; color: #1E293B; }
            QMenu::item:selected { background-color: #EFF6FF; color: #3B82F6; border-radius: 4px; }
        """)
        from PyQt5.QtWidgets import QAction
        from services.icon_service import IconService
        edit_action = QAction("Düzenle", menu)
        edit_action.setIcon(IconService.get("edit", "#2980B9"))
        menu.addAction(edit_action)
        delete_action = QAction("Sil", menu)
        delete_action.setIcon(IconService.get("delete"))
        menu.addAction(delete_action)

        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if action == delete_action:
            self.delete_selected_row()
        elif action == edit_action:
            self.open_edit_dialog()

    def delete_selected_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            show_toast("Silmek için bir satır seçin.", "warning")
            return

        row_index = selected_rows[0].row()
        activity_id = self.table.item(row_index, 0).data(Qt.UserRole)

        confirm = QMessageBox.question(
            self, "Onay", "Bu kaydı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.controller.delete_activity(activity_id, self.on_delete_finished)

    def on_delete_finished(self, result):
        success, msg = result
        if success:
            self.refresh_data()
            show_toast("Kayıt başarıyla silindi.", "success")
        else:
            show_toast(msg, "error")
