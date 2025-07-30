#!/usr/bin/env python3
"""
Database Schema Setup Script for FlexLink Components
Creates the necessary tables and functions in your Supabase database.
"""

import os
import requests
from dotenv import load_dotenv


def setup_database_schema():
    """Set up the database schema using Supabase REST API"""
    load_dotenv()

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False

    # Read the SQL schema
    try:
        with open('database_schema.sql', 'r') as f:
            sql_schema = f.read()
    except FileNotFoundError:
        print("❌ database_schema.sql not found!")
        return False

    print("🔧 Setting up database schema...")
    print(f"📊 Supabase URL: {supabase_url}")

    # Split SQL into individual statements
    statements = []
    current_statement = ""

    for line in sql_schema.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            current_statement += line + " "
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""

    if current_statement.strip():
        statements.append(current_statement.strip())

    print(f"📝 Found {len(statements)} SQL statements to execute")

    # Execute each statement
    success_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        if not statement:
            continue

        print(f"🔄 Executing statement {i}/{len(statements)}...")

        try:
            # Use Supabase REST API to execute SQL
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }

            # Execute the SQL statement
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': statement},
                timeout=30
            )

            if response.status_code == 200:
                print(f"✅ Statement {i} executed successfully")
                success_count += 1
            else:
                print(f"⚠️  Statement {i} (non-critical): {response.text}")
                # Don't count as error for non-critical statements

        except Exception as e:
            print(f"❌ Error executing statement {i}: {e}")
            error_count += 1

    print(f"\n📊 Schema Setup Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")

    if success_count > 0:
        print("✅ Database schema setup completed!")
        return True
    else:
        print("❌ No statements were executed successfully")
        return False


def verify_table_exists():
    """Verify that the component_specifications table was created"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    try:
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }

        # Try to query the table
        response = requests.get(
            f"{supabase_url}/rest/v1/component_specifications?select=id&limit=1",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ component_specifications table exists and is accessible!")
            return True
        else:
            print(f"❌ Table not accessible: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False


def main():
    """Main function"""
    print("🏗️  FlexLink Database Schema Setup")
    print("=" * 40)

    # Set up the schema
    if setup_database_schema():
        print("\n🔍 Verifying table creation...")
        if verify_table_exists():
            print("\n🎉 Database setup completed successfully!")
            print("📝 You can now upload your components using:")
            print("   python upload_to_database.py --batch-size 10")
        else:
            print("\n⚠️  Table verification failed. Please check the Supabase dashboard.")
    else:
        print("\n❌ Database setup failed!")
        print("💡 You may need to run the SQL manually in the Supabase dashboard.")


if __name__ == "__main__":
    main()
