#!/usr/bin/env python3
"""
Test script for FlexLink Image Extraction System
"""

import os
import sys
from pathlib import Path

# Add extractors to path
sys.path.append('extractors')


def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from image_extractor import FlexLinkImageExtractor
        print("✅ Image extractor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import image extractor: {e}")
        return False

    try:
        from upload_images_to_database import FlexLinkImageUploader
        print("✅ Image uploader imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import image uploader: {e}")
        return False

    try:
        from extract_and_upload_images import FlexLinkImageProcessor
        print("✅ Image processor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import image processor: {e}")
        return False

    return True


def test_dependencies():
    """Test that required dependencies are available"""
    print("\n🔍 Testing dependencies...")

    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF available")
    except ImportError:
        print("❌ PyMuPDF not available - run: pip install PyMuPDF")
        return False

    try:
        import PIL
        print("✅ Pillow (PIL) available")
    except ImportError:
        print("❌ Pillow not available - run: pip install Pillow")
        return False

    try:
        import supabase
        print("✅ Supabase available")
    except ImportError:
        print("❌ Supabase not available - run: pip install supabase")
        return False

    try:
        import requests
        print("✅ Requests available")
    except ImportError:
        print("❌ Requests not available - run: pip install requests")
        return False

    return True


def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")

    # Check for .env file
    if not os.path.exists('.env'):
        print(
            "⚠️  No .env file found - you'll need to create one with Supabase credentials")
        return False

    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment")
        return False

    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY not found in environment")
        return False

    print("✅ Environment variables configured")
    return True


def test_image_extractor():
    """Test image extractor functionality"""
    print("\n🔍 Testing image extractor...")

    try:
        from image_extractor import FlexLinkImageExtractor

        extractor = FlexLinkImageExtractor()
        print("✅ Image extractor initialized successfully")

        # Test blueprint detection logic
        from PIL import Image
        import io

        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='white')
        test_text = "Technical drawing with dimensions 25.4mm"

        is_blueprint = extractor._is_blueprint_drawing(test_image, test_text)
        print(f"✅ Blueprint detection test: {is_blueprint}")

        return True

    except Exception as e:
        print(f"❌ Image extractor test failed: {e}")
        return False


def test_database_schema():
    """Test database schema file exists"""
    print("\n🔍 Testing database schema...")

    schema_file = Path("database/create_images_table.sql")
    if not schema_file.exists():
        print("❌ Database schema file not found: database/create_images_table.sql")
        return False

    print("✅ Database schema file exists")
    return True


def test_web_interface():
    """Test web interface file exists"""
    print("\n🔍 Testing web interface...")

    web_file = Path("web/image_viewer.html")
    if not web_file.exists():
        print("❌ Web interface file not found: web/image_viewer.html")
        return False

    print("✅ Web interface file exists")
    return True


def test_documentation():
    """Test documentation files exist"""
    print("\n🔍 Testing documentation...")

    docs_file = Path("docs/IMAGE_EXTRACTION_GUIDE.md")
    if not docs_file.exists():
        print("❌ Documentation file not found: docs/IMAGE_EXTRACTION_GUIDE.md")
        return False

    print("✅ Documentation file exists")
    return True


def main():
    """Run all tests"""
    print("🧪 FlexLink Image Extraction System Test")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Image Extractor", test_image_extractor),
        ("Database Schema", test_database_schema),
        ("Web Interface", test_web_interface),
        ("Documentation", test_documentation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! The image extraction system is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Set up your Supabase database")
        print("2. Run the database schema: database/create_images_table.sql")
        print("3. Test with a PDF: python extractors/extract_and_upload_images.py --pdf your_catalog.pdf")
        print("4. View images: open web/image_viewer.html in your browser")
    else:
        print("❌ Some tests failed. Please fix the issues above before using the system.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
