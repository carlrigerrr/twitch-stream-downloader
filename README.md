# Twitch Video Downloader

A powerful desktop application for downloading Twitch videos with advanced filtering options. Built with Python and CustomTkinter for a modern, user-friendly interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- **Advanced Filtering**: Filter videos by date, language, type, duration, and view count
- **Batch Downloads**: Download multiple videos concurrently with queue management
- **Quality Selection**: Choose from multiple quality options (best, 1080p60, 720p, etc.)
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Metadata Saving**: Optionally save video metadata as JSON files
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Secure Credentials**: Safe storage of Twitch API credentials
- **Smart Filtering**: Client-side filtering for precise video selection

## Screenshots

```
┌─────────────────────────────────────────────────────────┐
│  Twitch Video Downloader                                │
├─────────────────────────────────────────────────────────┤
│ Category URL: https://www.twitch.tv/directory/...      │
│ Filters: Days Back, Max Videos, Language, Type         │
│ Duration & View Filters                                 │
│ Videos List with Checkboxes                            │
│ Download Progress Bar                                   │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- Streamlink (for video downloading)
- Twitch Developer Account (for API credentials)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/twitch-stream-downloader.git
cd twitch-stream-downloader
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Streamlink

**Windows:**
```bash
pip install streamlink
```

**macOS:**
```bash
brew install streamlink
# or
pip install streamlink
```

**Linux:**
```bash
sudo apt-get install streamlink
# or
pip install streamlink
```

### Step 4: Get Twitch API Credentials

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console)
2. Log in with your Twitch account
3. Click "Register Your Application"
4. Fill in the details:
   - **Name**: Your application name (e.g., "My Video Downloader")
   - **OAuth Redirect URLs**: `http://localhost`
   - **Category**: Application Integration
5. Click "Create"
6. Copy your **Client ID** and **Client Secret**

### Step 5: Configure Credentials

1. Run the application:
   ```bash
   python main.py
   ```
2. Click the "⚙ Settings" button
3. Enter your Twitch Client ID and Client Secret
4. Click "Test Credentials" to verify
5. Click "Save"

## Usage

### Quick Start

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Enter a Twitch category URL:**
   - Example: `https://www.twitch.tv/directory/category/rust/videos/highlight`
   - You can find these URLs by browsing Twitch categories

3. **Configure filters** (optional):
   - Days Back: How far back to search (1-365 days)
   - Max Videos: Maximum number of videos to fetch (10-500)
   - Language: Filter by language (en, es, de, etc.)
   - Type: Filter by video type (archive, highlight, upload)
   - Duration: Min/Max video length in minutes
   - Views: Min/Max view count

4. **Click "🔍 Fetch Videos"**
   - The app will fetch videos from Twitch
   - Videos matching your filters will appear in the list

5. **Select videos to download:**
   - Videos are selected by default
   - Use checkboxes to select/deselect
   - Use "Select All" / "Deselect All" buttons

6. **Configure output:**
   - Choose download folder
   - Select quality (best, 1080p, 720p, etc.)
   - Select format (mp4, mkv)

7. **Click "⬇ Download Selected"**
   - Downloads will start automatically
   - Progress is shown in real-time
   - Multiple videos download concurrently

### URL Format

The application accepts Twitch category URLs in these formats:

```
https://www.twitch.tv/directory/category/{game_name}
https://www.twitch.tv/directory/category/{game_name}/videos/highlight
https://www.twitch.tv/directory/game/{game_name}
```

Examples:
- `https://www.twitch.tv/directory/category/rust`
- `https://www.twitch.tv/directory/category/league-of-legends/videos/highlight`
- `https://www.twitch.tv/directory/game/valorant`

### Filter Examples

**Example 1: Recent Popular Videos**
- Days Back: 7
- Max Videos: 25
- Min Views: 10000
- Sort By: Views

**Example 2: Long-Form Content**
- Days Back: 30
- Min Duration: 60 minutes
- Max Duration: 180 minutes
- Type: archive

**Example 3: Highlights in Specific Language**
- Days Back: 14
- Language: en
- Type: highlight
- Min Duration: 5 minutes
- Max Duration: 30 minutes

## Settings

### Twitch API Credentials
- **Client ID**: Your Twitch application client ID
- **Client Secret**: Your Twitch application client secret
- **Test Button**: Verify credentials are working

### Download Settings
- **Concurrent Downloads**: Number of simultaneous downloads (1-5)
- **Retry Attempts**: How many times to retry failed downloads (0-5)
- **Skip Duplicates**: Avoid re-downloading existing files
- **Create Subfolders**: Organize downloads into category folders
- **Save Metadata**: Save video information as JSON files

### Application Settings
- **Theme**: Dark or Light mode
- **Notifications**: Enable/disable system notifications

## Troubleshooting

### "Streamlink not found" Error

**Solution**: Install streamlink using pip or your package manager:
```bash
pip install streamlink
```

### "Authentication failed" Error

**Causes**:
- Invalid Client ID or Client Secret
- Credentials not saved
- Network connectivity issues

**Solution**:
1. Verify credentials in Twitch Developer Console
2. Re-enter credentials in Settings
3. Click "Test Credentials" to verify
4. Check internet connection

### "No videos found" Error

**Causes**:
- Filters too restrictive
- Category has no recent videos
- Invalid category URL

**Solution**:
1. Loosen filter criteria (increase date range, remove view filters)
2. Try a different category
3. Verify URL format is correct

### Download Fails

**Causes**:
- Network interruption
- Invalid video URL
- Twitch video no longer available
- Disk space full

**Solution**:
1. Check internet connection
2. Ensure sufficient disk space
3. Try re-downloading
4. Check application logs in `logs/` folder

### Application Won't Start

**Solution**:
1. Verify Python version: `python --version` (should be 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check logs in `logs/` directory
4. Run with: `python main.py` to see error messages

## File Structure

```
twitch-stream-downloader/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for credentials
├── .gitignore                   # Git ignore rules
├── README.md                    # Documentation
├── config/
│   └── settings.json           # User settings (auto-generated)
├── src/
│   ├── gui/
│   │   ├── main_window.py      # Main application window
│   │   └── settings_window.py  # Settings dialog
│   ├── api/
│   │   ├── twitch_client.py    # Twitch API wrapper
│   │   └── video_fetcher.py    # Video fetching logic
│   ├── downloader/
│   │   ├── streamlink_manager.py  # Download management
│   │   └── download_queue.py      # Queue management
│   ├── models/
│   │   ├── video.py            # Video data model
│   │   └── filter_config.py    # Filter configuration
│   └── utils/
│       ├── config_manager.py   # Settings management
│       ├── logger.py           # Logging system
│       └── validators.py       # Input validation
├── downloads/                   # Default download folder
└── logs/                        # Application logs
```

## Configuration Files

### .env (Optional)
```
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_CLIENT_SECRET=your_client_secret_here
```

### config/settings.json (Auto-generated)
```json
{
    "theme": "dark",
    "download_folder": "downloads",
    "concurrent_downloads": 3,
    "default_quality": "best",
    "twitch_client_id": "...",
    "twitch_client_secret": "..."
}
```

## Development

### Running from Source

```bash
# Clone repository
git clone https://github.com/yourusername/twitch-stream-downloader.git
cd twitch-stream-downloader

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Project Dependencies

- **customtkinter**: Modern GUI framework
- **requests**: HTTP library for API calls
- **streamlink**: Video downloading
- **python-dotenv**: Environment variable management
- **Pillow**: Image processing

## API Rate Limits

Twitch API allows:
- **800 requests per minute** per client ID
- The application respects these limits automatically
- Large fetches (500+ videos) may take time

## Privacy & Security

- **Credentials**: Stored locally in `config/settings.json`
- **No Data Collection**: Application doesn't send data anywhere except Twitch API
- **Local Processing**: All filtering and processing happens on your computer
- **Secure Storage**: Credentials are stored in plain text locally (keep your computer secure)

## Frequently Asked Questions

**Q: Can I download subscriber-only content?**
A: No, the application only works with publicly available videos.

**Q: Does this work with live streams?**
A: No, it only works with VODs (videos on demand). Use streamlink directly for live streams.

**Q: Can I download videos from specific streamers?**
A: Currently, the app focuses on category-based downloads. You can filter results by streamer name manually.

**Q: What's the maximum video quality?**
A: The maximum quality depends on what's available on Twitch, typically up to 1080p60.

**Q: Will this get my Twitch account banned?**
A: No, the application uses official Twitch APIs and respects all rate limits.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Uses [Streamlink](https://streamlink.github.io/) for downloads
- Powered by [Twitch API](https://dev.twitch.tv/)

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in the `logs/` directory
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Log files (remove sensitive info)

## Roadmap

Future features planned:
- [ ] Download history tracking
- [ ] Scheduled downloads
- [ ] Filter preset saving
- [ ] Thumbnail previews
- [ ] Streamer-specific downloads
- [ ] Video preview before download
- [ ] Export download list

---

**Disclaimer**: This tool is for personal use only. Respect content creators' rights and Twitch's Terms of Service. Only download content you have permission to download.
