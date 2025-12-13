"""
This module provides a service to interact with the yt-dlp library.
"""
import yt_dlp

# Quality display name -> yt-dlp format string
QUALITY_OPTIONS = {
    "Best": "bestvideo+bestaudio/best",
    "4K": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "1440p": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "Audio Only": "bestaudio/best",
}

# Ordered list for UI display (highest to lowest quality)
QUALITY_OPTIONS_LIST = ["Best", "4K", "1440p", "1080p", "720p", "480p", "360p", "Audio Only"]

# Video container formats
VIDEO_FORMAT_OPTIONS = {
    "MP4": "mp4",
    "WebM": "webm",
    "MKV": "mkv",
}

VIDEO_FORMAT_OPTIONS_LIST = ["MP4", "WebM", "MKV"]

# Audio formats (used when "Audio Only" quality is selected)
AUDIO_FORMAT_OPTIONS = {
    "M4A": "m4a",
    "MP3": "mp3",
    "OGG": "ogg",
}

AUDIO_FORMAT_OPTIONS_LIST = ["M4A", "MP3", "OGG"]

# Subtitle language options
# Key: Display name, Value: yt-dlp language code
SUBTITLE_LANGUAGE_OPTIONS = {
    "Auto (All Available)": "all",
    "English": "en",
    "Chinese (Simplified)": "zh-Hans",
    "Chinese (Traditional)": "zh-Hant",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
}

SUBTITLE_LANGUAGE_OPTIONS_LIST = [
    "Auto (All Available)", "English", "Chinese (Simplified)", "Chinese (Traditional)",
    "Spanish", "French", "German", "Japanese", "Korean", "Portuguese", "Russian"
]

# Download preset configurations
# Key: Preset display name
# Value: dict with 'quality' and 'format' keys
DOWNLOAD_PRESETS = {
    "High Quality": {"quality": "Best", "format": "MP4"},
    "Balanced": {"quality": "1080p", "format": "MP4"},
    "Fast Download": {"quality": "720p", "format": "MP4"},
    "Audio Only": {"quality": "Audio Only", "format": "M4A"},
    "Custom": {"quality": None, "format": None},
}

DOWNLOAD_PRESETS_LIST = ["High Quality", "Balanced", "Fast Download", "Audio Only", "Custom"]

# Tooltips for each preset
DOWNLOAD_PRESET_TOOLTIPS = {
    "High Quality": "Best available quality in MP4 format. Larger file sizes.",
    "Balanced": "1080p resolution in MP4 format. Good balance of quality and size.",
    "Fast Download": "720p resolution in MP4 format. Smaller files, faster downloads.",
    "Audio Only": "Extract audio only in M4A format. No video.",
    "Custom": "Use your own quality and format settings.",
}


def get_format_string(quality: str) -> str:
    """Returns the yt-dlp format string for a given quality option.

    Args:
        quality (str): The quality display name (e.g., "1080p", "Best", "Audio Only").

    Returns:
        str: The yt-dlp format string, or "best" as fallback for unknown values.
    """
    return QUALITY_OPTIONS.get(quality, "best")


def get_video_format_ext(format_name: str) -> str:
    """Returns the file extension for a given video format option.

    Args:
        format_name (str): The format display name (e.g., "MP4", "WebM").

    Returns:
        str: The file extension, or "mp4" as fallback for unknown values.
    """
    return VIDEO_FORMAT_OPTIONS.get(format_name, "mp4")


def get_audio_format_ext(format_name: str) -> str:
    """Returns the file extension for a given audio format option.

    Args:
        format_name (str): The format display name (e.g., "MP3", "M4A").

    Returns:
        str: The file extension, or "m4a" as fallback for unknown values.
    """
    return AUDIO_FORMAT_OPTIONS.get(format_name, "m4a")


def get_subtitle_lang_code(language_name: str) -> str:
    """Returns the yt-dlp language code for a given subtitle language option.

    Args:
        language_name (str): The language display name (e.g., "English", "Chinese (Simplified)").

    Returns:
        str: The yt-dlp language code, or "en" as fallback for unknown values.
    """
    return SUBTITLE_LANGUAGE_OPTIONS.get(language_name, "en")


def get_preset_config(preset_name: str) -> dict:
    """Returns the quality and format configuration for a given preset.

    Args:
        preset_name (str): The preset display name (e.g., "High Quality", "Balanced").

    Returns:
        dict: A dictionary with 'quality' and 'format' keys, or None values for "Custom".
    """
    return DOWNLOAD_PRESETS.get(preset_name, {"quality": None, "format": None})


def detect_preset_from_settings(quality: str, format_name: str) -> str:
    """Detects which preset matches the given quality and format settings.

    Args:
        quality (str): The quality setting (e.g., "Best", "1080p").
        format_name (str): The format setting (e.g., "MP4", "M4A").

    Returns:
        str: The matching preset name, or "Custom" if no preset matches.
    """
    for preset_name, config in DOWNLOAD_PRESETS.items():
        if preset_name == "Custom":
            continue
        if config["quality"] == quality and config["format"] == format_name:
            return preset_name
    return "Custom"


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
                return ("This Bilibili video or collection requires authentication. "
                        "Please refer to the documentation for cookie setup.")
            elif 'too many requests' in error_lower or '412' in error_lower:
                return ("Too many requests. Bilibili may be rate limiting. "
                        "Please wait a few minutes and try again.")
            elif 'empty' in error_lower and 'playlist' in error_lower:
                return "The Bilibili collection or user space appears to be empty."
        
        # Detect Xiaohongshu URLs
        is_xiaohongshu = 'xiaohongshu.com' in url or 'xhslink.com' in url

        if is_xiaohongshu:
            if 'no video formats found' in error_lower:
                return ("This Xiaohongshu content could not be extracted. "
                        "It may require authentication or is restricted.")
            elif 'unsupported url' in error_lower:
                return ("The Xiaohongshu URL is not supported or invalid. "
                        "Please check the URL.")
            elif 'http error 404' in error_lower or 'not found' in error_lower:
                return "This Xiaohongshu content or user could not be found."
            elif 'http error 403' in error_lower or 'forbidden' in error_lower:
                return ("Access denied. This Xiaohongshu content may be private or require authentication. "
                        "Please refer to the documentation for cookie setup.")
            elif 'empty' in error_lower and 'playlist' in error_lower:
                return "The Xiaohongshu user profile appears to be empty."
        
        # Generic error messages
        if 'network' in error_lower or 'connection' in error_lower:
            return f"Failed to fetch video. Check your internet connection. Details: {error_msg}"
        elif 'invalid' in error_lower or 'not found' in error_lower:
            return f"Invalid or unavailable video URL. Details: {error_msg}"
        
        # Return original error if no specific pattern matched
        return error_msg


    def download_video(self, video_url, download_folder_path, video_resolution="best",
                        video_format="mp4", audio_format="m4a", progress_hook=None, cookies_file=None,
                        subtitles_enabled=False, subtitle_language="en", embed_subtitles=False):
        """
        Downloads a video to the specified folder using yt-dlp.

        Args:
            video_url (str): The URL of the video to download.
            download_folder_path (str): The path to the folder where the video should be saved.
            video_resolution (str): The desired video resolution/quality format string.
            video_format (str): The desired video container format (mp4, webm, mkv).
            audio_format (str): The desired audio format for audio-only downloads (mp3, m4a, ogg).
            progress_hook (callable, optional): A function to call for progress updates. Defaults to None.
            cookies_file (str, optional): Path to a Netscape-style cookies file. Defaults to None.
            subtitles_enabled (bool): Whether to download subtitles. Defaults to False.
            subtitle_language (str): The yt-dlp language code for subtitles. Defaults to "en".
            embed_subtitles (bool): Whether to embed subtitles in the video. Defaults to False.

        Returns:
            tuple: (True, subtitle_status, None) on success, (False, None, error_message) on failure.
            subtitle_status can be: "with_subs", "no_subs", "subs_embedded", or None.
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
            'noplaylist': True,  # Ensure only single video is downloaded
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
        
        # Detect audio-only mode and apply appropriate post-processor
        is_audio_only = video_resolution == "bestaudio/best"
        postprocessors = []
        
        if is_audio_only:
            # Audio extraction with format conversion
            codec_map = {'mp3': 'mp3', 'm4a': 'aac', 'ogg': 'vorbis'}
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec_map.get(audio_format, 'aac'),
                'preferredquality': '192',
            })
        else:
            # Video download with container format
            ydl_opts['merge_output_format'] = video_format
        
        # Handle subtitle options
        subtitle_status = None
        if subtitles_enabled and not is_audio_only:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True  # Also try auto-generated subtitles
            if subtitle_language == "all":
                ydl_opts['allsubtitles'] = True
            else:
                ydl_opts['subtitleslangs'] = [subtitle_language]
            
            if embed_subtitles:
                postprocessors.append({
                    'key': 'FFmpegEmbedSubtitle',
                })
        
        if postprocessors:
            ydl_opts['postprocessors'] = postprocessors
        
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(video_url, download=True)
                
                # Determine subtitle status
                if subtitles_enabled and not is_audio_only:
                    subtitle_status = self._check_subtitle_result(result, embed_subtitles)
            
            return True, subtitle_status, None
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # Check for FFmpeg-related errors
            if 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
                return False, None, "FFmpeg is required for audio/subtitle processing. Please install FFmpeg and try again."
            return False, None, self._format_error_message(video_url, error_msg)
        except Exception as e:
            return False, None, f"An unexpected error occurred: {str(e)}"

    def _check_subtitle_result(self, result, embed_subtitles):
        """Checks the download result to determine subtitle status.
        
        Args:
            result: The yt-dlp extraction result dictionary.
            embed_subtitles (bool): Whether subtitles were supposed to be embedded.
            
        Returns:
            str: "with_subs", "no_subs", or "subs_embedded"
        """
        if result is None:
            return "no_subs"
        
        has_subtitles = bool(result.get('subtitles') or result.get('automatic_captions'))
        requested_subtitles = result.get('requested_subtitles')
        
        if requested_subtitles:
            if embed_subtitles:
                return "subs_embedded"
            return "with_subs"
        elif has_subtitles:
            # Subtitles were available but maybe not in requested language
            return "with_subs"
        else:
            return "no_subs"
