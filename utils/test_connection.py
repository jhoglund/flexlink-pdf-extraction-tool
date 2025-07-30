#!/usr/bin/env python3
"""
Quick test to verify Supabase connection works
Save this as test_connection.py
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_supabase_connection():
    print("🚀 Testing FlexLink Supabase Connection")
    print("=" * 50)

    # Get credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    # Check if credentials exist
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        print("   Add: SUPABASE_URL=https://vpgawhkvfibhzafkdcsa.supabase.co")
        return False

    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY not found in .env file")
        print("   Add your publishable key from Supabase dashboard")
        return False

    print(f"✅ Found SUPABASE_URL: {supabase_url}")
    print(f"✅ Found SUPABASE_ANON_KEY: {supabase_key[:20]}...")

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")

        # Test database connection by counting systems
        result = supabase.table("conveyor_systems").select(
            "count", count="exact").execute()
        system_count = result.count

        print(f"✅ Database connected! Found {system_count} conveyor systems")

        # Show a few systems as example
        systems = supabase.table("conveyor_systems").select(
            "code, name").limit(3).execute()

        print("\n📋 Sample systems in database:")
        for system in systems.data:
            print(f"   • {system['code']}: {system['name']}")

        print(f"\n🎉 Connection test successful!")
        print("You're ready to run the full data extractor.")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that you've run the SQL schema in Supabase SQL Editor")
        print("2. Verify your publishable key is correct")
        print("3. Make sure your .env file is in the same folder as this script")
        return False


if __name__ == "__main__":
    # Instructions
    print("Before running this test:")
    print("1. Make sure you've run the SQL schema in Supabase")
    print("2. Create a .env file with your credentials")
    print("3. Install: pip install supabase python-dotenv")
    print()

    test_supabase_connection()
