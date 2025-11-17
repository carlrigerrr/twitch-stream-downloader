"""
Configuration manager for storing and retrieving application settings.
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from src.utils.logger import logger


class ConfigManager:
    """Manages application configuration and credentials."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "settings.json"

        # Load environment variables
        load_dotenv()

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

        # Load or create default settings
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from JSON file or create defaults."""
        default_settings = {
            "theme": "dark",
            "download_folder": str(Path("downloads").absolute()),
            "concurrent_downloads": 3,
            "default_quality": "best",
            "default_format": "mp4",
            "language": "en",
            "notifications": True,
            "retry_attempts": 3,
            "skip_duplicates": True,
            "create_subfolders": True,
            "save_metadata": True,
            "minimize_to_tray": False,
            "twitch_client_id": os.getenv("TWITCH_CLIENT_ID", ""),
            "twitch_client_secret": os.getenv("TWITCH_CLIENT_SECRET", ""),
            "last_category_url": "",
            "filter_presets": {}
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded_settings)
                    logger.info("Settings loaded successfully")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self):
        """Save current settings to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key, value, auto_save=True):
        """Set a setting value."""
        self.settings[key] = value
        if auto_save:
            self.save_settings()

    def update_many(self, updates):
        """
        Update multiple settings at once and save only once.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.settings.update(updates)
        self.save_settings()

    def get_twitch_credentials(self):
        """Get Twitch API credentials."""
        return {
            "client_id": self.settings.get("twitch_client_id", ""),
            "client_secret": self.settings.get("twitch_client_secret", "")
        }

    def set_twitch_credentials(self, client_id, client_secret):
        """Set Twitch API credentials."""
        self.settings["twitch_client_id"] = client_id
        self.settings["twitch_client_secret"] = client_secret
        self.save_settings()

    def save_filter_preset(self, name, filters):
        """Save a filter preset."""
        if "filter_presets" not in self.settings:
            self.settings["filter_presets"] = {}
        self.settings["filter_presets"][name] = filters
        self.save_settings()

    def get_filter_preset(self, name):
        """Get a filter preset."""
        return self.settings.get("filter_presets", {}).get(name)

    def get_all_presets(self):
        """Get all filter presets."""
        return self.settings.get("filter_presets", {})

    def delete_filter_preset(self, name):
        """Delete a filter preset."""
        if name in self.settings.get("filter_presets", {}):
            del self.settings["filter_presets"][name]
            self.save_settings()


# Global config instance
config = ConfigManager()
