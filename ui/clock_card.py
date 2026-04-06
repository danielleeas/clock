from __future__ import annotations
import math
from typing import Callable, Optional

from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QDateTime, QTimeZone, QDate, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QCursor
from PySide6.QtWidgets import QApplication


class ClockCard(QFrame):
    """
    One timezone clock card.

    Supports two display modes:
      - Grid mode (default): stacked vertical layout with large time.
      - List mode: compact horizontal strip.

    Drag-to-reorder is handled via callbacks set by DragContainer:
      on_drag_start(card, global_pos)
      on_drag_move(card, global_pos)
      on_drag_end(card, global_pos)
    """

    def __init__(
        self,
        label: str,
        tz_id: str,
        on_remove: Callable[["ClockCard"], None],
        on_drag_start: Optional[Callable] = None,
        on_drag_move: Optional[Callable] = None,
        on_drag_end: Optional[Callable] = None,
        use_24h: bool = True,
        show_seconds: bool = True,
        list_mode: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.card_label = label
        self.tz_id = tz_id
        self._timezone = QTimeZone(tz_id.encode())
        self._on_remove = on_remove
        self._on_drag_start = on_drag_start
        self._on_drag_move = on_drag_move
        self._on_drag_end = on_drag_end
        self._use_24h = use_24h
        self._show_seconds = show_seconds
        self._list_mode = list_mode

        self._drag_start: Optional[QPoint] = None
        self._dragging: bool = False

        self._is_home = self._detect_home()

        self._build_ui()
        self.set_list_mode(list_mode)

    # ── Detection helpers ────────────────────────────────────────────────────

    def _detect_home(self) -> bool:
        sys_id = QTimeZone.systemTimeZoneId()
        return sys_id.data().decode() == self.tz_id

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        """Build both grid and list layouts; show the appropriate one."""
        # ── Grid layout ──────────────────────────────────────────────────────
        self._grid_widget = QWidget()
        gv = QVBoxLayout(self._grid_widget)
        gv.setContentsMargins(14, 10, 14, 12)
        gv.setSpacing(2)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(6)

        self._drag_handle_g = QLabel("⠿")
        self._drag_handle_g.setObjectName("DragHandle")
        self._drag_handle_g.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

        self._city_label_g = QLabel(self.card_label)
        self._city_label_g.setObjectName("CityLabel")

        self._home_badge_g = QLabel("HOME")
        self._home_badge_g.setObjectName("BadgeHome")
        self._home_badge_g.setVisible(self._is_home)

        self._remove_btn_g = QPushButton("×")
        self._remove_btn_g.setObjectName("RemoveBtn")
        self._remove_btn_g.setToolTip("Remove clock")
        self._remove_btn_g.clicked.connect(lambda: self._on_remove(self))

        header.addWidget(self._drag_handle_g)
        header.addWidget(self._city_label_g)
        header.addWidget(self._home_badge_g)
        header.addStretch()
        header.addWidget(self._remove_btn_g)

        # Time
        self._time_label_g = QLabel("--:--:--")
        self._time_label_g.setObjectName("TimeLabel")
        self._time_label_g.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Day offset badge row
        day_row = QHBoxLayout()
        day_row.setSpacing(6)
        self._day_badge_g = QLabel()
        self._day_badge_g.setVisible(False)
        self._date_label_g = QLabel("---")
        self._date_label_g.setObjectName("DateLabel")
        day_row.addWidget(self._day_badge_g)
        day_row.addWidget(self._date_label_g)
        day_row.addStretch()

        # UTC offset
        self._offset_label_g = QLabel("")
        self._offset_label_g.setObjectName("OffsetLabel")

        gv.addLayout(header)
        gv.addSpacing(4)
        gv.addWidget(self._time_label_g)
        gv.addLayout(day_row)
        gv.addStretch()
        gv.addWidget(self._offset_label_g)

        # ── List layout ──────────────────────────────────────────────────────
        self._list_widget = QWidget()
        lv = QHBoxLayout(self._list_widget)
        lv.setContentsMargins(12, 8, 12, 8)
        lv.setSpacing(12)

        self._drag_handle_l = QLabel("⠿")
        self._drag_handle_l.setObjectName("DragHandle")
        self._drag_handle_l.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

        self._city_label_l = QLabel(self.card_label)
        self._city_label_l.setObjectName("CityLabel")
        self._city_label_l.setMinimumWidth(120)

        self._home_badge_l = QLabel("HOME")
        self._home_badge_l.setObjectName("BadgeHome")
        self._home_badge_l.setVisible(self._is_home)

        self._time_label_l = QLabel("--:--:--")
        self._time_label_l.setObjectName("TimeLabelList")
        self._time_label_l.setMinimumWidth(130)

        self._day_badge_l = QLabel()
        self._day_badge_l.setVisible(False)

        self._date_label_l = QLabel("---")
        self._date_label_l.setObjectName("DateLabel")
        self._date_label_l.setMinimumWidth(160)

        self._offset_label_l = QLabel("")
        self._offset_label_l.setObjectName("OffsetLabel")
        self._offset_label_l.setMinimumWidth(80)

        self._remove_btn_l = QPushButton("×")
        self._remove_btn_l.setObjectName("RemoveBtn")
        self._remove_btn_l.setToolTip("Remove clock")
        self._remove_btn_l.clicked.connect(lambda: self._on_remove(self))

        lv.addWidget(self._drag_handle_l)
        lv.addWidget(self._city_label_l)
        lv.addWidget(self._home_badge_l)
        lv.addStretch()
        lv.addWidget(self._time_label_l)
        lv.addWidget(self._day_badge_l)
        lv.addWidget(self._date_label_l)
        lv.addWidget(self._offset_label_l)
        lv.addWidget(self._remove_btn_l)

        # Outer wrapper
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._grid_widget)
        outer.addWidget(self._list_widget)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_format(self, use_24h: bool, show_seconds: bool) -> None:
        self._use_24h = use_24h
        self._show_seconds = show_seconds

    def set_list_mode(self, enabled: bool) -> None:
        self._list_mode = enabled
        if enabled:
            self.setObjectName("ClockCardList")
            self.setMinimumHeight(0)
            self.setMaximumHeight(16_777_215)
            self._grid_widget.setVisible(False)
            self._list_widget.setVisible(True)
        else:
            self.setObjectName("ClockCard")
            self.setMinimumSize(200, 150)
            self.setMaximumHeight(16_777_215)
            self._grid_widget.setVisible(True)
            self._list_widget.setVisible(False)
        # Re-polish so stylesheet re-evaluates object name
        self.style().unpolish(self)
        self.style().polish(self)

    def set_drop_target(self, active: bool) -> None:
        self.setProperty("drop_target", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_dragging(self, active: bool) -> None:
        self.setProperty("dragging", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def tick(self) -> None:
        """Refresh displayed time. Called every second."""
        now = QDateTime.currentDateTimeUtc().toTimeZone(self._timezone)

        fmt = self._time_format()
        self._time_label_g.setText(now.toString(fmt))
        self._time_label_l.setText(now.toString(fmt))

        date_str = now.toString("ddd, MMM d yyyy")
        self._date_label_g.setText(date_str)
        self._date_label_l.setText(date_str)

        offset = self._fmt_offset(now)
        self._offset_label_g.setText(offset)
        self._offset_label_l.setText(offset)

        self._update_day_badge(now)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _time_format(self) -> str:
        if self._use_24h:
            return "HH:mm:ss" if self._show_seconds else "HH:mm"
        return "hh:mm:ss AP" if self._show_seconds else "hh:mm AP"

    def _fmt_offset(self, now: QDateTime) -> str:
        secs = self._timezone.offsetFromUtc(now)
        h, rem = divmod(abs(secs), 3600)
        m = rem // 60
        sign = "+" if secs >= 0 else "−"
        return f"UTC {sign}{h:02d}:{m:02d}"

    def _update_day_badge(self, now: QDateTime) -> None:
        local_date = QDate.currentDate()
        card_date = now.date()
        diff = local_date.daysTo(card_date)

        if diff == 0:
            for badge in (self._day_badge_g, self._day_badge_l):
                badge.setVisible(False)
            return

        if diff == 1:
            text, name = "+1 Tomorrow", "BadgeTomorrow"
        elif diff == -1:
            text, name = "−1 Yesterday", "BadgeYesterday"
        elif diff > 0:
            text, name = f"+{diff} days", "BadgeTomorrow"
        else:
            text, name = f"{diff} days", "BadgeYesterday"

        for badge in (self._day_badge_g, self._day_badge_l):
            badge.setText(text)
            badge.setObjectName(name)
            badge.style().unpolish(badge)
            badge.style().polish(badge)
            badge.setVisible(True)

    # ── Mouse events (drag) ───────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
            self._dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._drag_start is None:
            return
        delta = event.position().toPoint() - self._drag_start
        if not self._dragging and delta.manhattanLength() >= QApplication.startDragDistance():
            self._dragging = True
            self.grabMouse()
            if self._on_drag_start:
                self._on_drag_start(self, event.globalPosition().toPoint())
        if self._dragging and self._on_drag_move:
            self._on_drag_move(self, event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.releaseMouse()
            self._dragging = False
            if self._on_drag_end:
                self._on_drag_end(self, event.globalPosition().toPoint())
        self._drag_start = None
        super().mouseReleaseEvent(event)
