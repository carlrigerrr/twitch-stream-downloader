"""
Settings window for configuring Twitch credentials and application settings.
"""
import customtkinter as ctk
from src.utils.config_manager import config
from src.utils.validators import validate_credentials
from src.api.video_fetcher import VideoFetcher
from src.utils.logger import logger
import threading


class SettingsWindow(ctk.CTkToplevel):
    """Settings window for the application."""

    def __init__(self, parent):
        """
        Initialize settings window.

        Args:
            parent: Parent window
        """
        super().__init__(parent)

        self.title("Settings")
        self.geometry("500x600")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Initialize variables
        self.client_id_var = ctk.StringVar(value=config.get("twitch_client_id", ""))
        self.client_secret_var = ctk.StringVar(value=config.get("twitch_client_secret", ""))
        self.concurrent_var = ctk.StringVar(value=str(config.get("concurrent_downloads", 3)))
        self.retry_var = ctk.StringVar(value=str(config.get("retry_attempts", 3)))
        self.skip_duplicates_var = ctk.BooleanVar(value=config.get("skip_duplicates", True))
        self.create_subfolders_var = ctk.BooleanVar(value=config.get("create_subfolders", True))
        self.save_metadata_var = ctk.BooleanVar(value=config.get("save_metadata", True))
        self.theme_var = ctk.StringVar(value=config.get("theme", "dark"))

        self.status_label = None
        self.test_button = None

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets for the settings window."""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Twitch API Credentials Section
        cred_frame = ctk.CTkFrame(main_frame)
        cred_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            cred_frame,
            text="Twitch API Credentials",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Client ID
        ctk.CTkLabel(cred_frame, text="Client ID:").pack(anchor="w", padx=10, pady=(5, 0))
        client_id_entry = ctk.CTkEntry(
            cred_frame,
            textvariable=self.client_id_var,
            width=400,
            show="*"
        )
        client_id_entry.pack(padx=10, pady=(0, 5))

        # Client Secret
        ctk.CTkLabel(cred_frame, text="Client Secret:").pack(anchor="w", padx=10, pady=(5, 0))
        client_secret_entry = ctk.CTkEntry(
            cred_frame,
            textvariable=self.client_secret_var,
            width=400,
            show="*"
        )
        client_secret_entry.pack(padx=10, pady=(0, 10))

        # Test credentials button
        self.test_button = ctk.CTkButton(
            cred_frame,
            text="Test Credentials",
            command=self._test_credentials,
            width=150
        )
        self.test_button.pack(pady=(0, 5))

        # Status label
        self.status_label = ctk.CTkLabel(
            cred_frame,
            text="",
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 10))

        # Download Settings Section
        download_frame = ctk.CTkFrame(main_frame)
        download_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            download_frame,
            text="Download Settings",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Concurrent downloads
        ctk.CTkLabel(
            download_frame,
            text="Concurrent Downloads:"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkOptionMenu(
            download_frame,
            values=["1", "2", "3", "4", "5"],
            variable=self.concurrent_var,
            width=200
        ).pack(anchor="w", padx=10, pady=(0, 5))

        # Retry attempts
        ctk.CTkLabel(
            download_frame,
            text="Retry Failed Downloads:"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkOptionMenu(
            download_frame,
            values=["0", "1", "2", "3", "5"],
            variable=self.retry_var,
            width=200
        ).pack(anchor="w", padx=10, pady=(0, 5))

        # Checkboxes
        ctk.CTkCheckBox(
            download_frame,
            text="Skip duplicate files",
            variable=self.skip_duplicates_var
        ).pack(anchor="w", padx=10, pady=5)

        ctk.CTkCheckBox(
            download_frame,
            text="Create category subfolders",
            variable=self.create_subfolders_var
        ).pack(anchor="w", padx=10, pady=5)

        ctk.CTkCheckBox(
            download_frame,
            text="Save metadata (JSON)",
            variable=self.save_metadata_var
        ).pack(anchor="w", padx=10, pady=(5, 10))

        # Application Settings Section
        app_frame = ctk.CTkFrame(main_frame)
        app_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            app_frame,
            text="Application",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Theme
        ctk.CTkLabel(app_frame, text="Theme:").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkOptionMenu(
            app_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            width=200,
            command=self._change_theme
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_settings,
            width=100
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left", padx=10)

    def _test_credentials(self):
        """Test Twitch API credentials."""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()

        # Validate format
        is_valid, error = validate_credentials(client_id, client_secret)
        if not is_valid:
            self._update_status(error, "red")
            return

        # Disable button during test
        self.test_button.configure(state="disabled")
        self._update_status("Testing credentials...", "gray")

        def test_thread():
            """Run test in background thread."""
            try:
                fetcher = VideoFetcher(client_id, client_secret)
                success, message = fetcher.test_connection()

                # Update UI in main thread
                self.after(0, lambda: self._test_complete(success, message))
            except Exception as e:
                self.after(0, lambda: self._test_complete(False, str(e)))

        threading.Thread(target=test_thread, daemon=True).start()

    def _test_complete(self, success, message):
        """Handle test completion."""
        self.test_button.configure(state="normal")

        if success:
            self._update_status(f"✓ {message}", "green")
        else:
            self._update_status(f"✗ {message}", "red")

    def _update_status(self, message, color):
        """Update status label."""
        if self.status_label:
            self.status_label.configure(text=message, text_color=color)

    def _change_theme(self, theme):
        """Change application theme."""
        ctk.set_appearance_mode(theme)

    def _save_settings(self):
        """Save settings to config."""
        try:
            # Save credentials
            config.set("twitch_client_id", self.client_id_var.get().strip())
            config.set("twitch_client_secret", self.client_secret_var.get().strip())

            # Save download settings
            config.set("concurrent_downloads", int(self.concurrent_var.get()))
            config.set("retry_attempts", int(self.retry_var.get()))
            config.set("skip_duplicates", self.skip_duplicates_var.get())
            config.set("create_subfolders", self.create_subfolders_var.get())
            config.set("save_metadata", self.save_metadata_var.get())

            # Save theme
            config.set("theme", self.theme_var.get())

            logger.info("Settings saved successfully")

            # Show success message
            self._update_status("✓ Settings saved successfully!", "green")

            # Close window after 1 second
            self.after(1000, self.destroy)

        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self._update_status(f"✗ Error: {str(e)}", "red")
