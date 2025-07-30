#!/usr/bin/env python3
"""
Master script for processing the main FlexLink catalog
This script orchestrates the entire workflow from database cleanup to final extraction.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Supabase credentials:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_ANON_KEY=your_supabase_anon_key")
        return False

    # Check if required files exist
    required_files = [
        'component_extractor.py',
        'extract_large_catalog.py',
        'clear_database.py'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return False

    print("✅ All prerequisites met!")
    return True


def get_catalog_file():
    """Get the catalog file path from user input"""
    print("\n📁 Catalog File Selection")
    print("=" * 30)

    # Look for PDF files in current directory
    pdf_files = list(Path('.').glob('*.pdf'))

    if pdf_files:
        print("Found PDF files in current directory:")
        for i, pdf_file in enumerate(pdf_files, 1):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"  {i}. {pdf_file.name} ({size_mb:.1f} MB)")

        while True:
            try:
                choice = input(
                    f"\nSelect a file (1-{len(pdf_files)}) or enter full path: ").strip()

                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(pdf_files):
                        return str(pdf_files[idx])
                    else:
                        print("❌ Invalid selection!")
                else:
                    # User entered a path
                    if os.path.exists(choice):
                        return choice
                    else:
                        print("❌ File not found!")
            except ValueError:
                print("❌ Invalid input!")
    else:
        # No PDF files found, ask for path
        while True:
            path = input(
                "Enter the path to your FlexLink catalog PDF: ").strip()
            if os.path.exists(path):
                return path
            else:
                print("❌ File not found!")


def confirm_workflow(catalog_file: str):
    """Confirm the workflow with the user"""
    file_size = os.path.getsize(catalog_file) / (1024 * 1024)  # MB

    print("\n🔄 Workflow Confirmation")
    print("=" * 30)
    print(f"Catalog file: {catalog_file}")
    print(f"File size: {file_size:.1f} MB")
    print("\nThis workflow will:")
    print("1. 🧹 Clear existing component data from database")
    print("2. 📖 Extract components from the large catalog")
    print("3. 🔄 Remove duplicates automatically")
    print("4. 📦 Process in batches for reliability")
    print("5. 💾 Save results to data/large_catalog_extraction/")
    print("6. 🗄️  Upload to Supabase database")

    response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    return response in ['yes', 'y']


def run_workflow(catalog_file: str, batch_size: int = 50):
    """Run the complete workflow"""
    print("\n🚀 Starting FlexLink Main Catalog Processing")
    print("=" * 50)

    start_time = time.time()

    try:
        # Step 1: Clear database
        print("\n🧹 Step 1: Clearing existing database...")
        from clear_database import clear_component_data
        if not clear_component_data():
            print("❌ Failed to clear database!")
            return False

        # Step 2: Extract from large catalog
        print("\n📖 Step 2: Extracting from large catalog...")
        from extract_large_catalog import LargeCatalogExtractor

        load_dotenv()
        extractor = LargeCatalogExtractor()

        results = extractor.extract_from_large_pdf(
            catalog_file,
            batch_size=batch_size,
            save_progress=True
        )

        if 'error' in results:
            print(f"❌ Extraction failed: {results['error']}")
            return False

        # Step 3: Summary
        total_time = time.time() - start_time
        print(f"\n🎉 Workflow completed successfully!")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📊 Components extracted: {results['total_components']}")
        print(f"🔄 Duplicates removed: {results.get('duplicates_removed', 0)}")
        print(f"🗄️  Uploaded to database: {results['components_uploaded']}")

        return True

    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process main FlexLink catalog")
    parser.add_argument("catalog_file", nargs='?',
                        help="Path to the FlexLink catalog PDF")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Batch size for processing (default: 50)")
    parser.add_argument("--no-confirm", action="store_true",
                        help="Skip confirmation prompts")

    args = parser.parse_args()

    print("🏭 FlexLink Main Catalog Processor")
    print("=" * 40)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Get catalog file
    if args.catalog_file:
        catalog_file = args.catalog_file
        if not os.path.exists(catalog_file):
            print(f"❌ Catalog file not found: {catalog_file}")
            sys.exit(1)
    else:
        catalog_file = get_catalog_file()

    # Confirm workflow (unless --no-confirm is used)
    if not args.no_confirm and not confirm_workflow(catalog_file):
        print("❌ Workflow cancelled.")
        sys.exit(0)

    # Use provided batch size or get from user
    batch_size = args.batch_size
    if not args.no_confirm:
        try:
            user_batch_size = input(
                f"\nEnter batch size (default {batch_size}): ") or str(batch_size)
            batch_size = int(user_batch_size)
        except ValueError:
            pass

    # Run workflow
    success = run_workflow(catalog_file, batch_size)

    if success:
        print("\n✅ Main catalog processing completed successfully!")
        print("📁 Check data/large_catalog_extraction/ for detailed results")
        print("🌐 Your web app should now show the updated component data")
    else:
        print("\n❌ Main catalog processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
