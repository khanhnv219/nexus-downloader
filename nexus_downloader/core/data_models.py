"""
This module contains the data models for the application.
"""
from dataclasses import dataclass
from enum import Enum, auto

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
