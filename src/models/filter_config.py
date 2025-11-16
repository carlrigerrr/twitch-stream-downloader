"""
Filter configuration model for video filtering.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class FilterConfig:
    """Configuration for filtering Twitch videos."""

    days_back: int = 7
    max_videos: int = 10
    language: str = "all"
    video_type: str = "all"  # "all", "archive", "highlight", "upload"
    min_duration: Optional[int] = None  # in minutes
    max_duration: Optional[int] = None  # in minutes
    min_views: Optional[int] = None
    max_views: Optional[int] = None
    sort_by: str = "time"  # "time", "trending", "views"

    def to_dict(self):
        """Convert filter config to dictionary."""
        return {
            "days_back": self.days_back,
            "max_videos": self.max_videos,
            "language": self.language,
            "video_type": self.video_type,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "min_views": self.min_views,
            "max_views": self.max_views,
            "sort_by": self.sort_by
        }

    @classmethod
    def from_dict(cls, data):
        """Create FilterConfig from dictionary."""
        return cls(
            days_back=data.get("days_back", 7),
            max_videos=data.get("max_videos", 10),
            language=data.get("language", "all"),
            video_type=data.get("video_type", "all"),
            min_duration=data.get("min_duration"),
            max_duration=data.get("max_duration"),
            min_views=data.get("min_views"),
            max_views=data.get("max_views"),
            sort_by=data.get("sort_by", "time")
        )

    def matches_video(self, video):
        """
        Check if a video matches the filter criteria.

        Args:
            video: Video instance to check

        Returns:
            bool: True if video matches all filter criteria
        """
        # Check language
        if self.language != "all" and video.language != self.language:
            return False

        # Check video type
        if self.video_type != "all" and video.video_type != self.video_type:
            return False

        # Check duration (in minutes)
        duration_min = video.duration_minutes
        if self.min_duration is not None and duration_min < self.min_duration:
            return False
        if self.max_duration is not None and duration_min > self.max_duration:
            return False

        # Check views
        if self.min_views is not None and video.view_count < self.min_views:
            return False
        if self.max_views is not None and video.view_count > self.max_views:
            return False

        return True

    def get_summary(self):
        """Get a human-readable summary of the filters."""
        filters = []

        filters.append(f"Last {self.days_back} days")
        filters.append(f"Max {self.max_videos} videos")

        if self.language != "all":
            filters.append(f"Language: {self.language}")

        if self.video_type != "all":
            filters.append(f"Type: {self.video_type}")

        if self.min_duration is not None or self.max_duration is not None:
            min_d = self.min_duration or 0
            max_d = self.max_duration or "∞"
            filters.append(f"Duration: {min_d}-{max_d} min")

        if self.min_views is not None or self.max_views is not None:
            min_v = self.min_views or 0
            max_v = self.max_views or "∞"
            filters.append(f"Views: {min_v}-{max_v}")

        return " | ".join(filters)
