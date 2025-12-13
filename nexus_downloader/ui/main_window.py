"""
Main application window for the Nexus Downloader.
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QComboBox,
    QLabel,
    QMessageBox,
    QSystemTrayIcon,
    QStyle,
    QProgressBar,
    QFileDialog,
    QTabWidget,
)
from PySide6.QtCore import Qt
from nexus_downloader.core.download_manager import DownloadManager
from nexus_downloader.core.yt_dlp_service import (
    QUALITY_OPTIONS_LIST,
    get_format_string,
    VIDEO_FORMAT_OPTIONS_LIST,
    AUDIO_FORMAT_OPTIONS_LIST,
    get_video_format_ext,
    get_audio_format_ext,
    SUBTITLE_LANGUAGE_OPTIONS_LIST,
    get_subtitle_lang_code,
    DOWNLOAD_PRESETS_LIST,
    DOWNLOAD_PRESET_TOOLTIPS,
    get_preset_config,
    detect_preset_from_settings,
    detect_platform,
    sanitize_folder_name,
)
from datetime import datetime
from nexus_downloader.ui.settings_dialog import SettingsDialog
from nexus_downloader.services.settings_service import SettingsService, AppSettings # Import SettingsService and AppSettings
from nexus_downloader.core.data_models import DownloadStatus, DownloadItem, HistoryEntry
from nexus_downloader.core.url_validator import URLValidator
from nexus_downloader.services.history_service import HistoryService
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    The main window of the Nexus Downloader application.
    It provides the basic UI elements for URL input, download controls, and a table view.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nexus Downloader")
        self.resize(1000, 700)  # Set initial window size (width x height)
        # Theme is now applied at application level in __main__.py

        self.settings_service = SettingsService() # Instantiate SettingsService
        self.app_settings = self._load_initial_settings() # Load settings on startup
        self.history_service = HistoryService()  # Instantiate HistoryService

        self.download_manager = DownloadManager()
        self.download_manager.set_concurrent_downloads(self.app_settings.concurrent_downloads_limit) 
        
        # Flag to prevent race condition in checkbox synchronization
        self._updating_from_select_all = False
        
        # Download progress tracking
        self._download_queue_total = 0
        self._download_completed_count = 0
        self._batch_success_count = 0
        self._batch_fail_count = 0

        # System Tray Icon for notifications
        self.tray_icon = QSystemTrayIcon(self)
        # Use a standard icon since we don't have a custom one yet
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.tray_icon.setVisible(True)
        self.tray_icon.messageClicked.connect(self._on_notification_clicked)
        
        # Custom output folder tracking (None means use default)
        self._current_output_folder = None
        
        # Organization settings
        self._organization_enabled = self.app_settings.organization_enabled
        self._organize_by_platform = self.app_settings.organize_by_platform
        self._organize_by_date = self.app_settings.organize_by_date
        self._organize_by_quality = self.app_settings.organize_by_quality
        self._organize_by_uploader = self.app_settings.organize_by_uploader
        self._date_format = self.app_settings.date_format

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Top bar for URL input and Settings button
        top_bar_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        self.get_urls_button = QPushButton("Get Download Urls")
        self.settings_button = QPushButton("Settings") # Add Settings button
        top_bar_layout.addWidget(self.url_input)
        top_bar_layout.addWidget(self.get_urls_button)
        top_bar_layout.addWidget(self.settings_button) # Add Settings button to layout
        main_layout.addLayout(top_bar_layout) # Use top_bar_layout instead of url_layout

        # Select All checkbox
        select_all_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Select All")
        select_all_layout.addWidget(self.select_all_checkbox)
        select_all_layout.addStretch()
        main_layout.addLayout(select_all_layout)

        # Preset selection
        preset_layout = QHBoxLayout()
        self.preset_label = QLabel("Preset:")
        self.preset_combobox = QComboBox()
        self.preset_combobox.addItems(DOWNLOAD_PRESETS_LIST)
        # Set default from settings or detect from current quality/format
        if self.app_settings.download_preset in DOWNLOAD_PRESETS_LIST:
            self.preset_combobox.setCurrentText(self.app_settings.download_preset)
        else:
            detected = detect_preset_from_settings(
                self.app_settings.video_resolution,
                self.app_settings.video_format
            )
            self.preset_combobox.setCurrentText(detected)
        # Add tooltips
        for i in range(self.preset_combobox.count()):
            preset_name = self.preset_combobox.itemText(i)
            self.preset_combobox.setItemData(i, DOWNLOAD_PRESET_TOOLTIPS.get(preset_name, ""), Qt.ToolTipRole)
        preset_layout.addWidget(self.preset_label)
        preset_layout.addWidget(self.preset_combobox)
        preset_layout.addStretch()
        main_layout.addLayout(preset_layout)

        # Resolution and Format selection
        resolution_layout = QHBoxLayout()
        self.resolution_label = QLabel("Quality:")
        self.resolution_combobox = QComboBox()
        self.resolution_combobox.addItems(QUALITY_OPTIONS_LIST)
        # Set default quality from settings
        if self.app_settings.video_resolution in QUALITY_OPTIONS_LIST:
            self.resolution_combobox.setCurrentText(self.app_settings.video_resolution)
        resolution_layout.addWidget(self.resolution_label)
        resolution_layout.addWidget(self.resolution_combobox)
        
        # Format selection
        self.format_label = QLabel("Format:")
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(VIDEO_FORMAT_OPTIONS_LIST)
        # Set default format from settings
        if self.app_settings.video_format in VIDEO_FORMAT_OPTIONS_LIST:
            self.format_combobox.setCurrentText(self.app_settings.video_format)
        resolution_layout.addWidget(self.format_label)
        resolution_layout.addWidget(self.format_combobox)
        
        main_layout.addLayout(resolution_layout)
        
        # Subtitle controls
        subtitle_layout = QHBoxLayout()
        self.subtitle_checkbox = QCheckBox("Download Subtitles")
        self.subtitle_checkbox.setChecked(self.app_settings.subtitles_enabled)
        subtitle_layout.addWidget(self.subtitle_checkbox)
        
        self.subtitle_language_label = QLabel("Language:")
        self.subtitle_language_combobox = QComboBox()
        self.subtitle_language_combobox.addItems(SUBTITLE_LANGUAGE_OPTIONS_LIST)
        if self.app_settings.subtitle_language in SUBTITLE_LANGUAGE_OPTIONS_LIST:
            self.subtitle_language_combobox.setCurrentText(self.app_settings.subtitle_language)
        self.subtitle_language_combobox.setEnabled(self.app_settings.subtitles_enabled)
        subtitle_layout.addWidget(self.subtitle_language_label)
        subtitle_layout.addWidget(self.subtitle_language_combobox)
        
        self.embed_subtitles_checkbox = QCheckBox("Embed Subtitles")
        self.embed_subtitles_checkbox.setChecked(self.app_settings.embed_subtitles)
        self.embed_subtitles_checkbox.setEnabled(self.app_settings.subtitles_enabled)
        subtitle_layout.addWidget(self.embed_subtitles_checkbox)
        
        subtitle_layout.addStretch()
        main_layout.addLayout(subtitle_layout)
        
        # Connect subtitle checkbox state change
        self.subtitle_checkbox.stateChanged.connect(self._on_subtitle_checkbox_changed)
        
        # Connect preset change to auto-apply quality/format
        self.preset_combobox.currentTextChanged.connect(self._on_preset_changed)
        
        # Connect quality change to update format options and detect custom preset
        self.resolution_combobox.currentTextChanged.connect(self._on_quality_changed)
        
        # Connect format change to detect custom preset
        self.format_combobox.currentTextChanged.connect(self._update_preset_from_current_settings)

        # Output folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Output Folder:")
        self.folder_combobox = QComboBox()
        self.folder_combobox.setMinimumWidth(150)
        self._populate_folder_combobox()
        self.folder_path_display = QLineEdit()
        self.folder_path_display.setReadOnly(True)
        self.folder_path_display.setText(self.app_settings.download_folder_path)
        self.browse_folder_button = QPushButton("Browse...")
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_combobox)
        folder_layout.addWidget(self.folder_path_display, 1)  # stretch factor 1
        folder_layout.addWidget(self.browse_folder_button)
        main_layout.addLayout(folder_layout)
        
        # Connect folder selection signals
        self.folder_combobox.currentIndexChanged.connect(self._on_folder_combobox_changed)
        self.browse_folder_button.clicked.connect(self._on_browse_folder_clicked)

        # Path preview label for folder organization
        self.path_preview_label = QLabel()
        self.path_preview_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self.path_preview_label)
        self._update_path_preview()

        # Tab widget for Downloads and History
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Downloads tab
        downloads_tab = QWidget()
        downloads_layout = QVBoxLayout(downloads_tab)
        downloads_layout.setContentsMargins(0, 0, 0, 0)

        # Download list
        self.download_table = QTableWidget()
        self.download_table.setColumnCount(5)
        self.download_table.setHorizontalHeaderLabels(["", "Title", "Quality", "Format", "Status"])
        self.download_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.download_table.setSelectionMode(QTableWidget.NoSelection)
        downloads_layout.addWidget(self.download_table)

        self.tab_widget.addTab(downloads_tab, "Downloads")

        # History tab
        self.history_tab = QWidget()
        history_layout = QVBoxLayout(self.history_tab)
        history_layout.setContentsMargins(0, 0, 0, 0)

        # History search
        self.history_search_input = QLineEdit()
        self.history_search_input.setPlaceholderText("Search history...")
        history_layout.addWidget(self.history_search_input)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Title", "Platform", "Size", "Path"])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(2, 100)
        self.history_table.setColumnWidth(3, 80)
        self.history_table.setColumnWidth(4, 200)
        history_layout.addWidget(self.history_table)

        # History action buttons
        history_buttons_layout = QHBoxLayout()
        self.open_file_button = QPushButton("Open File")
        self.open_file_button.setEnabled(False)
        self.open_history_folder_button = QPushButton("Open Folder")
        self.open_history_folder_button.setEnabled(False)
        self.redownload_button = QPushButton("Re-download")
        self.redownload_button.setEnabled(False)
        history_buttons_layout.addWidget(self.open_file_button)
        history_buttons_layout.addWidget(self.open_history_folder_button)
        history_buttons_layout.addWidget(self.redownload_button)
        history_buttons_layout.addStretch()
        history_layout.addLayout(history_buttons_layout)

        self.tab_widget.addTab(self.history_tab, "History")

        # Download button
        self.download_button = QPushButton("Download")
        main_layout.addWidget(self.download_button)
        
        # Stop Download button
        self.stop_download_button = QPushButton("Stop Download")
        self.stop_download_button.setEnabled(False)  # Disabled by default
        main_layout.addWidget(self.stop_download_button)

        # Open Download Folder button
        self.open_folder_button = QPushButton("Open Download Folder")
        main_layout.addWidget(self.open_folder_button)

        # Clear buttons layout
        clear_buttons_layout = QHBoxLayout()
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_all_button = QPushButton("Clear List")
        clear_buttons_layout.addWidget(self.clear_completed_button)
        clear_buttons_layout.addWidget(self.clear_all_button)
        main_layout.addLayout(clear_buttons_layout)

        # Connect signals
        self.get_urls_button.clicked.connect(self.start_fetch)
        self.download_button.clicked.connect(self.start_download)
        self.stop_download_button.clicked.connect(self.stop_download)  # Connect stop button
        self.settings_button.clicked.connect(self._open_settings_dialog) # Connect settings button
        self.open_folder_button.clicked.connect(self._on_open_download_folder_button_clicked)
        self.clear_completed_button.clicked.connect(self._clear_completed_downloads)
        self.clear_all_button.clicked.connect(self._clear_all_downloads)
        self.download_manager.fetch_finished.connect(self.on_fetch_finished)
        self.download_manager.fetch_error.connect(self.on_fetch_error)
        self.download_manager.download_progress.connect(self.on_download_progress)
        self.download_manager.download_finished.connect(self.on_download_finished)
        self.download_manager.download_error.connect(self.on_download_error)
        self.download_manager.download_cancelled.connect(self.on_download_cancelled)  # Connect cancelled signal
        self.select_all_checkbox.stateChanged.connect(self._on_select_all_checkbox_state_changed)

        # History tab signals
        self.history_search_input.textChanged.connect(self._on_history_search_input_textChanged)
        self.history_table.itemSelectionChanged.connect(self._on_history_table_selectionChanged)
        self.open_file_button.clicked.connect(self._on_open_file_button_clicked)
        self.open_history_folder_button.clicked.connect(self._on_open_history_folder_button_clicked)
        self.redownload_button.clicked.connect(self._on_redownload_button_clicked)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_open_download_folder_button_clicked(self):
        """
        Opens the download folder.
        """
        if self.app_settings.download_folder_path and os.path.isdir(self.app_settings.download_folder_path):
            os.startfile(self.app_settings.download_folder_path)
        else:
            QMessageBox.warning(self, "Directory Not Found", "The download directory is not set or does not exist.")

    # _load_stylesheet() removed - theme is now applied at application level in __main__.py

    def _on_select_all_checkbox_state_changed(self, state):
        """
        Handles the state change of the "Select All" checkbox.
        """
        # Set flag to prevent race condition
        self._updating_from_select_all = True
        
        # Handle both integer and Qt.CheckState enum
        is_checked = (state == Qt.Checked) or (state == 2)
        
        # Update all individual checkboxes
        for row in range(self.download_table.rowCount()):
            checkbox_item = self.download_table.cellWidget(row, 0)
            if checkbox_item:
                checkbox_item.setChecked(is_checked)
        
        # Clear flag after updates complete
        self._updating_from_select_all = False

    def _on_item_state_changed(self, state):
        """Handles state changes of individual item checkboxes."""
        # Don't update during bulk "Select All" operation
        if self._updating_from_select_all:
            return
        
        # Check if all items are checked
        all_checked = True
        for row in range(self.download_table.rowCount()):
            checkbox = self.download_table.cellWidget(row, 0)
            if checkbox and not checkbox.isChecked():
                all_checked = False
                break
        
        # Update "Select All" checkbox without triggering its signal
        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setChecked(all_checked)
        self.select_all_checkbox.blockSignals(False)

    def _on_quality_changed(self, quality: str):
        """Updates format dropdown based on quality selection.
        
        When 'Audio Only' is selected, shows audio format options.
        Otherwise, shows video format options.
        
        Args:
            quality (str): The selected quality option.
        """
        # Block format combobox signal during update to prevent multiple custom detections
        self.format_combobox.blockSignals(True)
        
        if quality == "Audio Only":
            self.format_combobox.clear()
            self.format_combobox.addItems(AUDIO_FORMAT_OPTIONS_LIST)
            if self.app_settings.audio_format in AUDIO_FORMAT_OPTIONS_LIST:
                self.format_combobox.setCurrentText(self.app_settings.audio_format)
        else:
            self.format_combobox.clear()
            self.format_combobox.addItems(VIDEO_FORMAT_OPTIONS_LIST)
            if self.app_settings.video_format in VIDEO_FORMAT_OPTIONS_LIST:
                self.format_combobox.setCurrentText(self.app_settings.video_format)
        
        self.format_combobox.blockSignals(False)
        
        # Detect if current selection matches a preset
        self._update_preset_from_current_settings()
        
        # Update path preview when quality changes
        self._update_path_preview()

    def _on_preset_changed(self, preset_name: str):
        """Applies preset settings when a preset is selected.
        
        Args:
            preset_name (str): The selected preset name.
        """
        if preset_name == "Custom":
            return  # Don't change anything for Custom
        
        config = get_preset_config(preset_name)
        if config["quality"] and config["format"]:
            # Block signals to prevent triggering custom detection
            self.resolution_combobox.blockSignals(True)
            self.format_combobox.blockSignals(True)
            
            # Apply quality
            self.resolution_combobox.setCurrentText(config["quality"])
            # Trigger format dropdown update for Audio Only
            self._on_quality_changed(config["quality"])
            # Apply format
            self.format_combobox.setCurrentText(config["format"])
            
            self.resolution_combobox.blockSignals(False)
            self.format_combobox.blockSignals(False)

    def _update_preset_from_current_settings(self):
        """Updates preset dropdown based on current quality/format selection."""
        current_quality = self.resolution_combobox.currentText()
        current_format = self.format_combobox.currentText()
        detected_preset = detect_preset_from_settings(current_quality, current_format)
        
        # Block signals to prevent recursive calls
        self.preset_combobox.blockSignals(True)
        self.preset_combobox.setCurrentText(detected_preset)
        self.preset_combobox.blockSignals(False)

    def _on_subtitle_checkbox_changed(self, state):
        """Handles state change of the subtitle checkbox."""
        is_enabled = state == 2  # Qt.Checked
        self.subtitle_language_combobox.setEnabled(is_enabled)
        self.embed_subtitles_checkbox.setEnabled(is_enabled)

    def _populate_folder_combobox(self) -> None:
        """Populates the folder combobox with default, recent folders, and presets."""
        self.folder_combobox.blockSignals(True)
        self.folder_combobox.clear()
        
        # Add "Use Default" as first option
        self.folder_combobox.addItem("Use Default", "default")
        
        # Add recent folders
        if self.app_settings.recent_folders:
            self.folder_combobox.insertSeparator(self.folder_combobox.count())
            for folder in self.app_settings.recent_folders:
                display_name = os.path.basename(folder) or folder
                self.folder_combobox.addItem(f"Recent: {display_name}", folder)
        
        # Add folder presets
        if self.app_settings.folder_presets:
            self.folder_combobox.insertSeparator(self.folder_combobox.count())
            for name, path in self.app_settings.folder_presets.items():
                self.folder_combobox.addItem(f"Preset: {name}", path)
        
        self.folder_combobox.blockSignals(False)

    def _on_folder_combobox_changed(self, index: int) -> None:
        """Handles folder combobox selection change.
        
        Args:
            index (int): The selected index.
        """
        if index < 0:
            return
        
        folder_path = self.folder_combobox.itemData(index)
        if folder_path == "default":
            self._current_output_folder = None
            self.folder_path_display.setText(self.app_settings.download_folder_path)
        else:
            self._current_output_folder = folder_path
            self.folder_path_display.setText(folder_path)

    def _on_browse_folder_clicked(self) -> None:
        """Opens a folder dialog for selecting custom output folder."""
        start_dir = self._current_output_folder or self.app_settings.download_folder_path
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            start_dir,
            QFileDialog.ShowDirsOnly
        )
        if folder:
            folder = os.path.normpath(folder)
            self._current_output_folder = folder
            self.folder_path_display.setText(folder)
            # Reset combobox to show custom selection
            self.folder_combobox.blockSignals(True)
            self.folder_combobox.setCurrentIndex(-1)
            self.folder_combobox.blockSignals(False)

    def _validate_folder(self, folder_path: str) -> tuple:
        """Validates that a folder exists and is writable.
        
        Args:
            folder_path (str): The folder path to validate.
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not folder_path:
            return False, "No folder path specified."
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            # Try to create it
            try:
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"Created folder: {folder_path}")
            except OSError as e:
                return False, f"Could not create folder: {e}"
        
        # Check if it's a directory
        if not os.path.isdir(folder_path):
            return False, "The specified path is not a directory."
        
        # Check if writable
        if not os.access(folder_path, os.W_OK):
            return False, "The folder is not writable."
        
        return True, ""

    def _add_recent_folder(self, folder_path: str) -> None:
        """Adds a folder to the recent folders list.
        
        Maintains max 5 recent folders. Duplicates are moved to the front.
        
        Args:
            folder_path (str): The folder path to add.
        """
        folder_path = os.path.normpath(folder_path)
        
        # Don't add the default folder to recent
        default_folder = os.path.normpath(self.app_settings.download_folder_path)
        if folder_path == default_folder:
            return
        
        # Remove if already exists (will re-add at front)
        if folder_path in self.app_settings.recent_folders:
            self.app_settings.recent_folders.remove(folder_path)
        
        # Add to front
        self.app_settings.recent_folders.insert(0, folder_path)
        
        # Limit to 5 folders
        self.app_settings.recent_folders = self.app_settings.recent_folders[:5]
        
        # Save settings
        try:
            self.settings_service.save_settings(self.app_settings)
            # Update combobox
            self._populate_folder_combobox()
        except Exception as e:
            logger.error(f"Failed to save recent folders: {e}")

    def _update_path_preview(self) -> None:
        """Updates the path preview label based on organization settings."""
        if not self._organization_enabled:
            self.path_preview_label.setText("Organization: Disabled")
            return
        
        # Build preview path components
        components = []
        
        if self._organize_by_platform:
            components.append("{Platform}")
        
        if self._organize_by_date:
            # Show actual date format preview
            now = datetime.now()
            if self._date_format == "YYYY-MM-DD":
                components.append(now.strftime("%Y-%m-%d"))
            elif self._date_format == "YYYY-MM":
                components.append(now.strftime("%Y-%m"))
            elif self._date_format == "YYYY":
                components.append(now.strftime("%Y"))
        
        if self._organize_by_quality:
            quality = self.resolution_combobox.currentText()
            components.append(quality)
        
        if self._organize_by_uploader:
            components.append("{Uploader}")
        
        if components:
            preview_path = "/".join(components) + "/"
            self.path_preview_label.setText(f"Preview: {preview_path}")
        else:
            self.path_preview_label.setText("Organization: Enabled (no rules selected)")

    def _generate_organized_path(self, base_folder: str, url: str, uploader: str = None) -> str:
        """Generates an organized folder path based on organization settings.
        
        Args:
            base_folder (str): The base output folder.
            url (str): The video URL (for platform detection).
            uploader (str, optional): The uploader/channel name.
            
        Returns:
            str: The organized folder path.
        """
        if not self._organization_enabled:
            return base_folder
        
        components = [base_folder]
        
        # Platform subfolder
        if self._organize_by_platform:
            platform = detect_platform(url)
            components.append(sanitize_folder_name(platform))
        
        # Date subfolder
        if self._organize_by_date:
            now = datetime.now()
            if self._date_format == "YYYY-MM-DD":
                date_folder = now.strftime("%Y-%m-%d")
            elif self._date_format == "YYYY-MM":
                date_folder = now.strftime("%Y-%m")
            elif self._date_format == "YYYY":
                date_folder = now.strftime("%Y")
            else:
                date_folder = now.strftime("%Y-%m")  # Default fallback
            components.append(date_folder)
        
        # Quality subfolder
        if self._organize_by_quality:
            quality = self.resolution_combobox.currentText()
            components.append(sanitize_folder_name(quality))
        
        # Uploader subfolder
        if self._organize_by_uploader and uploader:
            components.append(sanitize_folder_name(uploader))
        
        return os.path.join(*components)

    def _load_initial_settings(self) -> AppSettings:
        """Loads settings on application startup, handling potential errors."""
        try:
            settings = self.settings_service.load_settings()
            logger.info("Settings loaded successfully.")
            return settings
        except Exception as e:
            logger.error(f"Failed to load settings: {e}. Using default settings.")
            QMessageBox.warning(self, "Settings Error", 
                                "Failed to load application settings. Default settings will be used.")
            return AppSettings() # Return default settings on error

    def _get_cookies_path_for_url(self, url: str) -> str:
        """Returns the appropriate cookies file path based on the URL.

        Args:
            url (str): The video URL.

        Returns:
            str: Path to the cookies file, or empty string if not configured.
        """
        url_lower = url.lower()
        if 'bilibili.com' in url_lower or 'b23.tv' in url_lower:
            return self.app_settings.bilibili_cookies_path
        elif 'xiaohongshu.com' in url_lower or 'xhslink.com' in url_lower:
            return self.app_settings.xiaohongshu_cookies_path
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return self.app_settings.facebook_cookies_path
        return ""

    def _open_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(
            self.app_settings.concurrent_downloads_limit,
            self.app_settings.download_folder_path,
            self.app_settings.facebook_cookies_path,
            self.app_settings.bilibili_cookies_path,
            self.app_settings.xiaohongshu_cookies_path,
            self.app_settings.video_resolution,
            self.app_settings.video_format,
            self.app_settings.audio_format,
            self.app_settings.subtitles_enabled,
            self.app_settings.subtitle_language,
            self.app_settings.embed_subtitles,
            self.app_settings.download_preset,
            self.app_settings.folder_presets,
            self.app_settings.organization_enabled,
            self.app_settings.organize_by_platform,
            self.app_settings.organize_by_date,
            self.app_settings.organize_by_quality,
            self.app_settings.organize_by_uploader,
            self.app_settings.date_format,
            self
        )
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()

    def _on_settings_saved(self, new_limit: int, new_download_path: str, new_cookies_path: str,
                           new_bilibili_cookies_path: str, new_xiaohongshu_cookies_path: str,
                           new_video_resolution: str, new_video_format: str, new_audio_format: str,
                           new_subtitles_enabled: bool, new_subtitle_language: str, new_embed_subtitles: bool,
                           new_download_preset: str, new_folder_presets: dict,
                           new_organization_enabled: bool, new_organize_by_platform: bool,
                           new_organize_by_date: bool, new_organize_by_quality: bool,
                           new_organize_by_uploader: bool, new_date_format: str):
        """Handles the settings_saved signal from the SettingsDialog."""
        self.app_settings.concurrent_downloads_limit = new_limit
        self.app_settings.download_folder_path = new_download_path
        self.app_settings.facebook_cookies_path = new_cookies_path
        self.app_settings.bilibili_cookies_path = new_bilibili_cookies_path
        self.app_settings.xiaohongshu_cookies_path = new_xiaohongshu_cookies_path
        self.app_settings.video_resolution = new_video_resolution
        self.app_settings.video_format = new_video_format
        self.app_settings.audio_format = new_audio_format
        self.app_settings.subtitles_enabled = new_subtitles_enabled
        self.app_settings.subtitle_language = new_subtitle_language
        self.app_settings.embed_subtitles = new_embed_subtitles
        self.app_settings.download_preset = new_download_preset
        self.app_settings.folder_presets = new_folder_presets
        self.app_settings.organization_enabled = new_organization_enabled
        self.app_settings.organize_by_platform = new_organize_by_platform
        self.app_settings.organize_by_date = new_organize_by_date
        self.app_settings.organize_by_quality = new_organize_by_quality
        self.app_settings.organize_by_uploader = new_organize_by_uploader
        self.app_settings.date_format = new_date_format
        
        # Update local organization settings
        self._organization_enabled = new_organization_enabled
        self._organize_by_platform = new_organize_by_platform
        self._organize_by_date = new_organize_by_date
        self._organize_by_quality = new_organize_by_quality
        self._organize_by_uploader = new_organize_by_uploader
        self._date_format = new_date_format
        
        # Update subtitle controls in main window
        self.subtitle_checkbox.setChecked(new_subtitles_enabled)
        if new_subtitle_language in SUBTITLE_LANGUAGE_OPTIONS_LIST:
            self.subtitle_language_combobox.setCurrentText(new_subtitle_language)
        self.embed_subtitles_checkbox.setChecked(new_embed_subtitles)
        
        # Update preset dropdown in main window
        if new_download_preset in DOWNLOAD_PRESETS_LIST:
            self.preset_combobox.setCurrentText(new_download_preset)
        
        # Update folder combobox with new presets and update path display
        self._populate_folder_combobox()
        self.folder_path_display.setText(self._current_output_folder or new_download_path)
        
        # Update path preview
        self._update_path_preview()
        
        try:
            self.settings_service.save_settings(self.app_settings)
            self.download_manager.update_settings(self.app_settings)
            QMessageBox.information(self, "Settings Saved", 
                                    f"Settings saved successfully.")
            logger.info(f"Settings saved: {self.app_settings}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Save Error", 
                                 f"Failed to save settings: {e}. Please try again.")

    def _find_row_by_url(self, video_url):
        """Finds a row in the table by its video URL."""
        for row in range(self.download_table.rowCount()):
            item = self.download_table.item(row, 1) # Title item
            if item and item.data(Qt.UserRole) == video_url:
                return row
        return -1

    def _update_item_status(self, row, status, text_override=None, progress_value=None):
        """Updates the status and text of a table row."""
        progress_bar = self.download_table.cellWidget(row, 4)  # Status is now column 4
        if isinstance(progress_bar, QProgressBar):
            if status == DownloadStatus.DOWNLOADING and progress_value is not None:
                progress_bar.setValue(int(progress_value))
                progress_bar.setFormat(f"Downloading {progress_value}%")
            elif status == DownloadStatus.COMPLETED:
                progress_bar.setValue(100)
                progress_bar.setFormat("Completed")
            elif status == DownloadStatus.ERROR:
                progress_bar.setValue(0)
                progress_bar.setFormat("Error")
            elif status == DownloadStatus.CANCELLED:
                progress_bar.setValue(0)
                progress_bar.setFormat("Cancelled")
            else:
                progress_bar.setValue(0)
                progress_bar.setFormat(status.name.replace('_', ' ').title())
        
        if text_override and status != DownloadStatus.DOWNLOADING: 
            # Only update title text if not downloading (to avoid flickering or overwriting)
            # Actually, text_override was used for progress in title before. 
            # Now we use progress bar, so we might not need text_override for progress anymore.
            # But let's keep it for other uses if any.
            title_item = self.download_table.item(row, 1)
            if title_item:
                title_item.setText(text_override)

    def _set_fetch_button_loading_state(self, is_loading: bool) -> None:
        """Sets the loading state of the Get Download Urls button.
        
        Args:
            is_loading (bool): True to show loading state, False to restore normal state.
        """
        if is_loading:
            self.get_urls_button.setText("Fetching URLs...")
            self.get_urls_button.setEnabled(False)
        else:
            self.get_urls_button.setText("Get Download Urls")
            self.get_urls_button.setEnabled(True)

    def _set_download_button_loading_state(self, is_loading: bool, current: int = 0, total: int = 0) -> None:
        """Sets the loading state of the Download button with progress tracking.
        
        Args:
            is_loading (bool): True to show loading state, False to restore normal state.
            current (int): Current number of completed downloads.
            total (int): Total number of downloads in queue.
        """
        if is_loading:
            if total > 0:
                self.download_button.setText(f"Downloading {current}/{total}")
            else:
                self.download_button.setText("Downloading...")
            self.download_button.setEnabled(False)
        else:
            self.download_button.setText("Download")
            self.download_button.setEnabled(True)

    def start_fetch(self) -> None:
        """
        Starts fetching video information from the URL in the input box.
        """
        url = self.url_input.text()
        if url:
            if not URLValidator.is_valid_url(url):
                QMessageBox.warning(self, "Invalid URL", "The entered URL is not supported.")
                return

            self._set_fetch_button_loading_state(True)
            cookies_path = self._get_cookies_path_for_url(url)
            self.download_manager.start_fetch_job(url, cookies_path)

    def start_download(self):
        """
        Starts downloading the selected videos.
        """
        # Determine base output folder
        base_folder = self._current_output_folder or self.app_settings.download_folder_path
        
        # Validate base folder before starting downloads
        is_valid, error_message = self._validate_folder(base_folder)
        if not is_valid:
            QMessageBox.critical(self, "Folder Error", f"Cannot download to the selected folder:\n{error_message}")
            return
        
        video_urls_to_queue = []
        for row in range(self.download_table.rowCount()):
            checkbox_item = self.download_table.cellWidget(row, 0)
            if checkbox_item and checkbox_item.isChecked():
                title_item = self.download_table.item(row, 1)
                video_url = title_item.data(Qt.UserRole)
                if video_url:
                    video_urls_to_queue.append(video_url)
                    self._update_item_status(row, DownloadStatus.QUEUED)
        
        if video_urls_to_queue:
            # Generate organized output folder if organization is enabled
            # Use first URL to determine platform for the batch
            first_url = video_urls_to_queue[0] if video_urls_to_queue else ""
            output_folder = self._generate_organized_path(base_folder, first_url)
            
            # Create organized folder if it doesn't exist
            if self._organization_enabled and output_folder != base_folder:
                is_valid, error_message = self._validate_folder(output_folder)
                if not is_valid:
                    QMessageBox.critical(self, "Folder Error", 
                                         f"Cannot create organized folder:\n{error_message}")
                    return
            
            # Initialize progress tracking
            self._download_queue_total = len(video_urls_to_queue)
            self._download_completed_count = 0
            self._batch_success_count = 0
            self._batch_fail_count = 0
            self._set_download_button_loading_state(True, 0, self._download_queue_total)
            
            # Enable stop button
            self.stop_download_button.setEnabled(True)
            
            selected_resolution = self.resolution_combobox.currentText()
            resolution_format = get_format_string(selected_resolution)
            selected_format = self.format_combobox.currentText()
            
            # Determine format based on quality selection
            if selected_resolution == "Audio Only":
                video_format = "mp4"  # Not used for audio-only
                audio_format = get_audio_format_ext(selected_format)
            else:
                video_format = get_video_format_ext(selected_format)
                audio_format = "m4a"  # Not used for video downloads
            
            # Get subtitle settings
            subtitles_enabled = self.subtitle_checkbox.isChecked()
            subtitle_language = get_subtitle_lang_code(self.subtitle_language_combobox.currentText())
            embed_subtitles = self.embed_subtitles_checkbox.isChecked()
            
            self.download_manager.start_download_job(
                video_urls_to_queue, resolution_format, video_format, audio_format,
                subtitles_enabled, subtitle_language, embed_subtitles,
                output_folder
            )
            
            # Add to recent folders if using custom folder
            if self._current_output_folder:
                self._add_recent_folder(self._current_output_folder)
    
    def stop_download(self) -> None:
        """Stops all active and queued downloads.
        
        Disables the stop button immediately to prevent multiple clicks (debouncing).
        Calls the download manager to cancel all downloads.
        """
        # Disable stop button immediately (debouncing)
        self.stop_download_button.setEnabled(False)
        
        # Call download manager to stop all downloads
        self.download_manager.stop_all_downloads()

    def on_fetch_finished(self, videos):
        """
        Handles the finished signal from the FetchWorker.
        """
        self._set_fetch_button_loading_state(False)
        if videos:
            for video_info in videos:
                row_position = self.download_table.rowCount()
                self.download_table.insertRow(row_position)

                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self._on_item_state_changed)
                self.download_table.setCellWidget(row_position, 0, checkbox)
                
                # Update "Select All" checkbox state if a new unchecked item is added
                if self.select_all_checkbox.isChecked():
                    self.select_all_checkbox.blockSignals(True)
                    self.select_all_checkbox.setChecked(False)
                    self.select_all_checkbox.blockSignals(False)

                title = video_info.get('title', 'Unknown Title')
                # Try multiple field names for video URL
                # Single videos use 'webpage_url' or 'original_url'
                # Playlist entries use 'url'
                video_url = video_info.get('webpage_url') or video_info.get('url') or video_info.get('original_url', '')
                title_item = QTableWidgetItem(title)
                title_item.setData(Qt.UserRole, video_url)
                self.download_table.setItem(row_position, 1, title_item)

                # Quality column
                resolution = self.resolution_combobox.currentText()
                resolution_item = QTableWidgetItem(resolution)
                self.download_table.setItem(row_position, 2, resolution_item)

                # Format column
                format_text = self.format_combobox.currentText()
                format_item = QTableWidgetItem(format_text)
                self.download_table.setItem(row_position, 3, format_item)

                # Use QProgressBar for status (now column 4)
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setValue(0)
                progress_bar.setFormat(DownloadStatus.PENDING.name.replace('_', ' ').title())
                self.download_table.setCellWidget(row_position, 4, progress_bar)


    def on_fetch_error(self, error_message):
        """
        Handles the error signal from the FetchWorker.
        """
        self._set_fetch_button_loading_state(False)
        QMessageBox.critical(self, "Error", error_message)

    def on_download_progress(self, video_url, progress_data):
        """
        Handles the progress signal from the DownloadWorker for a specific video.
        """
        row = self._find_row_by_url(video_url)
        if row != -1:
            progress = progress_data.get('_percent_str', '0.0%')
            # Strip ANSI escape codes
            import re
            clean_progress = re.sub(r'\x1b\[[0-9;]*m', '', progress)
            
            try:
                # Extract number from string like " 45.5%"
                percent_str = clean_progress.strip().replace('%', '')
                percent = float(percent_str)
                self._update_item_status(row, DownloadStatus.DOWNLOADING, progress_value=percent)
            except ValueError:
                # Fallback if parsing fails
                self._update_item_status(row, DownloadStatus.DOWNLOADING, text_override=f"{self.download_table.item(row, 1).text()} ({clean_progress})")

    def _check_and_enable_button(self) -> None:
        """Checks if all downloads are complete and re-enables the download button."""
        if self.download_manager.is_idle():
            self._set_download_button_loading_state(False)
            # Also disable stop button when all downloads complete
            self.stop_download_button.setEnabled(False)
            
            # Show completion notification if we processed a batch
            if self._download_queue_total > 0:
                self._show_completion_notification()

    def _show_completion_notification(self):
        """Displays a system notification with download results."""
        title = "Downloads Complete"
        message = f"Successful: {self._batch_success_count}, Failed: {self._batch_fail_count}"
        
        if self._batch_fail_count == 0:
            message = "All downloads completed successfully."
        
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 10000)

    def _on_notification_clicked(self):
        """Brings the window to front when notification is clicked."""
        self.show()
        self.activateWindow()
        self.raise_()

    def _record_to_history(self, video_url: str, status: str) -> None:
        """Records a download to history.

        Args:
            video_url: The URL of the video.
            status: The status string ("completed", "failed", "cancelled").
        """
        row = self._find_row_by_url(video_url)
        if row == -1:
            return

        try:
            title = self.download_table.item(row, 1).text() if self.download_table.item(row, 1) else "Unknown"
            quality = self.download_table.item(row, 2).text() if self.download_table.item(row, 2) else "Unknown"
            format_str = self.download_table.item(row, 3).text() if self.download_table.item(row, 3) else "Unknown"
            platform = detect_platform(video_url)

            # Construct file path
            base_folder = self._current_output_folder or self.app_settings.download_folder_path
            if self._organization_enabled:
                base_folder = self._generate_organized_path(base_folder, video_url)

            # Get format extension
            if quality == "Audio Only":
                ext = get_audio_format_ext(format_str)
            else:
                ext = get_video_format_ext(format_str)

            safe_title = sanitize_folder_name(title)
            file_path = os.path.join(base_folder, f"{safe_title}.{ext}")

            # Get file size if file exists
            file_size = 0
            if status == "completed" and os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    pass

            entry = HistoryEntry(
                url=video_url,
                title=title,
                platform=platform,
                download_date=HistoryEntry.create_timestamp(),
                file_path=file_path,
                file_size=file_size,
                quality=quality,
                format=format_str,
                status=status
            )
            self.history_service.add_entry(entry)
        except Exception as e:
            logger.error(f"Failed to record download to history: {e}")

    def on_download_finished(self, video_url, subtitle_status=""):
        """
        Handles the finished signal from the DownloadWorker for a specific video.
        
        Args:
            video_url (str): The URL of the completed video.
            subtitle_status (str): Status of subtitles: "with_subs", "no_subs", "subs_embedded", or "".
        """
        row = self._find_row_by_url(video_url)
        if row != -1:
            # Update status based on subtitle result
            progress_bar = self.download_table.cellWidget(row, 4)
            if isinstance(progress_bar, QProgressBar):
                progress_bar.setValue(100)
                if subtitle_status == "subs_embedded":
                    progress_bar.setFormat("Completed (Subs Embedded)")
                elif subtitle_status == "with_subs":
                    progress_bar.setFormat("Completed (With Subs)")
                elif subtitle_status == "no_subs":
                    progress_bar.setFormat("Completed (No Subs)")
                else:
                    progress_bar.setFormat("Completed")

        # Record to history
        self._record_to_history(video_url, "completed")
        
        # Update progress
        self._download_completed_count += 1
        self._batch_success_count += 1
        if self._download_queue_total > 0:
            self._set_download_button_loading_state(True, self._download_completed_count, self._download_queue_total)
        
        self._check_and_enable_button()

    def on_download_error(self, video_url, error_message):
        """
        Handles the error signal from the DownloadWorker for a specific video.
        """
        row = self._find_row_by_url(video_url)
        if row != -1:
            self._update_item_status(row, DownloadStatus.ERROR)
        QMessageBox.warning(self, "Download Error", f"Error downloading {video_url}: {error_message}")

        # Record to history
        self._record_to_history(video_url, "failed")
        
        # Update progress (errors count as "completed")
        self._download_completed_count += 1
        self._batch_fail_count += 1
        if self._download_queue_total > 0:
            self._set_download_button_loading_state(True, self._download_completed_count, self._download_queue_total)
        
        self._check_and_enable_button()
    
    def on_download_cancelled(self, video_url: str) -> None:
        """Handles the cancelled signal from the DownloadWorker for a specific video.
        
        Updates the download status to CANCELLED and manages progress tracking.
        
        Args:
            video_url (str): The URL of the cancelled video.
        """
        row = self._find_row_by_url(video_url)
        if row != -1:
            self._update_item_status(row, DownloadStatus.CANCELLED)

        # Record to history
        self._record_to_history(video_url, "cancelled")
        
        # Update progress (cancelled downloads count as "completed")
        self._download_completed_count += 1
        # Cancelled items are neither success nor fail in this context, or could be fail? 
        # Let's count them as fail for notification summary or just ignore?
        # Story says "Successful: X, Failed: Y". Cancelled is technically failed to download.
        self._batch_fail_count += 1 
        
        if self._download_queue_total > 0:
            self._set_download_button_loading_state(True, self._download_completed_count, self._download_queue_total)
        
        self._check_and_enable_button()

    # History tab methods
    def _format_file_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _format_date(self, iso_date: str) -> str:
        """Format ISO 8601 date to human-readable string."""
        try:
            dt = datetime.fromisoformat(iso_date)
            return dt.strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            return iso_date

    def _populate_history_table(self, entries=None) -> None:
        """Populates the history table with entries.

        Args:
            entries: List of HistoryEntry objects. If None, uses all history.
        """
        if entries is None:
            entries = self.history_service.get_all()

        self.history_table.setRowCount(0)
        for entry in entries:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)

            # Date
            date_item = QTableWidgetItem(self._format_date(entry.download_date))
            date_item.setData(Qt.UserRole, entry.id)
            self.history_table.setItem(row, 0, date_item)

            # Title
            title_item = QTableWidgetItem(entry.title)
            self.history_table.setItem(row, 1, title_item)

            # Platform
            platform_item = QTableWidgetItem(entry.platform)
            self.history_table.setItem(row, 2, platform_item)

            # Size
            size_item = QTableWidgetItem(self._format_file_size(entry.file_size))
            self.history_table.setItem(row, 3, size_item)

            # Path
            path_item = QTableWidgetItem(entry.file_path)
            path_item.setToolTip(entry.file_path)
            self.history_table.setItem(row, 4, path_item)

    def _get_history_entry_at_row(self, row: int) -> HistoryEntry | None:
        """Gets the HistoryEntry for a given row.

        Args:
            row: The row index.

        Returns:
            HistoryEntry if found, None otherwise.
        """
        if row < 0 or row >= self.history_table.rowCount():
            return None
        date_item = self.history_table.item(row, 0)
        if date_item:
            entry_id = date_item.data(Qt.UserRole)
            return self.history_service.get_entry_by_id(entry_id)
        return None

    def _on_tab_changed(self, index: int) -> None:
        """Handles tab change to refresh history when History tab is selected."""
        if index == 1:  # History tab
            self._populate_history_table()

    def _on_history_search_input_textChanged(self, text: str) -> None:
        """Handles history search input changes."""
        entries = self.history_service.search(text)
        self._populate_history_table(entries)

    def _on_history_table_selectionChanged(self) -> None:
        """Enables/disables history action buttons based on selection."""
        has_selection = self.history_table.currentRow() >= 0
        self.open_file_button.setEnabled(has_selection)
        self.open_history_folder_button.setEnabled(has_selection)
        self.redownload_button.setEnabled(has_selection)

    def _on_open_file_button_clicked(self) -> None:
        """Opens the selected history entry's file."""
        row = self.history_table.currentRow()
        entry = self._get_history_entry_at_row(row)
        if entry:
            if os.path.exists(entry.file_path):
                os.startfile(entry.file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"File no longer exists:\n{entry.file_path}")

    def _on_open_history_folder_button_clicked(self) -> None:
        """Opens the folder containing the selected history entry's file."""
        row = self.history_table.currentRow()
        entry = self._get_history_entry_at_row(row)
        if entry:
            folder_path = os.path.dirname(entry.file_path)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                QMessageBox.warning(self, "Folder Not Found", f"Folder no longer exists:\n{folder_path}")

    def _on_redownload_button_clicked(self) -> None:
        """Re-downloads the selected history entry."""
        row = self.history_table.currentRow()
        entry = self._get_history_entry_at_row(row)
        if entry:
            self.url_input.setText(entry.url)
            self.tab_widget.setCurrentIndex(0)  # Switch to Downloads tab
            self.start_fetch()

    def _clear_completed_downloads(self):
        """Removes all completed downloads from the list."""
        rows_to_remove = []
        for row in range(self.download_table.rowCount()):
            # Check status widget (QProgressBar in column 4)
            progress_bar = self.download_table.cellWidget(row, 4)
            if isinstance(progress_bar, QProgressBar):
                if progress_bar.format() == "Completed":
                    rows_to_remove.append(row)
        
        # Remove in reverse order to maintain indices
        for row in sorted(rows_to_remove, reverse=True):
            self.download_table.removeRow(row)

    def _clear_all_downloads(self):
        """Removes all downloads from the list. 
        Stops active downloads first if any.
        """
        if not self.download_manager.is_idle():
            reply = QMessageBox.question(
                self, 
                "Active Downloads", 
                "Downloads are currently in progress. Clearing the list will stop them. Continue?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            
            self.stop_download()
            
        self.download_table.setRowCount(0)
        # Reset counters
        self._download_queue_total = 0
        self._download_completed_count = 0
        self._batch_success_count = 0
        self._batch_fail_count = 0
        self._set_download_button_loading_state(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
