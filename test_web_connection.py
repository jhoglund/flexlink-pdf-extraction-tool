#!/usr/bin/env python3
"""
Test Web Connection
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


def test_web_connection():
    """Test the web interface database connection"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
        print("❌ Supabase not available")
        return

    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Test systems table query (same as web interface)
        response = supabase.table('systems').select(
            '*').order('system_code').execute()

        if response.data:
            print(
                f"✅ Systems table query successful: {len(response.data)} systems found")
            print(
                f"📋 Sample system: {response.data[0]['system_code']} - {response.data[0]['system_name']}")

            # Check if all required fields exist
            required_fields = ['system_code', 'system_name',
                               'chain_width', 'max_load', 'applications']
            missing_fields = []

            for field in required_fields:
                if field not in response.data[0]:
                    missing_fields.append(field)

            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")

        else:
            print("❌ No data found in systems table")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_web_connection()
