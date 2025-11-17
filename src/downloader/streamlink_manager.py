"""
Streamlink manager for downloading Twitch videos.
"""
import subprocess
import os
import json
import threading
from pathlib import Path
from src.utils.logger import logger
from src.utils.validators import sanitize_filename


class DownloadStatus:
    """Download status enumeration."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class DownloadTask:
    """Represents a single download task."""

    def __init__(self, video, output_folder, quality="best", format_type="mp4"):
        """
        Initialize download task.

        Args:
            video: Video object
            output_folder: Output folder path
            quality: Video quality (best, 1080p60, 720p, etc.)
            format_type: Output format (mp4, mkv, etc.)
        """
        self.video = video
        self.output_folder = output_folder
        self.quality = quality
        self.format_type = format_type
        self.status = DownloadStatus.PENDING
        self.progress = 0.0
        self.speed = "0 KB/s"
        self.eta = "Unknown"
        self.error_message = ""
        self.output_file = ""
        self.process = None
        self.cancelled = False

        # Generate output filename
        self._generate_output_path()

    def _generate_output_path(self):
        """Generate output file path."""
        # Sanitize video title for filename
        safe_title = sanitize_filename(self.video.title)

        # Create filename with video ID to ensure uniqueness
        filename = f"{safe_title}_{self.video.id}.{self.format_type}"

        # Full output path
        self.output_file = os.path.join(self.output_folder, filename)

    def get_metadata_path(self):
        """Get path for metadata JSON file."""
        return self.output_file.replace(f".{self.format_type}", "_metadata.json")


class StreamlinkManager:
    """Manager for downloading videos using streamlink."""

    def __init__(self, max_retries=3):
        """
        Initialize streamlink manager.

        Args:
            max_retries: Maximum number of retry attempts for failed downloads
        """
        self.max_retries = max_retries
        self.active_downloads = {}
        self.download_lock = threading.Lock()

    def check_streamlink_installed(self):
        """
        Check if streamlink is installed.

        Returns:
            tuple: (is_installed, version_or_error)
        """
        try:
            result = subprocess.run(
                ["streamlink", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Streamlink found: {version}")
                return True, version
            else:
                return False, "Streamlink command failed"
        except FileNotFoundError:
            return False, "Streamlink not installed"
        except Exception as e:
            return False, str(e)

    def download_video(self, task, progress_callback=None, completion_callback=None):
        """
        Download a video using streamlink.

        Args:
            task: DownloadTask instance
            progress_callback: Function to call with progress updates (progress, speed, eta)
            completion_callback: Function to call when download completes (success, task)
        """
        def run_download():
            try:
                # Check if streamlink is installed
                is_installed, version_or_error = self.check_streamlink_installed()
                if not is_installed:
                    task.status = DownloadStatus.FAILED
                    task.error_message = f"Streamlink not installed: {version_or_error}"
                    logger.error(f"Cannot download - {task.error_message}")
                    logger.error("Install streamlink with: pip install streamlink")
                    if completion_callback:
                        completion_callback(False, task)
                    return

                # Ensure output directory exists
                Path(task.output_folder).mkdir(parents=True, exist_ok=True)

                # Check if file already exists
                if os.path.exists(task.output_file):
                    logger.warning(f"File already exists: {task.output_file}")
                    task.status = DownloadStatus.FAILED
                    task.error_message = "File already exists"
                    if completion_callback:
                        completion_callback(False, task)
                    return

                # Update status
                task.status = DownloadStatus.DOWNLOADING
                logger.info(f"Starting download: {task.video.title}")
                logger.info(f"Video URL: {task.video.url}")

                # Build streamlink command
                video_url = task.video.url

                # If quality is "best", let streamlink choose the best available
                # Otherwise, try the specified quality with fallback to best
                quality_arg = task.quality if task.quality else "best"

                command = [
                    "streamlink",
                    video_url,
                    quality_arg,
                    "-o", task.output_file,
                    "--force",  # Overwrite if exists
                    "--twitch-disable-ads"  # Disable ad check
                ]

                # Start streamlink process
                logger.info(f"Streamlink command: {' '.join(command)}")

                task.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                # Collect stderr output for error reporting
                stderr_output = []

                # Monitor output for progress
                for line in task.process.stderr:
                    stderr_output.append(line.strip())

                    if task.cancelled:
                        task.process.terminate()
                        task.status = DownloadStatus.CANCELLED
                        logger.info(f"Download cancelled: {task.video.title}")
                        if completion_callback:
                            completion_callback(False, task)
                        return

                    # Log streamlink output for debugging
                    logger.debug(f"Streamlink: {line.strip()}")

                    # Parse progress from streamlink output
                    # Example: "Written 123.45 MB (12%) [1.23 MB/s]"
                    self._parse_progress(line, task, progress_callback)

                # Wait for process to complete
                task.process.wait()

                # Check if download was successful
                if task.process.returncode == 0 and os.path.exists(task.output_file):
                    task.status = DownloadStatus.COMPLETED
                    task.progress = 100.0
                    logger.info(f"Download completed: {task.video.title}")

                    # Save metadata if configured
                    self._save_metadata(task)

                    if progress_callback:
                        progress_callback(100.0, "Complete", "0s")

                    if completion_callback:
                        completion_callback(True, task)
                else:
                    # Capture detailed error information
                    task.status = DownloadStatus.FAILED
                    error_details = '\n'.join(stderr_output[-10:])  # Last 10 lines of stderr
                    task.error_message = f"Streamlink failed (exit code {task.process.returncode})"

                    logger.error(f"Download failed: {task.video.title}")
                    logger.error(f"Exit code: {task.process.returncode}")
                    logger.error(f"Streamlink output:\n{error_details}")

                    if completion_callback:
                        completion_callback(False, task)

            except Exception as e:
                task.status = DownloadStatus.FAILED
                task.error_message = str(e)
                logger.error(f"Download error for {task.video.title}: {e}")

                if completion_callback:
                    completion_callback(False, task)

            finally:
                # Clean up
                with self.download_lock:
                    if task.video.id in self.active_downloads:
                        del self.active_downloads[task.video.id]

        # Start download in separate thread
        with self.download_lock:
            self.active_downloads[task.video.id] = task

        download_thread = threading.Thread(target=run_download, daemon=True)
        download_thread.start()

        return task

    def _parse_progress(self, line, task, progress_callback):
        """Parse progress information from streamlink output."""
        import re

        # Try to extract progress percentage
        # Streamlink doesn't always provide progress, so this is best-effort
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
        if percent_match:
            task.progress = float(percent_match.group(1))

        # Try to extract speed
        speed_match = re.search(r'\[([^\]]+/s)\]', line)
        if speed_match:
            task.speed = speed_match.group(1)

        # Call progress callback if provided
        if progress_callback and task.progress > 0:
            progress_callback(task.progress, task.speed, task.eta)

    def _save_metadata(self, task):
        """Save video metadata to JSON file."""
        try:
            metadata_path = task.get_metadata_path()
            metadata = task.video.to_dict()
            metadata["download_info"] = {
                "quality": task.quality,
                "format": task.format_type,
                "output_file": task.output_file
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)

            logger.info(f"Metadata saved: {metadata_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def cancel_download(self, video_id):
        """
        Cancel an active download.

        Args:
            video_id: Video ID of the download to cancel

        Returns:
            bool: True if cancelled, False if not found
        """
        with self.download_lock:
            if video_id in self.active_downloads:
                task = self.active_downloads[video_id]
                task.cancelled = True

                if task.process and task.process.poll() is None:
                    task.process.terminate()

                logger.info(f"Download cancelled: {task.video.title}")
                return True

        return False

    def get_active_download(self, video_id):
        """
        Get active download task by video ID.

        Args:
            video_id: Video ID

        Returns:
            DownloadTask or None
        """
        with self.download_lock:
            return self.active_downloads.get(video_id)

    def get_all_active_downloads(self):
        """
        Get all active downloads.

        Returns:
            list: List of DownloadTask objects
        """
        with self.download_lock:
            return list(self.active_downloads.values())
