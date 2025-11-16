"""
Twitch Video Downloader - Main Entry Point

A desktop application for downloading Twitch videos with advanced filtering options.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.utils.logger import logger


def main():
    """Main application entry point."""
    try:
        logger.info("Starting Twitch Video Downloader")

        # Create and run the application
        app = MainWindow()
        app.mainloop()

        logger.info("Application closed")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
