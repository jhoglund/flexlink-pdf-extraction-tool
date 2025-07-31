#!/usr/bin/env python3
"""
Setup Systems Table in Supabase
Creates the systems table and populates it with FlexLink system data
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Run: pip install supabase")


def setup_systems_table():
    """Set up the systems table in Supabase"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
        print("❌ Supabase not configured properly")
        return False

    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Read the SQL file
        sql_file = Path("database/create_systems_table.sql")
        if not sql_file.exists():
            print(f"❌ SQL file not found: {sql_file}")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("📝 Executing SQL to create systems table...")

        # Execute the SQL using rpc (we'll need to create a function for this)
        # For now, let's use the raw SQL execution
        try:
            # Try to execute the SQL directly
            result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
            print("✅ Systems table created successfully")
            return True
        except Exception as e:
            print(f"⚠️  Direct SQL execution failed: {e}")
            print("📋 Please run the SQL manually in your Supabase SQL editor:")
            print(f"📄 File: {sql_file}")
            return False

    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Setting up FlexLink Systems Table...")

    success = setup_systems_table()

    if success:
        print("✅ Systems table setup complete!")
        print("🔄 Now you can run: python update_systems_database.py")
    else:
        print("❌ Systems table setup failed!")
        print("📋 Please manually execute the SQL in your Supabase SQL editor")


if __name__ == "__main__":
    main()
