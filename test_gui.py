"""
Minimal GUI test to verify CustomTkinter is working and show the Settings button.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import customtkinter as ctk
    from src.gui.settings_window import SettingsWindow
    from src.utils.config_manager import config

    print("Creating test window...")

    # Set theme
    ctk.set_appearance_mode("dark")

    # Create simple test window
    root = ctk.CTk()
    root.title("Twitch Downloader - GUI Test")
    root.geometry("600x400")

    # Main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Title
    title = ctk.CTkLabel(
        main_frame,
        text="GUI Test - Verify Settings Button",
        font=("Arial", 16, "bold")
    )
    title.pack(pady=20)

    # Info
    info = ctk.CTkLabel(
        main_frame,
        text="If you can see this window, CustomTkinter is working!\n\nClick the Settings button below to configure Twitch credentials.",
        font=("Arial", 12)
    )
    info.pack(pady=20)

    # Settings button (prominently displayed)
    def open_settings():
        SettingsWindow(root)

    settings_btn = ctk.CTkButton(
        main_frame,
        text="⚙ Open Settings",
        command=open_settings,
        width=200,
        height=50,
        font=("Arial", 14, "bold")
    )
    settings_btn.pack(pady=30)

    # Instructions
    instructions = ctk.CTkLabel(
        main_frame,
        text="In the Settings window, you can:\n• Enter your Twitch Client ID and Client Secret\n• Test your credentials\n• Configure download preferences",
        font=("Arial", 11),
        justify="left"
    )
    instructions.pack(pady=20)

    # Run
    print("✓ Test window created successfully!")
    print("✓ If you don't see the window, check if it's behind other windows.")
    print("✓ Look for the '⚙ Open Settings' button in the window.")

    root.mainloop()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nPlease install dependencies first:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
