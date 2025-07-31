#!/usr/bin/env python3
"""
Setup script for FlexLink Image Database
Creates the product_images table and related functions in Supabase
"""

import os
import requests
import json
from dotenv import load_dotenv


def setup_database():
    """Set up the product_images table in Supabase"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False

    print("🔧 Setting up database schema...")

    # Read the SQL schema
    try:
        with open('database/create_images_table.sql', 'r') as f:
            sql_schema = f.read()
    except FileNotFoundError:
        print("❌ SQL schema file not found: database/create_images_table.sql")
        return False

    # Split the SQL into individual statements
    statements = [stmt.strip()
                  for stmt in sql_schema.split(';') if stmt.strip()]

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    success_count = 0
    total_statements = len(statements)

    for i, statement in enumerate(statements, 1):
        if not statement:
            continue

        try:
            # Execute SQL statement via Supabase REST API
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': statement}
            )

            if response.status_code in [200, 201]:
                print(f"✅ Statement {i}/{total_statements}: Success")
                success_count += 1
            else:
                print(
                    f"⚠️ Statement {i}/{total_statements}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Statement {i}/{total_statements}: Error - {e}")

    print(f"\n📊 Database Setup Summary:")
    print(f"   Total statements: {total_statements}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {total_statements - success_count}")

    if success_count > 0:
        print("✅ Database setup completed!")
        return True
    else:
        print("❌ Database setup failed!")
        return False


def test_database_connection():
    """Test the database connection and table existence"""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }

    try:
        # Test connection by trying to query the table
        response = requests.get(
            f"{supabase_url}/rest/v1/product_images?select=count",
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Database connection successful!")
            print("✅ product_images table exists!")
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def main():
    print("🚀 FlexLink Database Setup")
    print("=" * 40)

    # Step 1: Set up database schema
    if setup_database():
        print("\n🔍 Testing database connection...")

        # Step 2: Test connection
        if test_database_connection():
            print("\n🎉 Database setup completed successfully!")
            print("You can now upload images to the database.")
        else:
            print("\n⚠️ Database setup may have issues.")
    else:
        print("\n❌ Database setup failed!")


if __name__ == "__main__":
    main()
