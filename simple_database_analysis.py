#!/usr/bin/env python3
"""
Simple Database Analysis Script
Analyzes tables in the FlexLink database to identify duplicates and unnecessary data
"""

import os
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Run: pip install supabase")


class SimpleDatabaseAnalyzer:
    def __init__(self):
        """Initialize the database analyzer"""
        load_dotenv()

        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

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
            print("⚠️  Supabase not configured or not available")

    def analyze_known_tables(self) -> Dict[str, Any]:
        """Analyze the known tables in the database"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        tables_analysis = {}
        known_tables = ['systems', 'component_specifications',
                        'images', 'extracted_images']

        for table in known_tables:
            try:
                # Get table data
                response = self.supabase.table(table).select('*').execute()

                if response.data:
                    # Get column names from first row
                    columns = list(
                        response.data[0].keys()) if response.data else []

                    tables_analysis[table] = {
                        'exists': True,
                        'row_count': len(response.data),
                        'columns': columns,
                        # First 2 rows as sample
                        'sample_data': response.data[:2]
                    }
                else:
                    tables_analysis[table] = {
                        'exists': True,
                        'row_count': 0,
                        'columns': [],
                        'sample_data': []
                    }

            except Exception as e:
                tables_analysis[table] = {
                    'exists': False,
                    'error': str(e)
                }

        return tables_analysis

    def analyze_system_data_overlap(self) -> Dict[str, Any]:
        """Analyze overlap between systems and component_specifications tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get systems data
            systems_response = self.supabase.table('systems').select(
                'system_code, system_name, category').execute()
            systems_data = systems_response.data

            # Get component_specifications data
            components_response = self.supabase.table('component_specifications').select(
                'system_code, component_type').execute()
            components_data = components_response.data

            # Analyze overlap
            system_codes_in_systems = set(
                sys['system_code'] for sys in systems_data)
            system_codes_in_components = set(
                comp['system_code'] for comp in components_data if comp.get('system_code'))

            overlap = system_codes_in_systems.intersection(
                system_codes_in_components)
            only_in_systems = system_codes_in_systems - system_codes_in_components
            only_in_components = system_codes_in_components - system_codes_in_systems

            return {
                'systems_table_count': len(systems_data),
                'components_table_count': len(components_data),
                'overlapping_systems': list(overlap),
                'only_in_systems': list(only_in_systems),
                'only_in_components': list(only_in_components),
                'overlap_count': len(overlap),
                'systems_only_count': len(only_in_systems),
                'components_only_count': len(only_in_components)
            }

        except Exception as e:
            return {'error': f'Analysis failed: {e}'}

    def check_for_duplicate_data(self) -> Dict[str, Any]:
        """Check for duplicate data across tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            duplicates = {}

            # Check for duplicate system codes in systems table
            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            system_codes = [row['system_code']
                            for row in systems_response.data]
            duplicate_system_codes = [code for code in set(
                system_codes) if system_codes.count(code) > 1]

            if duplicate_system_codes:
                duplicates['system_codes'] = duplicate_system_codes

            # Check for duplicate system codes in component_specifications table
            components_response = self.supabase.table('component_specifications').select(
                'system_code, component_type').execute()
            component_system_codes = [
                row['system_code'] for row in components_response.data if row.get('system_code')]
            duplicate_component_system_codes = [code for code in set(
                component_system_codes) if component_system_codes.count(code) > 1]

            if duplicate_component_system_codes:
                duplicates['component_system_codes'] = duplicate_component_system_codes

            return {
                'duplicate_system_codes': len(duplicate_system_codes),
                'duplicate_component_system_codes': len(duplicate_component_system_codes),
                'duplicates': duplicates
            }

        except Exception as e:
            return {'error': f'Duplicate check failed: {e}'}

    def analyze_table_relationships(self) -> Dict[str, Any]:
        """Analyze relationships between tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            relationships = {}

            # Check if component_specifications references systems
            components_response = self.supabase.table(
                'component_specifications').select('system_code').execute()
            component_systems = set(
                row['system_code'] for row in components_response.data if row.get('system_code'))

            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            system_codes = set(row['system_code']
                               for row in systems_response.data)

            # Check foreign key relationships
            orphaned_components = component_systems - system_codes
            unused_systems = system_codes - component_systems

            relationships['orphaned_components'] = list(orphaned_components)
            relationships['unused_systems'] = list(unused_systems)
            relationships['valid_relationships'] = len(
                component_systems.intersection(system_codes))

            return relationships

        except Exception as e:
            return {'error': f'Relationship analysis failed: {e}'}

    def analyze_image_tables(self) -> Dict[str, Any]:
        """Analyze image-related tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            image_analysis = {}

            # Check images table
            try:
                images_response = self.supabase.table(
                    'images').select('*').execute()
                image_analysis['images_table'] = {
                    'exists': True,
                    'row_count': len(images_response.data),
                    'columns': list(images_response.data[0].keys()) if images_response.data else []
                }
            except Exception as e:
                image_analysis['images_table'] = {
                    'exists': False,
                    'error': str(e)
                }

            # Check extracted_images table
            try:
                extracted_images_response = self.supabase.table(
                    'extracted_images').select('*').execute()
                image_analysis['extracted_images_table'] = {
                    'exists': True,
                    'row_count': len(extracted_images_response.data),
                    'columns': list(extracted_images_response.data[0].keys()) if extracted_images_response.data else []
                }
            except Exception as e:
                image_analysis['extracted_images_table'] = {
                    'exists': False,
                    'error': str(e)
                }

            return image_analysis

        except Exception as e:
            return {'error': f'Image analysis failed: {e}'}

    def generate_analysis_report(self) -> str:
        """Generate a comprehensive analysis report"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            report = "# FlexLink Database Analysis Report\n\n"
            report += f"Generated on: {self._get_current_timestamp()}\n\n"

            # Analyze known tables
            tables_analysis = self.analyze_known_tables()
            report += "## Table Analysis\n\n"

            for table_name, analysis in tables_analysis.items():
                if analysis.get('exists', False):
                    report += f"### {table_name}\n"
                    report += f"- **Status**: ✅ Active\n"
                    report += f"- **Row Count**: {analysis['row_count']}\n"
                    report += f"- **Columns**: {len(analysis['columns'])}\n"
                    if analysis['columns']:
                        report += f"- **Column Names**: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}\n"
                    report += "\n"
                else:
                    report += f"### {table_name}\n"
                    report += f"- **Status**: ❌ Not found or error\n"
                    if 'error' in analysis:
                        report += f"- **Error**: {analysis['error']}\n"
                    report += "\n"

            # Analyze system data overlap
            report += "## System Data Overlap Analysis\n\n"
            overlap_analysis = self.analyze_system_data_overlap()

            if 'error' in overlap_analysis:
                report += f"❌ Overlap analysis failed: {overlap_analysis['error']}\n\n"
            else:
                report += f"- **Systems in Systems Table**: {overlap_analysis['systems_table_count']}\n"
                report += f"- **Components in Components Table**: {overlap_analysis['components_table_count']}\n"
                report += f"- **Overlapping Systems**: {overlap_analysis['overlap_count']}\n"
                report += f"- **Systems Only**: {overlap_analysis['systems_only_count']}\n"
                report += f"- **Components Only**: {overlap_analysis['components_only_count']}\n\n"

                if overlap_analysis['only_in_systems']:
                    report += f"**Systems only in systems table**: {', '.join(overlap_analysis['only_in_systems'])}\n\n"
                if overlap_analysis['only_in_components']:
                    report += f"**Systems only in components table**: {', '.join(overlap_analysis['only_in_components'])}\n\n"

            # Check for duplicates
            report += "## Duplicate Data Analysis\n\n"
            duplicate_analysis = self.check_for_duplicate_data()

            if 'error' in duplicate_analysis:
                report += f"❌ Duplicate analysis failed: {duplicate_analysis['error']}\n\n"
            else:
                report += f"- **Duplicate System Codes (Systems Table)**: {duplicate_analysis['duplicate_system_codes']}\n"
                report += f"- **Duplicate System Codes (Components Table)**: {duplicate_analysis['duplicate_component_system_codes']}\n\n"

                if duplicate_analysis['duplicates']:
                    report += "**Found Duplicates**:\n"
                    for dup_type, dup_data in duplicate_analysis['duplicates'].items():
                        report += f"- {dup_type}: {dup_data}\n"
                    report += "\n"

            # Analyze relationships
            report += "## Table Relationships Analysis\n\n"
            relationship_analysis = self.analyze_table_relationships()

            if 'error' in relationship_analysis:
                report += f"❌ Relationship analysis failed: {relationship_analysis['error']}\n\n"
            else:
                report += f"- **Valid Relationships**: {relationship_analysis['valid_relationships']}\n"
                report += f"- **Orphaned Components**: {len(relationship_analysis['orphaned_components'])}\n"
                report += f"- **Unused Systems**: {len(relationship_analysis['unused_systems'])}\n\n"

                if relationship_analysis['orphaned_components']:
                    report += f"**Orphaned Components**: {', '.join(relationship_analysis['orphaned_components'])}\n\n"
                if relationship_analysis['unused_systems']:
                    report += f"**Unused Systems**: {', '.join(relationship_analysis['unused_systems'])}\n\n"

            # Analyze image tables
            report += "## Image Tables Analysis\n\n"
            image_analysis = self.analyze_image_tables()

            if 'error' in image_analysis:
                report += f"❌ Image analysis failed: {image_analysis['error']}\n\n"
            else:
                for table_name, analysis in image_analysis.items():
                    if analysis.get('exists', False):
                        report += f"### {table_name}\n"
                        report += f"- **Status**: ✅ Active\n"
                        report += f"- **Row Count**: {analysis['row_count']}\n"
                        report += f"- **Columns**: {len(analysis['columns'])}\n"
                        if analysis['columns']:
                            report += f"- **Column Names**: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}\n"
                        report += "\n"
                    else:
                        report += f"### {table_name}\n"
                        report += f"- **Status**: ❌ Not found or error\n"
                        if 'error' in analysis:
                            report += f"- **Error**: {analysis['error']}\n"
                        report += "\n"

            # Recommendations
            report += "## Recommendations\n\n"

            # Check if all tables are needed
            systems_exists = tables_analysis.get(
                'systems', {}).get('exists', False)
            components_exists = tables_analysis.get(
                'component_specifications', {}).get('exists', False)

            if systems_exists and components_exists:
                overlap_count = overlap_analysis.get('overlap_count', 0)
                if overlap_count > 0:
                    report += "✅ **Systems and Components tables are complementary** - Both contain valuable data\n"
                else:
                    report += "⚠️ **Potential redundancy** - Systems and Components tables may have overlapping data\n"

            if duplicate_analysis.get('duplicate_system_codes', 0) > 0:
                report += "❌ **Duplicate system codes found** - Consider cleaning up duplicates\n"

            if relationship_analysis.get('orphaned_components', []):
                report += "⚠️ **Orphaned components found** - Components reference non-existent systems\n"

            if relationship_analysis.get('unused_systems', []):
                report += "ℹ️ **Unused systems found** - Systems without components (may be intentional)\n"

            # Check for redundant image tables
            images_exists = image_analysis.get(
                'images_table', {}).get('exists', False)
            extracted_images_exists = image_analysis.get(
                'extracted_images_table', {}).get('exists', False)

            if images_exists and extracted_images_exists:
                images_count = image_analysis['images_table']['row_count']
                extracted_count = image_analysis['extracted_images_table']['row_count']
                if images_count > 0 and extracted_count > 0:
                    report += "⚠️ **Multiple image tables found** - Consider consolidating image data\n"

            return report

        except Exception as e:
            return f"❌ Report generation failed: {e}"

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run the complete database analysis"""
        print("🔍 Starting comprehensive database analysis...")

        results = {
            'timestamp': self._get_current_timestamp(),
            'table_analyses': {},
            'overlap_analysis': {},
            'duplicate_analysis': {},
            'relationship_analysis': {},
            'image_analysis': {}
        }

        # Analyze known tables
        print("\n📊 Step 1: Analyzing table structures...")
        tables_analysis = self.analyze_known_tables()
        results['table_analyses'] = tables_analysis

        for table_name, analysis in tables_analysis.items():
            if analysis.get('exists', False):
                print(
                    f"✅ {table_name}: {analysis['row_count']} rows, {len(analysis['columns'])} columns")
            else:
                print(f"❌ {table_name}: {analysis.get('error', 'Not found')}")

        # Analyze system data overlap
        print("\n🔄 Step 2: Analyzing system data overlap...")
        overlap_analysis = self.analyze_system_data_overlap()
        results['overlap_analysis'] = overlap_analysis
        if 'error' not in overlap_analysis:
            print(
                f"✅ Overlap analysis: {overlap_analysis['overlap_count']} overlapping systems")
        else:
            print(f"❌ Overlap analysis failed: {overlap_analysis['error']}")

        # Check for duplicates
        print("\n🔍 Step 3: Checking for duplicate data...")
        duplicate_analysis = self.check_for_duplicate_data()
        results['duplicate_analysis'] = duplicate_analysis
        if 'error' not in duplicate_analysis:
            print(
                f"✅ Duplicate check: {duplicate_analysis['duplicate_system_codes']} duplicate system codes")
        else:
            print(f"❌ Duplicate check failed: {duplicate_analysis['error']}")

        # Analyze relationships
        print("\n🔗 Step 4: Analyzing table relationships...")
        relationship_analysis = self.analyze_table_relationships()
        results['relationship_analysis'] = relationship_analysis
        if 'error' not in relationship_analysis:
            print(
                f"✅ Relationship analysis: {relationship_analysis['valid_relationships']} valid relationships")
        else:
            print(
                f"❌ Relationship analysis failed: {relationship_analysis['error']}")

        # Analyze image tables
        print("\n🖼️ Step 5: Analyzing image tables...")
        image_analysis = self.analyze_image_tables()
        results['image_analysis'] = image_analysis
        if 'error' not in image_analysis:
            for table_name, analysis in image_analysis.items():
                if analysis.get('exists', False):
                    print(f"✅ {table_name}: {analysis['row_count']} rows")
                else:
                    print(
                        f"❌ {table_name}: {analysis.get('error', 'Not found')}")
        else:
            print(f"❌ Image analysis failed: {image_analysis['error']}")

        # Generate report
        print("\n📋 Step 6: Generating analysis report...")
        report = self.generate_analysis_report()
        results['report'] = report

        # Save report to file
        report_file = Path("database_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Analysis complete! Report saved to: {report_file}")

        return results


def main():
    """Main function"""
    analyzer = SimpleDatabaseAnalyzer()

    # Run analysis
    results = analyzer.run_full_analysis()

    # Print summary
    print("\n" + "="*50)
    print("DATABASE ANALYSIS SUMMARY")
    print("="*50)

    # Table summary
    tables = results.get('table_analyses', {})
    active_tables = [name for name, analysis in tables.items()
                     if analysis.get('exists', False)]
    print(f"📊 Active Tables: {len(active_tables)}")
    for table in active_tables:
        analysis = tables[table]
        print(f"  - {table}: {analysis['row_count']} rows")

    # Overlap summary
    if 'overlap_analysis' in results and 'error' not in results['overlap_analysis']:
        overlap = results['overlap_analysis']
        print(
            f"\n🔄 System Overlap: {overlap['overlap_count']} overlapping systems")
        print(f"  - Systems only: {overlap['systems_only_count']}")
        print(f"  - Components only: {overlap['components_only_count']}")

    # Duplicate summary
    if 'duplicate_analysis' in results and 'error' not in results['duplicate_analysis']:
        duplicates = results['duplicate_analysis']
        print(f"\n🔍 Duplicates Found:")
        print(f"  - System codes: {duplicates['duplicate_system_codes']}")
        print(
            f"  - Component system codes: {duplicates['duplicate_component_system_codes']}")

    # Relationship summary
    if 'relationship_analysis' in results and 'error' not in results['relationship_analysis']:
        relationships = results['relationship_analysis']
        print(f"\n🔗 Relationships:")
        print(f"  - Valid: {relationships['valid_relationships']}")
        print(
            f"  - Orphaned components: {len(relationships['orphaned_components'])}")
        print(f"  - Unused systems: {len(relationships['unused_systems'])}")

    # Image tables summary
    if 'image_analysis' in results and 'error' not in results['image_analysis']:
        images = results['image_analysis']
        print(f"\n🖼️ Image Tables:")
        for table_name, analysis in images.items():
            if analysis.get('exists', False):
                print(f"  - {table_name}: {analysis['row_count']} rows")

    print("="*50)


if __name__ == "__main__":
    main()
