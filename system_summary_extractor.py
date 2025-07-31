#!/usr/bin/env python3
"""
FlexLink System Summary Extractor
Extracts system summaries and creates comparison matrices from the product catalog
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
class SystemSummary:
    """Structured system summary data"""
    system_name: str
    system_code: str
    description: str
    features: List[str]
    applications: List[str]
    advantages: List[str]
    specifications: Dict[str, Any]
    page_reference: Optional[int] = None


class SystemSummaryExtractor:
    def __init__(self):
        """Initialize the system summary extractor"""
        # System identification patterns
        self.system_patterns = {
            'chain_systems': {
                'keywords': ['chain system', 'conveyor chain', 'flexible chain'],
                'system_codes': ['CS', 'Chain System']
            },
            'belt_systems': {
                'keywords': ['belt system', 'conveyor belt', 'modular belt'],
                'system_codes': ['BS', 'Belt System']
            },
            'roller_systems': {
                'keywords': ['roller system', 'roller conveyor', 'gravity roller'],
                'system_codes': ['RS', 'Roller System']
            },
            'slat_systems': {
                'keywords': ['slat system', 'slat conveyor', 'slat chain'],
                'system_codes': ['SS', 'Slat System']
            },
            'accumulation_systems': {
                'keywords': ['accumulation', 'accumulator', 'buffer'],
                'system_codes': ['AS', 'Accumulation System']
            },
            'sorting_systems': {
                'keywords': ['sorting', 'diverting', 'switching'],
                'system_codes': ['SOS', 'Sorting System']
            }
        }

    def extract_from_pdf(self, pdf_path: str) -> List[SystemSummary]:
        """Extract system summaries from PDF"""
        print(f"📖 Extracting system summaries from: {pdf_path}")

        # Extract text from PDF
        text_by_page = self._extract_text_from_pdf(pdf_path)

        # Extract system summaries
        all_systems = []
        for page_num, text in text_by_page.items():
            systems = self._extract_systems_from_text(text, page_num)
            all_systems.extend(systems)

        print(f"✅ Extracted {len(all_systems)} system summaries")
        return all_systems

    def _extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF pages"""
        text_by_page = {}

        try:
            # Try PyMuPDF first (faster for large files)
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

    def _extract_systems_from_text(self, text: str, page_num: int) -> List[SystemSummary]:
        """Extract system information from text"""
        systems = []
        lines = text.split('\n')

        # Look for system sections
        for i, line in enumerate(lines):
            # Check if this line indicates a new system
            system_info = self._detect_system_section(lines, i)
            if system_info:
                system_summary = self._extract_system_details(
                    lines, i, page_num)
                if system_summary:
                    systems.append(system_summary)

        return systems

    def _detect_system_section(self, lines: List[str], start_idx: int) -> Optional[Dict[str, str]]:
        """Detect if a line starts a new system section"""
        line = lines[start_idx].strip()

        # Look for system headers
        system_patterns = [
            r'^(\d+\.?\d*)\s*([A-Z][A-Za-z\s]+System)',
            r'^([A-Z][A-Za-z\s]+System)',
            r'^(\d+\.?\d*)\s*([A-Z][A-Za-z\s]+Chain)',
            r'^([A-Z][A-Za-z\s]+Chain)',
            r'^(\d+\.?\d*)\s*([A-Z][A-Za-z\s]+Belt)',
            r'^([A-Z][A-Za-z\s]+Belt)'
        ]

        for pattern in system_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return {
                    'system_code': match.group(1) if match.groups()[0].isdigit() else '',
                    'system_name': match.group(2) if match.groups()[0].isdigit() else match.group(1)
                }

        return None

    def _extract_system_details(self, lines: List[str], start_idx: int, page_num: int) -> Optional[SystemSummary]:
        """Extract detailed system information"""
        system_info = self._detect_system_section(lines, start_idx)
        if not system_info:
            return None

        # Extract description and features
        description = ""
        features = []
        applications = []
        advantages = []
        specifications = {}

        # Look for description in next few lines
        for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
            line = lines[i].strip()
            if not line or self._detect_system_section(lines, i):
                break

            # Extract description
            if not description and len(line) > 20:
                description = line

            # Extract features
            if any(keyword in line.lower() for keyword in ['feature', 'characteristic', 'capability']):
                features.append(line)

            # Extract applications
            if any(keyword in line.lower() for keyword in ['application', 'use', 'suitable for']):
                applications.append(line)

            # Extract advantages
            if any(keyword in line.lower() for keyword in ['advantage', 'benefit', 'advantageous']):
                advantages.append(line)

            # Extract specifications
            spec_match = re.search(r'([A-Za-z\s]+):\s*([\d\.]+)', line)
            if spec_match:
                spec_name = spec_match.group(1).strip()
                spec_value = spec_match.group(2)
                specifications[spec_name] = spec_value

        return SystemSummary(
            system_name=system_info['system_name'],
            system_code=system_info['system_code'],
            description=description,
            features=features,
            applications=applications,
            advantages=advantages,
            specifications=specifications,
            page_reference=page_num
        )

    def create_comparison_matrix(self, systems: List[SystemSummary]) -> Dict[str, Any]:
        """Create a comparison matrix for all systems"""
        matrix = {
            'systems': [],
            'comparison_data': {},
            'summary': {
                'total_systems': len(systems),
                'system_types': list(set(system.system_name for system in systems))
            }
        }

        for system in systems:
            matrix['systems'].append({
                'name': system.system_name,
                'code': system.system_code,
                'description': system.description,
                'features_count': len(system.features),
                'applications_count': len(system.applications),
                'advantages_count': len(system.advantages),
                'specifications_count': len(system.specifications),
                'page': system.page_reference
            })

        return matrix

    def save_summaries_to_json(self, systems: List[SystemSummary], output_file: str):
        """Save system summaries to JSON file"""
        data = {
            'extraction_date': datetime.now().isoformat(),
            'total_systems': len(systems),
            'systems': [asdict(system) for system in systems]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(systems)} system summaries to {output_file}")

    def save_matrix_to_csv(self, matrix: Dict[str, Any], output_file: str):
        """Save comparison matrix to CSV file"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['System Name', 'System Code', 'Description', 'Features Count',
                             'Applications Count', 'Advantages Count', 'Specifications Count', 'Page'])

            # Write data
            for system in matrix['systems']:
                writer.writerow([
                    system['name'],
                    system['code'],
                    system['description'][:100] +
                    '...' if len(system['description']
                                 ) > 100 else system['description'],
                    system['features_count'],
                    system['applications_count'],
                    system['advantages_count'],
                    system['specifications_count'],
                    system['page']
                ])

        print(f"💾 Saved comparison matrix to {output_file}")

    def generate_detailed_summaries(self, systems: List[SystemSummary]) -> str:
        """Generate detailed system summaries in markdown format"""
        markdown = "# FlexLink System Summaries\n\n"
        markdown += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown += f"Total systems analyzed: {len(systems)}\n\n"

        for i, system in enumerate(systems, 1):
            markdown += f"## {i}. {system.system_name}\n\n"

            if system.system_code:
                markdown += f"**System Code:** {system.system_code}\n\n"

            if system.description:
                markdown += f"**Description:** {system.description}\n\n"

            if system.features:
                markdown += "**Key Features:**\n"
                for feature in system.features:
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

            if system.specifications:
                markdown += "**Specifications:**\n"
                for spec_name, spec_value in system.specifications.items():
                    markdown += f"- {spec_name}: {spec_value}\n"
                markdown += "\n"

            if system.page_reference:
                markdown += f"**Page Reference:** {system.page_reference}\n\n"

            markdown += "---\n\n"

        return markdown


def main():
    """Main function to extract system summaries from the catalog"""
    pdf_path = "/Users/jonashoglund/Library/CloudStorage/GoogleDrive-jonas@stixy.com/My Drive/Projects/FlexLink/06. Resources & References/Product Catalog/Product Catalogue Aluminium.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return

    # Initialize extractor
    extractor = SystemSummaryExtractor()

    # Extract system summaries
    systems = extractor.extract_from_pdf(pdf_path)

    if not systems:
        print("❌ No systems found in the catalog")
        return

    # Create comparison matrix
    matrix = extractor.create_comparison_matrix(systems)

    # Save results
    output_dir = Path("data/system_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON summaries
    json_file = output_dir / "system_summaries.json"
    extractor.save_summaries_to_json(systems, str(json_file))

    # Save CSV matrix
    csv_file = output_dir / "system_comparison_matrix.csv"
    extractor.save_matrix_to_csv(matrix, str(csv_file))

    # Generate detailed markdown summaries
    markdown_content = extractor.generate_detailed_summaries(systems)
    markdown_file = output_dir / "system_summaries.md"
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"📊 Analysis complete!")
    print(f"📁 Results saved to: {output_dir}")
    print(f"📄 JSON summaries: {json_file}")
    print(f"📊 CSV matrix: {csv_file}")
    print(f"📝 Markdown summaries: {markdown_file}")


if __name__ == "__main__":
    main()
