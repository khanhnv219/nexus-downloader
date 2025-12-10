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
)
from nexus_downloader.ui.settings_dialog import SettingsDialog
from nexus_downloader.services.settings_service import SettingsService, AppSettings # Import SettingsService and AppSettings
from nexus_downloader.core.data_models import DownloadStatus, DownloadItem
from nexus_downloader.core.url_validator import URLValidator
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
        self._load_stylesheet()

        self.settings_service = SettingsService() # Instantiate SettingsService
        self.app_settings = self._load_initial_settings() # Load settings on startup

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
        
        # Connect quality change to update format options
        self.resolution_combobox.currentTextChanged.connect(self._on_quality_changed)

        # Download list
        self.download_table = QTableWidget()
        self.download_table.setColumnCount(5)
        self.download_table.setHorizontalHeaderLabels(["", "Title", "Quality", "Format", "Status"])
        self.download_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.download_table.setSelectionMode(QTableWidget.NoSelection)
        main_layout.addWidget(self.download_table)

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

    def _on_open_download_folder_button_clicked(self):
        """
        Opens the download folder.
        """
        if self.app_settings.download_folder_path and os.path.isdir(self.app_settings.download_folder_path):
            os.startfile(self.app_settings.download_folder_path)
        else:
            QMessageBox.warning(self, "Directory Not Found", "The download directory is not set or does not exist.")

    def _load_stylesheet(self):
        """Loads the stylesheet for the application."""
        style_file = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_file):
            with open(style_file, "r") as f:
                self.setStyleSheet(f.read())

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
            self
        )
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()

    def _on_settings_saved(self, new_limit: int, new_download_path: str, new_cookies_path: str,
                           new_bilibili_cookies_path: str, new_xiaohongshu_cookies_path: str,
                           new_video_resolution: str, new_video_format: str, new_audio_format: str):
        """Handles the settings_saved signal from the SettingsDialog."""
        self.app_settings.concurrent_downloads_limit = new_limit
        self.app_settings.download_folder_path = new_download_path
        self.app_settings.facebook_cookies_path = new_cookies_path
        self.app_settings.bilibili_cookies_path = new_bilibili_cookies_path
        self.app_settings.xiaohongshu_cookies_path = new_xiaohongshu_cookies_path
        self.app_settings.video_resolution = new_video_resolution
        self.app_settings.video_format = new_video_format
        self.app_settings.audio_format = new_audio_format
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
            
            self.download_manager.start_download_job(
                video_urls_to_queue, resolution_format, video_format, audio_format
            )
    
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

    def on_download_finished(self, video_url):
        """
        Handles the finished signal from the DownloadWorker for a specific video.
        """
        row = self._find_row_by_url(video_url)
        if row != -1:
            self._update_item_status(row, DownloadStatus.COMPLETED)
        
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
        
        # Update progress (cancelled downloads count as "completed")
        self._download_completed_count += 1
        # Cancelled items are neither success nor fail in this context, or could be fail? 
        # Let's count them as fail for notification summary or just ignore?
        # Story says "Successful: X, Failed: Y". Cancelled is technically failed to download.
        self._batch_fail_count += 1 
        
        if self._download_queue_total > 0:
            self._set_download_button_loading_state(True, self._download_completed_count, self._download_queue_total)
        
        self._check_and_enable_button()

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
