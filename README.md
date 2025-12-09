# Nexus Downloader

A powerful, user-friendly desktop application for downloading videos from YouTube, TikTok, Facebook, and Bilibili with advanced features like batch downloads, progress tracking, and quality selection.

![GitHub Release](https://img.shields.io/github/v/release/khanhnv219/nexus-downloader)
![GitHub License](https://img.shields.io/github/license/khanhnv219/nexus-downloader)

## Features

- 🎬 **Multi-Platform Support**: Download from YouTube, TikTok, Facebook, Bilibili, and Xiaohongshu
- 📦 **Batch Downloads**: Process multiple URLs at once
- 📊 **Real-time Progress**: Visual progress bars and status updates
- 🎯 **Quality Selection**: Choose your preferred video resolution
- 🚀 **Concurrent Downloads**: Download multiple videos simultaneously
- 💾 **Smart Path Management**: Portable download paths using `~`
- 🔔 **Completion Notifications**: Get notified when downloads finish
- 🧹 **List Management**: Clear completed or all downloads with one click
- ⚙️ **Cookie Support**: Use browser cookies for private/restricted videos
- 🎨 **Modern UI**: Clean, dark-themed interface built with PySide6
- **Bilibili**: Download single videos, user spaces (channels), and collections (playlists).
- **Xiaohongshu**: Download videos, short links, and user profiles.

## Installation

### Windows

Download the latest `NexusDownloader.exe` from the [Releases](https://github.com/khanhnv219/nexus-downloader/releases) page.

**Important**: You need [ffmpeg](https://ffmpeg.org/download.html) installed and in your system PATH for video processing.

### From Source

```bash
# Clone the repository
git clone https://github.com/khanhnv219/nexus-downloader.git
cd nexus-downloader

# Create virtual environment using uv (recommended)
uv venv venv

# Install dependencies
uv pip install --python venv -r requirements.txt

# Run the application
python -m nexus_downloader
```

## Requirements

- Python 3.11+
- PySide6
- yt-dlp
- ffmpeg (must be in system PATH)

## Usage

1. **Launch the application**
2. **Enter video URL(s)**: Paste one or multiple URLs in the input field
3. **Click "Get Download Urls"**: Fetch video information
4. **Select videos**: Check the videos you want to download
5. **Choose quality**: Select your preferred resolution
6. **Click "Download"**: Start downloading
7. **Monitor progress**: Watch the progress bars update in real-time

### Settings

Click the ⚙️ icon to configure:
- Download folder path
- Concurrent downloads limit (1-10)
- Browser cookies file (for restricted content)
- Video resolution preference

## Building from Source

To create a standalone executable:

```bash
# Install PyInstaller
uv pip install --python venv pyinstaller

# Build the executable
venv/Scripts/pyinstaller --noconfirm --onefile --windowed --name "NexusDownloader" --add-data "nexus_downloader/ui/styles.qss;nexus_downloader/ui" nexus_downloader/__main__.py

# Find the executable in dist/NexusDownloader.exe
```

## Development

### Project Structure

```
nexus-downloader/
├── nexus_downloader/
│   ├── __main__.py           # Application entry point
│   ├── core/
│   │   ├── download_manager.py   # Download orchestration
│   │   ├── data_models.py        # Data classes
│   │   └── ytdlp_service.py      # yt-dlp wrapper
│   ├── services/
│   │   └── settings_service.py   # Settings management
│   └── ui/
│       ├── main_window.py        # Main UI
│       ├── settings_dialog.py    # Settings UI
│       └── styles.qss            # Styling
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Running Tests

```bash
pytest
```

## Technologies

- **UI Framework**: PySide6 (Qt for Python)
- **Video Downloader**: yt-dlp
- **Settings Storage**: JSON
- **Build Tool**: PyInstaller
- **Package Manager**: uv

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the powerful download engine
- [PySide6](https://www.qt.io/qt-for-python) for the cross-platform UI framework

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub Issues](https://github.com/khanhnv219/nexus-downloader/issues) page.

---

Made with ❤️ by [Khanh Nguyen](https://github.com/khanhnv219)
