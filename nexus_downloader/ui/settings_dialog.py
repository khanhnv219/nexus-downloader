from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, 
    QLineEdit, QFileDialog, QComboBox, QCheckBox, QListWidget, QInputDialog,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Signal
from typing import Dict

from nexus_downloader.core.yt_dlp_service import (
    QUALITY_OPTIONS_LIST,
    VIDEO_FORMAT_OPTIONS_LIST,
    AUDIO_FORMAT_OPTIONS_LIST,
    SUBTITLE_LANGUAGE_OPTIONS_LIST,
    DOWNLOAD_PRESETS_LIST,
)

class SettingsDialog(QDialog):
    settings_saved = Signal(int, str, str, str, str, str, str, str, bool, str, bool, str, dict)
    # limit, download_path, fb_cookies, bilibili_cookies, xiaohongshu_cookies, resolution, 
    # video_format, audio_format, subtitles_enabled, subtitle_language, embed_subtitles, download_preset, folder_presets

    def __init__(self, current_concurrent_downloads_limit: int, current_download_folder_path: str,
                 current_facebook_cookies_path: str, current_bilibili_cookies_path: str,
                 current_xiaohongshu_cookies_path: str, current_video_resolution: str,
                 current_video_format: str, current_audio_format: str,
                 current_subtitles_enabled: bool, current_subtitle_language: str,
                 current_embed_subtitles: bool, current_download_preset: str,
                 current_folder_presets: Dict[str, str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 680)
        
        self.current_folder_presets = current_folder_presets.copy() if current_folder_presets else {}

        self.current_concurrent_downloads_limit = current_concurrent_downloads_limit
        self.current_download_folder_path = current_download_folder_path
        self.current_facebook_cookies_path = current_facebook_cookies_path
        self.current_bilibili_cookies_path = current_bilibili_cookies_path
        self.current_xiaohongshu_cookies_path = current_xiaohongshu_cookies_path
        self.current_video_resolution = current_video_resolution
        self.current_video_format = current_video_format
        self.current_audio_format = current_audio_format
        self.current_subtitles_enabled = current_subtitles_enabled
        self.current_subtitle_language = current_subtitle_language
        self.current_embed_subtitles = current_embed_subtitles
        self.current_download_preset = current_download_preset

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Concurrent Downloads Limit
        concurrent_downloads_layout = QHBoxLayout()
        self.concurrent_downloads_label = QLabel("Concurrent Downloads Limit:")
        self.concurrent_downloads_spinbox = QSpinBox()
        self.concurrent_downloads_spinbox.setRange(1, 10) # Default range, will be validated
        self.concurrent_downloads_spinbox.setValue(self.current_concurrent_downloads_limit)
        concurrent_downloads_layout.addWidget(self.concurrent_downloads_label)
        concurrent_downloads_layout.addWidget(self.concurrent_downloads_spinbox)
        main_layout.addLayout(concurrent_downloads_layout)

        # Download Folder Path
        download_path_layout = QHBoxLayout()
        self.download_path_label = QLabel("Download Folder:")
        self.download_path_lineedit = QLineEdit(self.current_download_folder_path)
        self.download_path_lineedit.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        download_path_layout.addWidget(self.download_path_label)
        download_path_layout.addWidget(self.download_path_lineedit)
        download_path_layout.addWidget(self.browse_button)
        main_layout.addLayout(download_path_layout)

        # Facebook Cookies Path
        cookies_path_layout = QHBoxLayout()
        self.cookies_path_label = QLabel("Facebook Cookies:")
        self.cookies_path_lineedit = QLineEdit(self.current_facebook_cookies_path)
        self.cookies_path_lineedit.setReadOnly(True)
        self.cookies_browse_button = QPushButton("Browse...")
        cookies_path_layout.addWidget(self.cookies_path_label)
        cookies_path_layout.addWidget(self.cookies_path_lineedit)
        cookies_path_layout.addWidget(self.cookies_browse_button)
        main_layout.addLayout(cookies_path_layout)

        # Bilibili Cookies Path
        bilibili_cookies_layout = QHBoxLayout()
        self.bilibili_cookies_label = QLabel("Bilibili Cookies:")
        self.bilibili_cookies_lineedit = QLineEdit(self.current_bilibili_cookies_path)
        self.bilibili_cookies_lineedit.setReadOnly(True)
        self.bilibili_cookies_browse_button = QPushButton("Browse...")
        bilibili_cookies_layout.addWidget(self.bilibili_cookies_label)
        bilibili_cookies_layout.addWidget(self.bilibili_cookies_lineedit)
        bilibili_cookies_layout.addWidget(self.bilibili_cookies_browse_button)
        main_layout.addLayout(bilibili_cookies_layout)

        # Xiaohongshu Cookies Path
        xiaohongshu_cookies_layout = QHBoxLayout()
        self.xiaohongshu_cookies_label = QLabel("Xiaohongshu Cookies:")
        self.xiaohongshu_cookies_lineedit = QLineEdit(self.current_xiaohongshu_cookies_path)
        self.xiaohongshu_cookies_lineedit.setReadOnly(True)
        self.xiaohongshu_cookies_browse_button = QPushButton("Browse...")
        xiaohongshu_cookies_layout.addWidget(self.xiaohongshu_cookies_label)
        xiaohongshu_cookies_layout.addWidget(self.xiaohongshu_cookies_lineedit)
        xiaohongshu_cookies_layout.addWidget(self.xiaohongshu_cookies_browse_button)
        main_layout.addLayout(xiaohongshu_cookies_layout)

        # Video Resolution
        video_resolution_layout = QHBoxLayout()
        self.video_resolution_label = QLabel("Default Quality:")
        self.video_resolution_combobox = QComboBox()
        self.video_resolution_combobox.addItems(QUALITY_OPTIONS_LIST)
        self.video_resolution_combobox.setCurrentText(self.current_video_resolution)
        video_resolution_layout.addWidget(self.video_resolution_label)
        video_resolution_layout.addWidget(self.video_resolution_combobox)
        main_layout.addLayout(video_resolution_layout)

        # Video Format
        video_format_layout = QHBoxLayout()
        self.video_format_label = QLabel("Default Video Format:")
        self.video_format_combobox = QComboBox()
        self.video_format_combobox.addItems(VIDEO_FORMAT_OPTIONS_LIST)
        self.video_format_combobox.setCurrentText(self.current_video_format)
        video_format_layout.addWidget(self.video_format_label)
        video_format_layout.addWidget(self.video_format_combobox)
        main_layout.addLayout(video_format_layout)

        # Audio Format
        audio_format_layout = QHBoxLayout()
        self.audio_format_label = QLabel("Default Audio Format:")
        self.audio_format_combobox = QComboBox()
        self.audio_format_combobox.addItems(AUDIO_FORMAT_OPTIONS_LIST)
        self.audio_format_combobox.setCurrentText(self.current_audio_format)
        audio_format_layout.addWidget(self.audio_format_label)
        audio_format_layout.addWidget(self.audio_format_combobox)
        main_layout.addLayout(audio_format_layout)

        # Default Preset
        preset_layout = QHBoxLayout()
        self.preset_label = QLabel("Default Preset:")
        self.preset_combobox = QComboBox()
        self.preset_combobox.addItems(DOWNLOAD_PRESETS_LIST)
        self.preset_combobox.setCurrentText(self.current_download_preset)
        preset_layout.addWidget(self.preset_label)
        preset_layout.addWidget(self.preset_combobox)
        main_layout.addLayout(preset_layout)

        # Subtitles Section
        subtitles_enabled_layout = QHBoxLayout()
        self.subtitles_enabled_checkbox = QCheckBox("Enable Subtitles by Default")
        self.subtitles_enabled_checkbox.setChecked(self.current_subtitles_enabled)
        subtitles_enabled_layout.addWidget(self.subtitles_enabled_checkbox)
        main_layout.addLayout(subtitles_enabled_layout)

        subtitle_language_layout = QHBoxLayout()
        self.subtitle_language_label = QLabel("Default Subtitle Language:")
        self.subtitle_language_combobox = QComboBox()
        self.subtitle_language_combobox.addItems(SUBTITLE_LANGUAGE_OPTIONS_LIST)
        self.subtitle_language_combobox.setCurrentText(self.current_subtitle_language)
        self.subtitle_language_combobox.setEnabled(self.current_subtitles_enabled)
        subtitle_language_layout.addWidget(self.subtitle_language_label)
        subtitle_language_layout.addWidget(self.subtitle_language_combobox)
        main_layout.addLayout(subtitle_language_layout)

        embed_subtitles_layout = QHBoxLayout()
        self.embed_subtitles_checkbox = QCheckBox("Embed Subtitles in Video (requires FFmpeg)")
        self.embed_subtitles_checkbox.setChecked(self.current_embed_subtitles)
        self.embed_subtitles_checkbox.setEnabled(self.current_subtitles_enabled)
        embed_subtitles_layout.addWidget(self.embed_subtitles_checkbox)
        main_layout.addLayout(embed_subtitles_layout)

        # Connect subtitle checkbox to enable/disable dependent controls
        self.subtitles_enabled_checkbox.stateChanged.connect(self._on_subtitles_enabled_changed)

        # Folder Presets Section
        presets_group = QGroupBox("Folder Presets")
        presets_layout = QVBoxLayout(presets_group)
        
        self.presets_list = QListWidget()
        self.presets_list.setMaximumHeight(80)
        self._refresh_presets_list()
        presets_layout.addWidget(self.presets_list)
        
        presets_buttons_layout = QHBoxLayout()
        self.add_preset_button = QPushButton("Add Preset")
        self.remove_preset_button = QPushButton("Remove Preset")
        presets_buttons_layout.addWidget(self.add_preset_button)
        presets_buttons_layout.addWidget(self.remove_preset_button)
        presets_layout.addLayout(presets_buttons_layout)
        
        main_layout.addWidget(presets_group)
        
        # Connect preset buttons
        self.add_preset_button.clicked.connect(self._on_add_preset_clicked)
        self.remove_preset_button.clicked.connect(self._on_remove_preset_clicked)

        # Spacer
        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Connections
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.cookies_browse_button.clicked.connect(self._on_cookies_browse_clicked)
        self.bilibili_cookies_browse_button.clicked.connect(self._on_bilibili_cookies_browse_clicked)
        self.xiaohongshu_cookies_browse_button.clicked.connect(self._on_xiaohongshu_cookies_browse_clicked)

    def _on_save_clicked(self):
        new_limit = self.concurrent_downloads_spinbox.value()
        new_download_path = self.download_path_lineedit.text()
        new_cookies_path = self.cookies_path_lineedit.text()
        new_bilibili_cookies_path = self.bilibili_cookies_lineedit.text()
        new_xiaohongshu_cookies_path = self.xiaohongshu_cookies_lineedit.text()
        new_video_resolution = self.video_resolution_combobox.currentText()
        new_video_format = self.video_format_combobox.currentText()
        new_audio_format = self.audio_format_combobox.currentText()
        new_subtitles_enabled = self.subtitles_enabled_checkbox.isChecked()
        new_subtitle_language = self.subtitle_language_combobox.currentText()
        new_embed_subtitles = self.embed_subtitles_checkbox.isChecked()
        new_download_preset = self.preset_combobox.currentText()
        self.settings_saved.emit(
            new_limit, new_download_path, new_cookies_path, new_bilibili_cookies_path,
            new_xiaohongshu_cookies_path, new_video_resolution, new_video_format, new_audio_format,
            new_subtitles_enabled, new_subtitle_language, new_embed_subtitles, new_download_preset,
            self.current_folder_presets
        )
        self.accept()

    def _refresh_presets_list(self) -> None:
        """Refreshes the presets list widget with current folder presets."""
        self.presets_list.clear()
        for name, path in self.current_folder_presets.items():
            self.presets_list.addItem(f"{name}: {path}")

    def _on_add_preset_clicked(self) -> None:
        """Opens dialogs to add a new folder preset."""
        name, ok = QInputDialog.getText(self, "Add Preset", "Enter preset name:")
        if not ok or not name.strip():
            return
        
        name = name.strip()
        if name in self.current_folder_presets:
            QMessageBox.warning(self, "Duplicate Name", f"A preset named '{name}' already exists.")
            return
        
        folder = QFileDialog.getExistingDirectory(self, f"Select folder for preset '{name}'")
        if folder:
            self.current_folder_presets[name] = folder
            self._refresh_presets_list()

    def _on_remove_preset_clicked(self) -> None:
        """Removes the selected preset from the list."""
        current_item = self.presets_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a preset to remove.")
            return
        
        # Extract preset name from list item text (format: "name: path")
        item_text = current_item.text()
        preset_name = item_text.split(":")[0].strip()
        
        if preset_name in self.current_folder_presets:
            del self.current_folder_presets[preset_name]
            self._refresh_presets_list()

    def _on_subtitles_enabled_changed(self, state):
        """Handles the state change of the subtitles enabled checkbox."""
        is_enabled = state == 2  # Qt.Checked
        self.subtitle_language_combobox.setEnabled(is_enabled)
        self.embed_subtitles_checkbox.setEnabled(is_enabled)

    def _on_browse_clicked(self):
        # Open a file dialog to select a directory
        # Start the dialog in the currently set download folder path
        initial_path = self.download_path_lineedit.text() if self.download_path_lineedit.text() else ""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Download Folder", initial_path)
        if folder_path:
            self.download_path_lineedit.setText(folder_path)
            self.current_download_folder_path = folder_path

    def _on_cookies_browse_clicked(self):
        # Open a file dialog to select a cookies file
        initial_path = self.cookies_path_lineedit.text() if self.cookies_path_lineedit.text() else ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cookies File", initial_path, "Text files (*.txt)")
        if file_path:
            self.cookies_path_lineedit.setText(file_path)
            self.current_facebook_cookies_path = file_path

    def _on_bilibili_cookies_browse_clicked(self):
        initial_path = self.bilibili_cookies_lineedit.text() if self.bilibili_cookies_lineedit.text() else ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Bilibili Cookies File", initial_path, "Text files (*.txt)")
        if file_path:
            self.bilibili_cookies_lineedit.setText(file_path)
            self.current_bilibili_cookies_path = file_path

    def _on_xiaohongshu_cookies_browse_clicked(self):
        initial_path = self.xiaohongshu_cookies_lineedit.text() if self.xiaohongshu_cookies_lineedit.text() else ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Xiaohongshu Cookies File", initial_path, "Text files (*.txt)")
        if file_path:
            self.xiaohongshu_cookies_lineedit.setText(file_path)
            self.current_xiaohongshu_cookies_path = file_path

    def get_concurrent_downloads_limit(self) -> int:
        return self.concurrent_downloads_spinbox.value()

    def get_download_folder_path(self) -> str:
        return self.download_path_lineedit.text()

    def get_facebook_cookies_path(self) -> str:
        return self.cookies_path_lineedit.text()

    def get_bilibili_cookies_path(self) -> str:
        return self.bilibili_cookies_lineedit.text()

    def get_xiaohongshu_cookies_path(self) -> str:
        return self.xiaohongshu_cookies_lineedit.text()

    def get_video_resolution(self) -> str:
        return self.video_resolution_combobox.currentText()

    def get_video_format(self) -> str:
        return self.video_format_combobox.currentText()

    def get_audio_format(self) -> str:
        return self.audio_format_combobox.currentText()

    def get_subtitles_enabled(self) -> bool:
        return self.subtitles_enabled_checkbox.isChecked()

    def get_subtitle_language(self) -> str:
        return self.subtitle_language_combobox.currentText()

    def get_embed_subtitles(self) -> bool:
        return self.embed_subtitles_checkbox.isChecked()

    def get_download_preset(self) -> str:
        return self.preset_combobox.currentText()
