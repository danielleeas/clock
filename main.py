import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("World Clock")
    app.setOrganizationName("worldclock")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app.setQuitOnLastWindowClosed(False)

    # Deferred imports: QObject-based singletons need QApplication to exist first
    from PySide6.QtWidgets import QSystemTrayIcon
    from ui.main_window import MainWindow

    window = MainWindow()

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        from ui.tray_icon import TrayIcon
        tray = TrayIcon(
            on_show_window=window.show_and_raise,
            on_quit=app.quit,
        )
        tray.show()
    else:
        # No tray available (e.g. GNOME without AppIndicator extension)
        app.setQuitOnLastWindowClosed(True)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
