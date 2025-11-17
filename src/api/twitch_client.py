"""
Twitch API client for authentication and API calls.
"""
import requests
import time
from datetime import datetime, timedelta, timezone
from src.utils.logger import logger


class TwitchClient:
    """Client for interacting with Twitch API."""

    def __init__(self, client_id, client_secret):
        """
        Initialize Twitch API client.

        Args:
            client_id: Twitch application client ID
            client_secret: Twitch application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://api.twitch.tv/helix"

    def authenticate(self):
        """
        Authenticate with Twitch API using Client Credentials flow.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }

            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)

            # Set expiration time (with 5 minute buffer)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            logger.info("Twitch API authentication successful")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch API authentication failed: {e}")
            return False

    def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            return self.authenticate()
        return True

    def _get_headers(self):
        """Get headers for API requests."""
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

    def test_credentials(self):
        """
        Test if credentials are valid.

        Returns:
            tuple: (success, message)
        """
        try:
            if not self.authenticate():
                return False, "Authentication failed. Check your credentials."

            # Test with a simple API call
            url = f"{self.base_url}/games/top"
            params = {"first": 1}

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()

            return True, "Credentials are valid!"

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False, "Invalid credentials"
            return False, f"API error: {e.response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_game_id(self, game_name):
        """
        Get game ID from game name.

        Args:
            game_name: Name of the game/category

        Returns:
            str: Game ID or None if not found
        """
        if not self._ensure_authenticated():
            logger.error("Authentication required")
            return None

        try:
            url = f"{self.base_url}/games"
            params = {"name": game_name}

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            games = data.get("data", [])

            if games:
                game_id = games[0].get("id")
                logger.info(f"Found game '{game_name}' with ID: {game_id}")
                return game_id
            else:
                logger.warning(f"Game '{game_name}' not found")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching game ID: {e}")
            return None

    def get_videos(self, game_id, filters, max_results=100):
        """
        Get videos for a specific game.

        Args:
            game_id: Twitch game ID
            filters: FilterConfig instance with filter criteria
            max_results: Maximum number of results to fetch

        Returns:
            list: List of video data dictionaries
        """
        if not self._ensure_authenticated():
            logger.error("Authentication required")
            return []

        try:
            url = f"{self.base_url}/videos"
            all_videos = []
            cursor = None

            # Calculate the date range (use timezone-aware datetime to match Twitch API)
            start_date = datetime.now(timezone.utc) - timedelta(days=filters.days_back)

            # Determine sort parameter
            sort_map = {
                "time": "time",
                "trending": "trending",
                "views": "views"
            }
            sort = sort_map.get(filters.sort_by, "time")

            # Determine type parameter
            type_param = None if filters.video_type == "all" else filters.video_type

            while len(all_videos) < max_results:
                params = {
                    "game_id": game_id,
                    "first": min(100, max_results - len(all_videos)),  # Max 100 per request
                    "sort": sort
                }

                if type_param:
                    params["type"] = type_param

                if cursor:
                    params["after"] = cursor

                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                videos = data.get("data", [])

                if not videos:
                    break

                # Filter videos by date
                for video in videos:
                    created_at = datetime.fromisoformat(video["created_at"].replace('Z', '+00:00'))

                    if created_at < start_date:
                        # Videos are sorted by time, so we can stop here
                        logger.info(f"Reached videos older than {filters.days_back} days")
                        return all_videos

                    all_videos.append(video)

                    if len(all_videos) >= max_results:
                        break

                # Check if there's a next page
                pagination = data.get("pagination", {})
                cursor = pagination.get("cursor")

                if not cursor:
                    break

                # Rate limiting: Twitch allows 800 requests per minute
                time.sleep(0.1)

            logger.info(f"Fetched {len(all_videos)} videos")
            return all_videos

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching videos: {e}")
            return []

    def get_video_by_id(self, video_id):
        """
        Get video information by video ID.

        Args:
            video_id: Twitch video ID

        Returns:
            dict: Video data or None if not found
        """
        if not self._ensure_authenticated():
            logger.error("Authentication required")
            return None

        try:
            url = f"{self.base_url}/videos"
            params = {"id": video_id}

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            videos = data.get("data", [])

            return videos[0] if videos else None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching video: {e}")
            return None
