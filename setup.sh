#!/bin/bash

echo "========================================"
echo "Twitch Video Downloader Setup"
echo "========================================"
echo ""

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Installing Streamlink..."
pip3 install streamlink

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Get Twitch API credentials from https://dev.twitch.tv/console"
echo "2. Run the application with: python3 main.py"
echo "3. Configure credentials in Settings"
echo ""
