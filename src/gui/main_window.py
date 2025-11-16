"""
Main application window for Twitch Video Downloader.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path

from src.gui.settings_window import SettingsWindow
from src.api.video_fetcher import VideoFetcher
from src.models.filter_config import FilterConfig
from src.downloader.download_queue import DownloadQueue
from src.utils.config_manager import config
from src.utils.logger import logger
from src.utils.validators import validate_twitch_url


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()

        self.title("Twitch Video Downloader")
        self.geometry("950x800")
        self.minsize(900, 700)  # Minimum window size

        # Set theme
        theme = config.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        # Initialize variables
        self.videos = []
        self.selected_videos = {}
        self.download_queue = None
        self.video_fetcher = None

        # Create UI variables
        self.url_var = ctk.StringVar(value=config.get("last_category_url", ""))
        self.days_back_var = ctk.StringVar(value="7")
        self.max_videos_var = ctk.StringVar(value="10")
        self.language_var = ctk.StringVar(value="all")
        self.video_type_var = ctk.StringVar(value="all")
        self.min_duration_var = ctk.StringVar(value="")
        self.max_duration_var = ctk.StringVar(value="")
        self.min_views_var = ctk.StringVar(value="")
        self.max_views_var = ctk.StringVar(value="")
        self.quality_var = ctk.StringVar(value=config.get("default_quality", "best"))
        self.format_var = ctk.StringVar(value=config.get("default_format", "mp4"))
        self.output_folder_var = ctk.StringVar(value=config.get("download_folder", "downloads"))

        # Create widgets
        self._create_widgets()

        # Initialize download queue
        self._init_download_queue()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with Settings button
        self._create_header(main_frame)

        # Input section
        self._create_input_section(main_frame)

        # Filters section
        self._create_filters_section(main_frame)

        # Output settings section
        self._create_output_section(main_frame)

        # Action buttons
        self._create_action_buttons(main_frame)

        # Videos list
        self._create_videos_list(main_frame)

        # Progress section
        self._create_progress_section(main_frame)

        # Bottom buttons
        self._create_bottom_buttons(main_frame)

    def _create_header(self, parent):
        """Create header section with app title and settings button."""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Twitch Video Downloader",
            font=("Arial", 18, "bold")
        )
        title_label.pack(side="left", padx=10, pady=10)

        # Settings button (prominent in header)
        settings_button = ctk.CTkButton(
            header_frame,
            text="⚙ Settings",
            command=self._open_settings,
            width=120,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        settings_button.pack(side="right", padx=10, pady=10)

        # Credentials status indicator
        creds = config.get_twitch_credentials()
        if creds["client_id"] and creds["client_secret"]:
            status_text = "✓ Credentials configured"
            status_color = "green"
        else:
            status_text = "⚠ Configure credentials in Settings"
            status_color = "orange"

        self.creds_status_label = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=("Arial", 10),
            text_color=status_color
        )
        self.creds_status_label.pack(side="right", padx=10)

    def _create_input_section(self, parent):
        """Create URL input section."""
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            input_frame,
            text="Input",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        url_frame = ctk.CTkFrame(input_frame)
        url_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(url_frame, text="Category URL:", width=100).pack(side="left", padx=5)

        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="https://www.twitch.tv/directory/category/rust/videos/highlight",
            width=600
        )
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)

    def _create_filters_section(self, parent):
        """Create filters section."""
        filters_frame = ctk.CTkFrame(parent)
        filters_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            filters_frame,
            text="Filters",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Row 1: Days back, Max videos, Language, Type
        row1 = ctk.CTkFrame(filters_frame)
        row1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row1, text="Days Back:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkOptionMenu(
            row1,
            values=["1", "3", "7", "14", "30", "90", "365"],
            variable=self.days_back_var,
            width=80
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(row1, text="Max Videos:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        ctk.CTkOptionMenu(
            row1,
            values=["10", "25", "50", "100", "500"],
            variable=self.max_videos_var,
            width=80
        ).grid(row=0, column=3, padx=5, pady=5)

        # Row 2: Language and Video Type
        row2 = ctk.CTkFrame(filters_frame)
        row2.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row2, text="Language:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkOptionMenu(
            row2,
            values=["all", "en", "es", "de", "fr", "it", "ru", "pt", "ja", "ko"],
            variable=self.language_var,
            width=100
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(row2, text="Type:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        ctk.CTkOptionMenu(
            row2,
            values=["all", "archive", "highlight", "upload"],
            variable=self.video_type_var,
            width=100
        ).grid(row=0, column=3, padx=5, pady=5)

        # Row 3: Duration range
        row3 = ctk.CTkFrame(filters_frame)
        row3.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row3, text="Duration (min):").pack(side="left", padx=5)
        ctk.CTkEntry(
            row3,
            textvariable=self.min_duration_var,
            placeholder_text="Min",
            width=80
        ).pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="-").pack(side="left", padx=2)
        ctk.CTkEntry(
            row3,
            textvariable=self.max_duration_var,
            placeholder_text="Max",
            width=80
        ).pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="minutes").pack(side="left", padx=5)

        # Row 4: Views range
        row4 = ctk.CTkFrame(filters_frame)
        row4.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(row4, text="Views:").pack(side="left", padx=5)
        ctk.CTkEntry(
            row4,
            textvariable=self.min_views_var,
            placeholder_text="Min",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="-").pack(side="left", padx=2)
        ctk.CTkEntry(
            row4,
            textvariable=self.max_views_var,
            placeholder_text="Max",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="views").pack(side="left", padx=5)

    def _create_output_section(self, parent):
        """Create output settings section."""
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            output_frame,
            text="Output",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Folder selection
        folder_frame = ctk.CTkFrame(output_frame)
        folder_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(folder_frame, text="Folder:", width=60).pack(side="left", padx=5)
        ctk.CTkEntry(
            folder_frame,
            textvariable=self.output_folder_var,
            width=500
        ).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(
            folder_frame,
            text="Browse",
            command=self._browse_folder,
            width=80
        ).pack(side="left", padx=5)

        # Quality and format
        quality_frame = ctk.CTkFrame(output_frame)
        quality_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(quality_frame, text="Quality:").pack(side="left", padx=5)
        ctk.CTkOptionMenu(
            quality_frame,
            values=["best", "1080p60", "1080p", "720p60", "720p", "480p", "360p"],
            variable=self.quality_var,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkLabel(quality_frame, text="Format:").pack(side="left", padx=(20, 5))
        ctk.CTkOptionMenu(
            quality_frame,
            values=["mp4", "mkv"],
            variable=self.format_var,
            width=80
        ).pack(side="left", padx=5)

    def _create_action_buttons(self, parent):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=5, pady=5)

        self.fetch_button = ctk.CTkButton(
            button_frame,
            text="🔍 Fetch Videos",
            command=self._fetch_videos,
            width=150,
            height=35,
            font=("Arial", 12, "bold")
        )
        self.fetch_button.pack(side="left", padx=10, pady=10)

        self.download_button = ctk.CTkButton(
            button_frame,
            text="⬇ Download Selected",
            command=self._download_selected,
            width=150,
            height=35,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.download_button.pack(side="left", padx=10, pady=10)

        # Select/Deselect all
        ctk.CTkButton(
            button_frame,
            text="Select All",
            command=self._select_all,
            width=100
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Deselect All",
            command=self._deselect_all,
            width=100
        ).pack(side="left", padx=5, pady=10)

    def _create_videos_list(self, parent):
        """Create videos list section."""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.videos_label = ctk.CTkLabel(
            list_frame,
            text="Videos Found (0)",
            font=("Arial", 12, "bold")
        )
        self.videos_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Scrollable frame for videos
        self.videos_scroll = ctk.CTkScrollableFrame(list_frame, height=200)
        self.videos_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _create_progress_section(self, parent):
        """Create download progress section."""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            progress_frame,
            text="Download Progress",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            text_color="gray"
        )
        self.progress_label.pack(anchor="w", padx=10, pady=5)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=800)
        self.progress_bar.pack(padx=10, pady=5)
        self.progress_bar.set(0)

        self.progress_stats = ctk.CTkLabel(
            progress_frame,
            text="0/0 videos | 0% complete",
            text_color="gray"
        )
        self.progress_stats.pack(anchor="w", padx=10, pady=(0, 10))

    def _create_bottom_buttons(self, parent):
        """Create bottom control buttons."""
        bottom_frame = ctk.CTkFrame(parent)
        bottom_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            bottom_frame,
            text="⚙ Settings",
            command=self._open_settings,
            width=100
        ).pack(side="left", padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(
            bottom_frame,
            text="❌ Cancel Downloads",
            command=self._cancel_downloads,
            width=150,
            fg_color="red",
            state="disabled"
        )
        self.cancel_button.pack(side="right", padx=10, pady=10)

    def _browse_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(
            initialdir=self.output_folder_var.get(),
            title="Select Download Folder"
        )
        if folder:
            self.output_folder_var.set(folder)
            config.set("download_folder", folder)

    def _fetch_videos(self):
        """Fetch videos from Twitch."""
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a category URL")
            return

        # Validate URL
        is_valid, game_name, error = validate_twitch_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", error)
            return

        # Get credentials
        creds = config.get_twitch_credentials()
        if not creds["client_id"] or not creds["client_secret"]:
            messagebox.showerror(
                "Credentials Required",
                "Please configure your Twitch API credentials in Settings"
            )
            self._open_settings()
            return

        # Create filter config
        filter_config = self._get_filter_config()

        # Disable fetch button
        self.fetch_button.configure(state="disabled", text="Fetching...")

        # Fetch in background thread
        def fetch_thread():
            try:
                self.video_fetcher = VideoFetcher(creds["client_id"], creds["client_secret"])
                success, videos, error = self.video_fetcher.fetch_videos(url, filter_config)

                # Update UI in main thread
                self.after(0, lambda: self._fetch_complete(success, videos, error))
            except Exception as e:
                self.after(0, lambda: self._fetch_complete(False, [], str(e)))

        threading.Thread(target=fetch_thread, daemon=True).start()

        # Save URL to config
        config.set("last_category_url", url)

    def _fetch_complete(self, success, videos, error):
        """Handle fetch completion."""
        self.fetch_button.configure(state="normal", text="🔍 Fetch Videos")

        if not success:
            messagebox.showerror("Fetch Error", f"Failed to fetch videos:\n{error}")
            return

        if not videos:
            messagebox.showinfo("No Videos", "No videos found matching your filters")
            return

        # Store videos and display
        self.videos = videos
        self._display_videos()

        # Enable download button
        self.download_button.configure(state="normal")

    def _display_videos(self):
        """Display videos in the list."""
        # Clear existing videos
        for widget in self.videos_scroll.winfo_children():
            widget.destroy()

        self.selected_videos.clear()

        # Update label
        self.videos_label.configure(text=f"Videos Found ({len(self.videos)})")

        # Display each video
        for video in self.videos:
            self._create_video_item(video)

    def _create_video_item(self, video):
        """Create a video list item."""
        item_frame = ctk.CTkFrame(self.videos_scroll)
        item_frame.pack(fill="x", padx=5, pady=2)

        # Checkbox
        var = ctk.BooleanVar(value=True)
        self.selected_videos[video.id] = var

        checkbox = ctk.CTkCheckBox(item_frame, text="", variable=var, width=30)
        checkbox.pack(side="left", padx=5)

        # Video info
        info_text = f"{video.title}\n{video.duration_formatted} | {video.view_count_formatted} views | {video.user_name}"
        label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            anchor="w",
            justify="left"
        )
        label.pack(side="left", fill="x", expand=True, padx=5)

    def _select_all(self):
        """Select all videos."""
        for var in self.selected_videos.values():
            var.set(True)

    def _deselect_all(self):
        """Deselect all videos."""
        for var in self.selected_videos.values():
            var.set(False)

    def _download_selected(self):
        """Start downloading selected videos."""
        selected = [v for v in self.videos if self.selected_videos[v.id].get()]

        if not selected:
            messagebox.showwarning("No Selection", "Please select videos to download")
            return

        # Ensure output folder exists
        output_folder = self.output_folder_var.get()
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        # Clear previous queue
        if self.download_queue:
            self.download_queue.cancel_all()

        self._init_download_queue()

        # Add videos to queue
        quality = self.quality_var.get()
        format_type = self.format_var.get()

        for video in selected:
            self.download_queue.add_download(video, output_folder, quality, format_type)

        # Start downloads
        self.download_queue.start()

        # Update UI
        self.download_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self._update_progress()

        logger.info(f"Started downloading {len(selected)} videos")

    def _init_download_queue(self):
        """Initialize download queue."""
        max_concurrent = config.get("concurrent_downloads", 3)
        self.download_queue = DownloadQueue(max_concurrent=max_concurrent)

        # Add callbacks
        self.download_queue.add_progress_callback(self._on_download_progress)
        self.download_queue.add_completion_callback(self._on_download_complete)

    def _on_download_progress(self, task, progress, speed, eta):
        """Handle download progress update."""
        self.after(0, self._update_progress)

    def _on_download_complete(self, task, success):
        """Handle download completion."""
        self.after(0, self._update_progress)

        # Check if all downloads are complete
        if self.download_queue.is_empty():
            self.after(0, self._all_downloads_complete)

    def _update_progress(self):
        """Update progress display."""
        if not self.download_queue:
            return

        stats = self.download_queue.get_stats()
        progress = self.download_queue.get_progress()

        # Update progress bar
        self.progress_bar.set(progress / 100)

        # Update labels
        self.progress_label.configure(
            text=f"Downloading... ({stats['active']} active, {stats['pending']} pending)",
            text_color="green"
        )

        self.progress_stats.configure(
            text=f"{stats['completed']}/{stats['total']} videos | {progress:.1f}% complete | {stats['failed']} failed"
        )

    def _all_downloads_complete(self):
        """Handle all downloads completion."""
        stats = self.download_queue.get_stats()

        self.progress_label.configure(
            text=f"Downloads complete! {stats['completed']} succeeded, {stats['failed']} failed",
            text_color="blue"
        )

        self.download_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

        # Show completion message
        if stats['failed'] == 0:
            messagebox.showinfo("Success", f"All {stats['completed']} videos downloaded successfully!")
        else:
            messagebox.showwarning(
                "Completed with errors",
                f"{stats['completed']} videos downloaded\n{stats['failed']} videos failed"
            )

    def _cancel_downloads(self):
        """Cancel all downloads."""
        if self.download_queue:
            self.download_queue.cancel_all()
            self.progress_label.configure(text="Downloads cancelled", text_color="red")
            self.cancel_button.configure(state="disabled")
            self.download_button.configure(state="normal")

    def _get_filter_config(self):
        """Get filter configuration from UI."""
        # Parse duration values
        min_duration = None
        max_duration = None
        if self.min_duration_var.get():
            try:
                min_duration = int(self.min_duration_var.get())
            except ValueError:
                pass
        if self.max_duration_var.get():
            try:
                max_duration = int(self.max_duration_var.get())
            except ValueError:
                pass

        # Parse view values
        min_views = None
        max_views = None
        if self.min_views_var.get():
            try:
                min_views = int(self.min_views_var.get())
            except ValueError:
                pass
        if self.max_views_var.get():
            try:
                max_views = int(self.max_views_var.get())
            except ValueError:
                pass

        return FilterConfig(
            days_back=int(self.days_back_var.get()),
            max_videos=int(self.max_videos_var.get()),
            language=self.language_var.get(),
            video_type=self.video_type_var.get(),
            min_duration=min_duration,
            max_duration=max_duration,
            min_views=min_views,
            max_views=max_views
        )

    def _open_settings(self):
        """Open settings window."""
        settings_window = SettingsWindow(self)

        # Wait for settings window to close, then refresh credential status
        self.wait_window(settings_window)
        self._refresh_credential_status()

    def _refresh_credential_status(self):
        """Refresh the credential status indicator."""
        if hasattr(self, 'creds_status_label'):
            creds = config.get_twitch_credentials()
            if creds["client_id"] and creds["client_secret"]:
                status_text = "✓ Credentials configured"
                status_color = "green"
            else:
                status_text = "⚠ Configure credentials in Settings"
                status_color = "orange"

            self.creds_status_label.configure(text=status_text, text_color=status_color)
