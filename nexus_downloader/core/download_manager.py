"""
This module provides a download manager to handle video fetching and downloading.
"""
from PySide6.QtCore import QObject, QThread, Signal, QThreadPool, QRunnable
from nexus_downloader.core.yt_dlp_service import YtDlpService
import yt_dlp
from nexus_downloader.services.settings_service import SettingsService, AppSettings # Import SettingsService and AppSettings
import os
import threading
from collections import deque

class FetchWorker(QObject):
    """
    A worker that fetches video information in a separate thread.
    """
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, url, cookies_file=None):
        super().__init__()
        self.url = url
        self.cookies_file = cookies_file
        self.yt_dlp_service = YtDlpService()

    def run(self):
        """
        Fetches video information and emits the finished signal.
        """
        videos, error = self.yt_dlp_service.get_video_info(self.url, self.cookies_file)
        if error:
            self.error.emit(error)
        else:
            self.finished.emit(videos)

class DownloadWorker(QRunnable):
    """
    A worker that downloads a video in a separate thread, designed for QThreadPool.
    """
    # QRunnable does not support signals directly, so we'll use a QObject for signals
    class Signals(QObject):
        progress = Signal(str, dict) # Emit video_url and progress data
        finished = Signal(str)       # Emit video_url
        error = Signal(str, str)     # Emit video_url and error message
        cancelled = Signal(str)      # Emit video_url when cancelled

    def __init__(self, video_url, download_folder_path, video_resolution, cookies_file, yt_dlp_service, cancellation_event=None):
        super().__init__()
        self.video_url = video_url
        self.download_folder_path = download_folder_path
        self.video_resolution = video_resolution
        self.cookies_file = cookies_file
        self.yt_dlp_service = yt_dlp_service
        self.cancellation_event = cancellation_event
        self.signals = self.Signals()

    def progress_hook(self, d):
        """Progress hook called by yt-dlp during download.
        
        Checks for cancellation and raises exception to interrupt yt-dlp.
        """
        # Check for cancellation during download
        if self.cancellation_event and self.cancellation_event.is_set():
            raise Exception("Download cancelled by user")
        
        if d['status'] == 'downloading':
            self.signals.progress.emit(self.video_url, d)

    def run(self):
        """
        Downloads the video and emits progress and finished signals.
        
        Checks for cancellation before starting download and handles cleanup if cancelled.
        """
        # Check for cancellation before starting
        if self.cancellation_event and self.cancellation_event.is_set():
            self._cleanup_incomplete_files()
            self.signals.cancelled.emit(self.video_url)
            return
        
        try:
            success, message = self.yt_dlp_service.download_video(
                self.video_url, 
                self.download_folder_path,
                self.video_resolution,
                progress_hook=self.progress_hook,
                cookies_file=self.cookies_file
            )
            
            # Check for cancellation after download attempt
            if self.cancellation_event and self.cancellation_event.is_set():
                self._cleanup_incomplete_files()
                self.signals.cancelled.emit(self.video_url)
                return
            
            if success:
                self.signals.finished.emit(self.video_url)
            else:
                self.signals.error.emit(self.video_url, message)
                
        except Exception as e:
            # Check if this was a cancellation
            if self.cancellation_event and self.cancellation_event.is_set():
                self._cleanup_incomplete_files()
                self.signals.cancelled.emit(self.video_url)
            else:
                # Real error
                self.signals.error.emit(self.video_url, str(e))
    
    def _cleanup_incomplete_files(self) -> None:
        """Cleans up incomplete download files (both regular and .part files).
        
        Uses robust retry logic to handle persistent file locks from yt-dlp/ffmpeg.
        Only deletes .part files modified in the last 60 seconds.
        """
        import logging
        import glob
        import time
        logger = logging.getLogger(__name__)
        
        try:
            # Initial delay to let yt-dlp/ffmpeg close file handles
            time.sleep(5.0)
            
            pattern = os.path.join(self.download_folder_path, '*')
            part_files = glob.glob(pattern + '.part')
            current_time = time.time()
            
            for part_file in part_files:
                try:
                    if os.path.exists(part_file):
                        file_mtime = os.path.getmtime(part_file)
                        if current_time - file_mtime < 60:  # Modified in last 60 seconds
                            # Retry deletion up to 10 times with 1s delays (10s total)
                            max_retries = 10
                            for attempt in range(max_retries):
                                try:
                                    os.remove(part_file)
                                    logger.info(f"Deleted partial file: {part_file}")
                                    break
                                except OSError as e:
                                    if attempt < max_retries - 1:
                                        time.sleep(1.0)  # Wait 1s between retries
                                    else:
                                        logger.warning(f"Failed to delete {part_file} after {max_retries} attempts: {e}")
                except Exception as e:
                    logger.warning(f"Error checking partial file {part_file}: {e}")
            
        except Exception as e:
            logger.warning(f"Error during file cleanup for {self.video_url}: {e}")

class DownloadManager(QObject):
    """
    Manages the fetching and downloading of videos.
    """
    fetch_finished = Signal(list)
    fetch_error = Signal(str)
    download_progress = Signal(str, dict) # Emit video_url and progress data
    download_finished = Signal(str)       # Emit video_url
    download_error = Signal(str, str)     # Emit video_url and error message
    download_cancelled = Signal(str)      # Emit video_url when cancelled

    def __init__(self):
        super().__init__()
        self.fetch_thread = None
        self.fetch_worker = None
        
        self.settings_service = SettingsService()
        self.app_settings = self._load_initial_settings()
        self.yt_dlp_service = YtDlpService()

        self.download_queue = deque()
        self.thread_pool = QThreadPool()
        self.set_concurrent_downloads(self.app_settings.concurrent_downloads_limit) # Use limit from settings
        self.video_resolution = "best" # Default value
        
        # Thread-safe cancellation event for download workers
        self._cancellation_event = threading.Event()

    def _load_initial_settings(self) -> AppSettings:
        """Loads settings on application startup, handling potential errors."""
        try:
            settings = self.settings_service.load_settings()
            return settings
        except Exception:
            return AppSettings() # Return default settings on error

    def set_concurrent_downloads(self, limit):
        """Sets the maximum number of concurrent downloads."""
        self.thread_pool.setMaxThreadCount(max(1, limit))

    def update_settings(self, settings: AppSettings):
        """Updates the settings used by the download manager."""
        self.app_settings = settings
        self.set_concurrent_downloads(settings.concurrent_downloads_limit)

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

    def is_idle(self) -> bool:
        """Checks if the download manager is currently idle.
        
        Returns:
            bool: True if no downloads are active or queued.
        """
        return self.thread_pool.activeThreadCount() == 0 and not self.download_queue
    
    def stop_all_downloads(self) -> None:
        """Stops all active and queued downloads.
        
        Sets the cancellation event to signal all workers to stop.
        Clears the download queue to prevent new downloads from starting.
        """
        # Set cancellation flag for all active workers
        self._cancellation_event.set()
        
        # Clear the queue to prevent new downloads
        self.download_queue.clear()

    def start_fetch_job(self, url, cookies_file=None):
        """
        Starts a new thread to fetch video information.

        Args:
            url (str): The URL of the video.
            cookies_file (str, optional): Path to a cookies file. Defaults to None.
        """
        self.fetch_thread = QThread()
        self.fetch_worker = FetchWorker(url, cookies_file)
        self.fetch_worker.moveToThread(self.fetch_thread)
        self.fetch_thread.started.connect(self.fetch_worker.run)
        self.fetch_worker.finished.connect(self.fetch_thread.quit)
        self.fetch_worker.finished.connect(self.fetch_worker.deleteLater)
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater)
        self.fetch_worker.finished.connect(self.fetch_finished)
        self.fetch_worker.error.connect(self.fetch_error)
        self.fetch_thread.start()

    def start_download_job(self, video_urls, video_resolution="best"):
        """
        Adds video URLs to the download queue and starts downloads if threads are available.

        Args:
            video_urls (list): A list of video URLs to download.
            video_resolution (str): The desired video resolution.
        """
        # Clear cancellation event for new download session
        self._cancellation_event.clear()
        
        self.video_resolution = video_resolution # Update the resolution here
        for url in video_urls:
            self.download_queue.append(url)
        self._start_next_download()

    def _start_next_download(self):
        """
        Starts the next download from the queue if the thread pool has capacity.
        """
        while self.download_queue and self.thread_pool.activeThreadCount() < self.thread_pool.maxThreadCount():
            video_url = self.download_queue.popleft()
            cookies_path = self._get_cookies_path_for_url(video_url)
            worker = DownloadWorker(
                video_url, 
                self.app_settings.download_folder_path, 
                self.video_resolution,
                cookies_path,
                self.yt_dlp_service,
                self._cancellation_event  # Pass cancellation event
            )
            worker.signals.progress.connect(self.download_progress)
            worker.signals.finished.connect(self.download_finished)
            worker.signals.error.connect(self.download_error)
            worker.signals.cancelled.connect(self.download_cancelled)  # Connect cancelled signal
            # Ensure the next download is triggered regardless of success or failure
            worker.signals.finished.connect(self._start_next_download)
            worker.signals.error.connect(self._start_next_download)
            worker.signals.cancelled.connect(self._start_next_download)  # Also trigger on cancellation
            self.thread_pool.start(worker)
