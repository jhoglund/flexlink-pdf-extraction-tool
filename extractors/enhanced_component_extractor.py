#!/usr/bin/env python3
"""
Enhanced Component Extractor for FlexLink Catalogs
Captures system-level application information and intro text for filtering by criteria like "washable", "food grade", etc.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
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
class SystemApplication:
    """System-level application information"""
    system_code: str
    title: str
    description: str
    applications: List[str]
    features: List[str]
    specifications: Dict[str, Any]
    page_reference: int


@dataclass
class EnhancedComponentSpecification:
    """Enhanced component specification with system application info"""
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
    # New fields for application information
    system_applications: List[str] = None
    system_features: List[str] = None
    washable: bool = False
    food_grade: bool = False
    high_temperature: bool = False
    chemical_resistant: bool = False
    hygienic: bool = False
    heavy_duty: bool = False

    def __post_init__(self):
        if self.specifications is None:
            self.specifications = {}
        if self.dimensions is None:
            self.dimensions = {}
        if self.materials is None:
            self.materials = []
        if self.compatibility is None:
            self.compatibility = []
        if self.system_applications is None:
            self.system_applications = []
        if self.system_features is None:
            self.system_features = []


class EnhancedComponentExtractor:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """Initialize the enhanced component extractor"""
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
        else:
            self.supabase = None
            print("⚠️  Supabase not configured")

        # System application patterns
        self.system_patterns = {
            'X45': {
                'keywords': ['X45', 'X45H', 'X45C'],
                'applications': ['general purpose', 'light duty', 'modular'],
                'features': ['modular', 'flexible', 'easy assembly']
            },
            'XS': {
                'keywords': ['XS', 'XSH', 'XSC'],
                'applications': ['small parts', 'precision', 'lightweight'],
                'features': ['compact', 'precise', 'lightweight']
            },
            'X65': {
                'keywords': ['X65', 'X65H', 'X65C'],
                'applications': ['heavy duty', 'industrial', 'robust'],
                'features': ['heavy duty', 'robust', 'industrial']
            },
            'X85': {
                'keywords': ['X85', 'X85H', 'X85C'],
                'applications': ['heavy duty', 'high load', 'industrial'],
                'features': ['high load', 'heavy duty', 'industrial']
            },
            'X180': {
                'keywords': ['X180', 'X180H', 'X180C'],
                'applications': ['heavy duty', 'high load', 'industrial'],
                'features': ['high load', 'heavy duty', 'industrial']
            },
            'X300': {
                'keywords': ['X300', 'X300H', 'X300C'],
                'applications': ['heavy duty', 'high load', 'industrial'],
                'features': ['high load', 'heavy duty', 'industrial']
            },
            'XH': {
                'keywords': ['XH', 'XHH', 'XHC'],
                'applications': ['hygienic', 'food grade', 'washable'],
                'features': ['hygienic', 'food grade', 'washable', 'stainless steel']
            },
            'XK': {
                'keywords': ['XK', 'XKH', 'XKC'],
                'applications': ['chemical resistant', 'corrosive environments'],
                'features': ['chemical resistant', 'corrosive resistant']
            }
        }

        # Application keywords for filtering
        self.application_keywords = {
            'washable': ['washable', 'wash-down', 'cleaning', 'hygienic', 'sanitary'],
            'food_grade': ['food grade', 'food safe', 'FDA', 'hygienic', 'sanitary'],
            'high_temperature': ['high temperature', 'heat resistant', 'thermal', 'hot'],
            'chemical_resistant': ['chemical resistant', 'corrosive', 'acid resistant', 'chemical'],
            'hygienic': ['hygienic', 'sanitary', 'clean', 'food grade'],
            'heavy_duty': ['heavy duty', 'industrial', 'robust', 'high load']
        }

    def extract_system_applications(self, pdf_path: str) -> List[SystemApplication]:
        """Extract system-level application information from PDF"""
        print(f"📖 Extracting system applications from: {pdf_path}")

        applications = []
        text_by_page = self._extract_text_from_pdf(pdf_path)

        for page_num, text in text_by_page.items():
            # Look for system introductions and descriptions
            for system_code, patterns in self.system_patterns.items():
                if any(keyword in text for keyword in patterns['keywords']):
                    # Extract system description
                    description = self._extract_system_description(
                        text, system_code)
                    if description:
                        application = SystemApplication(
                            system_code=system_code,
                            title=f"FlexLink {system_code} System",
                            description=description,
                            applications=patterns['applications'],
                            features=patterns['features'],
                            specifications=self._extract_system_specifications(
                                text, system_code),
                            page_reference=page_num
                        )
                        applications.append(application)

        return applications

    def _extract_system_description(self, text: str, system_code: str) -> Optional[str]:
        """Extract system description from text"""
        # Look for paragraphs that describe the system
        lines = text.split('\n')
        description_lines = []

        for i, line in enumerate(lines):
            if system_code in line and len(line) > 50:  # Likely a description
                # Get the next few lines as description
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip():
                        description_lines.append(lines[j].strip())
                break

        if description_lines:
            return ' '.join(description_lines)
        return None

    def _extract_system_specifications(self, text: str, system_code: str) -> Dict[str, Any]:
        """Extract system specifications from text"""
        specs = {}

        # Look for common specifications
        patterns = {
            'max_load': r'(\d+\.?\d*)\s*(?:kg|lb).*load',
            'temperature': r'(\d+\.?\d*)\s*°C',
            'speed': r'(\d+\.?\d*)\s*(?:m/min|ft/min)',
            'pitch': r'(\d+\.?\d*)\s*mm\s*pitch'
        }

        for spec_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs[spec_name] = float(match.group(1))

        return specs

    def extract_enhanced_components(self, pdf_path: str) -> List[EnhancedComponentSpecification]:
        """Extract components with enhanced application information"""
        print(f"📖 Extracting enhanced components from: {pdf_path}")

        # First extract system applications
        system_applications = self.extract_system_applications(pdf_path)

        # Create a mapping of system codes to their applications
        system_app_map = {app.system_code: app for app in system_applications}

        # Extract regular components
        from component_extractor import ComponentSpecificationExtractor
        base_extractor = ComponentSpecificationExtractor()
        base_components = base_extractor.extract_from_pdf(pdf_path)

        # Enhance components with application information
        enhanced_components = []

        for component in base_components:
            enhanced_comp = EnhancedComponentSpecification(
                system_code=component.system_code,
                component_type=component.component_type,
                component_name=component.component_name,
                part_number=component.part_number,
                specifications=component.specifications,
                dimensions=component.dimensions,
                materials=component.materials,
                compatibility=component.compatibility,
                weight_kg=component.weight_kg,
                price_euro=component.price_euro,
                description=component.description,
                image_url=component.image_url,
                page_reference=component.page_reference
            )

            # Add system application information
            if component.system_code in system_app_map:
                system_app = system_app_map[component.system_code]
                enhanced_comp.system_applications = system_app.applications
                enhanced_comp.system_features = system_app.features

                # Determine application flags
                enhanced_comp.washable = self._check_application_flag(
                    component, system_app, 'washable')
                enhanced_comp.food_grade = self._check_application_flag(
                    component, system_app, 'food_grade')
                enhanced_comp.high_temperature = self._check_application_flag(
                    component, system_app, 'high_temperature')
                enhanced_comp.chemical_resistant = self._check_application_flag(
                    component, system_app, 'chemical_resistant')
                enhanced_comp.hygienic = self._check_application_flag(
                    component, system_app, 'hygienic')
                enhanced_comp.heavy_duty = self._check_application_flag(
                    component, system_app, 'heavy_duty')

            enhanced_components.append(enhanced_comp)

        return enhanced_components

    def _check_application_flag(self, component: Any, system_app: SystemApplication, flag_name: str) -> bool:
        """Check if component meets application criteria"""
        # Check component specifications
        component_text = f"{component.component_name} {component.description}".lower(
        )

        # Check system applications
        system_text = f"{system_app.description} {' '.join(system_app.applications)}".lower(
        )

        # Check for keywords
        keywords = self.application_keywords.get(flag_name, [])

        for keyword in keywords:
            if keyword in component_text or keyword in system_text:
                return True

        return False

    def _extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF page by page"""
        text_by_page = {}

        try:
            # Try pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_by_page[page_num] = text
        except Exception as e:
            print(f"⚠️  pdfplumber failed: {e}")
            # Fallback to PyMuPDF
            try:
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text:
                        text_by_page[page_num + 1] = text
                doc.close()
            except Exception as e2:
                print(f"❌ Both PDF libraries failed: {e2}")

        return text_by_page

    def save_enhanced_components(self, components: List[EnhancedComponentSpecification], output_file: str):
        """Save enhanced components to JSON"""
        components_data = [asdict(comp) for comp in components]

        with open(output_file, 'w') as f:
            json.dump(components_data, f, indent=2)

        print(
            f"✅ Saved {len(components)} enhanced components to {output_file}")

    def upload_enhanced_components(self, components: List[EnhancedComponentSpecification]) -> bool:
        """Upload enhanced components to database"""
        if not self.supabase:
            print("❌ No database connection available")
            return False

        try:
            components_data = [asdict(comp) for comp in components]

            # Upload in batches
            batch_size = 20
            for i in range(0, len(components_data), batch_size):
                batch = components_data[i:i + batch_size]
                result = self.supabase.table(
                    'component_specifications').insert(batch).execute()
                print(f"✅ Uploaded batch {i//batch_size + 1}")

            return True
        except Exception as e:
            print(f"❌ Error uploading enhanced components: {e}")
            return False


def main():
    """Main function for testing"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract enhanced components with application information")
    parser.add_argument("pdf_file", help="Path to the PDF catalog file")
    parser.add_argument(
        "--output", default="data/enhanced_components.json", help="Output JSON file")
    parser.add_argument("--upload", action="store_true",
                        help="Upload to database")

    args = parser.parse_args()

    extractor = EnhancedComponentExtractor()

    # Extract enhanced components
    components = extractor.extract_enhanced_components(args.pdf_file)

    # Save to file
    extractor.save_enhanced_components(components, args.output)

    # Upload if requested
    if args.upload:
        extractor.upload_enhanced_components(components)


if __name__ == "__main__":
    main()
