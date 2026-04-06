from __future__ import annotations
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem,
    QDialogButtonBox, QPushButton
)
from PySide6.QtCore import Qt, QTimeZone

from data.timezones import ALL_ZONES, POPULAR_ZONES


class AddClockDialog(QDialog):
    """
    Searchable timezone picker.

    Shows popular timezones first, followed by all IANA zones.
    The search box filters by zone ID or display name in real-time.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Clock")
        self.setMinimumSize(420, 520)
        self.setModal(True)
        self._build_ui()
        self._populate()
        self._list.setFocus()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search timezone or city…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._filter)
        layout.addWidget(self._search)

        # List
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self.accept)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

        # Label row
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Display name:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Leave blank to use city name")
        name_row.addWidget(self._name_input)
        layout.addLayout(name_row)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _populate(self):
        # ── Popular section ──────────────────────────────────────────────────
        sep = QListWidgetItem("── Popular ──")
        sep.setFlags(Qt.ItemFlag.NoItemFlags)
        sep.setForeground(Qt.GlobalColor.gray)
        self._list.addItem(sep)

        popular_ids = {tz_id for _, tz_id in POPULAR_ZONES}
        for display, tz_id in POPULAR_ZONES:
            item = QListWidgetItem(f"  {display}  ({tz_id})")
            item.setData(Qt.ItemDataRole.UserRole, tz_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, display)
            self._list.addItem(item)

        # ── All zones section ────────────────────────────────────────────────
        sep2 = QListWidgetItem("── All timezones ──")
        sep2.setFlags(Qt.ItemFlag.NoItemFlags)
        sep2.setForeground(Qt.GlobalColor.gray)
        self._list.addItem(sep2)

        for tz_id in ALL_ZONES:
            if tz_id in popular_ids:
                continue
            item = QListWidgetItem(f"  {tz_id}")
            item.setData(Qt.ItemDataRole.UserRole, tz_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, "")
            self._list.addItem(item)

        # Select first real item
        self._select_first_valid()

    # ── Interaction ───────────────────────────────────────────────────────────

    def _filter(self, text: str):
        q = text.strip().lower()
        first_visible = None

        for i in range(self._list.count()):
            item = self._list.item(i)
            if not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                item.setHidden(bool(q))  # hide section headers when searching
                continue
            match = q in item.text().lower()
            item.setHidden(not match)
            if match and first_visible is None:
                first_visible = item

        if first_visible:
            self._list.setCurrentItem(first_visible)
            self._list.scrollToItem(first_visible)
        else:
            self._list.clearSelection()

    def _on_selection_changed(self, current: Optional[QListWidgetItem], _prev):
        if current is None:
            return
        # Auto-fill name field if user hasn't typed anything
        if self._name_input.text() == "":
            preferred = current.data(Qt.ItemDataRole.UserRole + 1)
            if not preferred:
                tz_id = current.data(Qt.ItemDataRole.UserRole) or ""
                preferred = tz_id.split("/")[-1].replace("_", " ")
            self._name_input.setPlaceholderText(preferred)

    def _select_first_valid(self):
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsEnabled and not item.isHidden():
                self._list.setCurrentItem(item)
                return

    # ── Result ────────────────────────────────────────────────────────────────

    def get_result(self) -> Optional[Tuple[str, str]]:
        """Returns (label, tz_id) or None if nothing valid is selected."""
        item = self._list.currentItem()
        if item is None or item.isHidden():
            return None
        tz_id = item.data(Qt.ItemDataRole.UserRole)
        if not tz_id:
            return None

        label = self._name_input.text().strip()
        if not label:
            label = self._name_input.placeholderText().strip()
        if not label:
            label = tz_id.split("/")[-1].replace("_", " ")

        return label, tz_id
