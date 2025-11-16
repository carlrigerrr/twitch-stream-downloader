"""
Video data model for Twitch videos.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Video:
    """Represents a Twitch video with its metadata."""

    id: str
    title: str
    url: str
    duration: int  # Duration in seconds
    view_count: int
    created_at: str
    thumbnail_url: str
    user_name: str
    user_id: str
    language: str
    video_type: str  # "archive", "highlight", "upload"
    description: Optional[str] = ""

    @property
    def duration_formatted(self):
        """Get duration in human-readable format (HH:MM:SS)."""
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @property
    def duration_minutes(self):
        """Get duration in minutes."""
        return self.duration // 60

    @property
    def view_count_formatted(self):
        """Get view count in human-readable format."""
        if self.view_count >= 1_000_000:
            return f"{self.view_count / 1_000_000:.1f}M"
        elif self.view_count >= 1_000:
            return f"{self.view_count / 1_000:.1f}K"
        else:
            return str(self.view_count)

    @property
    def created_at_formatted(self):
        """Get creation date in human-readable format."""
        try:
            dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return self.created_at

    def to_dict(self):
        """Convert video to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "duration": self.duration,
            "duration_formatted": self.duration_formatted,
            "view_count": self.view_count,
            "view_count_formatted": self.view_count_formatted,
            "created_at": self.created_at,
            "created_at_formatted": self.created_at_formatted,
            "thumbnail_url": self.thumbnail_url,
            "user_name": self.user_name,
            "user_id": self.user_id,
            "language": self.language,
            "video_type": self.video_type,
            "description": self.description
        }

    @classmethod
    def from_api_response(cls, data):
        """Create Video instance from Twitch API response."""
        # Parse duration from format like "1h2m3s" or "2m30s"
        duration_str = data.get('duration', '0s')
        duration = cls._parse_duration(duration_str)

        return cls(
            id=data.get('id', ''),
            title=data.get('title', 'Untitled'),
            url=data.get('url', ''),
            duration=duration,
            view_count=int(data.get('view_count', 0)),
            created_at=data.get('created_at', ''),
            thumbnail_url=data.get('thumbnail_url', ''),
            user_name=data.get('user_name', ''),
            user_id=data.get('user_id', ''),
            language=data.get('language', 'en'),
            video_type=data.get('type', 'archive'),
            description=data.get('description', '')
        )

    @staticmethod
    def _parse_duration(duration_str):
        """Parse Twitch duration format (e.g., '1h2m3s') to seconds."""
        import re

        total_seconds = 0

        # Extract hours
        hours_match = re.search(r'(\d+)h', duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600

        # Extract minutes
        minutes_match = re.search(r'(\d+)m', duration_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60

        # Extract seconds
        seconds_match = re.search(r'(\d+)s', duration_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))

        return total_seconds

    def __str__(self):
        """String representation of the video."""
        return f"{self.title} ({self.duration_formatted}) - {self.view_count_formatted} views"
