"""
Unit tests for Xiaohongshu error handling.
"""
import pytest
from nexus_downloader.core.yt_dlp_service import YtDlpService

class TestXiaohongshuErrorHandling:
    """Tests for Xiaohongshu-specific error handling."""
    
    def test_format_error_no_formats(self):
        """Test formatting for 'no video formats found' error."""
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/explore/123"
        error_msg = "ERROR: [XiaoHongShu] 123: No video formats found"
        
        formatted = service._format_error_message(url, error_msg)
        assert "This Xiaohongshu content could not be extracted" in formatted
        assert "require authentication" in formatted
        
    def test_format_error_unsupported_url(self):
        """Test formatting for 'unsupported url' error."""
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/explore/bad"
        error_msg = "ERROR: Unsupported URL: https://www.xiaohongshu.com/explore/bad"
        
        formatted = service._format_error_message(url, error_msg)
        assert "Invalid Xiaohongshu URL" in formatted
        
    def test_format_error_404(self):
        """Test formatting for 404 error."""
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/explore/123"
        error_msg = "HTTP Error 404: Not Found"
        
        formatted = service._format_error_message(url, error_msg)
        assert "no longer available" in formatted
        
    def test_format_error_403(self):
        """Test formatting for 403 error."""
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/explore/123"
        error_msg = "HTTP Error 403: Forbidden"
        
        formatted = service._format_error_message(url, error_msg)
        assert "Access denied" in formatted
        assert "requires authentication" in formatted
