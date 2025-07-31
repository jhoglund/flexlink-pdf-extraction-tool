#!/usr/bin/env python3
"""
Enhanced FlexLink System Extractor
Focuses on main FlexLink systems and extracts detailed information
"""

import os
import re
import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime


@dataclass
class FlexLinkSystem:
    """Structured FlexLink system data"""
    system_name: str
    system_code: str
    category: str
    description: str
    key_features: List[str]
    applications: List[str]
    advantages: List[str]
    technical_specs: Dict[str, Any]
    materials: List[str]
    page_reference: Optional[int] = None


class EnhancedSystemExtractor:
    def __init__(self):
        """Initialize the enhanced system extractor"""
        # Main FlexLink system categories
        self.main_systems = {
            'X65': {
                'name': 'X65 Chain System',
                'category': 'Chain Conveyor',
                'keywords': ['X65', 'X65H', 'X65 chain', 'X65 system'],
                'features': ['Standard chain system', 'Versatile', 'Modular design']
            },
            'X85': {
                'name': 'X85 Chain System',
                'category': 'Chain Conveyor',
                'keywords': ['X85', 'X85H', 'X85 chain', 'X85 system'],
                'features': ['Heavy duty', 'High load capacity', 'Robust design']
            },
            'XK': {
                'name': 'XK Pallet System',
                'category': 'Pallet Conveyor',
                'keywords': ['XK', 'XK pallet', 'XK system', 'pallet system'],
                'features': ['Pallet handling', 'Precision positioning', 'Flexible routing']
            },
            'XT': {
                'name': 'XT Pallet System',
                'category': 'Pallet Conveyor',
                'keywords': ['XT', 'XT pallet', 'XT system'],
                'features': ['Twin track', 'High precision', 'Advanced control']
            },
            'Modular Belt': {
                'name': 'Modular Plastic Belt System',
                'category': 'Belt Conveyor',
                'keywords': ['modular belt', 'plastic belt', 'belt system'],
                'features': ['Gentle handling', 'Wide belt options', 'Accumulation capability']
            },
            'Stainless Steel': {
                'name': 'Stainless Steel System',
                'category': 'Specialized Conveyor',
                'keywords': ['stainless steel', 'stainless', 'hygienic'],
                'features': ['Hygienic design', 'Corrosion resistant', 'Food grade']
            },
            'Guide Rail': {
                'name': 'Guide Rail System',
                'category': 'Support System',
                'keywords': ['guide rail', 'guiding', 'rail system'],
                'features': ['Product guidance', 'Curve support', 'Width adjustment']
            },
            'Structural': {
                'name': 'Structural System',
                'category': 'Support System',
                'keywords': ['structural', 'frame', 'support'],
                'features': ['Modular frame', 'Adjustable height', 'Rigid construction']
            }
        }

    def extract_main_systems(self, pdf_path: str) -> List[FlexLinkSystem]:
        """Extract main FlexLink systems from PDF"""
        print(f"📖 Extracting main FlexLink systems from: {pdf_path}")

        # Extract text from PDF
        text_by_page = self._extract_text_from_pdf(pdf_path)

        # Extract system information
        all_systems = []
        for page_num, text in text_by_page.items():
            systems = self._extract_system_info(text, page_num)
            all_systems.extend(systems)

        # Remove duplicates and filter for main systems
        unique_systems = self._filter_main_systems(all_systems)

        print(f"✅ Extracted {len(unique_systems)} main FlexLink systems")
        return unique_systems

    def _extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF pages"""
        text_by_page = {}

        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_by_page[page_num + 1] = text
            doc.close()
        except Exception as e:
            print(f"⚠️  PyMuPDF failed, trying pdfplumber: {e}")
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and text.strip():
                            text_by_page[page_num + 1] = text
            except Exception as e2:
                print(f"❌ Failed to extract text: {e2}")
                return {}

        return text_by_page

    def _extract_system_info(self, text: str, page_num: int) -> List[FlexLinkSystem]:
        """Extract system information from text"""
        systems = []
        lines = text.split('\n')

        # Look for system sections
        for i, line in enumerate(lines):
            system_match = self._identify_system(line)
            if system_match:
                system_info = self._extract_detailed_system_info(
                    lines, i, page_num, system_match)
                if system_info:
                    systems.append(system_info)

        return systems

    def _identify_system(self, line: str) -> Optional[Dict[str, str]]:
        """Identify if a line contains a main FlexLink system"""
        line_lower = line.lower()

        for system_key, system_info in self.main_systems.items():
            for keyword in system_info['keywords']:
                if keyword.lower() in line_lower:
                    return {
                        'system_key': system_key,
                        'system_name': system_info['name'],
                        'category': system_info['category'],
                        'matched_keyword': keyword
                    }

        return None

    def _extract_detailed_system_info(self, lines: List[str], start_idx: int,
                                      page_num: int, system_match: Dict[str, str]) -> Optional[FlexLinkSystem]:
        """Extract detailed system information"""
        description = ""
        key_features = []
        applications = []
        advantages = []
        technical_specs = {}
        materials = []

        # Extract information from surrounding lines
        for i in range(max(0, start_idx - 5), min(len(lines), start_idx + 20)):
            line = lines[i].strip()
            if not line:
                continue

            # Extract description
            if not description and len(line) > 30 and not any(keyword in line.lower() for keyword in ['page', 'chapter', 'section']):
                description = line

            # Extract features
            if any(keyword in line.lower() for keyword in ['feature', 'characteristic', 'capability', 'benefit']):
                key_features.append(line)

            # Extract applications
            if any(keyword in line.lower() for keyword in ['application', 'use', 'suitable for', 'designed for']):
                applications.append(line)

            # Extract advantages
            if any(keyword in line.lower() for keyword in ['advantage', 'benefit', 'advantageous', 'superior']):
                advantages.append(line)

            # Extract technical specifications
            spec_patterns = [
                r'(\w+)\s*:\s*([\d\.]+)\s*(mm|kg|m|N|W|V|A|Hz)',
                r'(\w+)\s*=\s*([\d\.]+)\s*(mm|kg|m|N|W|V|A|Hz)',
                r'([A-Za-z\s]+)\s*([\d\.]+)\s*(mm|kg|m|N|W|V|A|Hz)'
            ]

            for pattern in spec_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    spec_name = match[0].strip()
                    spec_value = match[1]
                    spec_unit = match[2]
                    technical_specs[f"{spec_name} ({spec_unit})"] = f"{spec_value} {spec_unit}"

            # Extract materials
            material_keywords = [
                'aluminium', 'steel', 'stainless steel', 'plastic', 'nylon', 'polyethylene']
            for material in material_keywords:
                if material in line.lower():
                    materials.append(material.title())

        return FlexLinkSystem(
            system_name=system_match['system_name'],
            system_code=system_match['system_key'],
            category=system_match['category'],
            description=description,
            key_features=key_features,
            applications=applications,
            advantages=advantages,
            technical_specs=technical_specs,
            materials=materials,
            page_reference=page_num
        )

    def _filter_main_systems(self, systems: List[FlexLinkSystem]) -> List[FlexLinkSystem]:
        """Filter and deduplicate main systems"""
        seen = set()
        unique_systems = []

        for system in systems:
            # Create unique key
            key = f"{system.system_code}_{system.page_reference}"

            if key not in seen:
                seen.add(key)
                unique_systems.append(system)

        return unique_systems

    def create_comparison_matrix(self, systems: List[FlexLinkSystem]) -> Dict[str, Any]:
        """Create a detailed comparison matrix"""
        matrix = {
            'systems': [],
            'categories': {},
            'summary': {
                'total_systems': len(systems),
                'categories': list(set(system.category for system in systems))
            }
        }

        # Group by category
        for system in systems:
            if system.category not in matrix['categories']:
                matrix['categories'][system.category] = []

            matrix['categories'][system.category].append({
                'name': system.system_name,
                'code': system.system_code,
                'description': system.description,
                'features_count': len(system.key_features),
                'applications_count': len(system.applications),
                'advantages_count': len(system.advantages),
                'specs_count': len(system.technical_specs),
                'materials': system.materials,
                'page': system.page_reference
            })

        return matrix

    def generate_detailed_summaries(self, systems: List[FlexLinkSystem]) -> str:
        """Generate detailed system summaries"""
        markdown = "# FlexLink Main System Summaries\n\n"
        markdown += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown += f"Total main systems analyzed: {len(systems)}\n\n"

        # Group by category
        categories = {}
        for system in systems:
            if system.category not in categories:
                categories[system.category] = []
            categories[system.category].append(system)

        for category, category_systems in categories.items():
            markdown += f"## {category}\n\n"

            for i, system in enumerate(category_systems, 1):
                markdown += f"### {i}. {system.system_name}\n\n"

                if system.system_code:
                    markdown += f"**System Code:** {system.system_code}\n\n"

                if system.description:
                    markdown += f"**Description:** {system.description}\n\n"

                if system.key_features:
                    markdown += "**Key Features:**\n"
                    for feature in system.key_features:
                        markdown += f"- {feature}\n"
                    markdown += "\n"

                if system.applications:
                    markdown += "**Applications:**\n"
                    for app in system.applications:
                        markdown += f"- {app}\n"
                    markdown += "\n"

                if system.advantages:
                    markdown += "**Advantages:**\n"
                    for advantage in system.advantages:
                        markdown += f"- {advantage}\n"
                    markdown += "\n"

                if system.technical_specs:
                    markdown += "**Technical Specifications:**\n"
                    for spec_name, spec_value in system.technical_specs.items():
                        markdown += f"- {spec_name}: {spec_value}\n"
                    markdown += "\n"

                if system.materials:
                    markdown += "**Materials:**\n"
                    for material in system.materials:
                        markdown += f"- {material}\n"
                    markdown += "\n"

                if system.page_reference:
                    markdown += f"**Page Reference:** {system.page_reference}\n\n"

                markdown += "---\n\n"

        return markdown

    def save_results(self, systems: List[FlexLinkSystem], output_dir: str):
        """Save all results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_file = output_path / "main_systems.json"
        data = {
            'extraction_date': datetime.now().isoformat(),
            'total_systems': len(systems),
            'systems': [asdict(system) for system in systems]
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Save CSV matrix
        csv_file = output_path / "main_systems_matrix.csv"
        matrix = self.create_comparison_matrix(systems)

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'System Name', 'System Code', 'Description',
                             'Features Count', 'Applications Count', 'Advantages Count',
                             'Specs Count', 'Materials', 'Page'])

            for category, category_systems in matrix['categories'].items():
                for system in category_systems:
                    writer.writerow([
                        category,
                        system['name'],
                        system['code'],
                        system['description'][:100] + '...' if len(
                            system['description']) > 100 else system['description'],
                        system['features_count'],
                        system['applications_count'],
                        system['advantages_count'],
                        system['specs_count'],
                        ', '.join(system['materials']),
                        system['page']
                    ])

        # Save markdown summaries
        markdown_content = self.generate_detailed_summaries(systems)
        markdown_file = output_path / "main_systems_summaries.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"💾 Results saved to: {output_dir}")
        print(f"📄 JSON: {json_file}")
        print(f"📊 CSV: {csv_file}")
        print(f"📝 Markdown: {markdown_file}")


def main():
    """Main function to extract main FlexLink systems"""
    pdf_path = "/Users/jonashoglund/Library/CloudStorage/GoogleDrive-jonas@stixy.com/My Drive/Projects/FlexLink/06. Resources & References/Product Catalog/Product Catalogue Aluminium.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return

    # Initialize extractor
    extractor = EnhancedSystemExtractor()

    # Extract main systems
    systems = extractor.extract_main_systems(pdf_path)

    if not systems:
        print("❌ No main FlexLink systems found in the catalog")
        return

    # Save results
    output_dir = "data/main_systems_analysis"
    extractor.save_results(systems, output_dir)

    print(f"📊 Analysis complete!")
    print(f"🔍 Found {len(systems)} main FlexLink systems")


if __name__ == "__main__":
    main()
