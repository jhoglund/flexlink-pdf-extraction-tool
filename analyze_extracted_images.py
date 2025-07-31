#!/usr/bin/env python3
"""
Analyze extracted images and show product associations
"""

import os
import re
from pathlib import Path


def analyze_extracted_images():
    """Analyze the extracted images and show what we know about them"""

    print("🔍 Analyzing Extracted Images")
    print("=" * 50)

    # Check if extracted_images directory exists
    images_dir = Path("extracted_images")
    if not images_dir.exists():
        print("❌ No extracted_images directory found")
        return

    # Get all image files
    image_files = list(images_dir.glob("*.png"))
    if not image_files:
        print("❌ No image files found in extracted_images directory")
        return

    print(f"📁 Found {len(image_files)} extracted images")
    print()

    # Analyze filename patterns
    print("📊 Filename Analysis:")
    page_numbers = set()
    for image_file in image_files:
        # Parse filename: image_004_000_52a9d822.png
        parts = image_file.stem.split('_')
        if len(parts) >= 3:
            page_number = int(parts[1])
            page_numbers.add(page_number)

    print(f"   Images span {len(page_numbers)} pages: {sorted(page_numbers)}")
    print()

    # Show what we know from the extraction process
    print("📋 Product Associations Detected During Extraction:")
    print("   (These were found in the surrounding text of images)")
    print()

    # Product codes found during extraction (from our earlier run)
    product_codes = [
        "X65", "161", "300", "100", "322", "1250", "2099", "200", "175", "230",
        "150", "125", "RS485", "180", "531", "D105", "XS", "480", "X45", "X180",
        "800", "V001", "102", "320", "240", "173", "2025", "104", "262", "3030",
        "D35", "160", "110", "H7", "X85"
    ]

    component_types = [
        "gear", "chain", "guide", "plate", "drive", "roller", "motor",
        "wheel", "sprocket", "support", "track", "link", "bracket"
    ]

    print(f"   ✅ {len(product_codes)} Product Codes Found:")
    for i, code in enumerate(product_codes, 1):
        print(f"      {i:2d}. {code}")

    print()
    print(f"   ✅ {len(component_types)} Component Types Found:")
    for i, component in enumerate(component_types, 1):
        print(f"      {i:2d}. {component}")

    print()
    print("⚠️  Current Limitation:")
    print("   The extracted images are saved with generic filenames")
    print("   The product associations were detected but not preserved in filenames")
    print("   This information is available in the database records")

    print()
    print("💡 To get better product associations:")
    print("   1. Upload images to database (they'll have product associations)")
    print("   2. Use the search functionality to find images by product code")
    print("   3. The web interface will show product associations")


def show_extraction_summary():
    """Show summary of what was extracted"""

    print("\n📊 Extraction Summary (from earlier run):")
    print("   Total images extracted: 508")
    print("   Blueprint images identified: 382")
    print("   Images saved locally: 370")
    print("   Product codes detected: 35")
    print("   Component types detected: 13")

    print()
    print("🎯 Key Product Codes Found:")
    print("   - X45, X65, XS (FlexLink system codes)")
    print("   - 161, 300, 100 (Part numbers)")
    print("   - RS485 (Communication protocol)")
    print("   - D35, D105 (Drive system codes)")

    print()
    print("🔧 Component Types Found:")
    print("   - chain, sprocket, gear (Transmission components)")
    print("   - motor, drive (Power components)")
    print("   - wheel, roller, guide (Support components)")
    print("   - plate, bracket, support (Structural components)")


def main():
    print("🔍 FlexLink Image Analysis")
    print("=" * 50)

    analyze_extracted_images()
    show_extraction_summary()

    print("\n📋 Next Steps:")
    print("1. Set up the database table (run database_setup.sql in Supabase)")
    print("2. Upload images to database (run upload_extracted_images.py)")
    print("3. Use search functionality to find images by product code")
    print("4. Browse images with product associations in web interface")


if __name__ == "__main__":
    main()
