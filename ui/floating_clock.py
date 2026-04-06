from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QDialog, QPushButton, QApplication
)
from PySide6.QtCore import Qt, QTimer, QDateTime, QTimeZone, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont

from app.persistence import load_clocks
from app.settings import AppSettings


# ── Opacity control dialog ────────────────────────────────────────────────────

class _OpacityDialog(QDialog):
    opacity_changed = Signal(float)

    def __init__(self, current_opacity: float, parent: QWidget | None = None):
        super().__init__(
            parent,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowTitle("Opacity")
        self.setModal(False)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QDialog {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QLabel {
                color: #e6edf3;
                font-size: 12px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #30363d;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: #58a6ff;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #58a6ff;
                border-radius: 2px;
            }
            QPushButton {
                background: #21262d;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.addWidget(QLabel("Transparency"))
        header.addStretch()
        close = QLabel("✕")
        close.setStyleSheet("color: #8b949e; font-size: 13px;")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.mousePressEvent = lambda _: self.close()
        header.addWidget(close)
        layout.addLayout(header)

        self._pct_label = QLabel(f"{int(current_opacity * 100)}%")
        self._pct_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._pct_label.setStyleSheet("color: #58a6ff; font-size: 12px;")

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(20, 100)
        self._slider.setValue(int(current_opacity * 100))
        self._slider.valueChanged.connect(self._on_change)

        row = QHBoxLayout()
        row.addWidget(QLabel("20%"))
        row.addWidget(self._slider, 1)
        row.addWidget(QLabel("100%"))

        layout.addLayout(row)
        layout.addWidget(self._pct_label)

        done = QPushButton("Done")
        done.clicked.connect(self.close)
        layout.addWidget(done)

    def _on_change(self, value: int):
        self._pct_label.setText(f"{value}%")
        self.opacity_changed.emit(value / 100.0)


# ── Floating clock window ─────────────────────────────────────────────────────

class FloatingClock(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(
            parent,
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool                    # no taskbar entry
            | Qt.WindowType.WindowTransparentForInput,  # click-through
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._settings = AppSettings.load()
        self._clocks: list[dict] = []
        self._tzones: list[QTimeZone] = []
        self._rows: list[tuple[QLabel, QLabel]] = []  # (label_widget, time_widget)

        self._build_shell()
        self.refresh_clocks()
        self._start_timer()
        self.setWindowOpacity(self._settings.float_opacity)

    # ── Shell (title bar + clock area) ────────────────────────────────────────

    def _build_shell(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Title bar ────────────────────────────────────────────────────────
        title_bar = QWidget()
        title_bar.setObjectName("FTitle")
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("""
            #FTitle {
                background: transparent;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        tb = QHBoxLayout(title_bar)
        tb.setContentsMargins(12, 0, 8, 0)
        tb.setSpacing(4)

        app_label = QLabel("⏱  World Clock")
        app_label.setStyleSheet("color: #8b949e; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")

        tb.addWidget(app_label)
        tb.addStretch()

        # opacity button
        opacity_btn = QLabel("◑")
        opacity_btn.setToolTip("Adjust transparency")
        opacity_btn.setStyleSheet("color: #8b949e; font-size: 13px; padding: 2px 4px;")
        opacity_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        opacity_btn.mousePressEvent = lambda _: self._open_opacity_dialog()

        close_btn = QLabel("✕")
        close_btn.setToolTip("Close floating clock")
        close_btn.setStyleSheet("color: #8b949e; font-size: 13px; padding: 2px 6px;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda _: self.hide()

        for w in (opacity_btn, close_btn):
            tb.addWidget(w)

        # ── Clock list area ───────────────────────────────────────────────────
        self._body = QWidget()
        self._body.setStyleSheet("background: transparent;")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(16, 6, 16, 14)
        self._body_layout.setSpacing(10)

        outer.addWidget(title_bar)
        outer.addWidget(self._body)

    def _clear_rows(self):
        for lbl, tim in self._rows:
            lbl.deleteLater()
            tim.deleteLater()
        self._rows.clear()
        # remove separator spacer items too
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

    def _delete_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh_clocks(self):
        """Reload clock list from disk and rebuild rows."""
        self._clear_rows()
        self._clocks = load_clocks()
        self._tzones = [QTimeZone(c["tz_id"].encode()) for c in self._clocks]

        for i, entry in enumerate(self._clocks):
            tz = self._tzones[i]
            if not tz.isValid():
                continue

            row = QHBoxLayout()
            row.setSpacing(0)

            lbl = QLabel(entry["label"])
            lbl.setStyleSheet(
                "color: #8b949e; font-size: 16px; font-family: 'Segoe UI','Ubuntu',sans-serif;"
            )
            lbl.setFixedWidth(130)

            tim = QLabel("--:--")
            tim.setStyleSheet(
                "color: #e6edf3; font-size: 22px; font-weight: bold;"
                "font-family: 'Consolas','Ubuntu Mono','DejaVu Sans Mono',monospace;"
            )
            tim.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(tim)
            self._body_layout.addLayout(row)
            self._rows.append((lbl, tim))

        self.adjustSize()
        self.tick()

    def update_format(self, use_24h: bool, show_seconds: bool):
        self._settings.use_24h = use_24h
        self._settings.show_seconds = show_seconds
        self.tick()

    def tick(self):
        fmt = self._time_format()
        for i, (_, tim) in enumerate(self._rows):
            if i >= len(self._tzones):
                break
            tz = self._tzones[i]
            if not tz.isValid():
                continue
            now = QDateTime.currentDateTimeUtc().toTimeZone(tz)
            tim.setText(now.toString(fmt))

    # ── Painting (rounded dark card) ──────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(13, 17, 23, 255)))      # #0d1117 solid
        painter.setPen(QPen(QColor(48, 54, 61), 1))            # #30363d border
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)

    def set_opacity(self, value: float):
        self.setWindowOpacity(value)
        self._settings.float_opacity = value
        self._settings.save()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _time_format(self) -> str:
        if self._settings.use_24h:
            return "HH:mm:ss" if self._settings.show_seconds else "HH:mm"
        return "hh:mm:ss AP" if self._settings.show_seconds else "hh:mm AP"

    def _start_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.tick)
        self._timer.start()

    # ── Position helper (called from main window) ─────────────────────────────

    def position_top_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        self.move(screen.right() - self.width() - 20, screen.top() + 20)
