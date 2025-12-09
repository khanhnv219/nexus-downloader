"""
Unit tests for the core module.
"""
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QCoreApplication, QObject, Signal
from nexus_downloader.core.yt_dlp_service import YtDlpService
from nexus_downloader.core.download_manager import DownloadManager, FetchWorker, DownloadWorker
import os

@pytest.fixture
def app(qapp):
    """Create a QApplication instance."""
    return qapp

@patch('yt_dlp.YoutubeDL')
def test_yt_dlp_service_get_single_video_info_success(mock_youtube_dl):
    """
    Test that get_video_info returns the correct info for a single video.
    """
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = {'title': 'Test Video'}
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

    service = YtDlpService()
    videos, error = service.get_video_info('some_url')

    assert videos == [{'title': 'Test Video'}]
    assert error is None

@patch('yt_dlp.YoutubeDL')
def test_yt_dlp_service_get_playlist_info_success(mock_youtube_dl):
    """
    Test that get_video_info returns the correct info for a playlist.
    """
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = {
        'entries': [{'title': 'Video 1'}, {'title': 'Video 2'}]
    }
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

    service = YtDlpService()
    videos, error = service.get_video_info('some_playlist_url')

    assert videos == [{'title': 'Video 1'}, {'title': 'Video 2'}]
    assert error is None

@patch('yt_dlp.YoutubeDL')
def test_yt_dlp_service_get_video_info_error(mock_youtube_dl):
    """
    Test that get_video_info returns an error message on error.
    """
    from yt_dlp.utils import DownloadError
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.side_effect = DownloadError('Test Error')
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

    service = YtDlpService()
    videos, error = service.get_video_info('some_url')

    assert videos is None
    assert error == 'Test Error'

@patch('yt_dlp.YoutubeDL')
def test_yt_dlp_service_download_video_success(mock_youtube_dl):
    """
    Test that download_video calls yt-dlp with the correct options and download path.
    """
    mock_ydl_instance = MagicMock()
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

    service = YtDlpService()
    test_url = "http://example.com/video"
    test_path = "/tmp/downloads"
    success, error = service.download_video(test_url, test_path)

    assert success is True
    assert error is None
    mock_youtube_dl.assert_called_once()
    
    # Check both positional and keyword arguments for ydl_opts
    call_args = mock_youtube_dl.call_args
    ydl_opts = {}
    if call_args.args:
        ydl_opts.update(call_args.args[0])
    if call_args.kwargs:
        ydl_opts.update(call_args.kwargs)

    assert ydl_opts['outtmpl'] == f'{test_path}/%(title)s.%(ext)s'
    mock_ydl_instance.download.assert_called_once_with([test_url])

def test_fetch_worker_single_video(qtbot, app):
    """
    Test the FetchWorker with a single video.
    """
    with patch('nexus_downloader.core.yt_dlp_service.YtDlpService.get_video_info') as mock_get_video_info:
        mock_get_video_info.return_value = ([{'title': 'Test Video'}], None)
        worker = FetchWorker('some_url')
        with qtbot.waitSignal(worker.finished) as blocker:
            worker.run()
        assert blocker.args == [[{'title': 'Test Video'}]]

def test_fetch_worker_playlist(qtbot, app):
    """
    Test the FetchWorker with a playlist.
    """
    with patch('nexus_downloader.core.yt_dlp_service.YtDlpService.get_video_info') as mock_get_video_info:
        mock_get_video_info.return_value = ([{'title': 'Video 1'}, {'title': 'Video 2'}], None)
        worker = FetchWorker('some_playlist_url')
        with qtbot.waitSignal(worker.finished) as blocker:
            worker.run()
        assert blocker.args == [[{'title': 'Video 1'}, {'title': 'Video 2'}]]

def test_fetch_worker_error(qtbot, app):
    """
    Test the FetchWorker when an error occurs.
    """
    with patch('nexus_downloader.core.yt_dlp_service.YtDlpService.get_video_info') as mock_get_video_info:
        mock_get_video_info.return_value = (None, 'Test Error')
        worker = FetchWorker('some_url')
        with qtbot.waitSignal(worker.error) as blocker:
            worker.run()
        assert blocker.args == ['Test Error']

@patch('nexus_downloader.core.download_manager.FetchWorker')
def test_download_manager_starts_fetch_job(MockFetchWorker, app):
    """
    Test that the DownloadManager starts a fetch job.
    """
    manager = DownloadManager()
    manager.start_fetch_job('some_url')
    assert manager.fetch_thread is not None
    assert manager.fetch_worker is not None
    manager.fetch_thread.quit()
    manager.fetch_thread.wait()


def test_download_manager_get_cookies_path_for_bilibili(app):
    """Test that the correct cookie path is returned for Bilibili URLs."""
    manager = DownloadManager()
    manager.app_settings.bilibili_cookies_path = "/path/to/bilibili.txt"
    manager.app_settings.xiaohongshu_cookies_path = "/path/to/xhs.txt"
    manager.app_settings.facebook_cookies_path = "/path/to/fb.txt"

    assert manager._get_cookies_path_for_url("https://www.bilibili.com/video/BV1234567") == "/path/to/bilibili.txt"
    assert manager._get_cookies_path_for_url("https://b23.tv/abcdef") == "/path/to/bilibili.txt"


def test_download_manager_get_cookies_path_for_xiaohongshu(app):
    """Test that the correct cookie path is returned for Xiaohongshu URLs."""
    manager = DownloadManager()
    manager.app_settings.bilibili_cookies_path = "/path/to/bilibili.txt"
    manager.app_settings.xiaohongshu_cookies_path = "/path/to/xhs.txt"
    manager.app_settings.facebook_cookies_path = "/path/to/fb.txt"

    assert manager._get_cookies_path_for_url("https://www.xiaohongshu.com/explore/123") == "/path/to/xhs.txt"
    assert manager._get_cookies_path_for_url("https://xhslink.com/abc") == "/path/to/xhs.txt"


def test_download_manager_get_cookies_path_for_facebook(app):
    """Test that the correct cookie path is returned for Facebook URLs."""
    manager = DownloadManager()
    manager.app_settings.bilibili_cookies_path = "/path/to/bilibili.txt"
    manager.app_settings.xiaohongshu_cookies_path = "/path/to/xhs.txt"
    manager.app_settings.facebook_cookies_path = "/path/to/fb.txt"

    assert manager._get_cookies_path_for_url("https://www.facebook.com/video/123") == "/path/to/fb.txt"
    assert manager._get_cookies_path_for_url("https://fb.watch/abc") == "/path/to/fb.txt"


def test_download_manager_get_cookies_path_for_other_sites(app):
    """Test that no cookie path is returned for unsupported sites."""
    manager = DownloadManager()
    manager.app_settings.bilibili_cookies_path = "/path/to/bilibili.txt"
    manager.app_settings.xiaohongshu_cookies_path = "/path/to/xhs.txt"
    manager.app_settings.facebook_cookies_path = "/path/to/fb.txt"

    assert manager._get_cookies_path_for_url("https://www.youtube.com/watch?v=abc") == ""
    assert manager._get_cookies_path_for_url("https://www.tiktok.com/@user") == ""

def test_download_worker(qtbot, app, mocker):
    """
    Test the DownloadWorker.
    """
    mock_yt_dlp_service_instance = mocker.patch('nexus_downloader.core.download_manager.YtDlpService').return_value
    mock_yt_dlp_service_instance.download_video.return_value = (True, None)

    test_url = 'some_url'
    test_path = '/tmp/downloads'
    test_resolution = 'best'
    test_cookies = 'cookies.txt'
    worker = DownloadWorker(test_url, test_path, test_resolution, test_cookies, mock_yt_dlp_service_instance)
    with qtbot.waitSignal(worker.signals.finished) as blocker:
        worker.run()
    assert blocker.args == [test_url]
    mock_yt_dlp_service_instance.download_video.assert_called_once_with(
        test_url, test_path, test_resolution, progress_hook=worker.progress_hook, cookies_file=test_cookies
    )

@pytest.mark.integration
def test_fetch_worker_tiktok_profile(qtbot, app):
    """
    Test the FetchWorker with a real TikTok profile URL.
    """
    # Using a real TikTok profile URL to test the integration
    tiktok_url = "https://www.tiktok.com/@google"
    worker = FetchWorker(tiktok_url)
    with qtbot.waitSignal(worker.finished, timeout=30000) as blocker:
        worker.run()
    
    # We expect a list of videos, so the list should not be empty
    assert blocker.args
    assert isinstance(blocker.args[0], list)
    assert len(blocker.args[0]) > 0

@pytest.mark.integration
def test_fetch_worker_invalid_tiktok_url(qtbot, app):
    """
    Test the FetchWorker with an invalid TikTok URL.
    """
    invalid_url = "https://www.tiktok.com/@invaliduser123456789"
    worker = FetchWorker(invalid_url)
    with qtbot.waitSignal(worker.error, timeout=30000) as blocker:
        worker.run()
    
    assert blocker.args
    assert isinstance(blocker.args[0], str)

    @pytest.mark.integration
    def test_fetch_worker_facebook_profile(qtbot, app):
        """
        Test the FetchWorker with a real Facebook profile URL.
        """
        pytest.skip("Facebook fetching is currently unreliable and requires a valid, logged-in cookie.")
        # Using a real Facebook profile URL to test the integration
        facebook_url = "https://www.facebook.com/Google"
        cookies_file_path = os.path.join(os.path.dirname(__file__), 'facebook_cookies.txt')
        worker = FetchWorker(facebook_url, cookies_file=cookies_file_path)
        with qtbot.waitSignal(worker.finished, timeout=30000) as blocker:
            worker.run()
        
        # We expect a list of videos, so the list should not be empty
        assert blocker.args
        assert isinstance(blocker.args[0], list)
        assert len(blocker.args[0]) > 0
@pytest.mark.integration
def test_fetch_worker_invalid_facebook_url(qtbot, app):
    """
    Test the FetchWorker with an invalid Facebook URL.
    """
    invalid_url = "https://www.facebook.com/invaliduser123456789"
    worker = FetchWorker(invalid_url)
    with qtbot.waitSignal(worker.error, timeout=30000) as blocker:
        worker.run()
    
    assert blocker.args
    assert isinstance(blocker.args[0], str)

# New tests for batch downloading
@patch('nexus_downloader.core.download_manager.YtDlpService')
def test_download_manager_queues_downloads(mock_yt_dlp_service, qtbot, app):
    """
    Test that DownloadManager correctly queues multiple downloads and starts them based on concurrency.
    """
    mock_yt_dlp_service_instance = mock_yt_dlp_service.return_value
    mock_yt_dlp_service_instance.download_video.return_value = (True, None)

    manager = DownloadManager()
    manager.thread_pool.setMaxThreadCount(1) # Set max concurrent downloads to 1 for easier testing

    with qtbot.waitSignals([manager.download_finished] * 3, timeout=10000):
        manager.start_download_job(['url1', 'url2', 'url3'])

    assert mock_yt_dlp_service_instance.download_video.call_count == 3

@patch('nexus_downloader.core.download_manager.YtDlpService')
def test_download_manager_concurrency_limit(mock_yt_dlp_service, qtbot, app):
    """
    Test that DownloadManager respects the concurrent download limit.
    """
    mock_yt_dlp_service_instance = mock_yt_dlp_service.return_value
    mock_yt_dlp_service_instance.download_video.return_value = (True, None)

    manager = DownloadManager()
    manager.thread_pool.setMaxThreadCount(2) # Set max concurrent downloads to 2

    with qtbot.waitSignals([manager.download_finished] * 4, timeout=10000):
        manager.start_download_job(['url1', 'url2', 'url3', 'url4'])

    assert mock_yt_dlp_service_instance.download_video.call_count == 4

def test_download_manager_set_concurrent_downloads(app):
    """
    Test that DownloadManager's set_concurrent_downloads method correctly updates the thread pool limit.
    """
    manager = DownloadManager()
    new_limit = 3
    manager.set_concurrent_downloads(new_limit)
    assert manager.thread_pool.maxThreadCount() == new_limit

    assert manager.thread_pool.maxThreadCount() == new_limit

@patch('nexus_downloader.core.download_manager.DownloadWorker')
@patch('nexus_downloader.core.download_manager.SettingsService') # Patch SettingsService where it's used in DownloadManager
def test_download_manager_uses_settings_download_path(MockSettingsService, MockDownloadWorker, app):
    """
    Test that DownloadManager retrieves the download_folder_path from AppSettings
    and passes it to the DownloadWorker.
    """
    # Mock AppSettings to return a specific download path
    mock_app_settings = MagicMock()
    mock_app_settings.concurrent_downloads_limit = 2
    mock_app_settings.download_folder_path = "/path/from/settings"

    # Mock SettingsService to return our mock AppSettings
    mock_settings_service_instance = MockSettingsService.return_value
    mock_settings_service_instance.load_settings.return_value = mock_app_settings

    # Create DownloadManager instance *after* mocking SettingsService
    manager = DownloadManager()

    # Simulate starting a download job
    test_url = "http://example.com/video"
    manager.start_download_job([test_url])

    # Assert that DownloadWorker was called with the correct download_folder_path
    MockDownloadWorker.assert_called_once()
    args, kwargs = MockDownloadWorker.call_args
    assert args[1] == mock_app_settings.download_folder_path # download_folder_path is the second argument

@patch('yt_dlp.YoutubeDL')
def test_yt_dlp_service_get_video_info_with_cookies(mock_youtube_dl):
    """
    Test that get_video_info passes the cookies file to yt-dlp.
    """
    mock_ydl_instance = MagicMock()
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

    service = YtDlpService()
    test_url = "https://www.facebook.com/reel/12345"
    cookies_file = "cookies.txt"
    service.get_video_info(test_url, cookies_file=cookies_file)

    mock_youtube_dl.assert_called_once()
    
    # Check both positional and keyword arguments for ydl_opts
    call_args = mock_youtube_dl.call_args
    ydl_opts = {}
    if call_args.args:
        ydl_opts.update(call_args.args[0])
    if call_args.kwargs:
        ydl_opts.update(call_args.kwargs)

    assert ydl_opts['cookiefile'] == cookies_file

@pytest.mark.integration
def test_fetch_worker_facebook_reel(qtbot, app):
    """
    Test the FetchWorker with a real Facebook Reel URL.
    This test requires a valid cookies file.
    """
    pytest.skip("Facebook Reels download is currently unreliable and requires a valid, logged-in cookie.")
    facebook_url = "https://www.facebook.com/reel/12345" # Replace with a real, public reel URL
    cookies_file_path = os.path.join(os.path.dirname(__file__), 'facebook_cookies.txt')
    if not os.path.exists(cookies_file_path):
        pytest.skip("Facebook cookies file not found. Skipping test.")

    worker = FetchWorker(facebook_url, cookies_file=cookies_file_path)
    with qtbot.waitSignal(worker.finished, timeout=30000) as blocker:
        worker.run()
    
    assert blocker.args
    assert isinstance(blocker.args[0], list)
    assert len(blocker.args[0]) > 0

# Placeholder for integration tests for downloading multiple files
@pytest.mark.integration
def test_download_manager_multiple_files_integration(qtbot, app):
    """
    Integration test for downloading multiple files concurrently.
    This test requires actual network access and may take a long time.
    It is currently a placeholder and needs to be implemented with real URLs and assertions.
    """
    pytest.skip("Integration test for multiple file downloads is a placeholder.")