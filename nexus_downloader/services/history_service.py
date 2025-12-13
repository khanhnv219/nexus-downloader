"""
Service for managing download history persistence using JSON.
"""
import json
import os
from dataclasses import asdict
from typing import List
import logging

from nexus_downloader.core.data_models import HistoryEntry

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing download history persistence."""
    HISTORY_FILE_NAME = "download_history.json"

    def __init__(self, history_dir: str = None):
        """Initialize the history service.

        Args:
            history_dir: Directory to store history file. Defaults to ~/.nexus_downloader/
        """
        if history_dir:
            self.history_dir = history_dir
        else:
            self.history_dir = os.path.join(os.path.expanduser("~"), ".nexus_downloader")
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_path = os.path.join(self.history_dir, self.HISTORY_FILE_NAME)
        self._history: List[HistoryEntry] = []
        self.load_history()

    def load_history(self) -> List[HistoryEntry]:
        """Load history from JSON file.

        Returns:
            List of HistoryEntry objects.
        """
        if not os.path.exists(self.history_path):
            self._history = []
            return self._history

        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._history = []
            for entry_dict in data:
                try:
                    entry = HistoryEntry(**entry_dict)
                    self._history.append(entry)
                except TypeError as e:
                    logger.warning(f"Skipping invalid history entry: {e}")
                    continue

            return self._history
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in history file: {e}. Starting fresh.")
            self._backup_and_reset()
            return self._history
        except OSError as e:
            logger.error(f"Error loading history: {e}")
            self._history = []
            return self._history

    def _backup_and_reset(self) -> None:
        """Backup corrupted history file and start fresh."""
        backup_path = self.history_path + ".backup"
        try:
            if os.path.exists(self.history_path):
                os.rename(self.history_path, backup_path)
                logger.info(f"Corrupted history backed up to {backup_path}")
        except OSError as e:
            logger.error(f"Failed to backup history: {e}")
        self._history = []

    def save_history(self) -> None:
        """Save history to JSON file."""
        try:
            data = [asdict(entry) for entry in self._history]
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error(f"Error saving history: {e}")
            raise

    def add_entry(self, entry: HistoryEntry) -> None:
        """Add entry and persist to file.

        Args:
            entry: HistoryEntry to add.
        """
        self._history.insert(0, entry)  # Add to beginning (most recent first)
        self.save_history()

    def search(self, query: str) -> List[HistoryEntry]:
        """Filter history by title, URL, or platform (case-insensitive).

        Args:
            query: Search string to match.

        Returns:
            List of matching HistoryEntry objects.
        """
        if not query:
            return self._history

        query_lower = query.lower()
        return [
            entry for entry in self._history
            if query_lower in entry.title.lower()
            or query_lower in entry.url.lower()
            or query_lower in entry.platform.lower()
        ]

    def get_all(self) -> List[HistoryEntry]:
        """Return all history entries.

        Returns:
            List of all HistoryEntry objects.
        """
        return self._history

    def get_entry_by_id(self, entry_id: str) -> HistoryEntry | None:
        """Get a specific history entry by ID.

        Args:
            entry_id: The UUID of the entry.

        Returns:
            HistoryEntry if found, None otherwise.
        """
        for entry in self._history:
            if entry.id == entry_id:
                return entry
        return None
