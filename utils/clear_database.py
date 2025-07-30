#!/usr/bin/env python3
"""
Database cleanup script for FlexLink Component Specifications
This script safely clears existing component data to prepare for a fresh import.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def clear_component_data():
    """Clear all existing component data from the database"""
    load_dotenv()

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("Please create a .env file with your Supabase credentials.")
        return False

    try:
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Get current count
        result = supabase.table('component_specifications').select(
            'id', count='exact').execute()
        current_count = result.count if hasattr(result, 'count') else 0
        print(f"📊 Current components in database: {current_count}")

        if current_count == 0:
            print("✅ Database is already empty!")
            return True

        # Ask for confirmation
        print(f"\n⚠️  This will delete {current_count} existing components!")
        response = input(
            "Are you sure you want to continue? (yes/no): ").lower().strip()

        if response not in ['yes', 'y']:
            print("❌ Operation cancelled.")
            return False

        # Delete all components
        print("🗑️  Deleting existing components...")
        result = supabase.table(
            'component_specifications').delete().neq('id', 0).execute()

        # Verify deletion
        result = supabase.table('component_specifications').select(
            'id', count='exact').execute()
        new_count = result.count if hasattr(result, 'count') else 0

        print(f"✅ Successfully deleted {current_count} components!")
        print(f"📊 Remaining components: {new_count}")

        return True

    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


def reset_sequences():
    """Reset the auto-increment sequence"""
    try:
        load_dotenv()
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )

        # Reset the sequence (this would need to be done via SQL)
        print("🔄 Note: To reset auto-increment sequence, run this SQL in Supabase:")
        print("ALTER SEQUENCE component_specifications_id_seq RESTART WITH 1;")

    except Exception as e:
        print(f"⚠️  Could not connect to reset sequence: {e}")


if __name__ == "__main__":
    print("🧹 FlexLink Database Cleanup")
    print("=" * 30)

    if clear_component_data():
        reset_sequences()
        print("\n✅ Database cleared successfully!")
        print("📝 Ready for fresh component import from main catalog.")
    else:
        print("\n❌ Failed to clear database.")
