"""
Dark theme module for Nexus Downloader.

This module provides a centralized theme configuration with color constants,
QPalette configuration, and stylesheet generation for consistent dark theme
appearance across all UI components.
"""
from PySide6.QtWidgets import QApplication

from .colors import *  # noqa: F401, F403 - Export all color constants
from .palette import create_dark_palette
from .styles import get_application_stylesheet


def apply_theme(app: QApplication) -> None:
    """Apply the dark theme to the application.

    This function applies both the QPalette for system-wide colors and
    the stylesheet for component-specific styling.

    Args:
        app: The QApplication instance to apply the theme to.
    """
    app.setPalette(create_dark_palette())
    app.setStyleSheet(get_application_stylesheet())
