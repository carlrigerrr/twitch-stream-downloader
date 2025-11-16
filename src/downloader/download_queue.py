"""
Download queue manager for handling multiple concurrent downloads.
"""
import threading
from queue import Queue
from src.downloader.streamlink_manager import StreamlinkManager, DownloadTask, DownloadStatus
from src.utils.logger import logger


class DownloadQueue:
    """Manages a queue of download tasks with concurrent download support."""

    def __init__(self, max_concurrent=3):
        """
        Initialize download queue.

        Args:
            max_concurrent: Maximum number of concurrent downloads
        """
        self.max_concurrent = max_concurrent
        self.queue = Queue()
        self.completed_downloads = []
        self.failed_downloads = []
        self.active_count = 0
        self.total_count = 0
        self.lock = threading.Lock()
        self.streamlink_manager = StreamlinkManager()
        self.is_running = False
        self.worker_thread = None
        self.progress_callbacks = []
        self.completion_callbacks = []

    def add_download(self, video, output_folder, quality="best", format_type="mp4"):
        """
        Add a download to the queue.

        Args:
            video: Video object
            output_folder: Output folder path
            quality: Video quality
            format_type: Output format

        Returns:
            DownloadTask: The created download task
        """
        task = DownloadTask(video, output_folder, quality, format_type)
        self.queue.put(task)
        self.total_count += 1
        logger.info(f"Added to queue: {video.title} (Queue size: {self.queue.qsize()})")
        return task

    def add_progress_callback(self, callback):
        """
        Add a callback for progress updates.

        Callback signature: callback(task, progress, speed, eta)
        """
        self.progress_callbacks.append(callback)

    def add_completion_callback(self, callback):
        """
        Add a callback for download completion.

        Callback signature: callback(task, success)
        """
        self.completion_callbacks.append(callback)

    def start(self):
        """Start processing the download queue."""
        if self.is_running:
            logger.warning("Download queue already running")
            return

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logger.info("Download queue started")

    def stop(self):
        """Stop processing the download queue."""
        self.is_running = False
        logger.info("Download queue stopped")

    def clear(self):
        """Clear all pending downloads from the queue."""
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except:
                    break
            self.total_count = self.active_count
        logger.info("Download queue cleared")

    def cancel_all(self):
        """Cancel all active downloads and clear the queue."""
        # Cancel active downloads
        active_downloads = self.streamlink_manager.get_all_active_downloads()
        for task in active_downloads:
            self.streamlink_manager.cancel_download(task.video.id)

        # Clear queue
        self.clear()

        logger.info("All downloads cancelled")

    def _process_queue(self):
        """Process downloads from the queue (runs in worker thread)."""
        while self.is_running:
            try:
                # Check if we can start a new download
                with self.lock:
                    can_start = self.active_count < self.max_concurrent

                if can_start and not self.queue.empty():
                    # Get next task from queue
                    task = self.queue.get()

                    # Increment active count
                    with self.lock:
                        self.active_count += 1

                    # Start download
                    self._start_download(task)

                else:
                    # Wait a bit before checking again
                    threading.Event().wait(0.5)

            except Exception as e:
                logger.error(f"Error in queue processor: {e}")

    def _start_download(self, task):
        """Start a download task."""
        def progress_callback(progress, speed, eta):
            """Handle progress updates."""
            for callback in self.progress_callbacks:
                try:
                    callback(task, progress, speed, eta)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")

        def completion_callback(success, completed_task):
            """Handle download completion."""
            # Decrement active count
            with self.lock:
                self.active_count -= 1

            # Add to completed or failed list
            if success:
                self.completed_downloads.append(completed_task)
            else:
                self.failed_downloads.append(completed_task)

            # Mark queue task as done
            self.queue.task_done()

            # Call completion callbacks
            for callback in self.completion_callbacks:
                try:
                    callback(completed_task, success)
                except Exception as e:
                    logger.error(f"Error in completion callback: {e}")

        # Start download
        self.streamlink_manager.download_video(
            task,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )

    def get_stats(self):
        """
        Get queue statistics.

        Returns:
            dict: Statistics about the download queue
        """
        with self.lock:
            return {
                "total": self.total_count,
                "active": self.active_count,
                "pending": self.queue.qsize(),
                "completed": len(self.completed_downloads),
                "failed": len(self.failed_downloads)
            }

    def get_progress(self):
        """
        Get overall progress.

        Returns:
            float: Overall progress percentage (0-100)
        """
        if self.total_count == 0:
            return 0.0

        completed_count = len(self.completed_downloads) + len(self.failed_downloads)
        return (completed_count / self.total_count) * 100

    def is_empty(self):
        """Check if queue is empty and no active downloads."""
        with self.lock:
            return self.queue.empty() and self.active_count == 0

    def wait_until_complete(self):
        """Block until all downloads are complete."""
        self.queue.join()
