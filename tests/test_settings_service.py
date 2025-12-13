import pytest
import os
import json
from nexus_downloader.services.settings_service import SettingsService, AppSettings


@pytest.fixture
def temp_settings_dir(tmp_path):
    """Fixture to create a temporary directory for settings."""
    settings_dir = tmp_path / "test_settings"
    settings_dir.mkdir()
    yield str(settings_dir)


@pytest.fixture
def settings_service(temp_settings_dir):
    """Fixture to provide a SettingsService instance with a temporary directory."""
    return SettingsService(settings_dir=temp_settings_dir)


def test_initial_settings_file_creation(temp_settings_dir):
    """Test that the settings file is created on first load."""
    service = SettingsService(settings_dir=temp_settings_dir)
    settings_path = os.path.join(temp_settings_dir, "settings.json")
    assert not os.path.exists(settings_path)
    service.load_settings()
    assert os.path.exists(settings_path)


def test_load_default_settings_if_no_data(settings_service):
    """Test that default settings are loaded if no data exists."""
    settings = settings_service.load_settings()
    assert settings.concurrent_downloads_limit == 2
    assert settings.facebook_cookies_path == ""
    assert settings.bilibili_cookies_path == ""
    assert settings.xiaohongshu_cookies_path == ""
    assert settings.video_resolution == "best"


def test_save_and_load_settings(settings_service):
    """Test saving and loading of AppSettings."""
    new_settings = AppSettings(
        download_folder_path="/new/path",
        concurrent_downloads_limit=5,
        facebook_cookies_path="/path/to/fb_cookies.txt",
        bilibili_cookies_path="/path/to/bilibili_cookies.txt",
        xiaohongshu_cookies_path="/path/to/xhs_cookies.txt",
        video_resolution="1080p"
    )
    settings_service.save_settings(new_settings)
    loaded_settings = settings_service.load_settings()
    assert loaded_settings.download_folder_path == "/new/path"
    assert loaded_settings.concurrent_downloads_limit == 5
    assert loaded_settings.facebook_cookies_path == "/path/to/fb_cookies.txt"
    assert loaded_settings.bilibili_cookies_path == "/path/to/bilibili_cookies.txt"
    assert loaded_settings.xiaohongshu_cookies_path == "/path/to/xhs_cookies.txt"
    assert loaded_settings.video_resolution == "1080p"


def test_save_and_load_bilibili_cookies(settings_service):
    """Test saving and loading Bilibili cookies path."""
    settings = AppSettings(bilibili_cookies_path="/cookies/bilibili.txt")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.bilibili_cookies_path == "/cookies/bilibili.txt"


def test_save_and_load_xiaohongshu_cookies(settings_service):
    """Test saving and loading Xiaohongshu cookies path."""
    settings = AppSettings(xiaohongshu_cookies_path="/cookies/xiaohongshu.txt")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.xiaohongshu_cookies_path == "/cookies/xiaohongshu.txt"


def test_load_settings_ignores_unknown_keys(settings_service, temp_settings_dir):
    """Test that unknown keys in JSON are ignored."""
    settings_path = os.path.join(temp_settings_dir, "settings.json")
    with open(settings_path, 'w') as f:
        json.dump({
            "concurrent_downloads_limit": 3,
            "unknown_key": "some_value"
        }, f)
    settings = settings_service.load_settings()
    assert settings.concurrent_downloads_limit == 3
    assert not hasattr(settings, 'unknown_key')


def test_load_settings_with_invalid_json(settings_service, temp_settings_dir):
    """Test loading settings when JSON is invalid returns defaults."""
    settings_path = os.path.join(temp_settings_dir, "settings.json")
    with open(settings_path, 'w') as f:
        f.write("{ invalid json }")
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


def test_path_portability_with_tilde(settings_service, temp_settings_dir):
    """Test that paths starting with ~ are saved and loaded correctly."""
    home = os.path.expanduser("~")
    test_path = os.path.join(home, "Downloads", "NexusTest")
    settings = AppSettings(download_folder_path=test_path)
    settings_service.save_settings(settings)

    # Check the raw JSON content
    settings_path = os.path.join(temp_settings_dir, "settings.json")
    with open(settings_path, 'r') as f:
        data = json.load(f)
    assert data['download_folder_path'].startswith("~")

    # Verify it loads back correctly
    loaded = settings_service.load_settings()
    assert loaded.download_folder_path == test_path


def test_default_video_format():
    """Test that the default video format is MP4."""
    settings = AppSettings()
    assert settings.video_format == "MP4"


def test_default_audio_format():
    """Test that the default audio format is M4A."""
    settings = AppSettings()
    assert settings.audio_format == "M4A"


def test_settings_video_format_persistence(settings_service):
    """Test video format setting saves and loads correctly."""
    settings = AppSettings(video_format="WebM")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.video_format == "WebM"


def test_settings_audio_format_persistence(settings_service):
    """Test audio format setting saves and loads correctly."""
    settings = AppSettings(audio_format="MP3")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.audio_format == "MP3"


def test_save_and_load_all_format_settings(settings_service):
    """Test saving and loading all format-related settings together."""
    settings = AppSettings(
        video_resolution="1080p",
        video_format="MKV",
        audio_format="OGG"
    )
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.video_resolution == "1080p"
    assert loaded.video_format == "MKV"
    assert loaded.audio_format == "OGG"


# Tests for subtitle settings
def test_default_subtitles_disabled():
    """Test that subtitles are disabled by default."""
    settings = AppSettings()
    assert settings.subtitles_enabled == False


def test_default_subtitle_language():
    """Test that default subtitle language is English."""
    settings = AppSettings()
    assert settings.subtitle_language == "English"


def test_default_embed_subtitles_disabled():
    """Test that embed subtitles is disabled by default."""
    settings = AppSettings()
    assert settings.embed_subtitles == False


def test_settings_subtitle_enabled_persistence(settings_service):
    """Test subtitle enabled setting saves and loads correctly."""
    settings = AppSettings(subtitles_enabled=True)
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.subtitles_enabled == True


def test_settings_subtitle_language_persistence(settings_service):
    """Test subtitle language setting saves and loads correctly."""
    settings = AppSettings(subtitle_language="Chinese (Simplified)")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.subtitle_language == "Chinese (Simplified)"


def test_settings_embed_subtitles_persistence(settings_service):
    """Test embed subtitles setting saves and loads correctly."""
    settings = AppSettings(embed_subtitles=True)
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.embed_subtitles == True


def test_save_and_load_all_subtitle_settings(settings_service):
    """Test saving and loading all subtitle-related settings together."""
    settings = AppSettings(
        subtitles_enabled=True,
        subtitle_language="Japanese",
        embed_subtitles=True
    )
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.subtitles_enabled == True
    assert loaded.subtitle_language == "Japanese"
    assert loaded.embed_subtitles == True


# Tests for download preset settings
def test_default_download_preset():
    """Test that default download preset is 'Balanced'."""
    settings = AppSettings()
    assert settings.download_preset == "Balanced"


def test_settings_download_preset_persistence(settings_service):
    """Test download preset setting saves and loads correctly."""
    settings = AppSettings(download_preset="High Quality")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.download_preset == "High Quality"


def test_settings_download_preset_custom_persistence(settings_service):
    """Test 'Custom' preset saves and loads correctly."""
    settings = AppSettings(download_preset="Custom")
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.download_preset == "Custom"


# Tests for recent_folders and folder_presets settings
def test_default_recent_folders_empty():
    """Test that default recent_folders is an empty list."""
    settings = AppSettings()
    assert settings.recent_folders == []


def test_default_folder_presets_empty():
    """Test that default folder_presets is an empty dict."""
    settings = AppSettings()
    assert settings.folder_presets == {}


def test_recent_folders_persistence(settings_service):
    """Test recent_folders setting saves and loads correctly."""
    folders = ["/path/to/folder1", "/path/to/folder2", "/path/to/folder3"]
    settings = AppSettings(recent_folders=folders)
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.recent_folders == folders


def test_folder_presets_persistence(settings_service):
    """Test folder_presets setting saves and loads correctly."""
    presets = {"Work": "/work/videos", "Personal": "/home/videos"}
    settings = AppSettings(folder_presets=presets)
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert loaded.folder_presets == presets


def test_recent_folders_max_five(settings_service):
    """Test that recent_folders can store up to 5 entries."""
    folders = [f"/path/to/folder{i}" for i in range(5)]
    settings = AppSettings(recent_folders=folders)
    settings_service.save_settings(settings)
    loaded = settings_service.load_settings()
    assert len(loaded.recent_folders) == 5
    assert loaded.recent_folders == folders
