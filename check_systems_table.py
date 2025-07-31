#!/usr/bin/env python3
"""
Check Systems Table Structure
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


def check_systems_table():
    """Check the actual structure of the systems table"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
        print("❌ Supabase not available")
        return

    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Get a sample of the systems table
        response = supabase.table('systems').select('*').limit(3).execute()

        if response.data:
            print(f"\n📊 Systems table has {len(response.data)} sample rows")
            print(f"📋 Columns: {list(response.data[0].keys())}")

            print("\n🔍 Sample data:")
            for i, row in enumerate(response.data):
                print(f"\nRow {i+1}:")
                for key, value in row.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ No data found in systems table")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_systems_table()
