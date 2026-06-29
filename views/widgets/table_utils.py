# views/widgets/table_utils.py
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt


def configure_table(
    table: QTableWidget,
    *,
    row_height: int = 52,
    resize_to_contents_cols: list | None = None,
    selection_behavior: QAbstractItemView.SelectionBehavior = QAbstractItemView.SelectRows,
) -> None:
    """Apply modern, consistent defaults to a QTableWidget.

    Call after setColumnCount() but before populating rows.
    The global tables.qss handles all visual styling; this sets behavioral defaults.

    Args:
        row_height: Default row height in pixels.
        resize_to_contents_cols: Column indices to use ResizeToContents mode
            instead of Stretch. All other columns remain Stretch.
        selection_behavior: SelectRows (default) or SelectItems for cell-level selection.
    """
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    for col in (resize_to_contents_cols or []):
        header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(row_height)
    table.setShowGrid(False)
    table.setAlternatingRowColors(False)
    table.setSelectionBehavior(selection_behavior)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setFocusPolicy(Qt.NoFocus)
