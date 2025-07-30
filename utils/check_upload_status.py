#!/usr/bin/env python3
"""
Upload Status Checker for FlexLink Components
Shows progress and status of component uploads.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


def check_upload_status(extraction_dir: str = "data/large_catalog_extraction"):
    """Check the status of component uploads"""
    extraction_path = Path(extraction_dir)

    print("📊 Upload Status Check")
    print("=" * 30)

    if not extraction_path.exists():
        print(f"❌ Extraction directory not found: {extraction_dir}")
        return

    # Check extraction summary
    summary_file = extraction_path / "extraction_summary.txt"
    if summary_file.exists():
        print("📋 Extraction Summary:")
        with open(summary_file, 'r') as f:
            print(f.read())
        print()

    # Check upload progress
    progress_file = extraction_path / "upload_progress.json"
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)

            print("📤 Upload Progress:")
            print(
                f"   Components uploaded: {progress_data.get('uploaded_components', 0)}")
            print(
                f"   Components failed: {progress_data.get('failed_components', 0)}")
            print(
                f"   Last update: {progress_data.get('timestamp', 'Unknown')}")

            # Calculate remaining
            all_components_file = extraction_path / "all_components.json"
            if all_components_file.exists():
                with open(all_components_file, 'r') as f:
                    all_components = json.load(f)

                total_components = len(all_components)
                uploaded = progress_data.get('uploaded_components', 0)
                remaining = total_components - uploaded

                print(f"   Total components: {total_components}")
                print(f"   Remaining: {remaining}")

                if remaining > 0:
                    percentage = (uploaded / total_components) * 100
                    print(f"   Progress: {percentage:.1f}%")
                else:
                    print("   ✅ Upload complete!")

        except Exception as e:
            print(f"⚠️  Could not read progress file: {e}")
    else:
        print("📤 Upload Progress: No upload started yet")

    # Check database connection
    print("\n🗄️  Database Connection:")
    load_dotenv()

    try:
        from component_extractor import ComponentSpecificationExtractor
        extractor = ComponentSpecificationExtractor()

        if extractor.supabase:
            try:
                result = extractor.supabase.table(
                    'component_specifications').select('id', count='exact').execute()
                db_count = result.count if hasattr(result, 'count') else 0
                print(f"   ✅ Connected to database")
                print(f"   📊 Components in database: {db_count}")
            except Exception as e:
                print(f"   ❌ Database connection failed: {e}")
        else:
            print("   ❌ No database connection available")
            print("   💡 Check your .env file and Supabase credentials")

    except Exception as e:
        print(f"   ❌ Error checking database: {e}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check upload status and progress")
    parser.add_argument("--extraction-dir", default="data/large_catalog_extraction",
                        help="Directory containing extraction results")

    args = parser.parse_args()

    check_upload_status(args.extraction_dir)


if __name__ == "__main__":
    main()
