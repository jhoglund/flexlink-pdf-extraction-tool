#!/usr/bin/env python3
"""
FlexLink PDF Extractor Tool
Extracts structured data from FlexLink catalog PDFs
"""

import os
import re
import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# You'll need to install these
# pip install PyMuPDF pdfplumber

try:
    import fitz  # PyMuPDF
    import pdfplumber
    PDF_LIBRARIES_AVAILABLE = True
except ImportError:
    PDF_LIBRARIES_AVAILABLE = False
    print("⚠️  PDF libraries not installed. Run: pip install PyMuPDF pdfplumber")


@dataclass
class ExtractedComponent:
    system_code: str
    name: str
    component_type: str
    specifications: Dict
    compatibility: List[str]
    description: str = ""
    page_number: int = 0


@dataclass
class ExtractedSystem:
    code: str
    name: str
    description: str
    chain_width_mm: Optional[int]
    max_load_per_link_kg: Optional[float]
    features: List[str]
    applications: List[str]


class FlexLinkPDFExtractor:
    def __init__(self):
        """Initialize the PDF extractor"""
        load_dotenv()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

        # Patterns for extracting different types of content
        self.system_patterns = {
            'system_code': r'([A-Z]+\d+[A-Z]*)\s*(?:\(.*?\))?',
            'chain_width': r'(\d+)\s*mm\s*chain',
            'max_load': r'(\d+\.?\d*)\s*kg.*(?:per\s*link|maximum)',
            'features_start': r'Features?\s*:?\s*',
            'applications_start': r'(?:Examples?\s*of\s*)?[Aa]pplications?\s*:?\s*'
        }

        self.component_patterns = {
            'drive_unit': r'drive\s*unit|motor|actuator',
            'chain': r'chain|belt|conveyor\s*chain',
            'bend': r'bend|curve|turn',
            'guide_rail': r'guide\s*rail|bracket|support',
            'idler': r'idler|roller|wheel'
        }

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF, page by page"""
        if not PDF_LIBRARIES_AVAILABLE:
            print("❌ PDF libraries not available")
            return {}

        page_texts = {}

        try:
            # Try with pdfplumber first (better for tables)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_texts[page_num] = text

            print(
                f"✅ Extracted text from {len(page_texts)} pages using pdfplumber")
            return page_texts

        except Exception as e:
            print(f"⚠️  pdfplumber failed: {e}")

            # Fallback to PyMuPDF
            try:
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        page_texts[page_num + 1] = text

                doc.close()
                print(
                    f"✅ Extracted text from {len(page_texts)} pages using PyMuPDF")
                return page_texts

            except Exception as e2:
                print(f"❌ Both PDF extraction methods failed: {e2}")
                return {}

    def extract_systems_from_text(self, page_texts: Dict[int, str]) -> List[ExtractedSystem]:
        """Extract system information from text"""
        systems = []

        for page_num, text in page_texts.items():
            lines = text.split('\n')

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Look for system headers
                system_match = re.search(
                    r'Conveyor\s*system\s*([A-Z]+\d+[A-Z]*)', line, re.IGNORECASE)
                if system_match:
                    system = self._extract_system_details(lines, i, page_num)
                    if system:
                        systems.append(system)

                i += 1

        return systems

    def _extract_system_details(self, lines: List[str], start_idx: int, page_num: int) -> Optional[ExtractedSystem]:
        """Extract detailed system information starting from a system header"""
        try:
            # Get the system code from the header
            header_line = lines[start_idx]
            code_match = re.search(r'([A-Z]+\d+[A-Z]*)', header_line)
            if not code_match:
                return None

            system_code = code_match.group(1)

            # Extract chain width
            chain_width = None
            width_match = re.search(r'(\d+)\s*mm', header_line)
            if width_match:
                chain_width = int(width_match.group(1))

            # Look for description, features, and applications in subsequent lines
            description = ""
            features = []
            applications = []
            max_load = None

            # Scan next 20 lines for details
            for i in range(start_idx + 1, min(start_idx + 20, len(lines))):
                line = lines[i].strip()

                if not line:
                    continue

                # Look for load information
                load_match = re.search(r'(\d+\.?\d*)\s*kg', line)
                if load_match and 'load' in line.lower():
                    max_load = float(load_match.group(1))

                # Look for features section
                if re.search(r'Features?\s*:?', line, re.IGNORECASE):
                    features.extend(self._extract_list_items(lines, i))

                # Look for applications section
                if re.search(r'(?:Examples?\s*of\s*)?[Aa]pplications?\s*:?', line, re.IGNORECASE):
                    applications.extend(self._extract_list_items(lines, i))

                # Build description from first substantial line
                if not description and len(line) > 20 and not line.isupper():
                    description = line

            return ExtractedSystem(
                code=system_code,
                name=f"Conveyor system {system_code}",
                description=description,
                chain_width_mm=chain_width,
                max_load_per_link_kg=max_load,
                features=features,
                applications=applications
            )

        except Exception as e:
            print(f"⚠️  Error extracting system details: {e}")
            return None

    def _extract_list_items(self, lines: List[str], start_idx: int) -> List[str]:
        """Extract list items starting from a section header"""
        items = []

        # Check if items are on the same line
        current_line = lines[start_idx]
        if ':' in current_line:
            after_colon = current_line.split(':', 1)[1].strip()
            if after_colon:
                items.extend([item.strip() for item in after_colon.split(',')])

        # Look for items in subsequent lines
        for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Stop if we hit another section
            if re.search(r'(Features?|Applications?|Examples?)\s*:?', line, re.IGNORECASE):
                break

            # Extract bullet points or comma-separated items
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                items.append(line[1:].strip())
            elif ',' in line:
                items.extend([item.strip() for item in line.split(',')])
            else:
                items.append(line)

        return [item for item in items if item and len(item) > 2]

    def extract_technical_tables(self, page_texts: Dict[int, str]) -> List[Dict]:
        """Extract technical data tables"""
        tables_data = []

        for page_num, text in page_texts.items():
            lines = text.split('\n')

            # Look for table indicators
            for i, line in enumerate(lines):
                if re.search(r'(technical\s*data|specifications|load\s*per\s*link)', line, re.IGNORECASE):
                    table_data = self._extract_table_from_text(lines, i)
                    if table_data:
                        tables_data.extend(table_data)

        return tables_data

    def _extract_table_from_text(self, lines: List[str], start_idx: int) -> List[Dict]:
        """Extract table data from text lines"""
        table_data = []

        # Look for table-like content in next 20 lines
        for i in range(start_idx, min(start_idx + 20, len(lines))):
            line = lines[i].strip()

            # Skip empty lines and headers
            if not line or len(line) < 10:
                continue

            # Look for system codes and specifications
            system_match = re.search(r'([A-Z]+\d+[A-Z]*)', line)
            if system_match:
                system_code = system_match.group(1)

                # Extract numerical values
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 2:
                    table_data.append({
                        'system_code': system_code,
                        'values': numbers,
                        'raw_line': line
                    })

        return table_data

    def process_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """Process a complete PDF file"""
        print(f"🔄 Processing PDF: {pdf_path}")

        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return {}

        # Extract text
        page_texts = self.extract_text_from_pdf(pdf_path)
        if not page_texts:
            print("❌ No text extracted from PDF")
            return {}

        # Extract structured data
        systems = self.extract_systems_from_text(page_texts)
        tables = self.extract_technical_tables(page_texts)

        print(
            f"✅ Extracted {len(systems)} systems and {len(tables)} table entries")

        return {
            'systems': systems,
            'tables': tables,
            'page_count': len(page_texts)
        }

    def save_extracted_data(self, extracted_data: Dict[str, Any], output_file: str):
        """Save extracted data to JSON"""
        # Convert dataclasses to dicts
        output = {
            'systems': [
                {
                    'code': s.code,
                    'name': s.name,
                    'description': s.description,
                    'chain_width_mm': s.chain_width_mm,
                    'max_load_per_link_kg': s.max_load_per_link_kg,
                    'features': s.features,
                    'applications': s.applications
                } for s in extracted_data.get('systems', [])
            ],
            'tables': extracted_data.get('tables', []),
            'page_count': extracted_data.get('page_count', 0)
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Saved extracted data to {output_file}")

    def upload_to_database(self, systems: List[ExtractedSystem]) -> bool:
        """Upload extracted systems to Supabase"""
        if not systems:
            print("❌ No systems to upload")
            return False

        # Convert to database format
        db_systems = []
        for system in systems:
            db_system = {
                "code": system.code,
                "name": system.name,
                "description": system.description,
                "chain_width_mm": system.chain_width_mm,
                "max_load_per_link_kg": system.max_load_per_link_kg,
                "features": system.features,
                "applications": system.applications,
                "is_active": True
            }
            db_systems.append(db_system)

        try:
            url = f"{self.supabase_url}/rest/v1/conveyor_systems"
            response = requests.post(
                url, headers=self.headers, json=db_systems)

            if response.status_code in [201, 200]:
                print(f"✅ Uploaded {len(db_systems)} systems to database")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error uploading to database: {e}")
            return False


def main():
    print("📄 FlexLink PDF Extractor Tool")
    print("=" * 40)

    if not PDF_LIBRARIES_AVAILABLE:
        print("\n🔧 First, install PDF processing libraries:")
        print("pip install PyMuPDF pdfplumber")
        return

    extractor = FlexLinkPDFExtractor()

    print("\nOptions:")
    print("1. Process a PDF file")
    print("2. Process multiple PDFs in a directory")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        pdf_path = input("Enter PDF file path: ").strip()
        if pdf_path:
            extracted_data = extractor.process_pdf_file(pdf_path)

            if extracted_data.get('systems'):
                # Save to JSON
                output_file = pdf_path.replace('.pdf', '_extracted.json')
                extractor.save_extracted_data(extracted_data, output_file)

                # Ask to upload to database
                upload = input("\nUpload to database? (y/n): ").strip().lower()
                if upload == 'y':
                    extractor.upload_to_database(extracted_data['systems'])

    elif choice == "2":
        directory = input("Enter directory path containing PDFs: ").strip()
        if os.path.isdir(directory):
            pdf_files = [f for f in os.listdir(
                directory) if f.endswith('.pdf')]
            print(f"Found {len(pdf_files)} PDF files")

            for pdf_file in pdf_files:
                pdf_path = os.path.join(directory, pdf_file)
                print(f"\n🔄 Processing {pdf_file}...")
                extracted_data = extractor.process_pdf_file(pdf_path)

                if extracted_data.get('systems'):
                    output_file = pdf_path.replace('.pdf', '_extracted.json')
                    extractor.save_extracted_data(extracted_data, output_file)


if __name__ == "__main__":
    main()
