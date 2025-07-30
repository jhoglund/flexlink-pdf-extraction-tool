#!/usr/bin/env python3
"""
Database setup script for FlexLink Component Specifications
This script provides instructions and validates the database connection.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def check_connection():
    """Check if we can connect to Supabase"""
    load_dotenv()

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("\n📝 Please create a .env file with:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_ANON_KEY=your_supabase_anon_key")
        print("\n🔗 Get these from your Supabase dashboard → Settings → API")
        return False

    try:
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully!")
        return True

    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False


def print_setup_instructions():
    """Print instructions for setting up the database"""
    print("\n📋 Database Setup Instructions:")
    print("=" * 50)
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy the contents of database_schema.sql")
    print("4. Paste and run the SQL in the editor")
    print("5. Verify the table was created in Table Editor")
    print("\n📁 The schema file is located at: database_schema.sql")


if __name__ == "__main__":
    print("🔧 FlexLink Database Setup")
    print("=" * 30)

    if check_connection():
        print_setup_instructions()

        # Test if the table exists
        try:
            from supabase import create_client
            load_dotenv()
            supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )

            # Try to query the table
            result = supabase.table('component_specifications').select(
                '*').limit(1).execute()
            print("\n✅ component_specifications table exists and is accessible!")

        except Exception as e:
            print(f"\n⚠️  Table not found or not accessible: {e}")
            print("Please run the SQL schema first.")
    else:
        print("\n❌ Cannot proceed without valid Supabase credentials.")
