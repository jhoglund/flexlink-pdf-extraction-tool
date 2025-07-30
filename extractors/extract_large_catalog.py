#!/usr/bin/env python3
"""
Enhanced Component Extractor for Large FlexLink Catalogs
Optimized for processing 500+ page catalogs with progress tracking and duplicate prevention.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import our component extractor
from component_extractor import ComponentSpecificationExtractor, ComponentSpecification


class LargeCatalogExtractor:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize the large catalog extractor"""
        self.extractor = ComponentSpecificationExtractor(
            supabase_url, supabase_key)
        self.processed_components = 0
        self.duplicate_components = 0
        self.failed_components = 0

    def extract_from_large_pdf(self, pdf_path: str, batch_size: int = 50,
                               save_progress: bool = True) -> Dict[str, Any]:
        """
        Extract components from a large PDF with progress tracking

        Args:
            pdf_path: Path to the PDF file
            batch_size: Number of components to process before saving
            save_progress: Whether to save progress to intermediate files
        """
        print(f"📖 Processing large catalog: {pdf_path}")
        print(f"📊 Batch size: {batch_size} components")

        # Check file size
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"📁 File size: {file_size:.1f} MB")

        # Create output directory
        output_dir = Path("data/large_catalog_extraction")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract components
        start_time = time.time()

        try:
            # Extract all components
            all_components = self.extractor.extract_from_pdf(pdf_path)

            print(f"✅ Extracted {len(all_components)} components from PDF")

            # Remove duplicates based on part_number and system_code
            unique_components = self._remove_duplicates(all_components)
            print(
                f"🔄 Removed {len(all_components) - len(unique_components)} duplicates")

            # Process in batches
            results = self._process_batches(
                unique_components, batch_size, output_dir, save_progress)

            # Calculate statistics
            processing_time = time.time() - start_time
            results['processing_time'] = processing_time
            results['file_size_mb'] = file_size
            results['components_per_minute'] = len(
                unique_components) / (processing_time / 60)

            # Save final results
            self._save_final_results(unique_components, results, output_dir)

            return results

        except Exception as e:
            print(f"❌ Error processing large catalog: {e}")
            return {'error': str(e)}

    def _remove_duplicates(self, components: List[ComponentSpecification]) -> List[ComponentSpecification]:
        """Remove duplicate components based on part_number and system_code"""
        seen = set()
        unique_components = []

        for component in components:
            # Create a unique key based on part_number and system_code
            key = f"{component.part_number}_{component.system_code}" if component.part_number else f"{component.component_name}_{component.system_code}"

            if key not in seen:
                seen.add(key)
                unique_components.append(component)
            else:
                self.duplicate_components += 1

        return unique_components

    def _process_batches(self, components: List[ComponentSpecification],
                         batch_size: int, output_dir: Path,
                         save_progress: bool) -> Dict[str, Any]:
        """Process components in batches"""
        total_components = len(components)
        batches = [components[i:i + batch_size]
                   for i in range(0, total_components, batch_size)]

        results = {
            'total_components': total_components,
            'total_batches': len(batches),
            'successful_batches': 0,
            'failed_batches': 0,
            'components_saved': 0,
            'components_uploaded': 0
        }

        print(f"📦 Processing {len(batches)} batches...")

        for i, batch in enumerate(batches, 1):
            print(
                f"🔄 Processing batch {i}/{len(batches)} ({len(batch)} components)")

            try:
                # Save batch to JSON
                batch_file = output_dir / f"batch_{i:03d}.json"
                self.extractor.save_to_json(batch, str(batch_file))
                results['components_saved'] += len(batch)

                # Upload to database if available
                if self.extractor.supabase:
                    if self.extractor.upload_to_database(batch):
                        results['components_uploaded'] += len(batch)
                        print(f"✅ Uploaded batch {i} to database")
                    else:
                        print(f"⚠️  Failed to upload batch {i} to database")
                        results['failed_batches'] += 1

                results['successful_batches'] += 1

                # Save progress
                if save_progress:
                    self._save_progress(results, output_dir)

            except Exception as e:
                print(f"❌ Error processing batch {i}: {e}")
                results['failed_batches'] += 1
                self.failed_components += len(batch)

        return results

    def _save_progress(self, results: Dict[str, Any], output_dir: Path):
        """Save current progress to a file"""
        progress_file = output_dir / "extraction_progress.json"

        progress_data = {
            'timestamp': time.time(),
            'results': results,
            'processed_components': self.processed_components,
            'duplicate_components': self.duplicate_components,
            'failed_components': self.failed_components
        }

        import json
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)

    def _save_final_results(self, components: List[ComponentSpecification],
                            results: Dict[str, Any], output_dir: Path):
        """Save final results and summary"""
        # Save all components
        final_json = output_dir / "all_components.json"
        final_csv = output_dir / "all_components.csv"

        self.extractor.save_to_json(components, str(final_json))
        self.extractor.save_to_csv(components, str(final_csv))

        # Save summary
        summary_file = output_dir / "extraction_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("FlexLink Large Catalog Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(
                f"Total components extracted: {results['total_components']}\n")
            f.write(f"Duplicates removed: {self.duplicate_components}\n")
            f.write(f"Failed components: {self.failed_components}\n")
            f.write(
                f"Processing time: {results['processing_time']:.2f} seconds\n")
            f.write(
                f"Components per minute: {results['components_per_minute']:.1f}\n")
            f.write(f"File size: {results['file_size_mb']:.1f} MB\n")
            f.write(
                f"Components uploaded to database: {results['components_uploaded']}\n")
            f.write(f"Successful batches: {results['successful_batches']}\n")
            f.write(f"Failed batches: {results['failed_batches']}\n")

        print(f"\n📊 Extraction Summary:")
        print(f"   Total components: {results['total_components']}")
        print(f"   Duplicates removed: {self.duplicate_components}")
        print(f"   Processing time: {results['processing_time']:.2f} seconds")
        print(
            f"   Components per minute: {results['components_per_minute']:.1f}")
        print(f"   Uploaded to database: {results['components_uploaded']}")
        print(f"\n📁 Results saved to: {output_dir}")


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract components from large FlexLink catalogs")
    parser.add_argument("pdf_file", help="Path to the PDF catalog file")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Number of components to process per batch (default: 50)")
    parser.add_argument("--no-progress", action="store_true",
                        help="Don't save progress files")
    parser.add_argument("--clear-db", action="store_true",
                        help="Clear existing database before extraction")

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.pdf_file):
        print(f"❌ File not found: {args.pdf_file}")
        sys.exit(1)

    # Clear database if requested
    if args.clear_db:
        print("🧹 Clearing existing database...")
        try:
            from clear_database import clear_component_data
            if not clear_component_data():
                print("❌ Failed to clear database. Aborting.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            sys.exit(1)

    # Initialize extractor
    load_dotenv()
    extractor = LargeCatalogExtractor()

    # Extract components
    results = extractor.extract_from_large_pdf(
        args.pdf_file,
        batch_size=args.batch_size,
        save_progress=not args.no_progress
    )

    if 'error' in results:
        print(f"❌ Extraction failed: {results['error']}")
        sys.exit(1)

    print("\n✅ Large catalog extraction completed successfully!")


if __name__ == "__main__":
    main()
