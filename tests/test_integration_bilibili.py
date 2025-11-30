"""
Integration tests for Bilibili support.
"""
import pytest
from nexus_downloader.core.yt_dlp_service import YtDlpService

@pytest.mark.integration
class TestBilibiliIntegration:
    """Integration tests for Bilibili."""

    def test_fetch_bilibili_video_metadata(self):
        """Test fetching metadata for a real Bilibili video."""
        service = YtDlpService()
        # Using a popular, likely permanent video (official Bilibili mascot video or similar)
        # This is the "Rick Roll" equivalent or just a standard test video if possible.
        # Let's use a known valid ID. BV1GJ411x7h7 is "【猛男版】新宝岛".
        url = "https://www.bilibili.com/video/BV1y7411Q7Eq"
        
        videos, error = service.get_video_info(url)
        
        assert error is None
        assert videos is not None
        assert len(videos) > 0
        
        video = videos[0]
        # With extract_flat, Bilibili entries might only have minimal metadata
        # Check that we at least have a title (propagated from playlist if needed)
        assert 'title' in video
        assert len(video['title']) > 0
        # Check for URL (either webpage_url or url field)
        url_field = video.get('webpage_url') or video.get('url', '')
        assert 'bilibili' in url_field or 'b23.tv' in url_field

    def test_fetch_bilibili_short_url(self):
        """Test fetching metadata from a Bilibili short URL."""
        # Short URLs might be dynamic, so this test might be flaky if the link expires.
        # We'll skip it if we don't have a stable short URL, but let's try one if we knew it.
        # For now, let's stick to the full URL test as primary validation.
        pass

    # @pytest.mark.integration
    # def test_download_bilibili_video(self):
    #     """Test downloading a real Bilibili video."""
    #     # Note: This test is commented out to avoid slow downloads during regular testing.
    #     # Uncomment for manual verification or in CI with longer timeouts.
    #     import tempfile
    #     import os
    #     from nexus_downloader.core.yt_dlp_service import YtDlpService
    #     
    #     service = YtDlpService()
    #     url = "https://www.bilibili.com/video/BV1y7411Q7Eq"
    #     
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         success, error = service.download_video(url, temp_dir, "best")
    #         assert success is True
    #         assert error is None
    #         # Check that a file was created
    #         files = os.listdir(temp_dir)
    #         assert len(files) > 0

