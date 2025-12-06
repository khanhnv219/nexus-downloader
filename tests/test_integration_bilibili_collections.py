"""
Integration tests for Bilibili Collections and User Spaces.
"""
import pytest
from nexus_downloader.core.yt_dlp_service import YtDlpService

@pytest.mark.integration
class TestBilibiliCollectionsIntegration:
    """Integration tests for Bilibili Collections and User Spaces."""

    def test_fetch_bilibili_collection_mocked(self):
        """
        Test fetching metadata for a Bilibili collection using a mock.
        This verifies that YtDlpService correctly handles the 'entries' structure
        returned by yt-dlp for playlists/collections.
        """
        from unittest.mock import MagicMock, patch
        
        # Mock response from yt-dlp for a collection
        mock_entries = [
            {
                'id': 'BV1xx411c7mD',
                'title': 'Video 1',
                'webpage_url': 'https://www.bilibili.com/video/BV1xx411c7mD',
                'thumbnail': 'http://example.com/thumb1.jpg'
            },
            {
                'id': 'BV1xx411c7mE',
                'title': 'Video 2',
                'webpage_url': 'https://www.bilibili.com/video/BV1xx411c7mE',
                'thumbnail': 'http://example.com/thumb2.jpg'
            }
        ]
        
        mock_info = {
            'id': 'ml123456',
            'title': 'Test Collection',
            'entries': mock_entries, # List of entries
            '_type': 'playlist'
        }
        
        with patch('nexus_downloader.core.yt_dlp_service.yt_dlp.YoutubeDL') as mock_ydl_cls:
            mock_instance = mock_ydl_cls.return_value
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.extract_info.return_value = mock_info
            
            service = YtDlpService()
            url = "https://www.bilibili.com/medialist/play/ml123456"
            
            videos, error = service.get_video_info(url)
            
            assert error is None
            assert videos is not None
            assert len(videos) == 2
            assert videos[0]['title'] == 'Video 1'
            assert videos[1]['title'] == 'Video 2'
            
            # Verify extract_info was called with the URL
            mock_instance.extract_info.assert_called_with(url, download=False)
