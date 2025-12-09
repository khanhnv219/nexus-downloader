from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QLineEdit, QFileDialog, QComboBox
from PySide6.QtCore import Signal

class SettingsDialog(QDialog):
    settings_saved = Signal(int, str, str, str, str, str) # limit, download_path, fb_cookies, bilibili_cookies, xiaohongshu_cookies, resolution

    def __init__(self, current_concurrent_downloads_limit: int, current_download_folder_path: str, current_facebook_cookies_path: str, current_bilibili_cookies_path: str, current_xiaohongshu_cookies_path: str, current_video_resolution: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 350)

        self.current_concurrent_downloads_limit = current_concurrent_downloads_limit
        self.current_download_folder_path = current_download_folder_path
        self.current_facebook_cookies_path = current_facebook_cookies_path
        self.current_bilibili_cookies_path = current_bilibili_cookies_path
        self.current_xiaohongshu_cookies_path = current_xiaohongshu_cookies_path
        self.current_video_resolution = current_video_resolution

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
        self.video_resolution_label = QLabel("Video Resolution:")
        self.video_resolution_combobox = QComboBox()
        self.video_resolution_combobox.addItems(["best", "1080p", "720p", "480p", "360p"])
        self.video_resolution_combobox.setCurrentText(self.current_video_resolution)
        video_resolution_layout.addWidget(self.video_resolution_label)
        video_resolution_layout.addWidget(self.video_resolution_combobox)
        main_layout.addLayout(video_resolution_layout)

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
        self.settings_saved.emit(new_limit, new_download_path, new_cookies_path, new_bilibili_cookies_path, new_xiaohongshu_cookies_path, new_video_resolution)
        self.accept()

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
