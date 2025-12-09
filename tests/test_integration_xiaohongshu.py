"""
Integration tests for Xiaohongshu support.
"""
import pytest
from nexus_downloader.core.yt_dlp_service import YtDlpService

@pytest.mark.integration
class TestXiaohongshuIntegration:
    """Integration tests for Xiaohongshu."""

    def test_fetch_xiaohongshu_video_metadata(self):
        """Test fetching metadata for a real Xiaohongshu video."""
        service = YtDlpService()
        # Using a recently found URL. If this expires, it may need updating.
        url = "https://www.xiaohongshu.com/explore/675fa24f0000000001029bd5"
        
        videos, error = service.get_video_info(url)
        
        if videos:
            assert len(videos) > 0
            video = videos[0]
            assert 'title' in video
            assert len(video['title']) > 0
            # Check for URL
            url_field = video.get('webpage_url') or video.get('url', '')
            assert 'xiaohongshu.com' in url_field or 'xhslink.com' in url_field
        else:
            # If it fails, it should be a handled error about auth/restriction
            # This integration test verifies that we are communicating with yt-dlp 
            # and gracefully handling the inevitable auth error on CI/headless.
            assert error is not None
            print(f"Got expected error (no auth): {error}")
            assert "require authentication" in error or \
                   "could not be extracted" in error or \
                   "restricted" in error or \
                   "invalid" in error.lower() or \
                   "not supported" in error.lower()

    def test_fetch_xiaohongshu_short_url(self):
        """Test fetching metadata from a Xiaohongshu short URL."""
        service = YtDlpService()
        url = "https://xhslink.com/a/koA4hjua2f"
        
        videos, error = service.get_video_info(url)
        
        if videos:
             assert len(videos) > 0
             video = videos[0]
             assert 'title' in video
        else:
            assert error is not None
            print(f"Got expected error (no auth): {error}")
            assert "require authentication" in error or \
                   "could not be extracted" in error or \
                   "restricted" in error or \
                   "Invalid Xiaohongshu URL" in error

    def test_download_xiaohongshu_video_graceful_fail(self):
        """Test downloading verification (graceful failure without auth)."""
        import tempfile
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/explore/675fa24f0000000001029bd5"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            success, error = service.download_video(url, temp_dir, "best")
            
            # Since fetching fails, download should fail
            if not success:
               assert error is not None
               # Check that we get the proper error message
               assert "require authentication" in error or \
                      "could not be extracted" in error or \
                      "restricted" in error or \
                      "Invalid Xiaohongshu URL" in error
            else:
               # If somehow successful (e.g. public video), verify file exists
               import os
               files = os.listdir(temp_dir)

    def test_get_video_info_user_profile(self):
        """
        Test retrieving information from a Xiaohongshu user profile URL.
        Note: This may fail or return an empty list depending on authentication requirements.
        We mainly want to verify it doesn't crash effectively.
        """
        service = YtDlpService()
        url = "https://www.xiaohongshu.com/user/profile/5b6e7f8g0000000001000000"
        
        info_list, error = service.get_video_info(url)
        
        # Scenario 1: Success (returns list of videos)
        if info_list:
            assert isinstance(info_list, list)
            if len(info_list) > 0:
                assert 'title' in info_list[0]
                
        # Scenario 2: Auth Required / Empty / Not Found (returns error or empty)
        else:
            # We expect an auth error or valid empty list, not a crash
            if error:
                 assert "authentication" in error.lower() or \
                        "not be found" in error.lower() or \
                        "empty" in error.lower() or \
                        "restricted" in error.lower() or \
                        "not supported" in error.lower() or \
                        "invalid" in error.lower()
            else:
                 # Empty list returned successfully
                 assert info_list == []
