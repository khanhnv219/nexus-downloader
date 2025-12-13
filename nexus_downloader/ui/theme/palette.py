"""
QPalette configuration for the Nexus Downloader dark theme.

This module provides the create_dark_palette() function that returns a
configured QPalette for system-wide dark theme colors.
"""
from PySide6.QtGui import QPalette, QColor

from .colors import (
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_DISABLED,
    ACCENT_PRIMARY,
    ACCENT_HOVER,
    BORDER,
)


def create_dark_palette() -> QPalette:
    """Create and return a dark theme QPalette.

    The palette configures colors for all standard Qt color roles including
    Active, Inactive, and Disabled color groups.

    Returns:
        QPalette: A configured dark theme palette.
    """
    palette = QPalette()

    # Window and base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_TERTIARY))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_SECONDARY))

    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_SECONDARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(TEXT_PRIMARY))

    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(BG_SECONDARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))

    # Highlight colors (selection, focus)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT_PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(TEXT_PRIMARY))

    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(ACCENT_PRIMARY))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(ACCENT_HOVER))

    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(BG_SECONDARY))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT_PRIMARY))

    # Other colors
    palette.setColor(QPalette.ColorRole.Light, QColor(BG_TERTIARY))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(BG_SECONDARY))
    palette.setColor(QPalette.ColorRole.Dark, QColor(BG_PRIMARY))
    palette.setColor(QPalette.ColorRole.Mid, QColor(BORDER))
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#000000"))

    # Disabled color group
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(TEXT_DISABLED))

    return palette
