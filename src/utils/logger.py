"""
Logging utility for the Twitch Video Downloader application.
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """Centralized logging system for the application."""

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

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create log filename with timestamp
        log_file = log_dir / f"twitch_downloader_{datetime.now().strftime('%Y%m%d')}.log"

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('TwitchDownloader')

    def info(self, message):
        """Log info message."""
        self.logger.info(message)

    def error(self, message):
        """Log error message."""
        self.logger.error(message)

    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)

    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)


# Global logger instance
logger = Logger()
