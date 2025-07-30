#!/usr/bin/env python3
"""
Resilient Database Upload Script for FlexLink Components
Handles intermittent internet connections with resume capability and progress tracking.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import our component extractor
from component_extractor import ComponentSpecificationExtractor, ComponentSpecification


class ResilientDatabaseUploader:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize the resilient uploader"""
        self.extractor = ComponentSpecificationExtractor(
            supabase_url, supabase_key)
        self.uploaded_components = 0
        self.failed_components = 0
        self.retry_count = 0
        self.max_retries = 3

    def upload_from_extraction(self, extraction_dir: str = "data/large_catalog_extraction",
                               batch_size: int = 20, resume: bool = True) -> Dict[str, Any]:
        """
        Upload components from extraction directory with resume capability

        Args:
            extraction_dir: Directory containing extraction results
            batch_size: Number of components to upload per batch
            resume: Whether to resume from previous upload
        """
        extraction_path = Path(extraction_dir)

        if not extraction_path.exists():
            print(f"❌ Extraction directory not found: {extraction_dir}")
            return {'error': 'Extraction directory not found'}

        # Check for all_components.json
        all_components_file = extraction_path / "all_components.json"
        if not all_components_file.exists():
            print(f"❌ No all_components.json found in {extraction_dir}")
            return {'error': 'No components file found'}

        print(f"📁 Loading components from: {all_components_file}")

        # Load components
        try:
            with open(all_components_file, 'r') as f:
                components_data = json.load(f)

            # Convert back to ComponentSpecification objects
            components = []
            for comp_data in components_data:
                component = ComponentSpecification(
                    system_code=comp_data['system_code'],
                    component_type=comp_data['component_type'],
                    component_name=comp_data['component_name'],
                    part_number=comp_data.get('part_number'),
                    specifications=comp_data.get('specifications', {}),
                    dimensions=comp_data.get('dimensions', {}),
                    materials=comp_data.get('materials', []),
                    compatibility=comp_data.get('compatibility', []),
                    weight_kg=comp_data.get('weight_kg'),
                    price_euro=comp_data.get('price_euro'),
                    description=comp_data.get('description', ''),
                    image_url=comp_data.get('image_url'),
                    page_reference=comp_data.get('page_reference')
                )
                components.append(component)

            print(f"✅ Loaded {len(components)} components")

        except Exception as e:
            print(f"❌ Error loading components: {e}")
            return {'error': str(e)}

        # Load progress if resuming
        progress_file = extraction_path / "upload_progress.json"
        uploaded_ids = set()

        if resume and progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                    uploaded_ids = set(progress_data.get('uploaded_ids', []))
                    self.uploaded_components = progress_data.get(
                        'uploaded_components', 0)
                    self.failed_components = progress_data.get(
                        'failed_components', 0)

                print(
                    f"🔄 Resuming upload: {self.uploaded_components} already uploaded")
            except Exception as e:
                print(f"⚠️  Could not load progress: {e}")

        # Filter out already uploaded components
        if uploaded_ids:
            original_count = len(components)
            components = [comp for comp in components if self._get_component_id(
                comp) not in uploaded_ids]
            print(
                f"🔄 Skipping {original_count - len(components)} already uploaded components")

        # Upload in batches
        return self._upload_batches(components, batch_size, extraction_path, progress_file, uploaded_ids)

    def _get_component_id(self, component: ComponentSpecification) -> str:
        """Generate a unique ID for a component"""
        return f"{component.part_number}_{component.system_code}" if component.part_number else f"{component.component_name}_{component.system_code}"

    def _upload_batches(self, components: List[ComponentSpecification],
                        batch_size: int, extraction_path: Path,
                        progress_file: Path, uploaded_ids: set) -> Dict[str, Any]:
        """Upload components in batches with retry logic"""
        total_components = len(components)
        batches = [components[i:i + batch_size]
                   for i in range(0, total_components, batch_size)]

        results = {
            'total_components': total_components,
            'total_batches': len(batches),
            'successful_batches': 0,
            'failed_batches': 0,
            'components_uploaded': 0,
            'components_failed': 0,
            'upload_time': 0
        }

        start_time = time.time()

        print(f"📦 Uploading {len(batches)} batches...")

        for i, batch in enumerate(batches, 1):
            print(
                f"🔄 Uploading batch {i}/{len(batches)} ({len(batch)} components)")

            success = False
            retries = 0

            while not success and retries < self.max_retries:
                try:
                    if self.extractor.supabase:
                        if self.extractor.upload_to_database(batch):
                            # Mark components as uploaded
                            for component in batch:
                                uploaded_ids.add(
                                    self._get_component_id(component))

                            results['components_uploaded'] += len(batch)
                            results['successful_batches'] += 1
                            self.uploaded_components += len(batch)

                            print(f"✅ Uploaded batch {i} successfully")
                            success = True
                        else:
                            raise Exception("Upload failed")
                    else:
                        print("⚠️  No database connection available")
                        success = True  # Skip if no connection

                except Exception as e:
                    retries += 1
                    print(
                        f"❌ Batch {i} failed (attempt {retries}/{self.max_retries}): {e}")

                    if retries < self.max_retries:
                        wait_time = 2 ** retries  # Exponential backoff
                        print(f"⏳ Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(
                            f"❌ Batch {i} failed after {self.max_retries} attempts")
                        results['failed_batches'] += 1
                        results['components_failed'] += len(batch)
                        self.failed_components += len(batch)

            # Save progress after each batch
            self._save_progress(progress_file, uploaded_ids, results)

        results['upload_time'] = time.time() - start_time
        return results

    def _save_progress(self, progress_file: Path, uploaded_ids: set, results: Dict[str, Any]):
        """Save upload progress"""
        progress_data = {
            'timestamp': time.time(),
            'uploaded_ids': list(uploaded_ids),
            'uploaded_components': self.uploaded_components,
            'failed_components': self.failed_components,
            'results': results
        }

        try:
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save progress: {e}")

    def check_connection(self) -> bool:
        """Check if database connection is available"""
        if not self.extractor.supabase:
            print("❌ No database connection available")
            print("Please check your .env file and Supabase credentials")
            return False

        try:
            # Try a simple query
            result = self.extractor.supabase.table(
                'component_specifications').select('id').limit(1).execute()
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload extracted components to database with resume capability")
    parser.add_argument("--extraction-dir", default="data/large_catalog_extraction",
                        help="Directory containing extraction results (default: data/large_catalog_extraction)")
    parser.add_argument("--batch-size", type=int, default=20,
                        help="Number of components to upload per batch (default: 20)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Don't resume from previous upload")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check database connection")

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Initialize uploader
    uploader = ResilientDatabaseUploader()

    # Check connection if requested
    if args.check_only:
        uploader.check_connection()
        return

    # Check connection
    if not uploader.check_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)

    # Upload components
    results = uploader.upload_from_extraction(
        extraction_dir=args.extraction_dir,
        batch_size=args.batch_size,
        resume=not args.no_resume
    )

    if 'error' in results:
        print(f"❌ Upload failed: {results['error']}")
        sys.exit(1)

    print(f"\n✅ Upload completed successfully!")
    print(f"📊 Components uploaded: {results['components_uploaded']}")
    print(f"❌ Components failed: {results['components_failed']}")
    print(f"⏱️  Upload time: {results['upload_time']:.2f} seconds")
    print(f"📁 Progress saved to: {args.extraction_dir}/upload_progress.json")


if __name__ == "__main__":
    main()
