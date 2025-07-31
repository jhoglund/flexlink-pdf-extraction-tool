#!/usr/bin/env python3
"""
Database Fix Script
Fixes identified issues in the FlexLink database
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


class DatabaseFixer:
    def __init__(self):
        """Initialize the database fixer"""
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

    def fix_orphaned_component(self) -> Dict[str, Any]:
        """Fix the orphaned component with lowercase system code"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # First, check if the orphaned component exists
            response = self.supabase.table('component_specifications').select(
                '*').eq('system_code', 'x180').execute()

            if not response.data:
                return {
                    'status': 'no_orphaned_components',
                    'message': 'No orphaned components found'
                }

            orphaned_count = len(response.data)
            print(
                f"🔍 Found {orphaned_count} orphaned component(s) with system_code 'x180'")

            # Update the orphaned component
            update_response = self.supabase.table('component_specifications').update({
                'system_code': 'X180'
            }).eq('system_code', 'x180').execute()

            if update_response.data:
                return {
                    'status': 'success',
                    'message': f'Successfully updated {len(update_response.data)} orphaned component(s)',
                    'updated_count': len(update_response.data)
                }
            else:
                return {
                    'status': 'no_updates',
                    'message': 'No components were updated'
                }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def standardize_system_codes(self) -> Dict[str, Any]:
        """Standardize all system codes to uppercase"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get all component_specifications with lowercase system codes
            response = self.supabase.table(
                'component_specifications').select('system_code').execute()

            lowercase_codes = []
            for row in response.data:
                system_code = row.get('system_code', '')
                if system_code and system_code != system_code.upper():
                    lowercase_codes.append(system_code)

            if not lowercase_codes:
                return {
                    'status': 'no_lowercase_codes',
                    'message': 'No lowercase system codes found'
                }

            print(
                f"🔍 Found {len(lowercase_codes)} component(s) with lowercase system codes")

            # Update each lowercase code to uppercase
            updated_count = 0
            for code in set(lowercase_codes):  # Use set to avoid duplicates
                uppercase_code = code.upper()
                update_response = self.supabase.table('component_specifications').update({
                    'system_code': uppercase_code
                }).eq('system_code', code).execute()

                if update_response.data:
                    updated_count += len(update_response.data)

            return {
                'status': 'success',
                'message': f'Successfully updated {updated_count} component(s)',
                'updated_count': updated_count,
                'lowercase_codes_found': len(lowercase_codes)
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def verify_system_relationships(self) -> Dict[str, Any]:
        """Verify that all components reference valid systems"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            # Get all unique system codes from component_specifications
            components_response = self.supabase.table(
                'component_specifications').select('system_code').execute()
            component_systems = set(
                row['system_code'] for row in components_response.data if row.get('system_code'))

            # Get all system codes from systems table
            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            valid_systems = set(row['system_code']
                                for row in systems_response.data)

            # Find orphaned components
            orphaned_systems = component_systems - valid_systems

            return {
                'status': 'success',
                'total_component_systems': len(component_systems),
                'valid_systems': len(valid_systems),
                'orphaned_systems': list(orphaned_systems),
                'orphaned_count': len(orphaned_systems),
                'valid_relationships': len(component_systems.intersection(valid_systems))
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def check_data_quality(self) -> Dict[str, Any]:
        """Check overall data quality after fixes"""
        if not self.supabase:
            return {'error': 'Supabase not available'}

        try:
            quality_report = {}

            # Check for duplicate system codes in systems table
            systems_response = self.supabase.table(
                'systems').select('system_code').execute()
            system_codes = [row['system_code']
                            for row in systems_response.data]
            duplicate_system_codes = [code for code in set(
                system_codes) if system_codes.count(code) > 1]

            quality_report['duplicate_system_codes'] = {
                'count': len(duplicate_system_codes),
                'codes': duplicate_system_codes
            }

            # Check for orphaned components
            relationship_check = self.verify_system_relationships()
            if relationship_check.get('status') == 'success':
                quality_report['orphaned_components'] = {
                    'count': relationship_check['orphaned_count'],
                    'systems': relationship_check['orphaned_systems']
                }

            # Check data distribution
            components_response = self.supabase.table(
                'component_specifications').select('system_code').execute()
            system_counts = {}
            for row in components_response.data:
                sys_code = row.get('system_code', 'Unknown')
                system_counts[sys_code] = system_counts.get(sys_code, 0) + 1

            quality_report['system_distribution'] = {
                'total_components': len(components_response.data),
                'systems_with_components': len(system_counts),
                'average_components_per_system': len(components_response.data) / len(system_counts) if system_counts else 0,
                'system_counts': system_counts
            }

            return quality_report

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def generate_fix_report(self, results: Dict[str, Any]) -> str:
        """Generate a report of the fixes applied"""
        report = "# Database Fix Report\n\n"
        report += f"Generated on: {self._get_current_timestamp()}\n\n"

        report += "## Fixes Applied\n\n"

        # Orphaned component fix
        if 'orphaned_fix' in results:
            fix_result = results['orphaned_fix']
            report += "### 1. Orphaned Component Fix\n"
            if fix_result.get('status') == 'success':
                report += f"- **Status**: ✅ Success\n"
                report += f"- **Updated Components**: {fix_result.get('updated_count', 0)}\n"
                report += f"- **Message**: {fix_result.get('message', '')}\n"
            else:
                report += f"- **Status**: ℹ️ {fix_result.get('message', 'No action needed')}\n"
            report += "\n"

        # System code standardization
        if 'standardization' in results:
            fix_result = results['standardization']
            report += "### 2. System Code Standardization\n"
            if fix_result.get('status') == 'success':
                report += f"- **Status**: ✅ Success\n"
                report += f"- **Updated Components**: {fix_result.get('updated_count', 0)}\n"
                report += f"- **Lowercase Codes Found**: {fix_result.get('lowercase_codes_found', 0)}\n"
            else:
                report += f"- **Status**: ℹ️ {fix_result.get('message', 'No action needed')}\n"
            report += "\n"

        # Data quality check
        if 'quality_check' in results:
            quality = results['quality_check']
            report += "### 3. Data Quality Assessment\n"

            # Duplicate system codes
            duplicates = quality.get('duplicate_system_codes', {})
            report += f"- **Duplicate System Codes**: {duplicates.get('count', 0)}\n"
            if duplicates.get('codes'):
                report += f"  - Codes: {', '.join(duplicates['codes'])}\n"

            # Orphaned components
            orphaned = quality.get('orphaned_components', {})
            report += f"- **Orphaned Components**: {orphaned.get('count', 0)}\n"
            if orphaned.get('systems'):
                report += f"  - Systems: {', '.join(orphaned['systems'])}\n"

            # Data distribution
            distribution = quality.get('system_distribution', {})
            report += f"- **Total Components**: {distribution.get('total_components', 0)}\n"
            report += f"- **Systems with Components**: {distribution.get('systems_with_components', 0)}\n"
            report += f"- **Average Components per System**: {distribution.get('average_components_per_system', 0):.1f}\n"
            report += "\n"

        # Recommendations
        report += "## Recommendations\n\n"

        if results.get('quality_check', {}).get('duplicate_system_codes', {}).get('count', 0) == 0:
            report += "✅ **No duplicate system codes found** - Data integrity is good\n"

        if results.get('quality_check', {}).get('orphaned_components', {}).get('count', 0) == 0:
            report += "✅ **No orphaned components found** - All relationships are valid\n"
        else:
            report += "⚠️ **Orphaned components still exist** - Consider additional cleanup\n"

        report += "\n## Next Steps\n\n"
        report += "1. **Monitor data quality** - Run regular checks\n"
        report += "2. **Add foreign key constraints** - For data integrity\n"
        report += "3. **Update scripts** - Remove references to non-existent tables\n"
        report += "4. **Backup data** - Before making structural changes\n"

        return report

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run_all_fixes(self) -> Dict[str, Any]:
        """Run all database fixes"""
        print("🔧 Starting database fixes...")

        results = {
            'timestamp': self._get_current_timestamp(),
            'fixes_applied': []
        }

        # Fix 1: Orphaned component
        print("\n🔍 Step 1: Fixing orphaned component...")
        orphaned_fix = self.fix_orphaned_component()
        results['orphaned_fix'] = orphaned_fix

        if orphaned_fix.get('status') == 'success':
            print(
                f"✅ Fixed {orphaned_fix.get('updated_count', 0)} orphaned component(s)")
            results['fixes_applied'].append('orphaned_component_fix')
        else:
            print(
                f"ℹ️ {orphaned_fix.get('message', 'No orphaned components found')}")

        # Fix 2: Standardize system codes
        print("\n📝 Step 2: Standardizing system codes...")
        standardization = self.standardize_system_codes()
        results['standardization'] = standardization

        if standardization.get('status') == 'success':
            print(
                f"✅ Updated {standardization.get('updated_count', 0)} component(s)")
            results['fixes_applied'].append('system_code_standardization')
        else:
            print(
                f"ℹ️ {standardization.get('message', 'No lowercase codes found')}")

        # Check 3: Verify relationships
        print("\n🔗 Step 3: Verifying system relationships...")
        relationship_check = self.verify_system_relationships()
        results['relationship_check'] = relationship_check

        if relationship_check.get('status') == 'success':
            print(
                f"✅ Found {relationship_check.get('valid_relationships', 0)} valid relationships")
            if relationship_check.get('orphaned_count', 0) > 0:
                print(
                    f"⚠️ {relationship_check.get('orphaned_count', 0)} orphaned systems found")
        else:
            print(
                f"❌ Relationship check failed: {relationship_check.get('error', 'Unknown error')}")

        # Check 4: Overall data quality
        print("\n📊 Step 4: Checking overall data quality...")
        quality_check = self.check_data_quality()
        results['quality_check'] = quality_check

        if 'error' not in quality_check:
            print(f"✅ Data quality check complete")
            distribution = quality_check.get('system_distribution', {})
            print(f"📈 {distribution.get('total_components', 0)} total components across {distribution.get('systems_with_components', 0)} systems")
        else:
            print(
                f"❌ Quality check failed: {quality_check.get('error', 'Unknown error')}")

        # Generate report
        print("\n📋 Step 5: Generating fix report...")
        report = self.generate_fix_report(results)
        results['report'] = report

        # Save report to file
        report_file = Path("database_fix_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Database fixes complete! Report saved to: {report_file}")

        return results


def main():
    """Main function"""
    fixer = DatabaseFixer()

    # Run fixes
    results = fixer.run_all_fixes()

    # Print summary
    print("\n" + "="*50)
    print("DATABASE FIX SUMMARY")
    print("="*50)

    print(f"🔧 Fixes Applied: {len(results.get('fixes_applied', []))}")
    for fix in results.get('fixes_applied', []):
        print(f"  - {fix}")

    if 'quality_check' in results and 'error' not in results['quality_check']:
        quality = results['quality_check']
        print(f"\n📊 Data Quality:")
        print(
            f"  - Duplicate system codes: {quality.get('duplicate_system_codes', {}).get('count', 0)}")
        print(
            f"  - Orphaned components: {quality.get('orphaned_components', {}).get('count', 0)}")
        print(
            f"  - Total components: {quality.get('system_distribution', {}).get('total_components', 0)}")

    print("="*50)


if __name__ == "__main__":
    main()
