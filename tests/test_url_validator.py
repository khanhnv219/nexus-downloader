"""
Unit tests for the URLValidator class.
"""
import pytest
from nexus_downloader.core.url_validator import URLValidator

class TestURLValidator:
    """Tests for the URLValidator class."""

    def test_is_bilibili_url_valid_video(self):
        """Test valid Bilibili video URL."""
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        assert URLValidator.is_bilibili_url(url) is True

    def test_is_bilibili_url_valid_short(self):
        """Test valid Bilibili short URL."""
        url = "https://b23.tv/av123456"
        assert URLValidator.is_bilibili_url(url) is True

    def test_is_bilibili_url_valid_space(self):
        """Test valid Bilibili user space URL."""
        url = "https://space.bilibili.com/1234567"
        assert URLValidator.is_bilibili_url(url) is True

    def test_is_bilibili_url_valid_collection(self):
        """Test valid Bilibili collection URL."""
        url = "https://www.bilibili.com/medialist/play/123456"
        assert URLValidator.is_bilibili_url(url) is True

    def test_is_bilibili_url_invalid(self):
        """Test invalid Bilibili URL."""
        url = "https://www.bilibili.com/read/cv123456" # Article URL, not video
        assert URLValidator.is_bilibili_url(url) is False
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert URLValidator.is_bilibili_url(url) is False

    def test_is_valid_url_bilibili(self):
        """Test is_valid_url with Bilibili URL."""
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        assert URLValidator.is_valid_url(url) is True

    def test_is_valid_url_others(self):
        """Test is_valid_url with other URLs (should pass for now)."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert URLValidator.is_valid_url(url) is True
