from __future__ import annotations
from typing import Optional, Callable, List, Dict

from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor

from ui.clock_card import ClockCard
from app.persistence import save_clocks


class DragContainer(QWidget):
    """
    Owns the ordered list of ClockCards and handles:
      - Grid / list layout reflow
      - Drag-to-reorder via mouse grab (no QDrag)
      - Persistence (saves on every mutation)

    The container does NOT own QTimer — the parent window ticks all cards.
    """

    def __init__(self, on_mutated: Optional[Callable] = None, parent=None):
        super().__init__(parent)
        self._cards: List[ClockCard] = []
        self._on_mutated = on_mutated  # called after add/remove/reorder

        self._list_mode = False
        self._use_24h = True
        self._show_seconds = True

        # Drag state
        self._drag_card: Optional[ClockCard] = None
        self._ghost: Optional[QLabel] = None
        self._drop_idx: int = -1

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Inner widget that holds the actual card layout
        self._inner = QWidget()
        self._inner.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._layout.addWidget(self._inner)
        self._layout.addStretch()

        self._inner_layout: Optional[QGridLayout | QVBoxLayout] = None
        self._rebuild_inner_layout()

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def cards(self) -> List[ClockCard]:
        return list(self._cards)

    def add_card(self, label: str, tz_id: str) -> ClockCard:
        card = ClockCard(
            label=label,
            tz_id=tz_id,
            on_remove=self._remove_card,
            on_drag_start=self._begin_drag,
            on_drag_move=self._update_drag,
            on_drag_end=self._end_drag,
            use_24h=self._use_24h,
            show_seconds=self._show_seconds,
            list_mode=self._list_mode,
        )
        self._cards.append(card)
        self._reflow()
        self._persist()
        if self._on_mutated:
            self._on_mutated()
        return card

    def set_format(self, use_24h: bool, show_seconds: bool):
        self._use_24h = use_24h
        self._show_seconds = show_seconds
        for card in self._cards:
            card.set_format(use_24h, show_seconds)

    def set_list_mode(self, enabled: bool):
        self._list_mode = enabled
        for card in self._cards:
            card.set_list_mode(enabled)
        self._rebuild_inner_layout()
        self._reflow()

    def tick_all(self):
        for card in self._cards:
            card.tick()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _rebuild_inner_layout(self):
        # Clear the inner widget
        old = self._inner.layout()
        if old:
            while old.count():
                old.takeAt(0)
            old.deleteLater()

        if self._list_mode:
            lv = QVBoxLayout(self._inner)
            lv.setContentsMargins(0, 0, 0, 0)
            lv.setSpacing(6)
            self._inner_layout = lv
        else:
            gv = QGridLayout(self._inner)
            gv.setContentsMargins(0, 0, 0, 0)
            gv.setSpacing(12)
            gv.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self._inner_layout = gv

    def _reflow(self):
        layout = self._inner_layout
        if layout is None:
            return

        # Remove all cards from layout (don't delete them)
        for card in self._cards:
            layout.removeWidget(card)
            card.setParent(None)  # type: ignore[arg-type]

        if self._list_mode:
            for card in self._cards:
                layout.addWidget(card)  # type: ignore[attr-defined]
        else:
            cols = self._column_count()
            for i, card in enumerate(self._cards):
                row, col = divmod(i, cols)
                layout.addWidget(card, row, col)  # type: ignore[attr-defined]

        # Re-parent cards to inner
        for card in self._cards:
            card.setParent(self._inner)
            card.show()

    def _column_count(self) -> int:
        w = self.width() or 800
        return max(1, w // 250)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._list_mode:
            self._reflow()

    # ── Remove ────────────────────────────────────────────────────────────────

    def _remove_card(self, card: ClockCard):
        if card not in self._cards:
            return
        self._cards.remove(card)
        card.setParent(None)  # type: ignore[arg-type]
        card.deleteLater()
        self._reflow()
        self._persist()
        if self._on_mutated:
            self._on_mutated()

    # ── Drag logic ────────────────────────────────────────────────────────────

    def _begin_drag(self, card: ClockCard, global_pos: QPoint):
        self._drag_card = card
        card.set_dragging(True)

        # Create floating ghost
        px = card.grab()
        ghost_px = QPixmap(px.size())
        ghost_px.fill(QColor(0, 0, 0, 0))
        painter = QPainter(ghost_px)
        painter.setOpacity(0.70)
        painter.drawPixmap(0, 0, px)
        painter.end()

        self._ghost = QLabel()
        self._ghost.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self._ghost.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._ghost.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._ghost.setPixmap(ghost_px)
        self._ghost.resize(card.size())
        self._ghost.move(
            global_pos.x() - card.width() // 2,
            global_pos.y() - card.height() // 2,
        )
        self._ghost.show()

    def _update_drag(self, card: ClockCard, global_pos: QPoint):
        if self._ghost:
            self._ghost.move(
                global_pos.x() - card.width() // 2,
                global_pos.y() - card.height() // 2,
            )

        # Find and highlight drop target
        local_pos = self._inner.mapFromGlobal(global_pos)
        new_drop_idx = self._find_drop_index(local_pos)

        if new_drop_idx != self._drop_idx:
            # Clear previous highlight
            if 0 <= self._drop_idx < len(self._cards):
                self._cards[self._drop_idx].set_drop_target(False)
            self._drop_idx = new_drop_idx
            # Highlight new target
            tgt = new_drop_idx if new_drop_idx < len(self._cards) else len(self._cards) - 1
            if 0 <= tgt < len(self._cards) and self._cards[tgt] is not card:
                self._cards[tgt].set_drop_target(True)

    def _end_drag(self, card: ClockCard, global_pos: QPoint):
        # Destroy ghost
        if self._ghost:
            self._ghost.deleteLater()
            self._ghost = None

        # Clear highlights
        for c in self._cards:
            c.set_drop_target(False)
            c.set_dragging(False)

        local_pos = self._inner.mapFromGlobal(global_pos)
        new_idx = self._find_drop_index(local_pos)

        src_idx = self._cards.index(card)
        if new_idx != src_idx and new_idx != src_idx + 1:
            self._cards.pop(src_idx)
            # Adjust insertion point after removal
            insert_at = new_idx if new_idx <= src_idx else new_idx - 1
            self._cards.insert(insert_at, card)
            self._persist()

        self._drag_card = None
        self._drop_idx = -1
        self._reflow()

    def _find_drop_index(self, pos: QPoint) -> int:
        """Return insertion index (0..len) based on local position in _inner."""
        for i, card in enumerate(self._cards):
            if card is self._drag_card:
                continue
            geom = card.geometry()
            cy = geom.center().y()
            cx = geom.center().x()
            # Above this card's row → insert before it
            if pos.y() < geom.top():
                return i
            # Same row, left of centre → insert before it
            if geom.top() <= pos.y() <= geom.bottom() and pos.x() < cx:
                return i
        return len(self._cards)

    # ── Persistence ───────────────────────────────────────────────────────────

    def _persist(self):
        save_clocks([{"label": c.card_label, "tz_id": c.tz_id} for c in self._cards])
