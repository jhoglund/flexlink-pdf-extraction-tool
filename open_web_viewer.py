#!/usr/bin/env python3
"""
Open the FlexLink Image Viewer in your browser
"""

import webbrowser
import os
from pathlib import Path


def open_web_viewer():
    """Open the web viewer in the default browser"""

    # Get the absolute path to the HTML file
    html_file = Path(__file__).parent / "web" / "image_viewer.html"

    if not html_file.exists():
        print("❌ Web viewer file not found!")
        print(f"Expected location: {html_file}")
        return False

    # Convert to file URL
    file_url = f"file://{html_file.absolute()}"

    print("🌐 Opening FlexLink Image Viewer...")
    print(f"📁 File: {html_file}")
    print(f"🔗 URL: {file_url}")
    print()
    print("📋 Instructions:")
    print("1. The web interface will open in your browser")
    print("2. Search for images by product code (e.g., X45, X65)")
    print("3. Filter by component type (e.g., chain, motor)")
    print("4. Click on images to see detailed information")
    print("5. Use 'Show Stats' to see database statistics")
    print()
    print("⚠️  Note: Make sure you've uploaded images to the database first!")
    print("   Run: python3 upload_extracted_images.py")

    # Open in browser
    webbrowser.open(file_url)

    return True


def main():
    print("🚀 FlexLink Web Viewer")
    print("=" * 40)

    if open_web_viewer():
        print("✅ Web viewer opened successfully!")
    else:
        print("❌ Failed to open web viewer")


if __name__ == "__main__":
    main()
