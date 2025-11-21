"""
Unit tests for the UI module.
"""
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QCheckBox
from PySide6.QtCore import QObject, Signal, Qt
from nexus_downloader.ui.main_window import MainWindow

class MockDownloadManager(QObject):
    """
    A mock DownloadManager for testing purposes.
    """
    fetch_finished = Signal(list)
    fetch_error = Signal(str)
    download_progress = Signal(str, dict)
    download_finished = Signal(str)
    download_error = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._concurrent_downloads_limit = 2 # Default value
        self._active_downloads = set()  # Track active downloads

    def start_fetch_job(self, url, cookies_file=None):
        """
        A mock method to start a fetch job.
        """
        pass

    def start_download_job(self, video_urls, video_resolution="best"):
        """
        A mock method to start a download job.
        """
        # Track downloads as active
        self._active_downloads.update(video_urls)

    def set_concurrent_downloads(self, limit: int):
        """
        Mock method to set the concurrent downloads limit.
        """
        self._concurrent_downloads_limit = limit

    def get_concurrent_downloads(self) -> int:
        """
        Mock method to get the concurrent downloads limit.
        """
        return self._concurrent_downloads_limit

    def is_idle(self) -> bool:
        """
        Mock method to check if the manager is idle.
        """
        return len(self._active_downloads) == 0
    
    def _mark_download_complete(self, url):
        """Helper to mark a download as complete."""
        self._active_downloads.discard(url)

@pytest.fixture
def app(qapp):
    """Create a QApplication instance."""
    return qapp

def test_main_window_creation(app):
    """Test if the main window can be created."""
    window = MainWindow()
    assert window is not None

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_main_window_fetch(qtbot, app):
    """Test the fetch functionality of the main window."""
    window = MainWindow()
    window.url_input.setText('some_url')
    
    with qtbot.waitSignal(window.download_manager.fetch_finished) as blocker:
        window.start_fetch()
        window.download_manager.fetch_finished.emit([{'title': 'Test Video', 'url': 'some_url'}])

    assert blocker.args == [[{'title': 'Test Video', 'url': 'some_url'}]]
    assert window.download_table.rowCount() == 1
    assert window.download_table.item(0, 1).text() == 'Test Video'
    assert window.download_table.item(0, 1).data(Qt.UserRole) == 'some_url'

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_main_window_fetch_playlist(qtbot, app):
    """Test the fetch functionality of the main window with a playlist."""
    window = MainWindow()
    window.url_input.setText('some_playlist_url')
    
    videos = [{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}]
    with qtbot.waitSignal(window.download_manager.fetch_finished) as blocker:
        window.start_fetch()
        window.download_manager.fetch_finished.emit(videos)

    assert blocker.args == [videos]
    assert window.download_table.rowCount() == 2
    assert window.download_table.item(0, 1).text() == 'Video 1'
    assert window.download_table.item(1, 1).text() == 'Video 2'

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_main_window_download(qtbot, app):
    """Test the download functionality of the main window."""
    window = MainWindow()
    
    # Add an item to the table
    window.on_fetch_finished([{'title': 'Test Video', 'url': 'some_url'}])
    
    # Check the checkbox
    checkbox = window.download_table.cellWidget(0, 0)
    checkbox.setChecked(True)

    with qtbot.waitSignal(window.download_manager.download_finished) as blocker:
        window.start_download()
        window.download_manager.download_finished.emit("some_url")

    assert blocker.args == ["some_url"]
    assert "Completed" in window.download_table.item(0, 3).text()

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_main_window_resolution_selection(qtbot, app):
    """Test that the selected resolution is passed to the download manager."""
    window = MainWindow()
    
    # Add an item to the table
    window.on_fetch_finished([{'title': 'Test Video', 'url': 'some_url'}])
    
    # Check the checkbox
    checkbox = window.download_table.cellWidget(0, 0)
    checkbox.setChecked(True)

    # Change resolution
    window.resolution_combobox.setCurrentText("720p")

    with patch.object(window.download_manager, 'start_download_job') as mock_start_download_job:
        window.start_download()
        mock_start_download_job.assert_called_once_with(['some_url'], "height<=720")

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_main_window_select_all_checkbox(qtbot, app):
    """Test the select all checkbox functionality."""
    window = MainWindow()
    
    # Add multiple items to the table
    window.on_fetch_finished([{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}])
    
    # Check the "Select All" checkbox
    window._on_select_all_checkbox_state_changed(Qt.Checked)
    
    # Verify that all individual checkboxes are checked
    for row in range(window.download_table.rowCount()):
        checkbox = window.download_table.cellWidget(row, 0)
        assert checkbox.isChecked()

    # Uncheck the "Select All" checkbox
    window._on_select_all_checkbox_state_changed(Qt.Unchecked)

    # Verify that all individual checkboxes are unchecked
    for row in range(window.download_table.rowCount()):
        checkbox = window.download_table.cellWidget(row, 0)
        assert not checkbox.isChecked()

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
@patch('os.startfile')
def test_main_window_open_download_folder(mock_startfile, qtbot, app):
    """Test the open download folder button functionality."""
    window = MainWindow()
    
    # Set a download folder path
    test_path = "C:/test/downloads"
    window.app_settings.download_folder_path = test_path
    
    # Mock os.path.isdir to return True
    with patch('os.path.isdir', return_value=True):
        window.open_folder_button.click()
        mock_startfile.assert_called_once_with(test_path)

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_select_all_sync_with_items(qtbot, app):
    """Test that "Select All" unchecks when an item is unchecked."""
    window = MainWindow()
    
    # Add multiple items to the table
    window.on_fetch_finished([{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}])
    
    # Check the "Select All" checkbox
    window._on_select_all_checkbox_state_changed(Qt.Checked)
    
    # Verify that all individual checkboxes are checked
    for row in range(window.download_table.rowCount()):
        checkbox = window.download_table.cellWidget(row, 0)
        assert checkbox.isChecked()

    # Uncheck one item - this should trigger _on_item_state_changed
    checkbox = window.download_table.cellWidget(0, 0)
    checkbox.setChecked(False)

    # Verify "Select All" is unchecked
    assert not window.select_all_checkbox.isChecked()

    # Check the item back - this should trigger _on_item_state_changed
    checkbox.setChecked(True)

    # Verify "Select All" is checked again
    assert window.select_all_checkbox.isChecked()


@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_fetch_button_loading_state(qtbot, app):
    """Test that fetch button shows loading state during fetch operation."""
    window = MainWindow()
    window.url_input.setText('some_youtube_url')
    
    # Verify initial button state
    assert window.get_urls_button.isEnabled()
    assert window.get_urls_button.text() == "Get Download Urls"
    
    # Start fetch and verify loading state
    window.start_fetch()
    assert not window.get_urls_button.isEnabled()
    assert window.get_urls_button.text() == "Fetching URLs..."
    
    # Simulate fetch completing
    window.download_manager.fetch_finished.emit([{'title': 'Test Video', 'url': 'test_url'}])
    
    # Verify button is restored to normal state
    assert window.get_urls_button.isEnabled()
    assert window.get_urls_button.text() == "Get Download Urls"

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_fetch_button_error_state(qtbot, app):
    """Test that fetch button returns to normal state on error."""
    window = MainWindow()
    window.url_input.setText('invalid_url')
    
    # Start fetch
    window.start_fetch()
    assert not window.get_urls_button.isEnabled()
    assert window.get_urls_button.text() == "Fetching URLs..."
    
    # Simulate fetch error
    with patch('PySide6.QtWidgets.QMessageBox.critical'):
        window.download_manager.fetch_error.emit("Test error message")
    
    # Verify button is restored to normal state
    assert window.get_urls_button.isEnabled()
    assert window.get_urls_button.text() == "Get Download Urls"

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_download_button_loading_state(qtbot, app):
    """Test that download button shows progress during downloads."""
    window = MainWindow()
    
    # Add items to download
    window.on_fetch_finished([
        {'title': 'Video 1', 'url': 'url1'},
        {'title': 'Video 2', 'url': 'url2'},
        {'title': 'Video 3', 'url': 'url3'}
    ])
    
    # Select all items
    for row in range(window.download_table.rowCount()):
        checkbox = window.download_table.cellWidget(row, 0)
        checkbox.setChecked(True)
    
    # Verify initial button state
    assert window.download_button.isEnabled()
    assert window.download_button.text() == "Download"
    
    # Start download
    window.start_download()
    assert not window.download_button.isEnabled()
    assert window.download_button.text() == "Downloading 0/3"
    
    # Simulate first download completing
    window.download_manager._mark_download_complete('url1')
    window.download_manager.download_finished.emit('url1')
    assert window.download_button.text() == "Downloading 1/3"
    assert not window.download_button.isEnabled()  # Still downloading
    
    # Simulate second download completing
    window.download_manager._mark_download_complete('url2')
    window.download_manager.download_finished.emit('url2')
    assert window.download_button.text() == "Downloading 2/3"
    assert not window.download_button.isEnabled()
    
    # Simulate third download completing - button should be restored
    window.download_manager._mark_download_complete('url3')
    window.download_manager.download_finished.emit('url3')
    assert window.download_button.isEnabled()
    assert window.download_button.text() == "Download"

@patch('nexus_downloader.ui.main_window.DownloadManager', new=MockDownloadManager)
def test_download_button_mixed_results(qtbot, app):
    """Test that download button handles success/error scenarios correctly."""
    window = MainWindow()
    
    # Add items
    window.on_fetch_finished([
        {'title': 'Video 1', 'url': 'url1'},
        {'title': 'Video 2', 'url': 'url2'}
    ])
    
    # Select all
    for row in range(window.download_table.rowCount()):
        checkbox = window.download_table.cellWidget(row, 0)
        checkbox.setChecked(True)
    
    # Start download
    window.start_download()
    assert window.download_button.text() == "Downloading 0/2"
    
    # One succeeds
    window.download_manager._mark_download_complete('url1')
    window.download_manager.download_finished.emit('url1')
    assert window.download_button.text() == "Downloading 1/2"
    
    # One fails - errors count as completed
    window.download_manager._mark_download_complete('url2')
    with patch('PySide6.QtWidgets.QMessageBox.warning'):
        window.download_manager.download_error.emit('url2', 'Test error')
    
    # Button should be restored after all complete (including errors)
    assert window.download_button.isEnabled()
    assert window.download_button.text() == "Download"
