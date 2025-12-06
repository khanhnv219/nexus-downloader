"""
Unit tests for Bilibili error handling in YtDlpService.
"""
import pytest
from nexus_downloader.core.yt_dlp_service import YtDlpService

class TestBilibiliErrorHandling:
    """Tests for Bilibili-specific error message formatting."""

    def setup_method(self):
        self.service = YtDlpService()
        self.bilibili_url = "https://www.bilibili.com/video/BV1xx411c7mD"

    def test_format_error_rate_limit(self):
        """Test rate limit error message."""
        error_msg = "HTTP Error 412: Precondition Failed"
        formatted = self.service._format_error_message(self.bilibili_url, error_msg)
        assert "Too many requests" in formatted
        assert "rate limiting" in formatted

    def test_format_error_too_many_requests(self):
        """Test explicit too many requests error."""
        error_msg = "Too many requests"
        formatted = self.service._format_error_message(self.bilibili_url, error_msg)
        assert "Too many requests" in formatted

    def test_format_error_private_collection(self):
        """Test private collection error message."""
        error_msg = "This video is private"
        formatted = self.service._format_error_message(self.bilibili_url, error_msg)
        assert "requires authentication" in formatted
        assert "collection" in formatted

    def test_format_error_empty_playlist(self):
        """Test empty playlist error message."""
        error_msg = "Playlist is empty"
        formatted = self.service._format_error_message(self.bilibili_url, error_msg)
        assert "collection or user space appears to be empty" in formatted

    def test_format_error_generic_network(self):
        """Test generic network error on Bilibili URL."""
        error_msg = "Network is unreachable"
        formatted = self.service._format_error_message(self.bilibili_url, error_msg)
        assert "Check your internet connection" in formatted
