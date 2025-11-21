import os
import json
import shutil
import pytest
from nexus_downloader.services.settings_service import SettingsService, AppSettings
from nexus_downloader.core.download_manager import DownloadManager

@pytest.fixture
def temp_settings_dir(tmp_path):
    """Fixture to provide a temporary directory for settings."""
    return str(tmp_path)

def test_config_creation_on_missing(temp_settings_dir):
    """Verify that settings.json is created if it doesn't exist."""
    settings_path = os.path.join(temp_settings_dir, "settings.json")
    assert not os.path.exists(settings_path)

    service = SettingsService(settings_dir=temp_settings_dir)
    service.load_settings()

    assert os.path.exists(settings_path)
    with open(settings_path, 'r') as f:
        data = json.load(f)
        assert "download_folder_path" in data
        assert "concurrent_downloads_limit" in data

def test_download_manager_update_settings():
    """Verify that DownloadManager updates its settings correctly."""
    manager = DownloadManager()
    
    # Create new settings
    new_settings = AppSettings(
        download_folder_path="/new/path",
        concurrent_downloads_limit=5
    )
    
    # Update settings
    manager.update_settings(new_settings)
    
    # Verify updates
    assert manager.app_settings.download_folder_path == "/new/path"
    assert manager.thread_pool.maxThreadCount() == 5
