#!/usr/bin/env python3
"""
FlexLink Component Specification Extractor
Extracts detailed component specifications from PDFs and formats them for database storage
"""

import os
import re
import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
from dotenv import load_dotenv

# PDF processing libraries
try:
    import fitz  # PyMuPDF
    import pdfplumber
    PDF_LIBRARIES_AVAILABLE = True
except ImportError:
    PDF_LIBRARIES_AVAILABLE = False
    print("⚠️  PDF libraries not installed. Run: pip install PyMuPDF pdfplumber")

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


@dataclass
class ComponentSpecification:
    """Structured component specification data"""
    system_code: str
    component_type: str
    component_name: str
    part_number: Optional[str] = None
    specifications: Dict[str, Any] = None
    dimensions: Dict[str, str] = None
    materials: List[str] = None
    compatibility: List[str] = None
    weight_kg: Optional[float] = None
    price_euro: Optional[float] = None
    description: str = ""
    image_url: Optional[str] = None
    page_reference: Optional[int] = None

    def __post_init__(self):
        if self.specifications is None:
            self.specifications = {}
        if self.dimensions is None:
            self.dimensions = {}
        if self.materials is None:
            self.materials = []
        if self.compatibility is None:
            self.compatibility = []


class ComponentSpecificationExtractor:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """Initialize the component specification extractor"""
        load_dotenv()

        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')

        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(
                    self.supabase_url, self.supabase_key)
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"❌ Failed to connect to Supabase: {e}")
                self.supabase = None
        elif not SUPABASE_AVAILABLE:
            self.supabase = None
            print("⚠️  Supabase not installed. Run: pip install supabase")
        else:
            self.supabase = None
            print(
                "⚠️  Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")

        # Component type patterns
        self.component_patterns = {
            'chain': {
                'keywords': ['chain', 'conveyor chain', 'flexible chain'],
                'spec_patterns': {
                    'pitch': r'(\d+\.?\d*)\s*mm\s*pitch',
                    'width': r'(\d+\.?\d*)\s*mm\s*width',
                    'max_load': r'(\d+\.?\d*)\s*kg.*(?:per\s*link|maximum)',
                    'material': r'(steel|stainless steel|plastic|nylon)',
                    'type': r'(plain|cleated|steel top|side flexing)'
                }
            },
            'sprocket': {
                'keywords': ['sprocket', 'drive sprocket', 'idler sprocket'],
                'spec_patterns': {
                    'teeth': r'(\d+)\s*teeth',
                    'bore': r'(\d+\.?\d*)\s*mm\s*bore',
                    'pitch': r'(\d+\.?\d*)\s*mm\s*pitch',
                    'material': r'(steel|stainless steel|plastic)',
                    'type': r'(drive|idler|tension)'
                }
            },
            'bearing': {
                'keywords': ['bearing', 'roller bearing', 'chain bearing'],
                'spec_patterns': {
                    'load_rating': r'(\d+\.?\d*)\s*kg.*load',
                    'bore': r'(\d+\.?\d*)\s*mm\s*bore',
                    'material': r'(steel|stainless steel|ceramic)',
                    'seals': r'(single|double|open)\s*(lip|contact)',
                    'type': r'(roller|ball|needle)'
                }
            },
            'track': {
                'keywords': ['track', 'guide rail', 'aluminum track'],
                'spec_patterns': {
                    'width': r'(\d+\.?\d*)\s*mm\s*width',
                    'height': r'(\d+\.?\d*)\s*mm\s*height',
                    'material': r'(aluminum|steel|stainless steel)',
                    'profile': r'(standard|low profile|high profile)',
                    'length': r'(\d+\.?\d*)\s*m\s*length'
                }
            },
            'drive_unit': {
                'keywords': ['drive unit', 'motor', 'actuator'],
                'spec_patterns': {
                    'power': r'(\d+\.?\d*)\s*kW',
                    'voltage': r'(\d+\.?\d*)\s*V',
                    'speed': r'(\d+\.?\d*)\s*rpm',
                    'torque': r'(\d+\.?\d*)\s*Nm',
                    'type': r'(end|intermediate|center)'
                }
            },
            'bend': {
                'keywords': ['bend', 'curve', 'turn', 'radius'],
                'spec_patterns': {
                    'radius': r'(\d+\.?\d*)\s*mm\s*radius',
                    'angle': r'(\d+\.?\d*)\s*degrees?',
                    'type': r'(horizontal|vertical|spiral)',
                    'direction': r'(left|right|up|down)'
                }
            }
        }

        # System code patterns
        self.system_patterns = {
            'x45': r'X45|X-45',
            'xs': r'XS|X-S',
            'x65': r'X65|X-65',
            'x85': r'X85|X-85',
            'xh': r'XH|X-H',
            'xk': r'XK|X-K',
            'x180': r'X180|X-180',
            'x300': r'X300|X-300'
        }

    def extract_from_pdf(self, pdf_path: str) -> List[ComponentSpecification]:
        """Extract component specifications from a PDF file"""
        if not PDF_LIBRARIES_AVAILABLE:
            print("❌ PDF libraries not available")
            return []

        print(f"📄 Processing PDF: {pdf_path}")

        try:
            # Extract text from PDF
            page_texts = self._extract_text_from_pdf(pdf_path)
            if not page_texts:
                print("❌ No text extracted from PDF")
                return []

            # Extract component specifications
            components = []
            for page_num, text in page_texts.items():
                page_components = self._extract_components_from_text(
                    text, page_num)
                components.extend(page_components)

            print(f"✅ Extracted {len(components)} component specifications")
            return components

        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return []

    def _extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF pages"""
        page_texts = {}

        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        page_texts[page_num] = text.strip()

            if not page_texts:
                # Fallback to PyMuPDF
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text and text.strip():
                        page_texts[page_num + 1] = text.strip()
                doc.close()

            return page_texts

        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return {}

    def _extract_components_from_text(self, text: str, page_num: int) -> List[ComponentSpecification]:
        """Extract component specifications from text"""
        components = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            # Detect component type
            component_type = self._detect_component_type(line)
            if not component_type:
                continue

            # Extract system code
            system_code = self._extract_system_code(line)
            if not system_code:
                continue

            # Extract component details
            component = self._extract_component_details(
                lines, i, component_type, system_code, page_num
            )
            if component:
                components.append(component)

        return components

    def _detect_component_type(self, text: str) -> Optional[str]:
        """Detect component type from text"""
        text_lower = text.lower()

        for comp_type, patterns in self.component_patterns.items():
            for keyword in patterns['keywords']:
                if keyword in text_lower:
                    return comp_type

        return None

    def _extract_system_code(self, text: str) -> Optional[str]:
        """Extract system code from text"""
        for system_name, pattern in self.system_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_component_details(self, lines: List[str], start_idx: int,
                                   component_type: str, system_code: str,
                                   page_num: int) -> Optional[ComponentSpecification]:
        """Extract detailed component information"""
        try:
            # Get component name from the line
            component_name = lines[start_idx].strip()

            # Extract specifications from surrounding lines
            specs = self._extract_specifications(
                lines, start_idx, component_type)

            # Extract part number if present
            part_number = self._extract_part_number(
                lines[start_idx:start_idx+5])

            # Extract dimensions
            dimensions = self._extract_dimensions(
                lines[start_idx:start_idx+10])

            # Extract materials
            materials = self._extract_materials(lines[start_idx:start_idx+10])

            # Extract compatibility
            compatibility = self._extract_compatibility(
                lines[start_idx:start_idx+10])

            # Extract weight and price
            weight_kg = self._extract_weight(lines[start_idx:start_idx+10])
            price_euro = self._extract_price(lines[start_idx:start_idx+10])

            return ComponentSpecification(
                system_code=system_code,
                component_type=component_type,
                component_name=component_name,
                part_number=part_number,
                specifications=specs,
                dimensions=dimensions,
                materials=materials,
                compatibility=compatibility,
                weight_kg=weight_kg,
                price_euro=price_euro,
                page_reference=page_num
            )

        except Exception as e:
            print(f"⚠️  Error extracting component details: {e}")
            return None

    def _extract_specifications(self, lines: List[str], start_idx: int,
                                component_type: str) -> Dict[str, Any]:
        """Extract specifications based on component type"""
        specs = {}
        patterns = self.component_patterns[component_type]['spec_patterns']

        # Look in surrounding lines
        search_lines = lines[max(0, start_idx-5):start_idx+10]
        text_block = ' '.join(search_lines)

        for spec_name, pattern in patterns.items():
            match = re.search(pattern, text_block, re.IGNORECASE)
            if match:
                try:
                    # Try to convert to number if possible
                    value = match.group(1)
                    if '.' in value:
                        specs[spec_name] = float(value)
                    elif value.isdigit():
                        specs[spec_name] = int(value)
                    else:
                        specs[spec_name] = value
                except:
                    specs[spec_name] = match.group(1)

        return specs

    def _extract_part_number(self, lines: List[str]) -> Optional[str]:
        """Extract part number from lines"""
        for line in lines:
            # Look for patterns like "Part No:", "P/N:", "Article:", etc.
            patterns = [
                r'part\s*no\.?\s*:?\s*([A-Z0-9\-]+)',
                r'p/n\s*:?\s*([A-Z0-9\-]+)',
                r'article\s*:?\s*([A-Z0-9\-]+)',
                r'item\s*:?\s*([A-Z0-9\-]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1)

        return None

    def _extract_dimensions(self, lines: List[str]) -> Dict[str, str]:
        """Extract dimensions from lines"""
        dimensions = {}
        text_block = ' '.join(lines)

        # Common dimension patterns
        patterns = {
            'length': r'(\d+\.?\d*)\s*mm\s*(?:length|l)',
            'width': r'(\d+\.?\d*)\s*mm\s*(?:width|w)',
            'height': r'(\d+\.?\d*)\s*mm\s*(?:height|h)',
            'diameter': r'(\d+\.?\d*)\s*mm\s*(?:diameter|d)',
            'thickness': r'(\d+\.?\d*)\s*mm\s*(?:thickness|t)'
        }

        for dim_name, pattern in patterns.items():
            match = re.search(pattern, text_block, re.IGNORECASE)
            if match:
                dimensions[dim_name] = f"{match.group(1)}mm"

        return dimensions

    def _extract_materials(self, lines: List[str]) -> List[str]:
        """Extract materials from lines"""
        materials = []
        text_block = ' '.join(lines)

        # Common material patterns
        material_patterns = [
            r'steel',
            r'stainless steel',
            r'aluminum',
            r'plastic',
            r'nylon',
            r'ceramic',
            r'brass',
            r'bronze'
        ]

        for pattern in material_patterns:
            if re.search(pattern, text_block, re.IGNORECASE):
                materials.append(pattern.title())

        return list(set(materials))  # Remove duplicates

    def _extract_compatibility(self, lines: List[str]) -> List[str]:
        """Extract compatibility information"""
        compatibility = []
        text_block = ' '.join(lines)

        # Look for system codes
        for system_name, pattern in self.system_patterns.items():
            if re.search(pattern, text_block, re.IGNORECASE):
                compatibility.append(system_name.upper())

        return list(set(compatibility))

    def _extract_weight(self, lines: List[str]) -> Optional[float]:
        """Extract weight from lines"""
        text_block = ' '.join(lines)

        # Weight patterns
        patterns = [
            r'(\d+\.?\d*)\s*kg',
            r'(\d+\.?\d*)\s*g',
            r'weight\s*:?\s*(\d+\.?\d*)\s*kg'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_block, re.IGNORECASE)
            if match:
                weight = float(match.group(1))
                if 'g' in pattern and weight < 1000:  # Convert grams to kg
                    weight = weight / 1000
                return weight

        return None

    def _extract_price(self, lines: List[str]) -> Optional[float]:
        """Extract price from lines"""
        text_block = ' '.join(lines)

        # Price patterns
        patterns = [
            r'(\d+\.?\d*)\s*€',
            r'(\d+\.?\d*)\s*euro',
            r'price\s*:?\s*(\d+\.?\d*)',
            r'cost\s*:?\s*(\d+\.?\d*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_block, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return None

    def save_to_json(self, components: List[ComponentSpecification], output_file: str):
        """Save extracted components to JSON file"""
        try:
            data = [asdict(component) for component in components]

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved {len(components)} components to {output_file}")

        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")

    def save_to_csv(self, components: List[ComponentSpecification], output_file: str):
        """Save extracted components to CSV file"""
        try:
            if not components:
                print("⚠️  No components to save")
                return

            # Collect all possible field names first
            all_fieldnames = set()
            rows = []

            for component in components:
                row = {
                    'system_code': component.system_code,
                    'component_type': component.component_type,
                    'component_name': component.component_name,
                    'part_number': component.part_number or '',
                    'description': component.description,
                    'weight_kg': component.weight_kg or '',
                    'price_euro': component.price_euro or '',
                    'page_reference': component.page_reference or '',
                    'materials': ', '.join(component.materials),
                    'compatibility': ', '.join(component.compatibility)
                }

                # Add specifications
                for key, value in component.specifications.items():
                    field_name = f'spec_{key}'
                    row[field_name] = str(value)
                    all_fieldnames.add(field_name)

                # Add dimensions
                for key, value in component.dimensions.items():
                    field_name = f'dim_{key}'
                    row[field_name] = value
                    all_fieldnames.add(field_name)

                rows.append(row)
                all_fieldnames.update(row.keys())

            # Ensure all rows have the same fields
            fieldnames = sorted(list(all_fieldnames))
            for row in rows:
                for field in fieldnames:
                    if field not in row:
                        row[field] = ''

            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

            print(f"✅ Saved {len(components)} components to {output_file}")

        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")

    def upload_to_database(self, components: List[ComponentSpecification]) -> bool:
        """Upload extracted components to Supabase database"""
        if not self.supabase:
            print("❌ Supabase not configured")
            return False

        try:
            # Convert to database format
            db_components = []
            for component in components:
                db_component = {
                    'system_code': component.system_code,
                    'component_type': component.component_type,
                    'name': component.component_name,
                    'part_number': component.part_number,
                    'specifications': component.specifications,
                    'dimensions': component.dimensions,
                    'materials': component.materials,
                    'compatibility': component.compatibility,
                    'weight_kg': component.weight_kg,
                    'price_euro': component.price_euro,
                    'description': component.description,
                    'image_url': component.image_url,
                    'page_reference': component.page_reference
                }
                db_components.append(db_component)

            # Upload to database
            result = self.supabase.table(
                'component_specifications').insert(db_components).execute()

            print(f"✅ Uploaded {len(components)} components to database")
            return True

        except Exception as e:
            print(f"❌ Error uploading to database: {e}")
            return False

    def create_sample_data(self) -> List[ComponentSpecification]:
        """Create sample component specifications for testing"""
        sample_components = [
            ComponentSpecification(
                system_code="X45",
                component_type="chain",
                component_name="X45 Plain Chain",
                part_number="X45-PC-1000",
                specifications={
                    "pitch": 25.4,
                    "width": 43,
                    "max_load": 2.5,
                    "material": "steel",
                    "type": "plain"
                },
                dimensions={
                    "length": "1000mm",
                    "width": "43mm",
                    "height": "12mm"
                },
                materials=["Steel"],
                compatibility=["X45"],
                weight_kg=0.85,
                price_euro=45.50,
                description="Standard plain chain for X45 system"
            ),
            ComponentSpecification(
                system_code="X45",
                component_type="sprocket",
                component_name="X45 Drive Sprocket 16T",
                part_number="X45-DS-16",
                specifications={
                    "teeth": 16,
                    "bore": 25,
                    "pitch": 25.4,
                    "material": "steel",
                    "type": "drive"
                },
                dimensions={
                    "diameter": "130mm",
                    "width": "20mm"
                },
                materials=["Steel"],
                compatibility=["X45"],
                weight_kg=0.45,
                price_euro=28.75,
                description="16-tooth drive sprocket for X45 system"
            )
        ]

        return sample_components


def main():
    """Main function for testing and demonstration"""
    extractor = ComponentSpecificationExtractor()

    # Test with sample data
    print("🧪 Testing with sample data...")
    sample_components = extractor.create_sample_data()

    # Save to files
    extractor.save_to_json(sample_components, 'data/sample_components.json')
    extractor.save_to_csv(sample_components, 'data/sample_components.csv')

    # Upload to database if available
    if extractor.supabase:
        extractor.upload_to_database(sample_components)

    print("✅ Component extraction test completed!")


if __name__ == "__main__":
    main()
