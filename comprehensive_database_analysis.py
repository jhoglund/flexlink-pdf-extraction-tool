#!/usr/bin/env python3
"""
Comprehensive Database Analysis Script
Discovers and analyzes ALL tables in the FlexLink database
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


class ComprehensiveDatabaseAnalyzer:
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

    def discover_all_tables(self) -> List[str]:
        """Discover all tables in the database"""
        if not self.supabase:
            return []

        try:
            # Try to get all tables using information_schema
            response = self.supabase.rpc('get_all_tables').execute()
            if response.data:
                return [table['table_name'] for table in response.data]

            # Fallback: try common table names and discover what exists
            common_tables = [
                'systems', 'component_specifications', 'product_images', 'images',
                'extracted_images', 'products', 'components', 'specifications',
                'system_components', 'product_specifications', 'image_metadata',
                'catalog_data', 'flexlink_systems', 'flexlink_components',
                'system_summaries', 'component_data', 'product_data',
                'catalog_images', 'extracted_data', 'system_data'
            ]

            existing_tables = []
            for table in common_tables:
                try:
                    # Try to query each table
                    response = self.supabase.table(
                        table).select('*').limit(1).execute()
                    existing_tables.append(table)
                    print(f"✅ Discovered table: {table}")
                except Exception as e:
                    # Table doesn't exist or error
                    pass

            return existing_tables

        except Exception as e:
            print(f"❌ Error discovering tables: {e}")
            return []

    def analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Analyze the structure and content of a table"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get table data (limit to avoid memory issues)
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

    def analyze_table_relationships(self, all_tables: List[str]) -> Dict[str, Any]:
        """Analyze relationships between all tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            relationships = {}

            # Check for foreign key relationships
            for table in all_tables:
                try:
                    # Get sample data to look for foreign keys
                    response = self.supabase.table(
                        table).select('*').limit(10).execute()
                    if response.data:
                        # Look for common foreign key patterns
                        sample_row = response.data[0]
                        foreign_keys = []

                        for column in sample_row.keys():
                            # Check if column might be a foreign key
                            if any(keyword in column.lower() for keyword in ['id', 'code', 'system', 'component', 'product']):
                                foreign_keys.append(column)

                        if foreign_keys:
                            relationships[table] = {
                                'potential_foreign_keys': foreign_keys,
                                'sample_values': {fk: sample_row.get(fk) for fk in foreign_keys}
                            }
                except:
                    pass

            return relationships

        except Exception as e:
            return {'error': f'Relationship analysis failed: {e}'}

    def analyze_data_overlap(self, all_tables: List[str]) -> Dict[str, Any]:
        """Analyze potential data overlap between tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            overlap_analysis = {}

            # Check for common columns across tables
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

            overlap_analysis['common_columns'] = common_columns
            overlap_analysis['table_columns'] = table_columns

            return overlap_analysis

        except Exception as e:
            return {'error': f'Overlap analysis failed: {e}'}

    def check_for_duplicates(self, all_tables: List[str]) -> Dict[str, Any]:
        """Check for duplicate data across all tables"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            duplicates = {}

            for table in all_tables:
                try:
                    # Check for duplicate primary keys or unique identifiers
                    response = self.supabase.table(
                        table).select('*').limit(100).execute()
                    if response.data:
                        # Look for ID columns
                        id_columns = [
                            col for col in response.data[0].keys() if 'id' in col.lower()]

                        for id_col in id_columns:
                            values = [row.get(id_col)
                                      for row in response.data if row.get(id_col)]
                            duplicate_values = [val for val in set(
                                values) if values.count(val) > 1]

                            if duplicate_values:
                                if table not in duplicates:
                                    duplicates[table] = {}
                                duplicates[table][id_col] = duplicate_values
                except:
                    pass

            return duplicates

        except Exception as e:
            return {'error': f'Duplicate check failed: {e}'}

    def categorize_tables(self, all_tables: List[str]) -> Dict[str, List[str]]:
        """Categorize tables by their apparent purpose"""
        categories = {
            'system_data': [],
            'component_data': [],
            'image_data': [],
            'product_data': [],
            'metadata': [],
            'other': []
        }

        for table in all_tables:
            table_lower = table.lower()

            if any(keyword in table_lower for keyword in ['system', 'systems']):
                categories['system_data'].append(table)
            elif any(keyword in table_lower for keyword in ['component', 'components', 'specification']):
                categories['component_data'].append(table)
            elif any(keyword in table_lower for keyword in ['image', 'images', 'photo', 'picture']):
                categories['image_data'].append(table)
            elif any(keyword in table_lower for keyword in ['product', 'products']):
                categories['product_data'].append(table)
            elif any(keyword in table_lower for keyword in ['meta', 'data', 'info', 'summary']):
                categories['metadata'].append(table)
            else:
                categories['other'].append(table)

        return categories

    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            report = "# Comprehensive FlexLink Database Analysis Report\n\n"
            report += f"Generated on: {self._get_current_timestamp()}\n\n"

            # Discover all tables
            print("🔍 Discovering all tables...")
            all_tables = self.discover_all_tables()
            report += f"## Database Overview\n\n"
            report += f"- **Total Tables Found**: {len(all_tables)}\n"
            report += f"- **Tables**: {', '.join(all_tables) if all_tables else 'None found'}\n\n"

            # Analyze each table
            report += "## Detailed Table Analysis\n\n"
            table_analyses = {}

            for table in all_tables:
                print(f"📊 Analyzing table: {table}")
                analysis = self.analyze_table_structure(table)
                table_analyses[table] = analysis

                if analysis.get('exists', False):
                    report += f"### {table}\n"
                    report += f"- **Status**: ✅ Active\n"
                    report += f"- **Row Count**: {analysis['row_count']}\n"
                    report += f"- **Columns**: {len(analysis['columns'])}\n"
                    if analysis['columns']:
                        report += f"- **Column Names**: {', '.join(analysis['columns'][:8])}{'...' if len(analysis['columns']) > 8 else ''}\n"
                    report += "\n"
                else:
                    report += f"### {table}\n"
                    report += f"- **Status**: ❌ Error\n"
                    if 'error' in analysis:
                        report += f"- **Error**: {analysis['error']}\n"
                    report += "\n"

            # Categorize tables
            print("📂 Categorizing tables...")
            categories = self.categorize_tables(all_tables)
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
            relationships = self.analyze_table_relationships(all_tables)
            if 'error' not in relationships:
                report += "## Table Relationships\n\n"
                for table, rel_data in relationships.items():
                    report += f"### {table}\n"
                    if 'potential_foreign_keys' in rel_data:
                        report += f"- **Potential Foreign Keys**: {', '.join(rel_data['potential_foreign_keys'])}\n"
                    report += "\n"

            # Analyze data overlap
            print("🔄 Analyzing data overlap...")
            overlap = self.analyze_data_overlap(all_tables)
            if 'error' not in overlap:
                report += "## Data Overlap Analysis\n\n"
                common_columns = overlap.get('common_columns', {})
                if common_columns:
                    report += "### Common Columns Across Tables\n"
                    for column, tables in common_columns.items():
                        report += f"- **{column}**: {', '.join(tables)}\n"
                    report += "\n"

            # Check for duplicates
            print("🔍 Checking for duplicates...")
            duplicates = self.check_for_duplicates(all_tables)
            if 'error' not in duplicates:
                report += "## Duplicate Data Analysis\n\n"
                if duplicates:
                    for table, dup_data in duplicates.items():
                        report += f"### {table}\n"
                        for column, dup_values in dup_data.items():
                            report += f"- **{column}**: {len(dup_values)} duplicate values\n"
                        report += "\n"
                else:
                    report += "✅ **No duplicate data found**\n\n"

            # Recommendations
            report += "## Recommendations\n\n"

            # Check for potential redundancy
            if len(all_tables) > 5:
                report += "⚠️ **Many tables found** - Consider if all are necessary\n"

            # Check for empty tables
            empty_tables = [table for table, analysis in table_analyses.items()
                            if analysis.get('exists', False) and analysis.get('row_count', 0) == 0]
            if empty_tables:
                report += f"⚠️ **Empty tables found**: {', '.join(empty_tables)} - Consider removing\n"

            # Check for similar tables
            if len(categories.get('system_data', [])) > 1:
                report += "⚠️ **Multiple system tables found** - Check for redundancy\n"

            if len(categories.get('component_data', [])) > 1:
                report += "⚠️ **Multiple component tables found** - Check for redundancy\n"

            if len(categories.get('image_data', [])) > 1:
                report += "⚠️ **Multiple image tables found** - Consider consolidation\n"

            report += "\n## Summary\n\n"
            report += f"- **Total Tables**: {len(all_tables)}\n"
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

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run the complete comprehensive database analysis"""
        print("🔍 Starting comprehensive database analysis...")

        results = {
            'timestamp': self._get_current_timestamp(),
            'all_tables': [],
            'table_analyses': {},
            'categories': {},
            'relationships': {},
            'overlap': {},
            'duplicates': {}
        }

        # Step 1: Discover all tables
        print("\n📂 Step 1: Discovering all tables...")
        all_tables = self.discover_all_tables()
        results['all_tables'] = all_tables
        print(f"✅ Found {len(all_tables)} tables")

        # Step 2: Analyze each table
        print("\n📊 Step 2: Analyzing table structures...")
        for table in all_tables:
            analysis = self.analyze_table_structure(table)
            results['table_analyses'][table] = analysis
            if analysis.get('exists', False):
                print(
                    f"✅ {table}: {analysis['row_count']} rows, {len(analysis['columns'])} columns")
            else:
                print(f"❌ {table}: {analysis.get('error', 'Not found')}")

        # Step 3: Categorize tables
        print("\n📂 Step 3: Categorizing tables...")
        categories = self.categorize_tables(all_tables)
        results['categories'] = categories
        for category, tables in categories.items():
            if tables:
                print(f"📁 {category}: {len(tables)} tables")

        # Step 4: Analyze relationships
        print("\n🔗 Step 4: Analyzing table relationships...")
        relationships = self.analyze_table_relationships(all_tables)
        results['relationships'] = relationships
        if 'error' not in relationships:
            print(f"✅ Found relationships in {len(relationships)} tables")
        else:
            print(f"❌ Relationship analysis failed: {relationships['error']}")

        # Step 5: Analyze data overlap
        print("\n🔄 Step 5: Analyzing data overlap...")
        overlap = self.analyze_data_overlap(all_tables)
        results['overlap'] = overlap
        if 'error' not in overlap:
            common_columns = overlap.get('common_columns', {})
            print(
                f"✅ Found {len(common_columns)} common columns across tables")
        else:
            print(f"❌ Overlap analysis failed: {overlap['error']}")

        # Step 6: Check for duplicates
        print("\n🔍 Step 6: Checking for duplicates...")
        duplicates = self.check_for_duplicates(all_tables)
        results['duplicates'] = duplicates
        if 'error' not in duplicates:
            total_duplicates = sum(len(table_dups)
                                   for table_dups in duplicates.values())
            print(
                f"✅ Found {total_duplicates} tables with potential duplicates")
        else:
            print(f"❌ Duplicate check failed: {duplicates['error']}")

        # Step 7: Generate report
        print("\n📋 Step 7: Generating comprehensive report...")
        report = self.generate_comprehensive_report()
        results['report'] = report

        # Save report to file
        report_file = Path("comprehensive_database_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(
            f"\n✅ Comprehensive analysis complete! Report saved to: {report_file}")

        return results


def main():
    """Main function"""
    analyzer = ComprehensiveDatabaseAnalyzer()

    # Run analysis
    results = analyzer.run_comprehensive_analysis()

    # Print summary
    print("\n" + "="*50)
    print("COMPREHENSIVE DATABASE ANALYSIS SUMMARY")
    print("="*50)

    print(f"📊 Total Tables: {len(results.get('all_tables', []))}")

    # Table summary by category
    categories = results.get('categories', {})
    for category, tables in categories.items():
        if tables:
            print(f"📁 {category.replace('_', ' ').title()}: {len(tables)} tables")
            for table in tables:
                analysis = results.get('table_analyses', {}).get(table, {})
                row_count = analysis.get('row_count', 0) if analysis.get(
                    'exists', False) else 0
                print(f"  - {table}: {row_count} rows")

    # Data quality summary
    duplicates = results.get('duplicates', {})
    if 'error' not in duplicates:
        total_duplicates = sum(len(table_dups)
                               for table_dups in duplicates.values())
        print(
            f"\n🔍 Duplicate Issues: {total_duplicates} tables with potential duplicates")

    print("="*50)


if __name__ == "__main__":
    main()
