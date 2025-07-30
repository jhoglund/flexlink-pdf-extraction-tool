#!/usr/bin/env python3
"""
FlexLink Component Extraction CLI
Command-line interface for extracting component specifications from PDFs
"""

import argparse
import sys
import os
from pathlib import Path
from component_extractor import ComponentSpecificationExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract FlexLink component specifications from PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from a single PDF and save to JSON
  python extract_components.py catalog.pdf --output components.json

  # Extract from multiple PDFs and save to CSV
  python extract_components.py *.pdf --format csv --output components.csv

  # Extract and upload to database
  python extract_components.py catalog.pdf --upload

  # Test with sample data
  python extract_components.py --test
        """
    )

    parser.add_argument(
        'pdf_files',
        nargs='*',
        help='PDF files to process (use --test for sample data)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path (JSON or CSV)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload extracted data to database'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test with sample data instead of processing PDFs'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Initialize extractor
    extractor = ComponentSpecificationExtractor()

    if args.test:
        print("🧪 Running test with sample data...")
        components = extractor.create_sample_data()

        if args.output:
            if args.format == 'json':
                extractor.save_to_json(components, args.output)
            else:
                extractor.save_to_csv(components, args.output)
        else:
            # Default output for test
            extractor.save_to_json(components, 'data/test_components.json')
            extractor.save_to_csv(components, 'data/test_components.csv')

        if args.upload:
            extractor.upload_to_database(components)

        print(
            f"✅ Test completed! Extracted {len(components)} sample components")
        return

    if not args.pdf_files:
        print("❌ No PDF files specified. Use --help for usage information.")
        sys.exit(1)

    # Process PDF files
    all_components = []

    for pdf_file in args.pdf_files:
        if not os.path.exists(pdf_file):
            print(f"⚠️  File not found: {pdf_file}")
            continue

        if not pdf_file.lower().endswith('.pdf'):
            print(f"⚠️  Skipping non-PDF file: {pdf_file}")
            continue

        print(f"📄 Processing: {pdf_file}")
        components = extractor.extract_from_pdf(pdf_file)
        all_components.extend(components)

        if args.verbose:
            print(f"   Found {len(components)} components")

    if not all_components:
        print("❌ No components extracted from any PDF files")
        sys.exit(1)

    print(f"\n✅ Total components extracted: {len(all_components)}")

    # Save to file
    if args.output:
        if args.format == 'json':
            extractor.save_to_json(all_components, args.output)
        else:
            extractor.save_to_csv(all_components, args.output)
    else:
        # Default output
        default_json = 'data/extracted_components.json'
        default_csv = 'data/extracted_components.csv'

        extractor.save_to_json(all_components, default_json)
        extractor.save_to_csv(all_components, default_csv)

        print(f"📁 Saved to: {default_json} and {default_csv}")

    # Upload to database
    if args.upload:
        if extractor.supabase:
            success = extractor.upload_to_database(all_components)
            if success:
                print("✅ Successfully uploaded to database")
            else:
                print("❌ Failed to upload to database")
        else:
            print("⚠️  Database not configured - skipping upload")

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total components: {len(all_components)}")

    # Group by system
    systems = {}
    for comp in all_components:
        if comp.system_code not in systems:
            systems[comp.system_code] = []
        systems[comp.system_code].append(comp)

    print(f"   Systems found: {len(systems)}")
    for system, comps in systems.items():
        print(f"     {system}: {len(comps)} components")

    # Group by component type
    types = {}
    for comp in all_components:
        if comp.component_type not in types:
            types[comp.component_type] = []
        types[comp.component_type].append(comp)

    print(f"   Component types: {len(types)}")
    for comp_type, comps in types.items():
        print(f"     {comp_type}: {len(comps)} components")


if __name__ == "__main__":
    main()
