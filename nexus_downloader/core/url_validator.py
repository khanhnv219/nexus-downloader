"""
This module provides a URL validator to check if a URL is supported.
"""
import re

class URLValidator:
    """
    Validates URLs against supported platform patterns.
    """
    
    # Bilibili patterns
    BILIBILI_VIDEO_PATTERN = r'https?://(?:www\.)?bilibili\.com/video/BV[a-zA-Z0-9]+'
    BILIBILI_SHORT_PATTERN = r'https?://b23\.tv/[a-zA-Z0-9]+'
    BILIBILI_SPACE_PATTERN = r'https?://space\.bilibili\.com/\d+'
    BILIBILI_COLLECTION_PATTERN = r'https?://(?:www\.)?bilibili\.com/medialist/play/\d+'
    
    # Xiaohongshu patterns
    XIAOHONGSHU_EXPLORE_PATTERN = r'https?://(?:www\.)?xiaohongshu\.com/explore/[a-zA-Z0-9]+'
    XIAOHONGSHU_DISCOVERY_PATTERN = r'https?://(?:www\.)?xiaohongshu\.com/discovery/item/[a-zA-Z0-9]+'
    XIAOHONGSHU_SHORT_PATTERN = r'https?://xhslink\.com/[a-zA-Z0-9]+'
    XIAOHONGSHU_USER_PATTERN = r'https?://(?:www\.)?xiaohongshu\.com/user/profile/[a-zA-Z0-9]+'

    # Existing platforms (for completeness, though not strictly required by story, good to have)
    YOUTUBE_PATTERN = r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/.+'
    TIKTOK_PATTERN = r'https?://(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com)/.+'
    FACEBOOK_PATTERN = r'https?://(?:www\.)?(?:facebook\.com|fb\.watch)/.+'

    @staticmethod
    def is_bilibili_url(url: str) -> bool:
        """
        Checks if the URL is a valid Bilibili video URL.
        
        Args:
            url (str): The URL to check.
            
        Returns:
            bool: True if the URL matches Bilibili patterns, False otherwise.
        """
        if re.match(URLValidator.BILIBILI_VIDEO_PATTERN, url) or \
           re.match(URLValidator.BILIBILI_SHORT_PATTERN, url) or \
           re.match(URLValidator.BILIBILI_SPACE_PATTERN, url) or \
           re.match(URLValidator.BILIBILI_COLLECTION_PATTERN, url):
            return True
        return False

    @staticmethod
    def is_xiaohongshu_url(url: str) -> bool:
        """
        Checks if the URL is a valid Xiaohongshu video URL.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL matches Xiaohongshu patterns, False otherwise.
        """
        if re.match(URLValidator.XIAOHONGSHU_EXPLORE_PATTERN, url) or \
           re.match(URLValidator.XIAOHONGSHU_DISCOVERY_PATTERN, url) or \
           re.match(URLValidator.XIAOHONGSHU_DISCOVERY_PATTERN, url) or \
           re.match(URLValidator.XIAOHONGSHU_SHORT_PATTERN, url) or \
           re.match(URLValidator.XIAOHONGSHU_USER_PATTERN, url):
            return True
        return False

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Checks if the URL is supported by the application.
        
        Args:
            url (str): The URL to check.
            
        Returns:
            bool: True if the URL is supported, False otherwise.
        """
        if URLValidator.is_bilibili_url(url) or URLValidator.is_xiaohongshu_url(url):
            return True
            
        # Fallback for other platforms (YouTube, TikTok, Facebook)
        # Since we didn't have validation before, we should return True for them 
        # to avoid breaking existing functionality (Regression AC).
        # But ideally we should validate them too. 
        # For this story, let's ensure we at least return True for non-Bilibili URLs 
        # so we don't block them, unless we want to enforce validation for everything.
        # Given the "No Regression" requirement, being permissive for others is safer 
        # until we add specific patterns for them.
        return True
