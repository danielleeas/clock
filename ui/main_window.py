from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QLabel, QMessageBox,
    QSizePolicy, QFrame, QSlider, QDialog
)
from PySide6.QtCore import Qt, QTimer, QTimeZone
from PySide6.QtGui import QKeySequence, QShortcut

from app.settings import AppSettings
from app.persistence import load_clocks
from ui.drag_container import DragContainer
from ui.add_clock_dialog import AddClockDialog
from ui.theme import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World Clock")
        self.setMinimumSize(720, 460)
        self.resize(1060, 640)
        self.setStyleSheet(STYLESHEET)

        self.settings = AppSettings.load()
        self._build_ui()
        self._load_clocks()
        self._start_timer()
        self._apply_settings_to_ui()
        self._init_floating_clock()

        # Keyboard shortcut: Ctrl+N → add clock
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._add_clock)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_vbox = QVBoxLayout(root)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = QWidget()
        toolbar.setObjectName("Toolbar")
        toolbar.setFixedHeight(58)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(20, 0, 20, 0)
        tb.setSpacing(8)

        title = QLabel("World Clock")
        title.setObjectName("AppTitle")

        self._btn_24h = self._tool_btn("24h", checkable=True, tooltip="Toggle 12/24-hour format")
        self._btn_secs = self._tool_btn("Seconds", checkable=True, tooltip="Show/hide seconds")
        self._btn_view = self._tool_btn("List", checkable=True, tooltip="Toggle list / grid view")
        self._btn_float = self._tool_btn("Float", checkable=True, tooltip="Show/hide floating clock overlay")
        self._btn_float_opacity = self._tool_btn("◑", tooltip="Adjust floating clock transparency")
        self._btn_float_opacity.setVisible(False)

        self._btn_24h.clicked.connect(self._toggle_24h)
        self._btn_secs.clicked.connect(self._toggle_seconds)
        self._btn_view.clicked.connect(self._toggle_view)
        self._btn_float.clicked.connect(self._toggle_float)
        self._btn_float_opacity.clicked.connect(self._open_float_opacity)

        add_btn = QPushButton("＋  Add Clock")
        add_btn.setObjectName("AddBtn")
        add_btn.setToolTip("Add a new timezone clock  (Ctrl+N)")
        add_btn.clicked.connect(self._add_clock)

        tb.addWidget(title)
        tb.addStretch()
        tb.addWidget(self._btn_24h)
        tb.addWidget(self._btn_secs)
        tb.addWidget(self._btn_view)
        tb.addWidget(self._btn_float)
        tb.addWidget(self._btn_float_opacity)
        tb.addSpacing(8)
        tb.addWidget(add_btn)

        # ── Separator ────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("Separator")
        sep.setFrameShape(QFrame.Shape.HLine)

        # ── Scroll area + DragContainer ──────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = DragContainer()
        self._scroll.setWidget(self._container)

        main_vbox.addWidget(toolbar)
        main_vbox.addWidget(sep)
        main_vbox.addWidget(self._scroll)

    def _tool_btn(self, text: str, *, checkable=False, tooltip="") -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("ToolBtn")
        btn.setCheckable(checkable)
        btn.setToolTip(tooltip)
        return btn

    # ── Load clocks ───────────────────────────────────────────────────────────

    def _load_clocks(self):
        for entry in load_clocks():
            tz = QTimeZone(entry["tz_id"].encode())
            if not tz.isValid():
                continue
            self._container.add_card(entry["label"], entry["tz_id"])

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _start_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._container.tick_all)
        self._timer.start()
        self._container.tick_all()

    # ── Settings toggles ──────────────────────────────────────────────────────

    def _apply_settings_to_ui(self):
        for btn in (self._btn_24h, self._btn_secs, self._btn_view, self._btn_float):
            btn.blockSignals(True)

        self._btn_24h.setChecked(self.settings.use_24h)
        self._btn_secs.setChecked(self.settings.show_seconds)
        self._btn_view.setChecked(not self.settings.grid_view)
        self._btn_float.setChecked(False)

        for btn in (self._btn_24h, self._btn_secs, self._btn_view, self._btn_float):
            btn.blockSignals(False)

        self._container.set_format(self.settings.use_24h, self.settings.show_seconds)
        self._container.set_list_mode(not self.settings.grid_view)

    def _toggle_24h(self, checked: bool):
        self.settings.use_24h = checked
        self.settings.save()
        self._container.set_format(self.settings.use_24h, self.settings.show_seconds)
        self._container.tick_all()
        self._float_clock.update_format(self.settings.use_24h, self.settings.show_seconds)

    def _toggle_seconds(self, checked: bool):
        self.settings.show_seconds = checked
        self.settings.save()
        self._container.set_format(self.settings.use_24h, self.settings.show_seconds)
        self._container.tick_all()
        self._float_clock.update_format(self.settings.use_24h, self.settings.show_seconds)

    def _toggle_view(self, checked: bool):
        self.settings.grid_view = not checked
        self.settings.save()
        self._container.set_list_mode(not self.settings.grid_view)

    # ── Floating clock ────────────────────────────────────────────────────────

    def _init_floating_clock(self):
        from ui.floating_clock import FloatingClock
        self._float_clock = FloatingClock()
        self._float_clock.position_top_right()

    def _toggle_float(self, checked: bool):
        if checked:
            self._float_clock.refresh_clocks()
            self._float_clock.position_top_right()
            self._float_clock.show()
        else:
            self._float_clock.hide()
        self._btn_float_opacity.setVisible(checked)

    def _open_float_opacity(self):
        """Open a small opacity slider dialog for the floating clock."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Float Opacity")
        dlg.setFixedWidth(280)
        dlg.setStyleSheet("""
            QDialog { background: #161b22; }
            QLabel { color: #e6edf3; font-size: 12px; }
            QSlider::groove:horizontal { height: 4px; background: #30363d; border-radius: 2px; }
            QSlider::handle:horizontal { width: 14px; height: 14px; margin: -5px 0;
                background: #58a6ff; border-radius: 7px; }
            QSlider::sub-page:horizontal { background: #58a6ff; border-radius: 2px; }
            QPushButton { background: #21262d; color: #e6edf3; border: 1px solid #30363d;
                border-radius: 4px; padding: 4px 14px; font-size: 12px; }
            QPushButton:hover { background: #30363d; }
        """)
        vbox = QVBoxLayout(dlg)
        vbox.setContentsMargins(16, 14, 16, 14)
        vbox.setSpacing(10)

        pct = QLabel(f"{int(self._float_clock.windowOpacity() * 100)}%")
        pct.setStyleSheet("color: #58a6ff; font-size: 12px;")

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(20, 100)
        slider.setValue(int(self._float_clock.windowOpacity() * 100))

        def on_change(v):
            pct.setText(f"{v}%")
            self._float_clock.set_opacity(v / 100.0)

        slider.valueChanged.connect(on_change)

        row = QHBoxLayout()
        row.addWidget(QLabel("20%"))
        row.addWidget(slider, 1)
        row.addWidget(QLabel("100%"))

        done = QPushButton("Done")
        done.clicked.connect(dlg.accept)

        vbox.addWidget(QLabel("Floating clock transparency:"))
        vbox.addLayout(row)
        vbox.addWidget(pct)
        vbox.addWidget(done)
        dlg.exec()

    # ── Add clock ─────────────────────────────────────────────────────────────

    def _add_clock(self):
        dialog = AddClockDialog(self)
        if dialog.exec():
            result = dialog.get_result()
            if not result:
                return
            label, tz_id = result
            tz = QTimeZone(tz_id.encode())
            if not tz.isValid():
                QMessageBox.warning(self, "Invalid Timezone",
                                    f'"{tz_id}" is not a valid timezone.')
                return
            card = self._container.add_card(label, tz_id)
            card.tick()
            if self._btn_float.isChecked():
                self._float_clock.refresh_clocks()

    # ── Window close → hide to tray ───────────────────────────────────────────

    def closeEvent(self, event):
        from PySide6.QtWidgets import QSystemTrayIcon, QApplication
        if QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
        else:
            event.accept()
            QApplication.quit()

    def show_and_raise(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
