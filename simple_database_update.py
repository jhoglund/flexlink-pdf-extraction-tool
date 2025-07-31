#!/usr/bin/env python3
"""
Simple FlexLink Systems Database Update
Updates Supabase database with system summaries and checks system availability
"""

import os
import csv
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


class SimpleDatabaseUpdater:
    def __init__(self):
        """Initialize the database updater"""
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

    def check_system_availability(self) -> Dict[str, Any]:
        """Check which systems are available in the database"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Check systems table
            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            available_systems = [row['system_code']
                                 for row in systems_response.data]

            # Check component_specifications table
            components_response = self.supabase.table(
                'component_specifications').select('system_code').execute()
            available_components = [row['system_code']
                                    for row in components_response.data]

            # Get unique system codes from components
            unique_component_systems = list(set(available_components))

            # All expected systems
            all_system_codes = ['X45', 'XS', 'X65', 'X85', 'XH', 'X180', 'X300',
                                'XK', 'XT', 'HU', 'WL', 'WK', 'XC', 'XF', 'XD', 'GR', 'CS']

            # Check which systems are missing
            missing_in_systems = [
                code for code in all_system_codes if code not in available_systems]
            missing_in_components = [
                code for code in all_system_codes if code not in unique_component_systems]

            return {
                'total_systems': len(all_system_codes),
                'available_in_systems_table': len(available_systems),
                'available_in_components_table': len(unique_component_systems),
                'missing_in_systems_table': missing_in_systems,
                'missing_in_components_table': missing_in_components,
                'systems_in_systems_table': available_systems,
                'systems_in_components_table': unique_component_systems
            }

        except Exception as e:
            return {'error': f'Database query failed: {e}'}

    def load_system_data(self) -> List[Dict[str, Any]]:
        """Load system data from the CSV file"""
        csv_file = Path("flexlink_complete_system_matrix.csv")

        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return []

        systems = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert CSV data to database format
                system_data = {
                    'system_code': row['System Code'],
                    'system_name': row['System Name'],
                    'category': row['Category'],
                    'description': row['Description'],
                    'key_features': self._parse_features(row['Key Features']),
                    'applications': self._parse_features(row['Applications']),
                    'advantages': self._parse_features(row['Advantages']),
                    'technical_specs': self._create_technical_specs(row),
                    'materials': self._parse_materials(row['Materials']),
                    'load_capacity': row['Load Capacity'],
                    'speed_range': row['Speed Range'],
                    'precision_level': row['Precision'],
                    'chain_pitch': row['Chain Pitch'],
                    'chain_width': row['Chain Width'],
                    'max_load': row['Max Load per Link'],
                    'temperature_range': row['Temperature Range'],
                    'page_reference': self._parse_page_reference(row['Page Reference'])
                }
                systems.append(system_data)

        return systems

    def _parse_features(self, features_str: str) -> List[str]:
        """Parse features string into array"""
        if not features_str or features_str == 'N/A':
            return []
        return [f.strip() for f in features_str.split(',') if f.strip()]

    def _parse_materials(self, materials_str: str) -> List[str]:
        """Parse materials string into array"""
        if not materials_str or materials_str == 'N/A':
            return []
        return [m.strip() for m in materials_str.split(',') if m.strip()]

    def _create_technical_specs(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Create technical specifications JSON object"""
        specs = {}

        if row['Chain Pitch'] and row['Chain Pitch'] != 'N/A':
            specs['chain_pitch'] = row['Chain Pitch']
        if row['Chain Width'] and row['Chain Width'] != 'N/A':
            specs['chain_width'] = row['Chain Width']
        if row['Max Load per Link'] and row['Max Load per Link'] != 'N/A':
            specs['max_load'] = row['Max Load per Link']
        if row['Speed Range'] and row['Speed Range'] != 'N/A':
            specs['speed_range'] = row['Speed Range']
        if row['Temperature Range'] and row['Temperature Range'] != 'N/A':
            specs['temperature_range'] = row['Temperature Range']
        if row['Precision'] and row['Precision'] != 'N/A':
            specs['precision'] = row['Precision']

        return specs

    def _parse_page_reference(self, page_str: str) -> int:
        """Parse page reference string to integer"""
        if not page_str or page_str == 'N/A':
            return 0
        try:
            # Handle ranges like "3-99" by taking the first number
            if '-' in page_str:
                return int(page_str.split('-')[0])
            return int(page_str)
        except ValueError:
            return 0

    def update_systems_table(self) -> Dict[str, Any]:
        """Update the systems table with all system data"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Load system data
            systems_data = self.load_system_data()

            if not systems_data:
                return {'error': 'No system data loaded'}

            print(f"📊 Updating {len(systems_data)} systems in database...")

            # Insert/update systems
            results = []
            for system in systems_data:
                try:
                    # Use upsert to insert or update
                    response = self.supabase.table(
                        'systems').upsert(system).execute()
                    results.append({
                        'system_code': system['system_code'],
                        'status': 'success',
                        'data': response.data
                    })
                    print(f"✅ Updated system: {system['system_code']}")
                except Exception as e:
                    results.append({
                        'system_code': system['system_code'],
                        'status': 'error',
                        'error': str(e)
                    })
                    print(
                        f"❌ Failed to update system {system['system_code']}: {e}")

            return {
                'total_systems': len(systems_data),
                'successful_updates': len([r for r in results if r['status'] == 'success']),
                'failed_updates': len([r for r in results if r['status'] == 'error']),
                'results': results
            }

        except Exception as e:
            return {'error': f'Database update failed: {e}'}

    def generate_simple_report(self) -> str:
        """Generate a simple database report"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            # Check system availability
            availability = self.check_system_availability()

            # Get basic statistics
            systems_response = self.supabase.table(
                'systems').select('*').execute()
            components_response = self.supabase.table(
                'component_specifications').select('*').execute()

            report = "# FlexLink Database Status Report\n\n"
            report += f"Generated on: {self._get_current_timestamp()}\n\n"

            # System availability
            report += "## System Availability\n\n"
            report += f"- **Total Systems**: {availability.get('total_systems', 0)}\n"
            report += f"- **Available in Systems Table**: {availability.get('available_in_systems_table', 0)}\n"
            report += f"- **Available in Components Table**: {availability.get('available_in_components_table', 0)}\n\n"

            if availability.get('missing_in_systems_table'):
                report += "### Missing in Systems Table:\n"
                for system in availability['missing_in_systems_table']:
                    report += f"- {system}\n"
                report += "\n"

            if availability.get('missing_in_components_table'):
                report += "### Missing in Components Table:\n"
                for system in availability['missing_in_components_table']:
                    report += f"- {system}\n"
                report += "\n"

            # Basic statistics
            report += "## Basic Statistics\n\n"
            report += f"- **Systems in Database**: {len(systems_response.data)}\n"
            report += f"- **Components in Database**: {len(components_response.data)}\n"

            # System categories
            categories = {}
            for system in systems_response.data:
                category = system.get('category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1

            report += "\n### Systems by Category:\n"
            for category, count in categories.items():
                report += f"- **{category}**: {count}\n"

            return report

        except Exception as e:
            return f"❌ Report generation failed: {e}"

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run_update(self) -> Dict[str, Any]:
        """Run the database update process"""
        print("🚀 Starting database update process...")

        results = {
            'timestamp': self._get_current_timestamp(),
            'steps': []
        }

        # Step 1: Check current availability
        print("\n📊 Step 1: Checking current system availability...")
        availability = self.check_system_availability()
        results['steps'].append({
            'step': 'availability_check',
            'result': availability
        })

        if 'error' in availability:
            print(f"❌ Availability check failed: {availability['error']}")
            return results

        print(
            f"✅ Found {availability.get('available_in_systems_table', 0)} systems in database")

        # Step 2: Update systems table
        print("\n📝 Step 2: Updating systems table...")
        systems_update = self.update_systems_table()
        results['steps'].append({
            'step': 'systems_update',
            'result': systems_update
        })

        # Step 3: Generate report
        print("\n📋 Step 3: Generating report...")
        report = self.generate_simple_report()
        results['steps'].append({
            'step': 'report',
            'result': {'report': report}
        })

        # Save report to file
        report_file = Path("database_status_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Database update complete! Report saved to: {report_file}")

        return results


def main():
    """Main function"""
    updater = SimpleDatabaseUpdater()

    # Run update
    results = updater.run_update()

    # Print summary
    print("\n" + "="*50)
    print("DATABASE UPDATE SUMMARY")
    print("="*50)

    for step in results['steps']:
        step_name = step['step'].replace('_', ' ').title()
        result = step['result']

        if 'error' in result:
            print(f"❌ {step_name}: {result['error']}")
        elif step['step'] == 'availability_check':
            print(
                f"✅ {step_name}: {result.get('total_systems', 0)} systems checked")
        elif step['step'] == 'systems_update':
            print(
                f"✅ {step_name}: {result.get('successful_updates', 0)} systems updated")
        elif step['step'] == 'report':
            print(f"✅ {step_name}: Report generated successfully")

    print("="*50)


if __name__ == "__main__":
    main()
