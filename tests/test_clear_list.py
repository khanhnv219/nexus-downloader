import pytest
from PySide6.QtWidgets import QTableWidget, QProgressBar, QMessageBox
from PySide6.QtCore import Qt
from unittest.mock import MagicMock, patch
from nexus_downloader.ui.main_window import MainWindow
from nexus_downloader.core.data_models import DownloadStatus

@pytest.fixture
def main_window(qtbot):
    """Fixture to create the MainWindow."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_clear_completed_downloads(main_window, qtbot):
    """Verify that 'Clear Completed' removes only completed items."""
    # Add 3 rows: Completed, Downloading, Completed
    main_window.download_table.setRowCount(3)
    
    # Row 0: Completed
    pb0 = QProgressBar()
    pb0.setFormat("Completed")
    main_window.download_table.setCellWidget(0, 3, pb0)
    
    # Row 1: Downloading
    pb1 = QProgressBar()
    pb1.setFormat("Downloading 50%")
    main_window.download_table.setCellWidget(1, 3, pb1)
    
    # Row 2: Completed
    pb2 = QProgressBar()
    pb2.setFormat("Completed")
    main_window.download_table.setCellWidget(2, 3, pb2)
    
    # Click Clear Completed
    main_window._clear_completed_downloads()
    
    # Should have 1 row left (the Downloading one)
    assert main_window.download_table.rowCount() == 1
    
    # Verify the remaining row is the "Downloading" one
    remaining_pb = main_window.download_table.cellWidget(0, 3)
    assert remaining_pb.format() == "Downloading 50%"

def test_clear_all_downloads_idle(main_window, qtbot):
    """Verify 'Clear List' removes all items when idle."""
    # Mock download manager to be idle
    main_window.download_manager.is_idle = MagicMock(return_value=True)
    
    # Add 2 rows
    main_window.download_table.setRowCount(2)
    
    # Click Clear List
    main_window._clear_all_downloads()
    
    # Should have 0 rows
    assert main_window.download_table.rowCount() == 0

def test_clear_all_downloads_busy_cancel(main_window, qtbot):
    """Verify 'Clear List' prompts and cancels if busy."""
    # Mock download manager to be BUSY
    main_window.download_manager.is_idle = MagicMock(return_value=False)
    
    # Mock QMessageBox to return No (Cancel)
    with patch.object(QMessageBox, 'question', return_value=QMessageBox.No) as mock_msg:
        main_window.download_table.setRowCount(2)
        main_window._clear_all_downloads()
        
        # Should NOT clear
        assert main_window.download_table.rowCount() == 2
        mock_msg.assert_called_once()

def test_clear_all_downloads_busy_confirm(main_window, qtbot):
    """Verify 'Clear List' stops downloads and clears if confirmed."""
    # Mock download manager to be BUSY
    main_window.download_manager.is_idle = MagicMock(return_value=False)
    main_window.stop_download = MagicMock()
    
    # Mock QMessageBox to return Yes (Confirm)
    with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
        main_window.download_table.setRowCount(2)
        main_window._clear_all_downloads()
        
        # Should call stop_download
        main_window.stop_download.assert_called_once()
        
        # Should clear list
        assert main_window.download_table.rowCount() == 0
