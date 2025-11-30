"""
This module provides a service to interact with the yt-dlp library.
"""
import yt_dlp

class YtDlpService:
    """
    A service class that wraps the yt-dlp library to fetch video information.
    """
    def get_video_info(self, url, cookies_file=None):
        """
        Fetches video information for the given URL using yt-dlp.
        If the URL is a playlist, it returns a list of video information dictionaries.

        Args:
            url (str): The URL of the video or playlist.
            cookies_file (str, optional): Path to a Netscape-style cookies file. Defaults to None.

        Returns:
            list: A list of dictionaries containing the video information.
            str: An error message if an error occurs.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            # DO NOT use 'extract_flat' here as it breaks single video metadata
            # Single videos need full metadata extraction to work properly
        }
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # It's a playlist
                    entries = list(info['entries']) # Convert to list if it's a generator
                    # Note: Without extract_flat, entries will have full metadata
                    # No need to propagate from parent playlist
                    return entries, None
                else:
                    # It's a single video
                    return [info], None
        except yt_dlp.utils.DownloadError as e:
            return None, self._format_error_message(url, str(e))
    
    def _format_error_message(self, url: str, error_msg: str) -> str:
        """
        Formats error messages with platform-specific context.
        
        Args:
            url (str): The URL that caused the error.
            error_msg (str): The original error message.
            
        Returns:
            str: A user-friendly error message.
        """
        error_lower = error_msg.lower()
        
        # Detect Bilibili URLs
        is_bilibili = 'bilibili.com' in url or 'b23.tv' in url
        
        if is_bilibili:
            if 'geo-restrict' in error_lower or 'not available in your region' in error_lower:
                return "This Bilibili video is not available in your region. You may need to use a VPN or proxy."
            elif 'deleted' in error_lower:
                return "This Bilibili video may have been deleted or is no longer available."
            elif 'private' in error_lower or 'members-only' in error_lower:
                return ("This Bilibili video requires authentication. "
                        "Please refer to the documentation for cookie setup.")
        
        # Generic error messages
        if 'network' in error_lower or 'connection' in error_lower:
            return f"Failed to fetch video. Check your internet connection. Details: {error_msg}"
        elif 'invalid' in error_lower or 'not found' in error_lower:
            return f"Invalid or unavailable video URL. Details: {error_msg}"
        
        # Return original error if no specific pattern matched
        return error_msg


    def download_video(self, video_url, download_folder_path, video_resolution="best", progress_hook=None, cookies_file=None):
        """
        Downloads a video to the specified folder using yt-dlp.

        Args:
            video_url (str): The URL of the video to download.
            download_folder_path (str): The path to the folder where the video should be saved.
            video_resolution (str): The desired video resolution.
            progress_hook (callable, optional): A function to call for progress updates. Defaults to None.
            cookies_file (str, optional): Path to a Netscape-style cookies file. Defaults to None.

        Returns:
            tuple: (True, None) on success, (False, error_message) on failure.
        """
        # Handle Bilibili format restrictions
        # Bilibili's "best" quality may require premium membership
        # Use a fallback format string that selects best available non-premium quality
        is_bilibili = 'bilibili.com' in video_url or 'b23.tv' in video_url
        
        if is_bilibili and video_resolution == "best":
            # Use format that selects best available format without requiring premium
            # This allows yt-dlp to fallback to lower quality if best is premium-only
            format_string = "bestvideo+bestaudio/best"
        else:
            format_string = video_resolution
        
        ydl_opts = {
            'format': format_string,
            'outtmpl': f'{download_folder_path}/%(title)s.%(ext)s',
            'noplaylist': True, # Ensure only single video is downloaded
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True, None
        except yt_dlp.utils.DownloadError as e:
            return False, self._format_error_message(video_url, str(e))
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}"
