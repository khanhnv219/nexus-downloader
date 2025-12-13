"""
This module contains the data models for the application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional
import uuid

class DownloadStatus(Enum):
    """
    Represents the status of a download.
    """
    PENDING = auto()
    QUEUED = auto()
    FETCHING = auto()
    READY = auto()
    DOWNLOADING = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    ERROR = auto()

@dataclass
class DownloadItem:
    """
    Represents a single video that can be downloaded.
    """
    video_url: str
    title: str = ""
    thumbnail_url: str = ""
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    file_size: str = ""
    error_message: str = ""
    resolution: str = ""
    selected: bool = False


@dataclass
class HistoryEntry:
    """Represents a single download history record."""
    url: str
    title: str
    platform: str
    download_date: str
    file_path: str
    file_size: int
    quality: str
    format: str
    status: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @staticmethod
    def create_timestamp() -> str:
        """Create an ISO 8601 formatted timestamp for the current time."""
        return datetime.now().isoformat()
