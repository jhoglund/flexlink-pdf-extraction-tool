#!/usr/bin/env python3
"""
FlexLink Image Extraction and Upload Tool
Extracts blueprint drawings from PDF catalog and uploads to database
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
from image_extractor import FlexLinkImageExtractor
from upload_images_to_database import FlexLinkImageUploader


class FlexLinkImageProcessor:
    def __init__(self):
        """Initialize the image processor"""
        self.extractor = FlexLinkImageExtractor()
        self.uploader = FlexLinkImageUploader()

    def process_pdf_and_upload(self, pdf_path: str, save_local: bool = True,
                               output_dir: str = "extracted_images") -> Dict[str, Any]:
        """Process PDF and upload images to database"""
        print(f"🔄 Starting complete image processing pipeline")
        print(f"📄 PDF: {pdf_path}")
        print(f"💾 Save locally: {save_local}")
        print(f"📁 Output directory: {output_dir}")

        # Step 1: Extract images from PDF
        print("\n📋 Step 1: Extracting images from PDF...")
        extraction_result = self.extractor.process_pdf_images(
            pdf_path,
            save_local=save_local,
            output_dir=output_dir
        )

        if not extraction_result or not extraction_result.get('blueprint_images'):
            print("❌ No blueprint images found in PDF")
            return {
                'success': False,
                'message': 'No blueprint images extracted',
                'extraction': extraction_result
            }

        # Step 2: Upload images to database
        print(
            f"\n📋 Step 2: Uploading {len(extraction_result['database_records'])} images to database...")
        upload_result = self.uploader.upload_images_to_database(
            extraction_result['database_records'])

        # Step 3: Get final statistics
        print("\n📋 Step 3: Getting final statistics...")
        final_stats = self.uploader.get_image_statistics()

        # Combine all results
        result = {
            'success': upload_result['success'],
            'extraction': extraction_result,
            'upload': upload_result,
            'final_stats': final_stats,
            'summary': {
                'total_images_extracted': extraction_result.get('total_images', 0),
                'blueprint_images_extracted': extraction_result.get('blueprint_images', 0),
                'images_uploaded': upload_result.get('success_count', 0),
                'upload_errors': upload_result.get('error_count', 0),
                'product_codes_found': extraction_result.get('product_codes_found', []),
                'component_types_found': extraction_result.get('component_types_found', [])
            }
        }

        # Print summary
        self._print_summary(result)

        return result

    def _print_summary(self, result: Dict[str, Any]):
        """Print a comprehensive summary of the processing results"""
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)

        summary = result['summary']

        print(f"📄 PDF Processing:")
        print(f"   Total images found: {summary['total_images_extracted']}")
        print(
            f"   Blueprint images identified: {summary['blueprint_images_extracted']}")

        print(f"\n💾 Database Upload:")
        print(f"   Images uploaded successfully: {summary['images_uploaded']}")
        print(f"   Upload errors: {summary['upload_errors']}")

        if summary['product_codes_found']:
            print(f"\n📋 Product Codes Found:")
            for code in summary['product_codes_found']:
                print(f"   - {code}")

        if summary['component_types_found']:
            print(f"\n🔧 Component Types Found:")
            for comp_type in summary['component_types_found']:
                print(f"   - {comp_type}")

        # Show final database statistics
        if 'final_stats' in result and 'error' not in result['final_stats']:
            stats = result['final_stats']
            print(f"\n📊 Database Statistics:")
            print(
                f"   Total images in database: {stats.get('total_images', 0)}")
            print(
                f"   Blueprint images in database: {stats.get('blueprint_images', 0)}")
            print(
                f"   Products with images: {stats.get('products_with_images', 0)}")
            print(
                f"   Average image size: {stats.get('avg_image_size_kb', 0):.2f} KB")
            print(
                f"   Average quality score: {stats.get('avg_quality_score', 0):.2f}")

        print("="*60)

        if result['success']:
            print("✅ Processing completed successfully!")
        else:
            print("❌ Processing completed with errors")

    def batch_process_pdfs(self, pdf_directory: str, save_local: bool = True) -> Dict[str, Any]:
        """Process multiple PDF files in a directory"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            print(f"❌ Directory not found: {pdf_directory}")
            return {'success': False, 'message': 'Directory not found'}

        # Find all PDF files
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in: {pdf_directory}")
            return {'success': False, 'message': 'No PDF files found'}

        print(f"📁 Found {len(pdf_files)} PDF files to process")

        results = []
        total_success = 0
        total_errors = 0

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n🔄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")

            try:
                result = self.process_pdf_and_upload(
                    str(pdf_file),
                    save_local=save_local,
                    output_dir=f"extracted_images/{pdf_file.stem}"
                )

                results.append({
                    'file': pdf_file.name,
                    'result': result
                })

                if result['success']:
                    total_success += 1
                else:
                    total_errors += 1

            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")
                total_errors += 1
                results.append({
                    'file': pdf_file.name,
                    'error': str(e)
                })

        # Create batch summary
        batch_summary = {
            'success': total_errors == 0,
            'total_files': len(pdf_files),
            'successful_files': total_success,
            'failed_files': total_errors,
            'results': results
        }

        print(f"\n📊 Batch Processing Summary:")
        print(f"   Total files: {batch_summary['total_files']}")
        print(f"   Successful: {batch_summary['successful_files']}")
        print(f"   Failed: {batch_summary['failed_files']}")

        return batch_summary

    def search_and_display_images(self, product_code: str = None,
                                  component_type: str = None,
                                  is_blueprint: bool = None):
        """Search for images and display results"""
        print("🔍 Searching for images in database...")

        images = self.uploader.search_images(
            product_code, component_type, is_blueprint)

        if not images:
            print("❌ No images found matching criteria")
            return

        print(f"📋 Found {len(images)} images:")
        print("-" * 80)
        print(
            f"{'Product Code':<15} {'Component':<12} {'Page':<6} {'Blueprint':<10} {'Quality':<8}")
        print("-" * 80)

        for img in images:
            product = img.get('product_code', 'Unknown')
            component = img.get('component_type', 'Unknown')
            page = img.get('page_number', 0)
            blueprint = "Yes" if img.get('is_blueprint') else "No"
            quality = f"{img.get('image_quality_score', 0):.2f}"

            print(
                f"{product:<15} {component:<12} {page:<6} {blueprint:<10} {quality:<8}")

    def get_database_statistics(self):
        """Display comprehensive database statistics"""
        print("📊 Getting database statistics...")

        stats = self.uploader.get_image_statistics()

        if 'error' in stats:
            print(f"❌ Error getting statistics: {stats['error']}")
            return

        print("\n" + "="*50)
        print("📊 DATABASE STATISTICS")
        print("="*50)
        print(f"Total images: {stats.get('total_images', 0)}")
        print(f"Blueprint images: {stats.get('blueprint_images', 0)}")
        print(f"Products with images: {stats.get('products_with_images', 0)}")
        print(
            f"Component types with images: {stats.get('component_types_with_images', 0)}")
        print(
            f"Average image size: {stats.get('avg_image_size_kb', 0):.2f} KB")
        print(
            f"Average quality score: {stats.get('avg_quality_score', 0):.2f}")
        print("="*50)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='FlexLink Image Extraction and Upload Tool')
    parser.add_argument('--pdf', type=str, help='Path to PDF file to process')
    parser.add_argument('--directory', type=str,
                        help='Directory containing PDF files to process')
    parser.add_argument('--no-save-local', action='store_true',
                        help='Do not save images locally')
    parser.add_argument('--output-dir', type=str, default='extracted_images',
                        help='Output directory for local images')
    parser.add_argument('--search', action='store_true',
                        help='Search for images in database')
    parser.add_argument('--product-code', type=str,
                        help='Product code for search')
    parser.add_argument('--component-type', type=str,
                        help='Component type for search')
    parser.add_argument('--blueprint-only', action='store_true',
                        help='Search only blueprint images')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics')

    args = parser.parse_args()

    processor = FlexLinkImageProcessor()

    if args.stats:
        processor.get_database_statistics()
        return

    if args.search:
        processor.search_and_display_images(
            product_code=args.product_code,
            component_type=args.component_type,
            is_blueprint=args.blueprint_only
        )
        return

    if args.pdf:
        # Process single PDF
        if not os.path.exists(args.pdf):
            print(f"❌ PDF file not found: {args.pdf}")
            return

        result = processor.process_pdf_and_upload(
            args.pdf,
            save_local=not args.no_save_local,
            output_dir=args.output_dir
        )

        if result['success']:
            print("✅ Processing completed successfully!")
        else:
            print("❌ Processing failed")

    elif args.directory:
        # Process multiple PDFs
        result = processor.batch_process_pdfs(
            args.directory,
            save_local=not args.no_save_local
        )

        if result['success']:
            print("✅ Batch processing completed successfully!")
        else:
            print("❌ Batch processing failed")

    else:
        # Interactive mode
        print("🔄 FlexLink Image Processor")
        print("1. Process single PDF")
        print("2. Process directory of PDFs")
        print("3. Search images in database")
        print("4. Show database statistics")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            pdf_path = input("Enter PDF path: ").strip()
            if pdf_path and os.path.exists(pdf_path):
                result = processor.process_pdf_and_upload(pdf_path)
                if result['success']:
                    print("✅ Processing completed successfully!")
                else:
                    print("❌ Processing failed")
            else:
                print("❌ Invalid PDF path")

        elif choice == "2":
            directory = input("Enter directory path: ").strip()
            if directory and os.path.exists(directory):
                result = processor.batch_process_pdfs(directory)
                if result['success']:
                    print("✅ Batch processing completed successfully!")
                else:
                    print("❌ Batch processing failed")
            else:
                print("❌ Invalid directory path")

        elif choice == "3":
            product_code = input(
                "Enter product code (or press Enter to skip): ").strip() or None
            component_type = input(
                "Enter component type (or press Enter to skip): ").strip() or None
            blueprint_only = input(
                "Search only blueprints? (y/n): ").strip().lower() == 'y'

            processor.search_and_display_images(
                product_code, component_type, blueprint_only)

        elif choice == "4":
            processor.get_database_statistics()

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
