"""
Input validation utilities.
"""
import re
from urllib.parse import urlparse


def validate_twitch_url(url):
    """
    Validate Twitch category URL.

    Expected format:
    - https://www.twitch.tv/directory/category/{game_name}/videos/{type}
    - https://www.twitch.tv/directory/game/{game_name}

    Returns:
        tuple: (is_valid, game_name, error_message)
    """
    if not url:
        return False, None, "URL cannot be empty"

    try:
        parsed = urlparse(url)

        if parsed.netloc not in ['www.twitch.tv', 'twitch.tv']:
            return False, None, "URL must be from twitch.tv"

        path = parsed.path

        # Match pattern: /directory/category/{game_name}
        category_pattern = r'/directory/category/([^/]+)'
        # Match pattern: /directory/game/{game_name}
        game_pattern = r'/directory/game/([^/]+)'

        category_match = re.search(category_pattern, path)
        game_match = re.search(game_pattern, path)

        if category_match:
            game_name = category_match.group(1)
            # URL decode the game name
            game_name = game_name.replace('%20', ' ')
            return True, game_name, ""
        elif game_match:
            game_name = game_match.group(1)
            game_name = game_name.replace('%20', ' ')
            return True, game_name, ""
        else:
            return False, None, "Invalid URL format. Expected: https://www.twitch.tv/directory/category/{game_name}"

    except Exception as e:
        return False, None, f"Invalid URL: {str(e)}"


def validate_number_range(value, min_val=None, max_val=None, field_name="Value"):
    """
    Validate that a number is within a specific range.

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        num = int(value) if value else 0

        if min_val is not None and num < min_val:
            return False, f"{field_name} must be at least {min_val}"

        if max_val is not None and num > max_val:
            return False, f"{field_name} must not exceed {max_val}"

        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid number"


def validate_duration_range(min_duration, max_duration):
    """
    Validate duration range (minimum must be less than maximum).

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        min_val = int(min_duration) if min_duration else 0
        max_val = int(max_duration) if max_duration else float('inf')

        if min_val < 0:
            return False, "Minimum duration cannot be negative"

        if max_val < 0:
            return False, "Maximum duration cannot be negative"

        if min_val > max_val:
            return False, "Minimum duration cannot be greater than maximum duration"

        return True, ""
    except ValueError:
        return False, "Duration values must be valid numbers"


def validate_view_range(min_views, max_views):
    """
    Validate view count range.

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        min_val = int(min_views) if min_views else 0
        max_val = int(max_views) if max_views else float('inf')

        if min_val < 0:
            return False, "Minimum views cannot be negative"

        if max_val < 0:
            return False, "Maximum views cannot be negative"

        if min_val > max_val:
            return False, "Minimum views cannot be greater than maximum views"

        return True, ""
    except ValueError:
        return False, "View count values must be valid numbers"


def validate_credentials(client_id, client_secret):
    """
    Validate Twitch API credentials format.

    Returns:
        tuple: (is_valid, error_message)
    """
    if not client_id or not client_id.strip():
        return False, "Client ID cannot be empty"

    if not client_secret or not client_secret.strip():
        return False, "Client Secret cannot be empty"

    if len(client_id) < 10:
        return False, "Client ID appears to be invalid (too short)"

    if len(client_secret) < 10:
        return False, "Client Secret appears to be invalid (too short)"

    return True, ""


def sanitize_filename(filename):
    """
    Sanitize filename by removing invalid characters.

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for Windows/Linux filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')

    # Limit filename length
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized if sanitized else "video"
