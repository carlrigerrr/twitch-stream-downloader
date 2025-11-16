"""
Test script to verify the application can start and check for issues.
"""
import sys
import os

print("Testing Twitch Video Downloader setup...")
print("=" * 50)

# Test 1: Check Python version
print(f"\n1. Python Version: {sys.version}")
if sys.version_info < (3, 8):
    print("   ❌ ERROR: Python 3.8 or higher required!")
else:
    print("   ✓ Python version OK")

# Test 2: Check imports
print("\n2. Checking dependencies...")
missing_deps = []

try:
    import customtkinter
    print("   ✓ customtkinter installed")
except ImportError:
    print("   ❌ customtkinter NOT installed")
    missing_deps.append("customtkinter")

try:
    import requests
    print("   ✓ requests installed")
except ImportError:
    print("   ❌ requests NOT installed")
    missing_deps.append("requests")

try:
    import PIL
    print("   ✓ Pillow installed")
except ImportError:
    print("   ❌ Pillow NOT installed")
    missing_deps.append("Pillow")

try:
    from dotenv import load_dotenv
    print("   ✓ python-dotenv installed")
except ImportError:
    print("   ❌ python-dotenv NOT installed")
    missing_deps.append("python-dotenv")

# Test 3: Check if streamlink is available
print("\n3. Checking streamlink...")
import subprocess
try:
    result = subprocess.run(
        ["streamlink", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"   ✓ streamlink installed: {result.stdout.strip()}")
    else:
        print("   ❌ streamlink command failed")
except FileNotFoundError:
    print("   ❌ streamlink NOT installed")
    print("   Install with: pip install streamlink")
except Exception as e:
    print(f"   ⚠ Could not check streamlink: {e}")

# Test 4: Check if src modules can be imported
print("\n4. Checking application modules...")
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.utils.logger import logger
    print("   ✓ Logger module OK")
except Exception as e:
    print(f"   ❌ Logger module error: {e}")

try:
    from src.utils.config_manager import config
    print("   ✓ Config manager OK")
except Exception as e:
    print(f"   ❌ Config manager error: {e}")

try:
    from src.gui.main_window import MainWindow
    print("   ✓ Main window module OK")
except Exception as e:
    print(f"   ❌ Main window error: {e}")

# Summary
print("\n" + "=" * 50)
if missing_deps:
    print("❌ MISSING DEPENDENCIES:")
    for dep in missing_deps:
        print(f"   - {dep}")
    print("\nInstall missing dependencies with:")
    print("   pip install -r requirements.txt")
else:
    print("✓ All dependencies installed!")
    print("\nYou can now run the application with:")
    print("   python main.py")

print("=" * 50)
