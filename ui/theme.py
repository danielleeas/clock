STYLESHEET = """
/* ─── Base ──────────────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Segoe UI", "Ubuntu", "Inter", system-ui, sans-serif;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: #161b22;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #58a6ff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

/* ─── Toolbar area ───────────────────────────────────────────── */
#Toolbar {
    background: #0d1117;
    border-bottom: 1px solid #21262d;
}

#AppTitle {
    color: #e6edf3;
    font-size: 17pt;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* ─── Toolbar buttons ────────────────────────────────────────── */
#ToolBtn {
    background: #161b22;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 9pt;
}
#ToolBtn:hover {
    background: #1c2333;
    color: #e6edf3;
    border-color: #58a6ff;
}
#ToolBtn:checked {
    background: #1d2d3e;
    color: #58a6ff;
    border-color: #58a6ff;
}

#AddBtn {
    background: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 9pt;
    font-weight: 600;
}
#AddBtn:hover {
    background: #2ea043;
    border-color: #3fb950;
}
#AddBtn:pressed { background: #196c2e; }

/* ─── Clock Card (grid mode) ─────────────────────────────────── */
#ClockCard {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}
#ClockCard:hover {
    background: #1c2333;
    border-color: #3b82f6;
}
#ClockCard[dragging="true"] {
    opacity: 0.4;
    border: 1px dashed #58a6ff;
}
#ClockCard[drop_target="true"] {
    background: #1d2d3e;
    border: 2px solid #58a6ff;
}

/* ─── Clock Card (list mode) ─────────────────────────────────── */
#ClockCardList {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
}
#ClockCardList:hover {
    background: #1c2333;
    border-color: #3b82f6;
}
#ClockCardList[drop_target="true"] {
    background: #1d2d3e;
    border: 2px solid #58a6ff;
}

/* ─── Card inner labels ──────────────────────────────────────── */
#DragHandle {
    color: #484f58;
    font-size: 14pt;
}
#DragHandle:hover { color: #8b949e; }

#CityLabel {
    color: #e6edf3;
    font-size: 11pt;
    font-weight: 600;
}

#TimeLabel {
    color: #f0f6fc;
    font-family: "Consolas", "Ubuntu Mono", "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 30pt;
    font-weight: 700;
    letter-spacing: -1px;
}

#TimeLabelList {
    color: #f0f6fc;
    font-family: "Consolas", "Ubuntu Mono", "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 16pt;
    font-weight: 700;
}

#DateLabel {
    color: #8b949e;
    font-size: 9pt;
}

#OffsetLabel {
    color: #484f58;
    font-size: 8pt;
}

/* ─── Badges ─────────────────────────────────────────────────── */
#BadgeHome {
    background: #122d20;
    color: #3fb950;
    border: 1px solid #238636;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 7pt;
    font-weight: 700;
}

#BadgeTomorrow {
    background: #1d2d3e;
    color: #58a6ff;
    border: 1px solid #1f6feb;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 7pt;
    font-weight: 700;
}

#BadgeYesterday {
    background: #2d1f0e;
    color: #f0883e;
    border: 1px solid #9e4f10;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 7pt;
    font-weight: 700;
}

/* ─── Remove button ──────────────────────────────────────────── */
#RemoveBtn {
    background: transparent;
    color: #484f58;
    border: none;
    border-radius: 10px;
    font-size: 14pt;
    font-weight: 400;
    padding: 0;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
}
#RemoveBtn:hover {
    background: #f85149;
    color: #ffffff;
}

/* ─── Dialogs ────────────────────────────────────────────────── */
QDialog {
    background: #161b22;
}

QLabel { color: #8b949e; }

QLineEdit, QComboBox {
    background: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #1f6feb;
}
QLineEdit:focus, QComboBox:focus { border-color: #58a6ff; }

QListWidget {
    background: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    outline: none;
}
QListWidget::item { padding: 6px 10px; border-radius: 4px; }
QListWidget::item:hover { background: #1c2333; }
QListWidget::item:selected { background: #1d2d3e; color: #58a6ff; }

QDialogButtonBox QPushButton {
    background: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 70px;
}
QDialogButtonBox QPushButton:hover {
    background: #30363d;
    border-color: #58a6ff;
}
QDialogButtonBox QPushButton[text="OK"] {
    background: #238636;
    border-color: #2ea043;
}
QDialogButtonBox QPushButton[text="OK"]:hover { background: #2ea043; }

QCheckBox { color: #e6edf3; spacing: 6px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background: #238636;
    border-color: #2ea043;
    image: none;
}
QCheckBox::indicator:hover { border-color: #58a6ff; }

/* ─── Section separator ──────────────────────────────────────── */
#Separator {
    background: #21262d;
    max-height: 1px;
    min-height: 1px;
}
"""
