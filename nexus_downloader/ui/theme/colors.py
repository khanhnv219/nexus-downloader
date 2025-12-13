"""
Color constants for the Nexus Downloader dark theme.

All colors are defined as hex strings and follow a consistent naming convention:
- BG_* : Background colors
- TEXT_* : Text colors
- ACCENT_* : Accent/highlight colors
- State colors: SUCCESS, ERROR, WARNING
- BORDER_* : Border colors
- TABLE_* : Table-specific colors
"""

# Background colors (dark to light progression for visual hierarchy)
BG_PRIMARY = "#101319"      # Main window background (darkest)
BG_SECONDARY = "#181C24"    # Panels, cards, dialogs
BG_TERTIARY = "#1E2330"     # Input fields, elevated surfaces
BG_HOVER = "#252B3B"        # Hover state for rows/items

# Text colors
TEXT_PRIMARY = "#E4E6EB"    # Primary text (light gray, not pure white)
TEXT_SECONDARY = "#8B8D94"  # Secondary text, placeholders
TEXT_DISABLED = "#5C5F66"   # Disabled text

# Accent colors (cyan/electric blue)
ACCENT_PRIMARY = "#00B4D8"  # Primary buttons, active states, links
ACCENT_HOVER = "#48CAE4"    # Hover state
ACCENT_PRESSED = "#0096B4"  # Pressed state

# State colors
SUCCESS = "#51CF66"         # Completed downloads
ERROR = "#FF6B6B"           # Failed downloads, error messages
WARNING = "#FFB347"         # Warnings, cancelled

# Border colors
BORDER = "#2D3340"          # Subtle borders
BORDER_FOCUS = "#00B4D8"    # Focus state (uses accent)

# Table colors
TABLE_ALT_ROW = "#141820"   # Alternating row background
TABLE_SELECTION = "#1A3A4A" # Selected row background
TABLE_GRIDLINE = "#1E2330"  # Table gridlines

# Progress bar colors
PROGRESS_BG = "#1E2330"     # Progress bar background
PROGRESS_CHUNK = "#00B4D8"  # Progress bar fill (accent)

# Scrollbar colors
SCROLLBAR_BG = "#101319"    # Scrollbar track
SCROLLBAR_HANDLE = "#2D3340"  # Scrollbar handle
SCROLLBAR_HANDLE_HOVER = "#3D4450"  # Scrollbar handle hover

# Font settings
FONT_FAMILY = '"Segoe UI", "Roboto", sans-serif'
FONT_SIZE_DEFAULT = "14px"
FONT_SIZE_SMALL = "12px"
FONT_SIZE_TITLE = "16px"
