"""
Unit tests for the HistoryService module.
"""
import os
import json
import pytest
import tempfile
from nexus_downloader.services.history_service import HistoryService
from nexus_downloader.core.data_models import HistoryEntry


@pytest.fixture
def temp_history_dir():
    """Create a temporary directory for history tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def history_service(temp_history_dir):
    """Create a HistoryService instance with a temporary directory."""
    return HistoryService(history_dir=temp_history_dir)


# HistoryEntry tests
def test_create_history_entry():
    """Test creating a HistoryEntry with all fields."""
    entry = HistoryEntry(
        url="https://youtube.com/watch?v=abc123",
        title="Test Video",
        platform="YouTube",
        download_date="2025-12-13T15:30:00",
        file_path="/downloads/test.mp4",
        file_size=12345678,
        quality="1080p",
        format="MP4",
        status="completed"
    )
    assert entry.url == "https://youtube.com/watch?v=abc123"
    assert entry.title == "Test Video"
    assert entry.platform == "YouTube"
    assert entry.download_date == "2025-12-13T15:30:00"
    assert entry.file_path == "/downloads/test.mp4"
    assert entry.file_size == 12345678
    assert entry.quality == "1080p"
    assert entry.format == "MP4"
    assert entry.status == "completed"
    assert entry.id is not None  # UUID auto-generated


def test_history_entry_uuid_unique():
    """Test that each HistoryEntry gets a unique UUID."""
    entry1 = HistoryEntry(
        url="url1", title="Title1", platform="YouTube",
        download_date="2025-12-13T15:30:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    )
    entry2 = HistoryEntry(
        url="url2", title="Title2", platform="YouTube",
        download_date="2025-12-13T15:30:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    )
    assert entry1.id != entry2.id


def test_history_entry_create_timestamp():
    """Test that create_timestamp returns ISO 8601 format."""
    timestamp = HistoryEntry.create_timestamp()
    assert "T" in timestamp  # ISO 8601 format has T separator


# HistoryService tests
def test_load_empty_history(history_service):
    """Test loading history when no file exists returns empty list."""
    history = history_service.load_history()
    assert history == []


def test_add_entry_to_history(history_service):
    """Test adding an entry to history."""
    entry = HistoryEntry(
        url="https://youtube.com/watch?v=test",
        title="Test Video",
        platform="YouTube",
        download_date=HistoryEntry.create_timestamp(),
        file_path="/downloads/test.mp4",
        file_size=1000000,
        quality="1080p",
        format="MP4",
        status="completed"
    )
    history_service.add_entry(entry)
    
    assert len(history_service.get_all()) == 1
    assert history_service.get_all()[0].url == "https://youtube.com/watch?v=test"


def test_history_persistence(history_service, temp_history_dir):
    """Test that history persists to JSON file and can be reloaded."""
    entry = HistoryEntry(
        url="https://youtube.com/watch?v=persist",
        title="Persistent Video",
        platform="YouTube",
        download_date="2025-12-13T10:00:00",
        file_path="/downloads/persist.mp4",
        file_size=5000000,
        quality="720p",
        format="MP4",
        status="completed"
    )
    history_service.add_entry(entry)
    
    # Create new service to reload from file
    new_service = HistoryService(history_dir=temp_history_dir)
    loaded = new_service.get_all()
    
    assert len(loaded) == 1
    assert loaded[0].url == "https://youtube.com/watch?v=persist"
    assert loaded[0].title == "Persistent Video"


def test_load_existing_history(history_service, temp_history_dir):
    """Test loading history entries from file."""
    # Add multiple entries
    for i in range(3):
        entry = HistoryEntry(
            url=f"https://youtube.com/video{i}",
            title=f"Video {i}",
            platform="YouTube",
            download_date=HistoryEntry.create_timestamp(),
            file_path=f"/downloads/video{i}.mp4",
            file_size=1000 * i,
            quality="1080p",
            format="MP4",
            status="completed"
        )
        history_service.add_entry(entry)
    
    # Reload
    new_service = HistoryService(history_dir=temp_history_dir)
    loaded = new_service.get_all()
    
    assert len(loaded) == 3


def test_search_by_title(history_service):
    """Test searching history by title."""
    history_service.add_entry(HistoryEntry(
        url="url1", title="Python Tutorial", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    ))
    history_service.add_entry(HistoryEntry(
        url="url2", title="JavaScript Guide", platform="YouTube",
        download_date="2025-12-13T11:00:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    ))
    
    results = history_service.search("python")
    assert len(results) == 1
    assert results[0].title == "Python Tutorial"


def test_search_by_platform(history_service):
    """Test searching history by platform."""
    history_service.add_entry(HistoryEntry(
        url="url1", title="Video 1", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    ))
    history_service.add_entry(HistoryEntry(
        url="url2", title="Video 2", platform="TikTok",
        download_date="2025-12-13T11:00:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    ))
    
    results = history_service.search("tiktok")
    assert len(results) == 1
    assert results[0].platform == "TikTok"


def test_search_by_url(history_service):
    """Test searching history by URL."""
    history_service.add_entry(HistoryEntry(
        url="https://youtube.com/abc123", title="Video 1", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    ))
    history_service.add_entry(HistoryEntry(
        url="https://tiktok.com/xyz789", title="Video 2", platform="TikTok",
        download_date="2025-12-13T11:00:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    ))
    
    results = history_service.search("abc123")
    assert len(results) == 1
    assert "abc123" in results[0].url


def test_search_case_insensitive(history_service):
    """Test that search is case-insensitive."""
    history_service.add_entry(HistoryEntry(
        url="url1", title="UPPERCASE Title", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    ))
    
    results = history_service.search("uppercase")
    assert len(results) == 1
    
    results = history_service.search("UPPERCASE")
    assert len(results) == 1


def test_search_empty_query(history_service):
    """Test that empty search returns all entries."""
    history_service.add_entry(HistoryEntry(
        url="url1", title="Video 1", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    ))
    history_service.add_entry(HistoryEntry(
        url="url2", title="Video 2", platform="TikTok",
        download_date="2025-12-13T11:00:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    ))
    
    results = history_service.search("")
    assert len(results) == 2


def test_get_entry_by_id(history_service):
    """Test getting a specific entry by ID."""
    entry = HistoryEntry(
        url="url1", title="Video 1", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    )
    history_service.add_entry(entry)
    
    found = history_service.get_entry_by_id(entry.id)
    assert found is not None
    assert found.id == entry.id
    assert found.title == "Video 1"


def test_get_entry_by_id_not_found(history_service):
    """Test getting an entry with non-existent ID returns None."""
    result = history_service.get_entry_by_id("non-existent-id")
    assert result is None


def test_entries_ordered_most_recent_first(history_service):
    """Test that entries are ordered with most recent first."""
    entry1 = HistoryEntry(
        url="url1", title="First Entry", platform="YouTube",
        download_date="2025-12-13T10:00:00", file_path="/test1.mp4",
        file_size=100, quality="720p", format="MP4", status="completed"
    )
    entry2 = HistoryEntry(
        url="url2", title="Second Entry", platform="YouTube",
        download_date="2025-12-13T11:00:00", file_path="/test2.mp4",
        file_size=200, quality="720p", format="MP4", status="completed"
    )
    history_service.add_entry(entry1)
    history_service.add_entry(entry2)
    
    entries = history_service.get_all()
    # Second entry should be first (most recent)
    assert entries[0].title == "Second Entry"
    assert entries[1].title == "First Entry"


def test_invalid_json_backup_and_reset(temp_history_dir):
    """Test that corrupted JSON file is backed up and service starts fresh."""
    # Create corrupted JSON file
    history_path = os.path.join(temp_history_dir, "download_history.json")
    with open(history_path, 'w') as f:
        f.write("{ invalid json }")
    
    # Create service - should handle corrupted file
    service = HistoryService(history_dir=temp_history_dir)
    
    # Should start with empty history
    assert len(service.get_all()) == 0
    
    # Backup file should exist
    backup_path = history_path + ".backup"
    assert os.path.exists(backup_path)
