from __future__ import annotations
import math
from typing import Optional, Callable

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtCore import QTimer, QTime, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen


class TrayIcon(QSystemTrayIcon):
    """
    System-tray icon showing a live analog clock.

    Updates every minute (aligned to the next whole minute at startup).
    The icon is drawn programmatically — no image files required.
    """

    def __init__(
        self,
        on_show_window: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._on_show_window = on_show_window
        self._on_quit = on_quit

        self._build_menu()
        self._update_icon()
        self._schedule_timer()
        self.activated.connect(self._on_activated)

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menu = QMenu()
        menu.addAction("Show Window", self._do_show)
        menu.addSeparator()
        menu.addAction("Quit", self._do_quit)
        self.setContextMenu(menu)
        self.setToolTip("World Clock")

    # ── Icon painting ─────────────────────────────────────────────────────────

    def _update_icon(self):
        self.setIcon(QIcon(self._paint_clock(QTime.currentTime())))
        now = QTime.currentTime()
        self.setToolTip(f"World Clock  •  {now.toString('HH:mm')}")

    def _paint_clock(self, t: QTime) -> QPixmap:
        size = 22
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)

        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy, r = size / 2, size / 2, size / 2 - 1.5

        # Face
        p.setPen(QPen(QColor("#58a6ff"), 1.2))
        p.setBrush(QColor("#161b22"))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Hour markers (4 at 12/3/6/9)
        p.setPen(QPen(QColor("#484f58"), 1.0))
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            inner = r * 0.82
            outer = r * 0.94
            p.drawLine(
                cx + inner * math.cos(angle), cy + inner * math.sin(angle),
                cx + outer * math.cos(angle), cy + outer * math.sin(angle),
            )

        # Hour hand
        hour_angle = math.radians(
            (t.hour() % 12 + t.minute() / 60) * 30 - 90
        )
        hr = r * 0.50
        p.setPen(QPen(QColor("#e6edf3"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(cx, cy, cx + hr * math.cos(hour_angle), cy + hr * math.sin(hour_angle))

        # Minute hand
        min_angle = math.radians(t.minute() * 6 - 90)
        mr = r * 0.72
        p.setPen(QPen(QColor("#58a6ff"), 1.3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(cx, cy, cx + mr * math.cos(min_angle), cy + mr * math.sin(min_angle))

        # Centre dot
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#e6edf3"))
        p.drawEllipse(cx - 1.5, cy - 1.5, 3, 3)

        p.end()
        return px

    # ── Timer (aligned to next whole minute) ─────────────────────────────────

    def _schedule_timer(self):
        now = QTime.currentTime()
        ms_to_next = (60 - now.second()) * 1000 - now.msec()

        self._oneshot = QTimer(self)
        self._oneshot.setSingleShot(True)
        self._oneshot.timeout.connect(self._on_first_minute)
        self._oneshot.start(ms_to_next)

    def _on_first_minute(self):
        self._update_icon()
        self._minute_timer = QTimer(self)
        self._minute_timer.setInterval(60_000)
        self._minute_timer.timeout.connect(self._update_icon)
        self._minute_timer.start()

    # ── Signals ───────────────────────────────────────────────────────────────

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._do_show()

    def _do_show(self):
        if self._on_show_window:
            self._on_show_window()

    def _do_quit(self):
        if self._on_quit:
            self._on_quit()
        else:
            QApplication.quit()
