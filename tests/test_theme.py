"""
Unit tests for the theme module.
"""
import re
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from nexus_downloader.ui.theme import (
    apply_theme,
    create_dark_palette,
    get_application_stylesheet,
)
from nexus_downloader.ui.theme.colors import (
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
)


# Color constant tests
class TestColorConstants:
    """Tests for color constants."""

    def test_color_constants_are_valid_hex(self):
        """All color constants should be valid hex color strings."""
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        colors = [
            BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_HOVER,
            TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED,
            ACCENT_PRIMARY, ACCENT_HOVER, ACCENT_PRESSED,
            SUCCESS, ERROR, WARNING,
            BORDER, BORDER_FOCUS,
            TABLE_ALT_ROW, TABLE_SELECTION,
        ]
        for color in colors:
            assert hex_pattern.match(color), f"Invalid hex color: {color}"

    def test_background_colors_are_defined(self):
        """Background colors should be defined."""
        assert BG_PRIMARY == "#101319"
        assert BG_SECONDARY == "#181C24"
        assert BG_TERTIARY == "#1E2330"
        assert BG_HOVER == "#252B3B"

    def test_text_colors_are_defined(self):
        """Text colors should be defined."""
        assert TEXT_PRIMARY == "#E4E6EB"
        assert TEXT_SECONDARY == "#8B8D94"
        assert TEXT_DISABLED == "#5C5F66"

    def test_accent_colors_are_defined(self):
        """Accent colors should be defined."""
        assert ACCENT_PRIMARY == "#00B4D8"
        assert ACCENT_HOVER == "#48CAE4"
        assert ACCENT_PRESSED == "#0096B4"

    def test_state_colors_are_defined(self):
        """State colors should be defined."""
        assert SUCCESS == "#51CF66"
        assert ERROR == "#FF6B6B"
        assert WARNING == "#FFB347"

    def test_border_colors_are_defined(self):
        """Border colors should be defined."""
        assert BORDER == "#2D3340"
        assert BORDER_FOCUS == "#00B4D8"


# Palette tests
class TestPalette:
    """Tests for QPalette configuration."""

    def test_create_dark_palette_returns_qpalette(self):
        """create_dark_palette should return a QPalette instance."""
        palette = create_dark_palette()
        assert isinstance(palette, QPalette)

    def test_palette_window_color(self):
        """Window color should match BG_PRIMARY."""
        palette = create_dark_palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        expected_color = QColor(BG_PRIMARY)
        assert window_color.name() == expected_color.name()

    def test_palette_text_color(self):
        """Text color should match TEXT_PRIMARY."""
        palette = create_dark_palette()
        text_color = palette.color(QPalette.ColorRole.Text)
        expected_color = QColor(TEXT_PRIMARY)
        assert text_color.name() == expected_color.name()

    def test_palette_highlight_color(self):
        """Highlight color should match ACCENT_PRIMARY."""
        palette = create_dark_palette()
        highlight_color = palette.color(QPalette.ColorRole.Highlight)
        expected_color = QColor(ACCENT_PRIMARY)
        assert highlight_color.name() == expected_color.name()

    def test_palette_base_color(self):
        """Base color should match BG_TERTIARY."""
        palette = create_dark_palette()
        base_color = palette.color(QPalette.ColorRole.Base)
        expected_color = QColor(BG_TERTIARY)
        assert base_color.name() == expected_color.name()

    def test_palette_button_color(self):
        """Button color should match BG_SECONDARY."""
        palette = create_dark_palette()
        button_color = palette.color(QPalette.ColorRole.Button)
        expected_color = QColor(BG_SECONDARY)
        assert button_color.name() == expected_color.name()

    def test_palette_disabled_text_color(self):
        """Disabled text color should match TEXT_DISABLED."""
        palette = create_dark_palette()
        disabled_text = palette.color(
            QPalette.ColorGroup.Disabled, 
            QPalette.ColorRole.Text
        )
        expected_color = QColor(TEXT_DISABLED)
        assert disabled_text.name() == expected_color.name()


# Stylesheet tests
class TestStylesheet:
    """Tests for stylesheet generation."""

    def test_get_application_stylesheet_returns_string(self):
        """get_application_stylesheet should return a non-empty string."""
        stylesheet = get_application_stylesheet()
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0

    def test_stylesheet_contains_qpushbutton(self):
        """Stylesheet should contain QPushButton styling."""
        stylesheet = get_application_stylesheet()
        assert "QPushButton" in stylesheet

    def test_stylesheet_contains_qlineedit(self):
        """Stylesheet should contain QLineEdit styling."""
        stylesheet = get_application_stylesheet()
        assert "QLineEdit" in stylesheet

    def test_stylesheet_contains_qtablewidget(self):
        """Stylesheet should contain QTableWidget styling."""
        stylesheet = get_application_stylesheet()
        assert "QTableWidget" in stylesheet

    def test_stylesheet_contains_qtabbar(self):
        """Stylesheet should contain QTabBar styling."""
        stylesheet = get_application_stylesheet()
        assert "QTabBar" in stylesheet

    def test_stylesheet_contains_qscrollbar(self):
        """Stylesheet should contain QScrollBar styling."""
        stylesheet = get_application_stylesheet()
        assert "QScrollBar" in stylesheet

    def test_stylesheet_contains_qprogressbar(self):
        """Stylesheet should contain QProgressBar styling."""
        stylesheet = get_application_stylesheet()
        assert "QProgressBar" in stylesheet

    def test_stylesheet_contains_qcombobox(self):
        """Stylesheet should contain QComboBox styling."""
        stylesheet = get_application_stylesheet()
        assert "QComboBox" in stylesheet

    def test_stylesheet_contains_qcheckbox(self):
        """Stylesheet should contain QCheckBox styling."""
        stylesheet = get_application_stylesheet()
        assert "QCheckBox" in stylesheet

    def test_stylesheet_contains_color_constants(self):
        """Stylesheet should use theme color constants."""
        stylesheet = get_application_stylesheet()
        # Check that the actual color values appear in the stylesheet
        assert BG_PRIMARY in stylesheet
        assert TEXT_PRIMARY in stylesheet
        assert ACCENT_PRIMARY in stylesheet


# Integration tests
class TestThemeIntegration:
    """Integration tests for theme application."""

    def test_apply_theme_sets_palette(self, qtbot, app):
        """apply_theme should set the application palette."""
        apply_theme(app)
        palette = app.palette()
        expected_window_color = QColor(BG_PRIMARY)
        assert palette.color(QPalette.ColorRole.Window).name() == expected_window_color.name()

    def test_apply_theme_sets_stylesheet(self, qtbot, app):
        """apply_theme should set the application stylesheet."""
        apply_theme(app)
        stylesheet = app.styleSheet()
        assert len(stylesheet) > 0
        assert "QPushButton" in stylesheet


# Fixtures
@pytest.fixture
def app(qtbot):
    """Provide a QApplication instance for testing."""
    return QApplication.instance()
