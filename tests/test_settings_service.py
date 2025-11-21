import pytest
import os
import sqlite3
from nexus_downloader.services.settings_service import SettingsService, AppSettings

@pytest.fixture
def temp_settings_db(tmp_path):
    """Fixture to create a temporary database path for testing."""
    db_path = tmp_path / "test_app_settings.db"
    yield str(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def settings_service(temp_settings_db):
    """Fixture to provide a SettingsService instance with a temporary database."""
    return SettingsService(db_path=temp_settings_db)

def test_initial_db_creation(temp_settings_db):
    """Test that the database and table are created on initialization."""
    assert not os.path.exists(temp_settings_db)
    service = SettingsService(db_path=temp_settings_db)
    assert os.path.exists(temp_settings_db)
    conn = sqlite3.connect(temp_settings_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';")
    assert cursor.fetchone() is not None
    conn.close()

def test_load_default_settings_if_no_data(settings_service):
    """Test that default settings are loaded if no data is in the DB."""
    settings = settings_service.load_settings()
    assert settings == AppSettings()

def test_save_and_load_settings(settings_service):
    """Test saving and loading of AppSettings."""
    new_settings = AppSettings(download_folder_path="/new/path", concurrent_downloads_limit=5)
    settings_service.save_settings(new_settings)
    loaded_settings = settings_service.load_settings()
    assert loaded_settings == new_settings

def test_save_and_load_partial_settings(settings_service):
    """Test saving and loading when only some settings are changed."""
    # Save only concurrent_downloads_limit
    partial_settings = AppSettings(concurrent_downloads_limit=7)
    settings_service.save_settings(partial_settings)
    loaded_settings = settings_service.load_settings()
    # download_folder_path should revert to default if not explicitly saved
    assert loaded_settings.concurrent_downloads_limit == 7
    assert loaded_settings.download_folder_path == AppSettings().download_folder_path

    # Save only download_folder_path
    partial_settings_2 = AppSettings(download_folder_path="/another/path")
    settings_service.save_settings(partial_settings_2)
    loaded_settings_2 = settings_service.load_settings()
    assert loaded_settings_2.download_folder_path == "/another/path"
    assert loaded_settings_2.concurrent_downloads_limit == AppSettings().concurrent_downloads_limit


def test_load_settings_with_invalid_int_value(settings_service, temp_settings_db):
    """Test loading settings when an int value in DB is invalid."""
    conn = sqlite3.connect(temp_settings_db)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('concurrent_downloads_limit', 'not_an_integer'))
    conn.commit()
    conn.close()

    settings = settings_service.load_settings()
    assert settings.concurrent_downloads_limit == AppSettings().concurrent_downloads_limit # Should revert to default
    assert settings.download_folder_path == AppSettings().download_folder_path # Other settings should be default

def test_save_settings_error_handling(settings_service, monkeypatch):
    """Test that save_settings re-raises SQLite errors."""
    monkeypatch.setattr('sqlite3.connect', lambda *args, **kwargs: (_ for _ in ()).throw(sqlite3.Error("Disk full")))
    with pytest.raises(sqlite3.Error):
        settings_service.save_settings(AppSettings())

def test_load_settings_error_handling(settings_service, monkeypatch):
    """Test that load_settings returns default on SQLite errors."""
    monkeypatch.setattr('sqlite3.connect', lambda *args, **kwargs: (_ for _ in ()).throw(sqlite3.Error("DB locked")))
    settings = settings_service.load_settings()
    assert settings == AppSettings()

def test_default_download_folder_path():
    """Test that the default download folder path is correctly set."""
    settings = AppSettings()
    assert settings.download_folder_path == os.path.join(os.path.expanduser("~"), "Downloads")

def test_custom_download_folder_path():
    """Test setting a custom download folder path."""
    custom_path = "/custom/downloads"
    settings = AppSettings(download_folder_path=custom_path)
    assert settings.download_folder_path == custom_path
