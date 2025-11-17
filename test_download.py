"""
Diagnostic tool to test video downloads and streamlink setup.
"""
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.utils.logger import logger

print("=" * 60)
print("Twitch Video Downloader - Download Diagnostic Tool")
print("=" * 60)

# Test 1: Check if streamlink is installed
print("\n1. Checking Streamlink Installation...")
try:
    result = subprocess.run(
        ["streamlink", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"   ✓ Streamlink installed: {result.stdout.strip()}")
    else:
        print(f"   ❌ Streamlink command failed")
        print(f"   Error: {result.stderr}")
except FileNotFoundError:
    print("   ❌ Streamlink NOT installed")
    print("   Install with: pip install streamlink")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error checking streamlink: {e}")
    sys.exit(1)

# Test 2: Check streamlink plugins
print("\n2. Checking Streamlink Twitch Plugin...")
try:
    result = subprocess.run(
        ["streamlink", "--plugins"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if "twitch" in result.stdout.lower():
        print("   ✓ Twitch plugin available")
    else:
        print("   ⚠ Twitch plugin not found")
        print("   You may need to update streamlink")
except Exception as e:
    print(f"   ⚠ Could not check plugins: {e}")

# Test 3: Test with a public Twitch VOD
print("\n3. Testing Download with Sample Video...")
print("   This will test downloading a short public Twitch video")

# Use a test video URL (you can replace this with a valid public video)
test_url = input("\n   Enter a Twitch video URL to test (or press Enter to skip): ").strip()

if test_url:
    print(f"\n   Testing: {test_url}")
    print("   Listing available qualities...")

    try:
        # List available streams
        result = subprocess.run(
            ["streamlink", test_url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("   ✓ Available streams:")
            print(result.stdout)

            # Try downloading first 10 seconds
            print("\n   Attempting to download first 10 seconds...")
            test_output = "test_download.mp4"

            download_result = subprocess.run(
                ["streamlink", test_url, "best", "-o", test_output, "--force"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if download_result.returncode == 0 and os.path.exists(test_output):
                file_size = os.path.getsize(test_output)
                print(f"   ✓ Download successful! File size: {file_size / 1024 / 1024:.2f} MB")
                print(f"   ✓ Test file saved as: {test_output}")
                print("   You can delete this test file if you want.")
            else:
                print("   ❌ Download failed!")
                print(f"   Exit code: {download_result.returncode}")
                print(f"   Error output:\n{download_result.stderr}")
        else:
            print("   ❌ Could not list streams")
            print(f"   Error: {result.stderr}")

    except Exception as e:
        print(f"   ❌ Error during test: {e}")
else:
    print("   Skipped download test")

# Test 4: Check output folder permissions
print("\n4. Checking Output Folder Permissions...")
test_folder = "downloads"
try:
    os.makedirs(test_folder, exist_ok=True)
    test_file = os.path.join(test_folder, "test_write.txt")

    with open(test_file, 'w') as f:
        f.write("test")

    os.remove(test_file)
    print(f"   ✓ Can write to {test_folder}")
except Exception as e:
    print(f"   ❌ Cannot write to {test_folder}: {e}")

# Summary
print("\n" + "=" * 60)
print("Diagnostic Summary:")
print("=" * 60)
print("""
If all checks passed, your setup is ready!

If downloads still fail, check the logs for specific errors:
- Look in the logs/ folder for detailed error messages
- Run 'python main.py' and check the console output
- Try downloading with a simpler filter first (just 1-2 videos)

Common Issues:
1. Streamlink not installed → pip install streamlink
2. Twitch API credentials not configured → Open Settings in app
3. Videos are subscriber-only or deleted → Try different videos
4. Network issues → Check internet connection
5. Disk space full → Free up some space

For more help, check the logs in the logs/ folder.
""")
print("=" * 60)
