import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class AppSettings:
    download_folder_path: str = field(default_factory=lambda: os.path.join(os.path.expanduser("~"), "Downloads"))
    concurrent_downloads_limit: int = 2
    facebook_cookies_path: str = ""
    bilibili_cookies_path: str = ""
    xiaohongshu_cookies_path: str = ""
    video_resolution: str = "best"
    video_format: str = "MP4"
    audio_format: str = "M4A"
    subtitles_enabled: bool = False
    subtitle_language: str = "English"
    embed_subtitles: bool = False
    download_preset: str = "Balanced"

class SettingsService:
    """
    Service for managing application settings persistence using JSON.
    """
    SETTINGS_FILE_NAME = "settings.json"

    def __init__(self, settings_dir: str = None):
        if settings_dir:
            self.settings_dir = settings_dir
        else:
            # Store settings in a user-specific application data directory
            self.settings_dir = os.path.join(os.path.expanduser("~"), ".nexus_downloader")
        
        os.makedirs(self.settings_dir, exist_ok=True)
        self.settings_path = os.path.join(self.settings_dir, self.SETTINGS_FILE_NAME)

    def load_settings(self) -> AppSettings:
        """Loads application settings from the JSON file. Returns default settings if none are found or an error occurs."""
        if not os.path.exists(self.settings_path):
            default_settings = AppSettings()
            self.save_settings(default_settings)
            return default_settings

        try:
            with open(self.settings_path, 'r') as f:
                settings_data = json.load(f)
            
            # Handle path portability: expand '~' to user home
            if 'download_folder_path' in settings_data:
                settings_data['download_folder_path'] = os.path.expanduser(settings_data['download_folder_path'])
            
            # Filter out unknown keys and ensure types
            valid_keys = AppSettings.__annotations__.keys()
            filtered_data = {k: v for k, v in settings_data.items() if k in valid_keys}
            
            # Convert types if necessary (JSON handles basic types well, but just in case)
            if 'concurrent_downloads_limit' in filtered_data:
                filtered_data['concurrent_downloads_limit'] = int(filtered_data['concurrent_downloads_limit'])

            return AppSettings(**filtered_data)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error loading settings from {self.settings_path}: {e}")
            return AppSettings() # Return default settings on error

    def save_settings(self, settings: AppSettings):
        """Saves application settings to the JSON file."""
        try:
            settings_dict = asdict(settings)
            
            # Handle path portability: replace user home with '~'
            user_home = os.path.expanduser("~")
            if settings_dict['download_folder_path'].startswith(user_home):
                settings_dict['download_folder_path'] = settings_dict['download_folder_path'].replace(user_home, "~", 1)
                # Ensure we use forward slashes for better cross-platform compatibility in JSON, 
                # though os.path handles separators. 
                # But '~' expansion relies on os.path.expanduser which handles OS separators.
                # Let's keep it simple: replace prefix.

            with open(self.settings_path, 'w') as f:
                json.dump(settings_dict, f, indent=4)
        except OSError as e:
            logger.error(f"Error saving settings to {self.settings_path}: {e}")
            raise # Re-raise to be handled by the caller

# Example usage (for testing/demonstration)
if __name__ == "__main__":
    # Configure logging for better visibility
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Use a temporary directory for demonstration
    temp_dir = os.path.join(os.getcwd(), "temp_settings_test")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    service = SettingsService(settings_dir=temp_dir)
    settings_file = os.path.join(temp_dir, "settings.json")
    if os.path.exists(settings_file):
        os.remove(settings_file) # Clean up previous run

    print("--- Loading initial settings (should be defaults) ---")
    current_settings = service.load_settings()
    print(f"Loaded: {current_settings}")

    print("\n--- Modifying and saving settings ---")
    current_settings.concurrent_downloads_limit = 5
    # Test path portability
    current_settings.download_folder_path = os.path.join(os.path.expanduser("~"), "Downloads", "NexusTest")
    
    try:
        service.save_settings(current_settings)
        print(f"Saved: {current_settings}")
        
        # Verify JSON content for portability
        with open(settings_file, 'r') as f:
            json_content = json.load(f)
            print(f"JSON Content: {json_content}")
            if json_content['download_folder_path'].startswith("~"):
                print("SUCCESS: Path stored with '~'")
            else:
                print("FAILURE: Path NOT stored with '~'")

    except Exception as e:
        print(f"Failed to save settings: {e}")

    print("\n--- Loading modified settings ---")
    reloaded_settings = service.load_settings()
    print(f"Reloaded: {reloaded_settings}")
    
    # Verify expansion
    expected_path = os.path.join(os.path.expanduser("~"), "Downloads", "NexusTest")
    if reloaded_settings.download_folder_path == expected_path:
         print(f"SUCCESS: Path expanded correctly to {reloaded_settings.download_folder_path}")
    else:
         print(f"FAILURE: Path expansion failed. Got {reloaded_settings.download_folder_path}, expected {expected_path}")

    print("\n--- Cleaning up temporary directory ---")
    import shutil
    shutil.rmtree(temp_dir)
    print("Temporary directory removed.")
