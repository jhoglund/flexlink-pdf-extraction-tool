#!/usr/bin/env python3
"""
Test Components Table
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


def test_components_table():
    """Test the components table"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
        print("❌ Supabase not available")
        return

    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Test components table query
        response = supabase.table('components').select('*').limit(5).execute()

        if response.data:
            print(
                f"✅ Components table query successful: {len(response.data)} components found")
            print(f"📋 Columns: {list(response.data[0].keys())}")

            print("\n🔍 Sample components:")
            for i, component in enumerate(response.data):
                print(f"\nComponent {i+1}:")
                print(f"  System Code: {component.get('system_code', 'N/A')}")
                print(f"  Name: {component.get('name', 'N/A')}")
                print(
                    f"  Component Type: {component.get('component_type', 'N/A')}")
                print(
                    f"  Compatibility: {component.get('compatibility', 'N/A')}")

            # Check for system codes
            system_codes = set(comp.get('system_code')
                               for comp in response.data if comp.get('system_code'))
            print(f"\n📊 System codes found: {list(system_codes)}")

        else:
            print("❌ No data found in components table")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_components_table()
