"""
Video fetcher that combines Twitch API calls with filtering logic.
"""
from src.api.twitch_client import TwitchClient
from src.models.video import Video
from src.models.filter_config import FilterConfig
from src.utils.logger import logger
from src.utils.validators import validate_twitch_url


class VideoFetcher:
    """Handles fetching and filtering videos from Twitch."""

    def __init__(self, client_id, client_secret):
        """
        Initialize video fetcher.

        Args:
            client_id: Twitch API client ID
            client_secret: Twitch API client secret
        """
        self.client = TwitchClient(client_id, client_secret)

    def test_connection(self):
        """
        Test Twitch API connection.

        Returns:
            tuple: (success, message)
        """
        return self.client.test_credentials()

    def fetch_videos(self, category_url, filters):
        """
        Fetch videos from a Twitch category URL with filters.

        Args:
            category_url: Twitch category URL
            filters: FilterConfig instance

        Returns:
            tuple: (success, videos_list, error_message)
        """
        # Validate URL
        is_valid, game_name, error = validate_twitch_url(category_url)
        if not is_valid:
            logger.error(f"Invalid URL: {error}")
            return False, [], error

        logger.info(f"Fetching videos for game: {game_name}")

        # Get game ID
        game_id = self.client.get_game_id(game_name)
        if not game_id:
            error_msg = f"Could not find game '{game_name}' on Twitch"
            logger.error(error_msg)
            return False, [], error_msg

        # Fetch videos (fetch more than needed to account for filtering)
        fetch_limit = filters.max_videos * 3  # Fetch 3x to ensure we have enough after filtering
        raw_videos = self.client.get_videos(game_id, filters, max_results=fetch_limit)

        if not raw_videos:
            error_msg = "No videos found for this category"
            logger.warning(error_msg)
            return False, [], error_msg

        # Convert to Video objects
        videos = []
        for video_data in raw_videos:
            try:
                video = Video.from_api_response(video_data)
                videos.append(video)
            except Exception as e:
                logger.error(f"Error parsing video data: {e}")
                continue

        logger.info(f"Parsed {len(videos)} videos from API response")

        # Apply client-side filters
        filtered_videos = self._apply_filters(videos, filters)

        # Limit to max_videos
        final_videos = filtered_videos[:filters.max_videos]

        logger.info(f"After filtering: {len(final_videos)} videos match criteria")

        return True, final_videos, ""

    def _apply_filters(self, videos, filters):
        """
        Apply filter criteria to videos list.

        Args:
            videos: List of Video objects
            filters: FilterConfig instance

        Returns:
            list: Filtered list of Video objects
        """
        filtered = []

        for video in videos:
            if filters.matches_video(video):
                filtered.append(video)

        return filtered

    def get_video_info(self, video_url):
        """
        Get information about a specific video from its URL.

        Args:
            video_url: Twitch video URL (e.g., https://www.twitch.tv/videos/123456789)

        Returns:
            tuple: (success, video, error_message)
        """
        import re

        # Extract video ID from URL
        match = re.search(r'/videos/(\d+)', video_url)
        if not match:
            return False, None, "Invalid video URL format"

        video_id = match.group(1)

        # Fetch video data
        video_data = self.client.get_video_by_id(video_id)
        if not video_data:
            return False, None, "Video not found"

        try:
            video = Video.from_api_response(video_data)
            return True, video, ""
        except Exception as e:
            logger.error(f"Error parsing video data: {e}")
            return False, None, f"Error parsing video: {str(e)}"
