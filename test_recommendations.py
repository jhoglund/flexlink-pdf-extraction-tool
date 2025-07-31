#!/usr/bin/env python3
"""
Test Recommendations Functionality
"""

import os
from dotenv import load_dotenv

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Run: pip install supabase")


def test_recommendations_data():
    """Test the recommendations data structure"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
        print("❌ Supabase not available")
        return

    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Test systems table for recommendations data
        response = supabase.table('systems').select('*').limit(5).execute()

        if response.data:
            print(
                f"✅ Systems table query successful: {len(response.data)} systems found")

            print("\n🔍 Sample systems for recommendations:")
            for i, system in enumerate(response.data):
                print(
                    f"\nSystem {i+1}: {system['system_code']} - {system['system_name']}")
                print(f"  Load Capacity: {system.get('max_load', 'N/A')}")
                print(f"  Speed Range: {system.get('speed_range', 'N/A')}")
                print(f"  Precision: {system.get('precision_level', 'N/A')}")
                print(f"  Category: {system.get('category', 'N/A')}")
                print(
                    f"  Applications: {len(system.get('applications', []))} apps")

            # Test compatibility analysis
            print("\n📊 Compatibility Analysis Test:")
            test_systems = response.data[:2]  # Use first 2 systems

            # Simulate the JavaScript compatibility logic
            avg_load = sum([
                1 if 'Light' in (s.get('max_load') or '') else
                2 if 'Medium' in (s.get('max_load') or '') else
                3 if 'Heavy' in (s.get('max_load') or '') else 1
                for s in test_systems
            ]) / len(test_systems)

            print(f"  Average Load Score: {avg_load:.1f}")

            # Find compatible systems
            compatible_count = 0
            for system in response.data:
                if system['system_code'] not in [s['system_code'] for s in test_systems]:
                    compatibility_score = 0

                    # Load compatibility
                    system_load = system.get('max_load', '')
                    if 'Light' in system_load and avg_load <= 1.5:
                        compatibility_score += 30
                    elif 'Medium' in system_load and 1.5 <= avg_load <= 2.5:
                        compatibility_score += 30
                    elif 'Heavy' in system_load and avg_load >= 2.5:
                        compatibility_score += 30

                    # Category compatibility
                    test_categories = [s.get('category') for s in test_systems]
                    if system.get('category') in test_categories:
                        compatibility_score += 20

                    if compatibility_score >= 50:
                        compatible_count += 1
                        print(
                            f"    Compatible: {system['system_code']} (Score: {compatibility_score})")

            print(f"  Total Compatible Systems: {compatible_count}")

        else:
            print("❌ No data found in systems table")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_recommendations_data()
