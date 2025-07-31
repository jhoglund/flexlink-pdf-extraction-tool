#!/usr/bin/env python3
"""
Update FlexLink Systems Database
Updates Supabase database with system summaries and checks system availability
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Run: pip install supabase")


class SystemsDatabaseUpdater:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize the database updater"""
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
            print("⚠️  Supabase not configured or not available")

        # All FlexLink systems from the catalog
        self.all_systems = {
            'X45': 'X45 Chain System',
            'XS': 'XS Chain System',
            'X65': 'X65 Chain System',
            'X85': 'X85 Chain System',
            'XH': 'XH Chain System',
            'X180': 'X180 Chain System',
            'X300': 'X300 Chain System',
            'XK': 'XK Pallet System',
            'XT': 'XT Pallet System',
            'HU': 'HU Pallet System',
            'WL': 'WL Modular Belt System',
            'WK': 'WK Modular Belt System',
            'XC': 'XC Structural System',
            'XF': 'XF Structural System',
            'XD': 'XD Structural System',
            'GR': 'Guide Rail System',
            'CS': 'Conveyor Support System'
        }

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

            # Check which systems are missing
            all_system_codes = list(self.all_systems.keys())
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

        import csv
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
        if row['Max Load'] and row['Max Load'] != 'N/A':
            specs['max_load'] = row['Max Load']
        if row['Speed Range'] and row['Speed Range'] != 'N/A':
            specs['speed_range'] = row['Speed Range']
        if row['Temperature Range'] and row['Temperature Range'] != 'N/A':
            specs['temperature_range'] = row['Temperature Range']
        if row['Precision'] and row['Precision'] != 'N/A':
            specs['precision'] = row['Precision']

        return specs

    def _parse_page_reference(self, page_str: str) -> Optional[int]:
        """Parse page reference string to integer"""
        if not page_str or page_str == 'N/A':
            return None
        try:
            # Handle ranges like "3-99" by taking the first number
            if '-' in page_str:
                return int(page_str.split('-')[0])
            return int(page_str)
        except ValueError:
            return None

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

    def add_sample_components(self) -> Dict[str, Any]:
        """Add sample components for systems that don't have any"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Check which systems don't have components
            availability = self.check_system_availability()
            if 'error' in availability:
                return availability

            missing_systems = availability['missing_in_components_table']

            if not missing_systems:
                return {'message': 'All systems have components'}

            print(
                f"🔧 Adding sample components for {len(missing_systems)} systems...")

            # Sample component data for each missing system
            sample_components = []

            for system_code in missing_systems:
                system_name = self.all_systems.get(
                    system_code, f'{system_code} System')

                # Create sample components based on system type
                if 'Chain' in system_name:
                    sample_components.extend([
                        {
                            'system_code': system_code,
                            'component_type': 'chain',
                            'name': f'{system_code} Plain Chain',
                            'part_number': f'{system_code}-PC-1000',
                            'specifications': {
                                'pitch': 25.4,
                                'width': 50,
                                'max_load': 2.5,
                                'material': 'steel',
                                'type': 'plain'
                            },
                            'dimensions': {
                                'length': '1000mm',
                                'width': '50mm',
                                'height': '12mm'
                            },
                            'materials': ['Steel'],
                            'compatibility': [system_code],
                            'weight_kg': 0.85,
                            'price_euro': 45.50,
                            'description': f'Standard plain chain for {system_code} system'
                        },
                        {
                            'system_code': system_code,
                            'component_type': 'sprocket',
                            'name': f'{system_code} Drive Sprocket 16T',
                            'part_number': f'{system_code}-DS-16',
                            'specifications': {
                                'teeth': 16,
                                'bore': 25,
                                'pitch': 25.4,
                                'material': 'steel',
                                'type': 'drive'
                            },
                            'dimensions': {
                                'diameter': '130mm',
                                'width': '20mm'
                            },
                            'materials': ['Steel'],
                            'compatibility': [system_code],
                            'weight_kg': 0.45,
                            'price_euro': 28.75,
                            'description': f'16-tooth drive sprocket for {system_code} system'
                        }
                    ])
                elif 'Belt' in system_name:
                    sample_components.append({
                        'system_code': system_code,
                        'component_type': 'belt',
                        'name': f'{system_code} Modular Belt',
                        'part_number': f'{system_code}-MB-1000',
                        'specifications': {
                            'width': 300,
                            'pitch': 12.7,
                            'material': 'polyethylene',
                            'type': 'modular'
                        },
                        'dimensions': {
                            'length': '1000mm',
                            'width': '300mm',
                            'thickness': '8mm'
                        },
                        'materials': ['Polyethylene'],
                        'compatibility': [system_code],
                        'weight_kg': 2.5,
                        'price_euro': 120.00,
                        'description': f'Modular belt for {system_code} system'
                    })
                elif 'Pallet' in system_name:
                    sample_components.append({
                        'system_code': system_code,
                        'component_type': 'pallet',
                        'name': f'{system_code} Standard Pallet',
                        'part_number': f'{system_code}-SP-200',
                        'specifications': {
                            'size': '200x200mm',
                            'material': 'aluminum',
                            'type': 'standard'
                        },
                        'dimensions': {
                            'length': '200mm',
                            'width': '200mm',
                            'height': '15mm'
                        },
                        'materials': ['Aluminum'],
                        'compatibility': [system_code],
                        'weight_kg': 0.8,
                        'price_euro': 85.00,
                        'description': f'Standard pallet for {system_code} system'
                    })
                else:
                    # Support systems
                    sample_components.append({
                        'system_code': system_code,
                        'component_type': 'support',
                        'name': f'{system_code} Support Bracket',
                        'part_number': f'{system_code}-SB-001',
                        'specifications': {
                            'load_capacity': 1000,
                            'material': 'aluminum',
                            'type': 'bracket'
                        },
                        'dimensions': {
                            'length': '100mm',
                            'width': '50mm',
                            'height': '20mm'
                        },
                        'materials': ['Aluminum'],
                        'compatibility': [system_code],
                        'weight_kg': 0.3,
                        'price_euro': 25.00,
                        'description': f'Support bracket for {system_code} system'
                    })

            # Insert sample components
            results = []
            for component in sample_components:
                try:
                    response = self.supabase.table(
                        'component_specifications').insert(component).execute()
                    results.append({
                        'system_code': component['system_code'],
                        'component_type': component['component_type'],
                        'status': 'success',
                        'data': response.data
                    })
                    print(
                        f"✅ Added {component['component_type']} for {component['system_code']}")
                except Exception as e:
                    results.append({
                        'system_code': component['system_code'],
                        'component_type': component['component_type'],
                        'status': 'error',
                        'error': str(e)
                    })
                    print(
                        f"❌ Failed to add component for {component['system_code']}: {e}")

            return {
                'total_components_added': len(sample_components),
                'successful_additions': len([r for r in results if r['status'] == 'success']),
                'failed_additions': len([r for r in results if r['status'] == 'error']),
                'results': results
            }

        except Exception as e:
            return {'error': f'Component addition failed: {e}'}

    def generate_database_report(self) -> str:
        """Generate a comprehensive database report"""
        if not self.supabase:
            return "❌ Supabase not available"

        try:
            # Check system availability
            availability = self.check_system_availability()

            # Get system statistics
            stats_response = self.supabase.rpc('get_system_stats').execute()
            system_stats = stats_response.data[0] if stats_response.data else {
            }

            # Get component statistics (simplified)
            try:
                comp_stats_response = self.supabase.rpc(
                    'get_component_stats').execute()
                component_stats = comp_stats_response.data[0] if comp_stats_response.data else {
                }
            except:
                # Fallback if function doesn't exist
                comp_response = self.supabase.table(
                    'component_specifications').select('*').execute()
                component_stats = {
                    'total_components': len(comp_response.data),
                    'systems_count': len(set(row['system_code'] for row in comp_response.data if 'system_code' in row)),
                    'component_types_count': len(set(row['component_type'] for row in comp_response.data if 'component_type' in row)),
                    'avg_price': 0,
                    'total_weight': 0
                }
            }

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

                # System statistics
                report += "## System Statistics\n\n"
                report += f"- **Total Systems**: {system_stats.get('total_systems', 0)}\n"
                report += f"- **Categories**: {system_stats.get('categories_count', 0)}\n"
                report += f"- **Chain Conveyors**: {system_stats.get('chain_conveyors', 0)}\n"
                report += f"- **Pallet Conveyors**: {system_stats.get('pallet_conveyors', 0)}\n"
                report += f"- **Belt Conveyors**: {system_stats.get('belt_conveyors', 0)}\n"
                report += f"- **Support Systems**: {system_stats.get('support_systems', 0)}\n\n"

                # Component statistics
                report += "## Component Statistics\n\n"
                report += f"- **Total Components**: {component_stats.get('total_components', 0)}\n"
                report += f"- **Systems with Components**: {component_stats.get('systems_count', 0)}\n"
                report += f"- **Component Types**: {component_stats.get('component_types_count', 0)}\n"
                report += f"- **Average Price**: €{component_stats.get('avg_price', 0):.2f}\n"
                report += f"- **Total Weight**: {component_stats.get('total_weight', 0):.2f} kg\n\n"

                return report

                except Exception as e:
                return f"❌ Report generation failed: {e}"

                def _get_current_timestamp(self) -> str:
                """Get current timestamp string"""
                from datetime import datetime
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                def run_full_update(self) -> Dict[str, Any]:
                """Run the complete database update process"""
                print("🚀 Starting full database update process...")

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

            # Step 2: Update systems table
            print("\n📝 Step 2: Updating systems table...")
            systems_update = self.update_systems_table()
            results['steps'].append({
                'step': 'systems_update',
                'result': systems_update
                })

            # Step 3: Add sample components
            print("\n🔧 Step 3: Adding sample components...")
            components_update = self.add_sample_components()
            results['steps'].append({
                'step': 'components_update',
                'result': components_update
                })

            # Step 4: Generate final report
            print("\n📋 Step 4: Generating final report...")
            report = self.generate_database_report()
            results['steps'].append({
                'step': 'final_report',
                'result': {'report': report}
                })

            # Save report to file
            report_file = Path("database_update_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

            print(
                f"\n✅ Database update complete! Report saved to: {report_file}")

            return results


            def main():
        """Main function to update the database"""
        updater = SystemsDatabaseUpdater()

            # Run full update
            results = updater.run_full_update()

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
                    elif step['step'] == 'components_update':
                    print(
                f"✅ {step_name}: {result.get('successful_additions', 0)} components added")
                    elif step['step'] == 'final_report':
                    print(f"✅ {step_name}: Report generated successfully")

                    print("="*50)


                if __name__ == "__main__":
                main()
