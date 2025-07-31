#!/usr/bin/env python3
"""
Re-extract PDF and upload images with proper product associations
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add extractors to path
sys.path.append('extractors')


def re_extract_and_upload():
    """Re-extract PDF and upload with proper metadata"""

    print("🔄 Re-extracting PDF with product associations...")
    print("=" * 50)

    # Import the extractor
    try:
        from image_extractor import FlexLinkImageExtractor
        from upload_images_to_database import FlexLinkImageUploader
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print(
            "Make sure you're in the correct directory and have all dependencies installed.")
        return False

    # Initialize extractor and uploader
    extractor = FlexLinkImageExtractor()
    uploader = FlexLinkImageUploader()

    # Find PDF files
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        print("Please place your FlexLink catalog PDF in this directory.")
        return False

    pdf_file = pdf_files[0]  # Use the first PDF found
    print(f"📄 Found PDF: {pdf_file.name}")

    # Process the PDF
    print(f"\n🔍 Processing {pdf_file.name}...")
    try:
        result = extractor.process_pdf_images(str(pdf_file), save_local=False)

        print(f"\n📊 Extraction Results:")
        print(f"   Total images extracted: {result.get('total_images', 0)}")
        print(f"   Blueprint images: {result.get('blueprint_images', 0)}")
        print(f"   Product codes found: {result.get('product_codes', 0)}")
        print(f"   Component types found: {result.get('component_types', 0)}")

        # Upload to database
        if result.get('database_records'):
            print(
                f"\n📤 Uploading {len(result['database_records'])} images to database...")

            upload_result = uploader.upload_images_to_database(
                result['database_records'])

            print(f"\n📊 Upload Results:")
            print(
                f"   Successfully uploaded: {upload_result.get('success_count', 0)}")
            print(f"   Failed uploads: {upload_result.get('error_count', 0)}")

            if upload_result.get('success_count', 0) > 0:
                print("✅ Upload completed with proper metadata!")

                # Show some examples of the metadata
                print(f"\n📋 Sample metadata from uploaded images:")
                for i, record in enumerate(result['database_records'][:3]):
                    print(f"   Image {i+1}:")
                    print(f"     Page: {record.get('page_number')}")
                    print(
                        f"     Product Code: {record.get('product_code', 'Not specified')}")
                    print(
                        f"     Component Type: {record.get('component_type', 'Not specified')}")
                    print(
                        f"     Associated Text: {record.get('associated_text', '')[:100]}...")
                    print()

                return True
            else:
                print("❌ Upload failed!")
                return False
        else:
            print("❌ No images to upload!")
            return False

    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False


def clear_existing_images():
    """Clear existing images from database"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }

    try:
        # Delete all existing images
        response = requests.delete(
            f"{supabase_url}/rest/v1/product_images",
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Cleared existing images from database")
            return True
        else:
            print(f"❌ Failed to clear database: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


def main():
    print("🚀 FlexLink PDF Re-Extraction with Metadata")
    print("=" * 50)

    # Check if user wants to clear existing data
    print("\n⚠️  This will re-extract the PDF and upload images with proper metadata.")
    print("   This may take several minutes depending on the PDF size.")

    clear_choice = input(
        "\nDo you want to clear existing images first? (y/N): ").strip().lower()

    if clear_choice == 'y':
        print("\n🗑️  Clearing existing images...")
        if not clear_existing_images():
            print("❌ Failed to clear database. Aborting.")
            return

    # Re-extract and upload
    success = re_extract_and_upload()

    if success:
        print("\n🎉 Success! Your images now have proper product associations.")
        print("   You can now browse them in the web viewer with product codes and component types.")
    else:
        print("\n❌ Re-extraction failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
