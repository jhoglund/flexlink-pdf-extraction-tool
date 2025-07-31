#!/usr/bin/env python3
"""
All Six Tables Analysis Script
Analyzes all 6 tables: component_specifications, components, conveyor_systems, product_images, system_compatibility, systems
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


class AllSixTablesAnalyzer:
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

    def analyze_all_six_tables(self) -> Dict[str, Any]:
        """Analyze all 6 tables from the image"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        # All 6 tables from the image
        all_tables = [
            'component_specifications',
            'components',
            'conveyor_systems',
            'product_images',
            'system_compatibility',
            'systems'
        ]

        table_analyses = {}

        for table in all_tables:
            print(f"📊 Analyzing table: {table}")
            analysis = self.analyze_table_structure(table)
            table_analyses[table] = analysis

            if analysis.get('exists', False):
                print(
                    f"✅ {table}: {analysis['row_count']} rows, {len(analysis['columns'])} columns")
            else:
                print(f"❌ {table}: {analysis.get('error', 'Not found')}")

        return table_analyses

    def analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Analyze the structure and content of a table"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get table data with limit to avoid timeouts
            response = self.supabase.table(
                table_name).select('*').limit(100).execute()

            if not response.data:
                return {
                    'table_name': table_name,
                    'exists': True,
                    'row_count': 0,
                    'columns': [],
                    'sample_data': [],
                    'status': 'empty'
                }

            # Get column names from first row
            columns = list(response.data[0].keys()) if response.data else []

            # Get total row count (approximate)
            try:
                count_response = self.supabase.table(
                    table_name).select('*', count='exact').execute()
                row_count = count_response.count if hasattr(
                    count_response, 'count') else len(response.data)
            except:
                row_count = len(response.data)  # Fallback

            return {
                'table_name': table_name,
                'exists': True,
                'row_count': row_count,
                'columns': columns,
                'sample_data': response.data[:3],  # First 3 rows as sample
                'status': 'active'
            }

        except Exception as e:
            return {
                'table_name': table_name,
                'exists': False,
                'error': str(e),
                'status': 'error'
            }

    def analyze_table_relationships(self) -> Dict[str, Any]:
        """Analyze relationships between all 6 tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            relationships = {}

            # Check for common columns across all 6 tables
            all_tables = [
                'component_specifications',
                'components',
                'conveyor_systems',
                'product_images',
                'system_compatibility',
                'systems'
            ]
            table_columns = {}

            for table in all_tables:
                try:
                    response = self.supabase.table(
                        table).select('*').limit(1).execute()
                    if response.data:
                        table_columns[table] = list(response.data[0].keys())
                except:
                    pass

            # Find common columns
            all_columns = set()
            for columns in table_columns.values():
                all_columns.update(columns)

            common_columns = {}
            for column in all_columns:
                tables_with_column = [
                    table for table, columns in table_columns.items() if column in columns]
                if len(tables_with_column) > 1:
                    common_columns[column] = tables_with_column

            # Check for foreign key relationships
            foreign_key_analysis = {}
            for table in all_tables:
                try:
                    response = self.supabase.table(
                        table).select('*').limit(10).execute()
                    if response.data:
                        sample_row = response.data[0]
                        potential_foreign_keys = []

                        for column in sample_row.keys():
                            # Look for potential foreign key patterns
                            if any(keyword in column.lower() for keyword in ['id', 'code', 'system', 'component', 'product', 'conveyor', 'compatibility']):
                                potential_foreign_keys.append(column)

                        if potential_foreign_keys:
                            foreign_key_analysis[table] = {
                                'potential_foreign_keys': potential_foreign_keys,
                                'sample_values': {fk: sample_row.get(fk) for fk in potential_foreign_keys}
                            }
                except:
                    pass

            return {
                'common_columns': common_columns,
                'foreign_key_analysis': foreign_key_analysis,
                'table_columns': table_columns
            }

        except Exception as e:
            return {'error': f'Relationship analysis failed: {e}'}

    def analyze_data_overlap(self) -> Dict[str, Any]:
        """Analyze potential data overlap between all 6 tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            overlap_analysis = {}

            # Check for duplicate data patterns across all 6 tables
            all_tables = [
                'component_specifications',
                'components',
                'conveyor_systems',
                'product_images',
                'system_compatibility',
                'systems'
            ]

            # Check for duplicate system codes
            system_codes = {}
            for table in ['systems', 'component_specifications', 'components', 'conveyor_systems', 'system_compatibility']:
                try:
                    response = self.supabase.table(
                        table).select('system_code').execute()
                    if response.data:
                        codes = [row.get('system_code')
                                 for row in response.data if row.get('system_code')]
                        system_codes[table] = codes
                except:
                    pass

            # Find overlapping system codes
            if system_codes:
                all_codes = set()
                for codes in system_codes.values():
                    all_codes.update(codes)

                overlap_analysis['system_codes'] = {
                    'all_codes': list(all_codes),
                    'by_table': system_codes
                }

            # Check for duplicate component data
            component_overlap = {}
            for table in ['component_specifications', 'components']:
                try:
                    response = self.supabase.table(table).select('*').execute()
                    if response.data:
                        component_overlap[table] = {
                            'row_count': len(response.data),
                            'columns': list(response.data[0].keys()) if response.data else []
                        }
                except:
                    pass

            overlap_analysis['component_overlap'] = component_overlap

            # Check for conveyor system data
            conveyor_overlap = {}
            for table in ['conveyor_systems', 'systems']:
                try:
                    response = self.supabase.table(table).select('*').execute()
                    if response.data:
                        conveyor_overlap[table] = {
                            'row_count': len(response.data),
                            'columns': list(response.data[0].keys()) if response.data else []
                        }
                except:
                    pass

            overlap_analysis['conveyor_overlap'] = conveyor_overlap

            return overlap_analysis

        except Exception as e:
            return {'error': f'Overlap analysis failed: {e}'}

    def categorize_tables(self, table_analyses: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize tables by their purpose"""
        categories = {
            'system_data': [],
            'component_data': [],
            'conveyor_data': [],
            'image_data': [],
            'compatibility_data': [],
            'other': []
        }

        for table_name, analysis in table_analyses.items():
            if analysis.get('exists', False):
                table_lower = table_name.lower()

                if 'system' in table_lower and 'compatibility' not in table_lower:
                    categories['system_data'].append(table_name)
                elif any(keyword in table_lower for keyword in ['component', 'specification']):
                    categories['component_data'].append(table_name)
                elif 'conveyor' in table_lower:
                    categories['conveyor_data'].append(table_name)
                elif any(keyword in table_lower for keyword in ['image', 'product_image']):
                    categories['image_data'].append(table_name)
                elif 'compatibility' in table_lower:
                    categories['compatibility_data'].append(table_name)
                else:
                    categories['other'].append(table_name)

        return categories

    def generate_complete_six_tables_report(self) -> str:
        """Generate a complete analysis report for all 6 tables"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            report = "# Complete FlexLink Database Analysis - All 6 Tables\n\n"
            report += f"Generated on: {self._get_current_timestamp()}\n\n"

            # Analyze all 6 tables
            print("📊 Analyzing all 6 tables...")
            table_analyses = self.analyze_all_six_tables()

            report += "## Database Overview\n\n"
            report += f"- **Total Tables**: 6\n"
            report += f"- **Tables**: component_specifications, components, conveyor_systems, product_images, system_compatibility, systems\n\n"

            # Detailed table analysis
            report += "## Detailed Table Analysis\n\n"

            for table_name, analysis in table_analyses.items():
                if analysis.get('exists', False):
                    report += f"### {table_name}\n"
                    report += f"- **Status**: ✅ Active\n"
                    report += f"- **Row Count**: {analysis['row_count']}\n"
                    report += f"- **Columns**: {len(analysis['columns'])}\n"
                    if analysis['columns']:
                        report += f"- **Column Names**: {', '.join(analysis['columns'][:8])}{'...' if len(analysis['columns']) > 8 else ''}\n"
                    report += "\n"
                else:
                    report += f"### {table_name}\n"
                    report += f"- **Status**: ❌ Error\n"
                    if 'error' in analysis:
                        report += f"- **Error**: {analysis['error']}\n"
                    report += "\n"

            # Categorize tables
            print("📂 Categorizing tables...")
            categories = self.categorize_tables(table_analyses)
            report += "## Table Categories\n\n"

            for category, tables in categories.items():
                if tables:
                    report += f"### {category.replace('_', ' ').title()}\n"
                    for table in tables:
                        analysis = table_analyses.get(table, {})
                        row_count = analysis.get('row_count', 0) if analysis.get(
                            'exists', False) else 0
                        report += f"- **{table}**: {row_count} rows\n"
                    report += "\n"

            # Analyze relationships
            print("🔗 Analyzing table relationships...")
            relationships = self.analyze_table_relationships()
            if 'error' not in relationships:
                report += "## Table Relationships\n\n"

                # Common columns
                common_columns = relationships.get('common_columns', {})
                if common_columns:
                    report += "### Common Columns Across Tables\n"
                    for column, tables in common_columns.items():
                        report += f"- **{column}**: {', '.join(tables)}\n"
                    report += "\n"

                # Foreign key analysis
                foreign_keys = relationships.get('foreign_key_analysis', {})
                if foreign_keys:
                    report += "### Potential Foreign Keys\n"
                    for table, fk_data in foreign_keys.items():
                        report += f"#### {table}\n"
                        report += f"- **Potential Foreign Keys**: {', '.join(fk_data['potential_foreign_keys'])}\n"
                    report += "\n"

            # Analyze data overlap
            print("🔄 Analyzing data overlap...")
            overlap = self.analyze_data_overlap()
            if 'error' not in overlap:
                report += "## Data Overlap Analysis\n\n"

                # System codes overlap
                system_codes = overlap.get('system_codes', {})
                if system_codes:
                    report += "### System Codes Distribution\n"
                    for table, codes in system_codes.get('by_table', {}).items():
                        report += f"- **{table}**: {len(codes)} system codes\n"
                    report += "\n"

                # Component overlap
                component_overlap = overlap.get('component_overlap', {})
                if component_overlap:
                    report += "### Component Data Overlap\n"
                    for table, data in component_overlap.items():
                        report += f"- **{table}**: {data['row_count']} rows, {len(data['columns'])} columns\n"
                    report += "\n"

                # Conveyor overlap
                conveyor_overlap = overlap.get('conveyor_overlap', {})
                if conveyor_overlap:
                    report += "### Conveyor System Data Overlap\n"
                    for table, data in conveyor_overlap.items():
                        report += f"- **{table}**: {data['row_count']} rows, {len(data['columns'])} columns\n"
                    report += "\n"

            # Recommendations
            report += "## Recommendations\n\n"

            # Check for potential redundancy
            component_tables = categories.get('component_data', [])
            if len(component_tables) > 1:
                report += "⚠️ **Multiple component tables found** - Check for redundancy between component tables\n"

            system_tables = categories.get('system_data', [])
            if len(system_tables) > 1:
                report += "⚠️ **Multiple system tables found** - Check for redundancy between system tables\n"

            conveyor_tables = categories.get('conveyor_data', [])
            if len(conveyor_tables) > 1:
                report += "⚠️ **Multiple conveyor tables found** - Check for redundancy between conveyor tables\n"

            # Check for empty tables
            empty_tables = [table for table, analysis in table_analyses.items()
                            if analysis.get('exists', False) and analysis.get('row_count', 0) == 0]
            if empty_tables:
                report += f"⚠️ **Empty tables found**: {', '.join(empty_tables)} - Consider removing\n"

            report += "\n## Summary\n\n"
            report += f"- **Total Tables**: 6\n"
            report += f"- **Active Tables**: {len([t for t, a in table_analyses.items() if a.get('exists', False)])}\n"
            report += f"- **Empty Tables**: {len(empty_tables)}\n"
            report += f"- **Categories**: {len([c for c, t in categories.items() if t])}\n"

            return report

        except Exception as e:
            return f"❌ Report generation failed: {e}"

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run_all_six_tables_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis for all 6 tables"""
        print("🔍 Starting analysis of all 6 tables...")

        results = {
            'timestamp': self._get_current_timestamp(),
            'table_analyses': {},
            'categories': {},
            'relationships': {},
            'overlap': {}
        }

        # Step 1: Analyze all 6 tables
        print("\n📊 Step 1: Analyzing all 6 tables...")
        table_analyses = self.analyze_all_six_tables()
        results['table_analyses'] = table_analyses

        # Step 2: Categorize tables
        print("\n📂 Step 2: Categorizing tables...")
        categories = self.categorize_tables(table_analyses)
        results['categories'] = categories
        for category, tables in categories.items():
            if tables:
                print(f"📁 {category}: {len(tables)} tables")

        # Step 3: Analyze relationships
        print("\n🔗 Step 3: Analyzing table relationships...")
        relationships = self.analyze_table_relationships()
        results['relationships'] = relationships
        if 'error' not in relationships:
            common_columns = relationships.get('common_columns', {})
            print(
                f"✅ Found {len(common_columns)} common columns across tables")
        else:
            print(f"❌ Relationship analysis failed: {relationships['error']}")

        # Step 4: Analyze data overlap
        print("\n🔄 Step 4: Analyzing data overlap...")
        overlap = self.analyze_data_overlap()
        results['overlap'] = overlap
        if 'error' not in overlap:
            print(f"✅ Overlap analysis complete")
        else:
            print(f"❌ Overlap analysis failed: {overlap['error']}")

        # Step 5: Generate report
        print("\n📋 Step 5: Generating complete report...")
        report = self.generate_complete_six_tables_report()
        results['report'] = report

        # Save report to file
        report_file = Path("all_six_tables_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(
            f"\n✅ Complete analysis of all 6 tables finished! Report saved to: {report_file}")

        return results


def main():
    """Main function"""
    analyzer = AllSixTablesAnalyzer()

    # Run analysis
    results = analyzer.run_all_six_tables_analysis()

    # Print summary
    print("\n" + "="*50)
    print("ALL SIX TABLES ANALYSIS SUMMARY")
    print("="*50)

    # Table summary
    table_analyses = results.get('table_analyses', {})
    active_tables = [name for name, analysis in table_analyses.items(
    ) if analysis.get('exists', False)]
    print(f"📊 Active Tables: {len(active_tables)}")
    for table in active_tables:
        analysis = table_analyses[table]
        print(
            f"  - {table}: {analysis['row_count']} rows, {len(analysis['columns'])} columns")

    # Category summary
    categories = results.get('categories', {})
    for category, tables in categories.items():
        if tables:
            print(
                f"\n📁 {category.replace('_', ' ').title()}: {len(tables)} tables")
            for table in tables:
                analysis = table_analyses.get(table, {})
                row_count = analysis.get('row_count', 0) if analysis.get(
                    'exists', False) else 0
                print(f"  - {table}: {row_count} rows")

    # Relationship summary
    relationships = results.get('relationships', {})
    if 'error' not in relationships:
        common_columns = relationships.get('common_columns', {})
        print(f"\n🔗 Common Columns: {len(common_columns)}")
        for column, tables in common_columns.items():
            print(f"  - {column}: {', '.join(tables)}")

    print("="*50)


if __name__ == "__main__":
    main()
