import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from nexus_downloader.ui.main_window import MainWindow
from nexus_downloader.core.data_models import DownloadStatus

# Create a single QApplication instance for all tests
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def main_window(qapp):
    with patch('nexus_downloader.ui.main_window.SettingsService'), \
         patch('nexus_downloader.ui.main_window.DownloadManager'):
        window = MainWindow()
        # Mock the tray icon to avoid actual system interactions and for verification
        window.tray_icon = MagicMock()
        return window

def test_notification_all_success(main_window):
    """Verify notification when all downloads succeed."""
    # Simulate starting a batch of 2 downloads
    main_window._download_queue_total = 2
    main_window._download_completed_count = 0
    main_window._batch_success_count = 0
    main_window._batch_fail_count = 0
    
    # Mock download manager to be BUSY (not idle) initially
    main_window.download_manager.is_idle.return_value = False

    # Simulate 1st download finishing
    main_window.on_download_finished("http://example.com/1")
    
    # Should NOT show notification yet because is_idle is False
    main_window.tray_icon.showMessage.assert_not_called()

    # Simulate 2nd download finishing AND manager becoming idle
    main_window.download_manager.is_idle.return_value = True
    main_window.on_download_finished("http://example.com/2")
    
    # Now it should show notification
    main_window.tray_icon.showMessage.assert_called_once()
    args = main_window.tray_icon.showMessage.call_args[0]
    assert "Downloads Complete" in args[0]
    assert "All downloads completed successfully" in args[1]

def test_notification_with_failures(main_window):
    """Verify notification when some downloads fail."""
    main_window._download_queue_total = 2
    main_window._download_completed_count = 0
    
    # 1st succeeds
    main_window.download_manager.is_idle.return_value = False
    main_window.on_download_finished("http://example.com/1")
    
    # 2nd fails
    main_window.download_manager.is_idle.return_value = True
    main_window.on_download_error("http://example.com/2", "Error")
    
    # Verify notification
    main_window.tray_icon.showMessage.assert_called_once()
    args = main_window.tray_icon.showMessage.call_args[0]
    assert "Downloads Complete" in args[0]
    assert "Successful: 1" in args[1]
    assert "Failed: 1" in args[1]

def test_notification_cancelled(main_window):
    """Verify notification when downloads are cancelled."""
    main_window._download_queue_total = 1
    main_window._download_completed_count = 0
    
    main_window.download_manager.is_idle.return_value = True
    main_window.on_download_cancelled("http://example.com/1")
    
    main_window.tray_icon.showMessage.assert_called_once()
    args = main_window.tray_icon.showMessage.call_args[0]
    assert "Successful: 0" in args[1]
    assert "Failed: 1" in args[1] # Cancelled counts as failed in current logic
