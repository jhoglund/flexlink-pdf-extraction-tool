#!/usr/bin/env python3
"""
Upload extracted images to Supabase database
"""

import os
import base64
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv


def upload_extracted_images():
    """Upload extracted images to Supabase database"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False

    # Check if extracted_images directory exists
    images_dir = Path("extracted_images")
    if not images_dir.exists():
        print("❌ No extracted_images directory found")
        print("Please run the image extraction first")
        return False

    # Get all image files
    image_files = list(images_dir.glob("*.png"))
    if not image_files:
        print("❌ No image files found in extracted_images directory")
        return False

    print(f"📁 Found {len(image_files)} images to upload")

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    success_count = 0
    error_count = 0

    for i, image_file in enumerate(image_files, 1):
        try:
            # Read image file
            with open(image_file, 'rb') as f:
                image_data = f.read()

            # Generate hash
            image_hash = hashlib.md5(image_data).hexdigest()

            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Parse filename to get metadata
            # Format: image_004_000_52a9d822.png
            filename_parts = image_file.stem.split('_')
            if len(filename_parts) >= 3:
                page_number = int(filename_parts[1])
                image_index = int(filename_parts[2])
            else:
                page_number = 1
                image_index = i

            # Prepare data for upload
            upload_data = {
                'image_hash': image_hash,
                'page_number': page_number,
                'x_coord': 0.0,  # Default values since we don't have coordinates
                'y_coord': 0.0,
                'width': 800.0,  # Default values
                'height': 600.0,
                'image_format': 'png',
                'image_data': image_base64,
                'associated_text': '',  # We don't have this from local files
                'product_code': '',  # We don't have this from local files
                'component_type': '',  # We don't have this from local files
                'is_blueprint': True,  # All extracted images are blueprints
                'image_quality_score': 0.8  # Default quality score
            }

            # Upload to Supabase
            response = requests.post(
                f"{supabase_url}/rest/v1/product_images",
                headers=headers,
                json=upload_data
            )

            if response.status_code in [200, 201]:
                print(f"✅ Uploaded {i}/{len(image_files)}: {image_file.name}")
                success_count += 1
            else:
                print(
                    f"❌ Failed to upload {image_file.name}: {response.status_code} - {response.text}")
                error_count += 1

        except Exception as e:
            print(f"❌ Error uploading {image_file.name}: {e}")
            error_count += 1

    print(f"\n📊 Upload Summary:")
    print(f"   Total images: {len(image_files)}")
    print(f"   Successfully uploaded: {success_count}")
    print(f"   Failed uploads: {error_count}")

    if success_count > 0:
        print("✅ Upload completed successfully!")
        return True
    else:
        print("❌ Upload failed!")
        return False


def test_database_connection():
    """Test if the database table exists and is accessible"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }

    try:
        # Test connection by trying to query the table
        response = requests.get(
            f"{supabase_url}/rest/v1/product_images?select=count",
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Database connection successful!")
            print("✅ product_images table exists and is accessible!")
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            print("Please make sure you've run the SQL setup commands in Supabase")
            return False

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def main():
    print("🚀 FlexLink Image Upload")
    print("=" * 40)

    # Step 1: Test database connection
    print("🔍 Testing database connection...")
    if not test_database_connection():
        print("\n📋 To set up the database:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of database_setup.sql")
        print("4. Execute the commands")
        print("5. Run this script again")
        return

    print("\n📤 Uploading extracted images...")

    # Step 2: Upload images
    if upload_extracted_images():
        print("\n🎉 Upload completed successfully!")
        print("You can now view your images in the Supabase dashboard or use the web interface.")
    else:
        print("\n❌ Upload failed!")


if __name__ == "__main__":
    main()
