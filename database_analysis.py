#!/usr/bin/env python3
"""
Database Analysis Script
Analyzes all tables in the FlexLink database to identify duplicates and unnecessary data
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


class DatabaseAnalyzer:
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

    def get_all_tables(self) -> List[str]:
        """Get all table names from the database"""
        if not self.supabase:
            return []

        try:
            # Query information_schema to get all tables
            response = self.supabase.rpc('get_all_tables').execute()
            if response.data:
                return [table['table_name'] for table in response.data]

            # Fallback: try to query each known table
            known_tables = [
                'systems', 'component_specifications', 'products',
                'images', 'extracted_images', 'system_components'
            ]

            existing_tables = []
            for table in known_tables:
                try:
                    response = self.supabase.table(
                        table).select('*').limit(1).execute()
                    existing_tables.append(table)
                except:
                    pass

            return existing_tables

        except Exception as e:
            print(f"❌ Error getting tables: {e}")
            return []

    def analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Analyze the structure and content of a table"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get table structure
            response = self.supabase.table(
                table_name).select('*').limit(10).execute()

            if not response.data:
                return {
                    'table_name': table_name,
                    'row_count': 0,
                    'columns': [],
                    'sample_data': [],
                    'status': 'empty'
                }

            # Get column names from first row
            columns = list(response.data[0].keys()) if response.data else []

            # Get total row count
            count_response = self.supabase.table(
                table_name).select('*', count='exact').execute()
            row_count = count_response.count if hasattr(
                count_response, 'count') else len(response.data)

            return {
                'table_name': table_name,
                'row_count': row_count,
                'columns': columns,
                'sample_data': response.data[:3],  # First 3 rows as sample
                'status': 'active'
            }

        except Exception as e:
            return {
                'table_name': table_name,
                'error': str(e),
                'status': 'error'
            }

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
                'system_code, component_type, component_name').execute()
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

            # Check for duplicate system codes
            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            system_codes = [row['system_code']
                            for row in systems_response.data]
            duplicate_system_codes = [code for code in set(
                system_codes) if system_codes.count(code) > 1]

            if duplicate_system_codes:
                duplicates['system_codes'] = duplicate_system_codes

            # Check for duplicate component names
            components_response = self.supabase.table('component_specifications').select(
                'component_name, system_code').execute()
            component_names = [(row['component_name'], row['system_code'])
                               for row in components_response.data if row.get('component_name')]
            duplicate_components = []

            for name, sys_code in component_names:
                if component_names.count((name, sys_code)) > 1:
                    duplicate_components.append((name, sys_code))

            if duplicate_components:
                duplicates['component_names'] = list(set(duplicate_components))

            return {
                'duplicate_system_codes': len(duplicate_system_codes),
                'duplicate_component_names': len(set(duplicate_components)),
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

    def generate_analysis_report(self) -> str:
        """Generate a comprehensive analysis report"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            report = "# FlexLink Database Analysis Report\n\n"
            report += f"Generated on: {self._get_current_timestamp()}\n\n"

            # Get all tables
            tables = self.get_all_tables()
            report += f"## Database Overview\n\n"
            report += f"- **Total Tables Found**: {len(tables)}\n"
            report += f"- **Tables**: {', '.join(tables) if tables else 'None found'}\n\n"

            # Analyze each table
            report += "## Table Analysis\n\n"
            table_analyses = {}

            for table in tables:
                analysis = self.analyze_table_structure(table)
                table_analyses[table] = analysis

                if 'error' in analysis:
                    report += f"### {table}\n"
                    report += f"- **Status**: ❌ Error - {analysis['error']}\n\n"
                else:
                    report += f"### {table}\n"
                    report += f"- **Status**: ✅ Active\n"
                    report += f"- **Row Count**: {analysis['row_count']}\n"
                    report += f"- **Columns**: {len(analysis['columns'])}\n"
                    report += f"- **Column Names**: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}\n\n"

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
                report += f"- **Duplicate System Codes**: {duplicate_analysis['duplicate_system_codes']}\n"
                report += f"- **Duplicate Component Names**: {duplicate_analysis['duplicate_component_names']}\n\n"

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

            # Recommendations
            report += "## Recommendations\n\n"

            # Check if all tables are needed
            if 'systems' in tables and 'component_specifications' in tables:
                overlap_count = overlap_analysis.get('overlap_count', 0)
                if overlap_count > 0:
                    report += "✅ **Systems and Components tables are complementary** - Both contain valuable data\n"
                else:
                    report += "⚠️ **Potential redundancy** - Systems and Components tables may have overlapping data\n"

            if duplicate_analysis.get('duplicate_system_codes', 0) > 0:
                report += "❌ **Duplicate system codes found** - Consider cleaning up duplicates\n"

            if duplicate_analysis.get('duplicate_component_names', 0) > 0:
                report += "❌ **Duplicate component names found** - Consider cleaning up duplicates\n"

            if relationship_analysis.get('orphaned_components', []):
                report += "⚠️ **Orphaned components found** - Components reference non-existent systems\n"

            if relationship_analysis.get('unused_systems', []):
                report += "ℹ️ **Unused systems found** - Systems without components (may be intentional)\n"

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
            'tables': self.get_all_tables(),
            'table_analyses': {},
            'overlap_analysis': {},
            'duplicate_analysis': {},
            'relationship_analysis': {}
        }

        # Analyze each table
        print("\n📊 Step 1: Analyzing table structures...")
        for table in results['tables']:
            analysis = self.analyze_table_structure(table)
            results['table_analyses'][table] = analysis
            if 'error' not in analysis:
                print(
                    f"✅ {table}: {analysis['row_count']} rows, {len(analysis['columns'])} columns")
            else:
                print(f"❌ {table}: {analysis['error']}")

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

        # Generate report
        print("\n📋 Step 5: Generating analysis report...")
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
    analyzer = DatabaseAnalyzer()

    # Run analysis
    results = analyzer.run_full_analysis()

    # Print summary
    print("\n" + "="*50)
    print("DATABASE ANALYSIS SUMMARY")
    print("="*50)

    print(f"📊 Tables Found: {len(results['tables'])}")
    for table in results['tables']:
        analysis = results['table_analyses'].get(table, {})
        if 'row_count' in analysis:
            print(f"  - {table}: {analysis['row_count']} rows")

    if 'overlap_analysis' in results and 'error' not in results['overlap_analysis']:
        overlap = results['overlap_analysis']
        print(
            f"\n🔄 System Overlap: {overlap['overlap_count']} overlapping systems")
        print(f"  - Systems only: {overlap['systems_only_count']}")
        print(f"  - Components only: {overlap['components_only_count']}")

    if 'duplicate_analysis' in results and 'error' not in results['duplicate_analysis']:
        duplicates = results['duplicate_analysis']
        print(f"\n🔍 Duplicates Found:")
        print(f"  - System codes: {duplicates['duplicate_system_codes']}")
        print(
            f"  - Component names: {duplicates['duplicate_component_names']}")

    if 'relationship_analysis' in results and 'error' not in results['relationship_analysis']:
        relationships = results['relationship_analysis']
        print(f"\n🔗 Relationships:")
        print(f"  - Valid: {relationships['valid_relationships']}")
        print(
            f"  - Orphaned components: {len(relationships['orphaned_components'])}")
        print(f"  - Unused systems: {len(relationships['unused_systems'])}")

    print("="*50)


if __name__ == "__main__":
    main()
