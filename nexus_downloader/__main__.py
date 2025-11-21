"""Main entry point for the Nexus Downloader application."""
import sys
from PySide6.QtWidgets import QApplication
from nexus_downloader.ui.main_window import MainWindow

def main():
    """Starts the Nexus Downloader application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # Add the current directory to the Python path to help with module imports
    sys.path.append('.')
    main()
