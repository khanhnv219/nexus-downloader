"""Main entry point for the Nexus Downloader application."""
import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from nexus_downloader.ui.main_window import MainWindow
from nexus_downloader.ui.theme import apply_theme


def main():
    """Starts the Nexus Downloader application."""
    app = QApplication(sys.argv)

    # Apply Fusion style for consistent cross-platform appearance
    app.setStyle(QStyleFactory.create("Fusion"))

    # Apply dark theme (palette + stylesheet)
    apply_theme(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # Add the current directory to the Python path to help with module imports
    sys.path.append('.')
    main()
