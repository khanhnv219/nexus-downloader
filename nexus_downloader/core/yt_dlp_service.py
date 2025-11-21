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
            'extract_flat': 'in_playlist'
        }
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # It's a playlist
                    return info['entries'], None
                else:
                    # It's a single video
                    return [info], None
        except yt_dlp.utils.DownloadError as e:
            return None, str(e)

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
        ydl_opts = {
            'format': video_resolution,
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
            return False, str(e)
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}"
