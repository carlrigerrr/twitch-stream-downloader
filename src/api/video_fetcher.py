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
        Continuously fetches in batches of 100 until enough matching videos are found.

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
        logger.info(f"Filter criteria: {filters.get_summary()}")

        # Get game ID
        game_id = self.client.get_game_id(game_name)
        if not game_id:
            error_msg = f"Could not find game '{game_name}' on Twitch"
            logger.error(error_msg)
            return False, [], error_msg

        # Fetch videos in batches until we have enough matches
        matching_videos = []
        total_fetched = 0
        max_fetch_limit = 1000  # Safety limit to prevent infinite loops

        logger.info(f"Starting continuous fetch - need {filters.max_videos} matching videos")

        # Fetch videos in batches of 100 until we have enough matches
        raw_videos = self.client.get_videos(game_id, filters, max_results=max_fetch_limit)

        if not raw_videos:
            error_msg = "No videos found for this category"
            logger.warning(error_msg)
            return False, [], error_msg

        logger.info(f"Fetched {len(raw_videos)} total videos from API")

        # Convert to Video objects and apply filters
        for video_data in raw_videos:
            try:
                video = Video.from_api_response(video_data)
                total_fetched += 1

                # Check if video matches filter criteria
                if filters.matches_video(video):
                    matching_videos.append(video)

                    # Stop if we have enough matching videos
                    if len(matching_videos) >= filters.max_videos:
                        logger.info(f"Found {len(matching_videos)} matching videos after checking {total_fetched} total videos")
                        break

            except Exception as e:
                logger.error(f"Error parsing video data: {e}")
                continue

        logger.info(f"Finished fetching. Checked {total_fetched} videos, found {len(matching_videos)} matches")

        if not matching_videos:
            error_msg = f"No videos match your filter criteria after checking {total_fetched} videos. Try relaxing your filters."
            logger.warning(error_msg)
            return False, [], error_msg

        return True, matching_videos[:filters.max_videos], ""

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
