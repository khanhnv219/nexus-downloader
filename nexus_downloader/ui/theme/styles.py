"""
QStyleSheet generation for the Nexus Downloader dark theme.

This module provides the get_application_stylesheet() function that returns
a complete stylesheet for component-specific styling beyond what QPalette provides.
"""
from .colors import (
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BG_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_DISABLED,
    ACCENT_PRIMARY,
    ACCENT_HOVER,
    ACCENT_PRESSED,
    SUCCESS,
    ERROR,
    WARNING,
    BORDER,
    BORDER_FOCUS,
    TABLE_ALT_ROW,
    TABLE_SELECTION,
    TABLE_GRIDLINE,
    PROGRESS_BG,
    PROGRESS_CHUNK,
    SCROLLBAR_BG,
    SCROLLBAR_HANDLE,
    SCROLLBAR_HANDLE_HOVER,
    FONT_FAMILY,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_HEADER,
    FONT_WEIGHT_MEDIUM,
    FONT_WEIGHT_SEMI_BOLD,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    BORDER_RADIUS_SM,
    BORDER_RADIUS_MD,
    BORDER_RADIUS_LG,
)


def get_application_stylesheet() -> str:
    """Generate and return the complete application stylesheet.

    Returns:
        str: The complete QStyleSheet string for the dark theme.
    """
    return f"""
/* Base widget styling */
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_DEFAULT};
    color: {TEXT_PRIMARY};
}}

/* Main window and dialogs */
QMainWindow, QDialog {{
    background-color: {BG_PRIMARY};
}}

/* Labels */
QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}

/* Line edits */
QLineEdit {{
    padding: 6px {SPACING_SM};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_PRIMARY};
}}

QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

QLineEdit:disabled {{
    color: {TEXT_DISABLED};
    background-color: {BG_SECONDARY};
}}

QLineEdit::placeholder {{
    color: {TEXT_SECONDARY};
}}

/* Push buttons */
QPushButton {{
    padding: {SPACING_SM} {SPACING_MD};
    border: 1px solid {ACCENT_PRIMARY};
    border-radius: {BORDER_RADIUS_MD};
    background-color: {ACCENT_PRIMARY};
    color: {TEXT_PRIMARY};
    font-weight: {FONT_WEIGHT_MEDIUM};
}}

QPushButton:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT_PRESSED};
}}

QPushButton:disabled {{
    background-color: {BG_SECONDARY};
    border-color: {BORDER};
    color: {TEXT_DISABLED};
}}

/* Secondary/outline buttons (can be applied via object name) */
QPushButton[secondary="true"] {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
}}

QPushButton[secondary="true"]:hover {{
    background-color: {BG_HOVER};
    border-color: {TEXT_SECONDARY};
}}

QPushButton[secondary="true"]:pressed {{
    background-color: {BG_TERTIARY};
    border-color: {ACCENT_PRIMARY};
}}

/* Combo boxes */
QComboBox {{
    padding: 6px {SPACING_SM};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {TEXT_SECONDARY};
}}

QComboBox:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: {SPACING_XS} solid transparent;
    border-right: {SPACING_XS} solid transparent;
    border-top: 6px solid {TEXT_SECONDARY};
    margin-right: {SPACING_SM};
}}

QComboBox QAbstractItemView {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT_PRIMARY};
    color: {TEXT_PRIMARY};
}}

/* Check boxes */
QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: {SPACING_SM};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {BG_TERTIARY};
}}

QCheckBox::indicator:hover {{
    border-color: {TEXT_SECONDARY};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_PRIMARY};
    border-color: {ACCENT_PRIMARY};
}}

QCheckBox::indicator:disabled {{
    background-color: {BG_SECONDARY};
    border-color: {BORDER};
}}

/* Progress bars */
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    text-align: center;
    color: {TEXT_PRIMARY};
    background-color: {PROGRESS_BG};
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {PROGRESS_CHUNK};
    border-radius: 3px;
}}

/* Tables */
QTableWidget, QTableView {{
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    gridline-color: {TABLE_GRIDLINE};
    alternate-background-color: {TABLE_ALT_ROW};
    selection-background-color: {TABLE_SELECTION};
}}

QTableWidget::item, QTableView::item {{
    padding: {SPACING_XS} {SPACING_SM};
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {TABLE_SELECTION};
    color: {TEXT_PRIMARY};
}}

QTableWidget::item:hover, QTableView::item:hover {{
    background-color: {BG_HOVER};
}}

QHeaderView::section {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    padding: 6px {SPACING_SM};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {TABLE_GRIDLINE};
    font-size: {FONT_SIZE_HEADER};
    font-weight: {FONT_WEIGHT_MEDIUM};
}}

QHeaderView::section:hover {{
    background-color: {BG_TERTIARY};
}}

/* Tab widget */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_SECONDARY};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {BG_PRIMARY};
    color: {TEXT_SECONDARY};
    padding: {SPACING_SM} {SPACING_MD};
    border-top-left-radius: {BORDER_RADIUS_SM};
    border-top-right-radius: {BORDER_RADIUS_SM};
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid {ACCENT_PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

/* Scroll bars */
QScrollBar:vertical {{
    background-color: {SCROLLBAR_BG};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {SCROLLBAR_HANDLE};
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {SCROLLBAR_HANDLE_HOVER};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {SCROLLBAR_BG};
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {SCROLLBAR_HANDLE};
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {SCROLLBAR_HANDLE_HOVER};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* Group boxes (for settings dialog) */
QGroupBox {{
    font-weight: {FONT_WEIGHT_MEDIUM};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    margin-top: 12px;
    padding-top: {SPACING_SM};
    background-color: {BG_SECONDARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 {SPACING_XS};
    color: {TEXT_PRIMARY};
    font-weight: {FONT_WEIGHT_SEMI_BOLD};
}}

/* List widgets (for settings navigation) */
QListWidget {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    color: {TEXT_PRIMARY};
    outline: none;
}}

QListWidget::item {{
    padding: {SPACING_SM} 12px;
    border-radius: {BORDER_RADIUS_SM};
    margin: 2px {SPACING_XS};
}}

QListWidget::item:selected {{
    background-color: {ACCENT_PRIMARY};
    color: {TEXT_PRIMARY};
}}

QListWidget::item:hover:!selected {{
    background-color: {BG_HOVER};
}}

/* Stacked widget */
QStackedWidget {{
    background-color: transparent;
}}

/* Message boxes and file dialogs inherit from QDialog */
QMessageBox {{
    background-color: {BG_PRIMARY};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}

/* Tooltips */
QToolTip {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    padding: {SPACING_XS} {SPACING_SM};
}}

/* Zone container styling for main window layout */
QFrame#topBarZone {{
    background-color: {BG_SECONDARY};
    border-bottom: 1px solid {BORDER};
}}

QFrame#centerZone {{
    background-color: {BG_PRIMARY};
}}

QFrame#bottomBarZone {{
    background-color: {BG_SECONDARY};
    border-top: 1px solid {BORDER};
}}

/* Menu (if needed) */
QMenu {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    padding: {SPACING_XS};
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
    border-radius: {BORDER_RADIUS_SM};
}}

QMenu::item:selected {{
    background-color: {ACCENT_PRIMARY};
}}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {{
    padding: {SPACING_XS} {SPACING_SM};
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {BORDER_FOCUS};
}}

/* Text edit (if needed) */
QTextEdit, QPlainTextEdit {{
    border: 1px solid {BORDER};
    border-radius: {BORDER_RADIUS_SM};
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_PRIMARY};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {BORDER_FOCUS};
}}
"""
