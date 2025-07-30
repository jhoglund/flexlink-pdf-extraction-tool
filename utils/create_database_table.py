#!/usr/bin/env python3
"""
Simple Database Table Creator for FlexLink Components
Creates the component_specifications table in your Supabase database.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def create_component_table():
    """Create the component_specifications table"""
    load_dotenv()

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        return False

    try:
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Create the table using raw SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS component_specifications (
            id SERIAL PRIMARY KEY,
            system_code VARCHAR(20) NOT NULL,
            component_type VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            part_number VARCHAR(100),
            specifications JSONB DEFAULT '{}',
            dimensions JSONB DEFAULT '{}',
            materials TEXT[] DEFAULT '{}',
            compatibility TEXT[] DEFAULT '{}',
            weight_kg DECIMAL(8,3),
            price_euro DECIMAL(10,2),
            description TEXT,
            image_url TEXT,
            page_reference INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """

        print("🔄 Creating component_specifications table...")

        # Execute the SQL using Supabase's RPC function
        try:
            result = supabase.rpc(
                'exec_sql', {'sql': create_table_sql}).execute()
            print("✅ Table created successfully!")
        except Exception as e:
            print(f"⚠️  Could not execute SQL directly: {e}")
            print("💡 You'll need to create the table manually in the Supabase dashboard")
            return False

        # Create indexes
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_component_specifications_system_code ON component_specifications(system_code);",
            "CREATE INDEX IF NOT EXISTS idx_component_specifications_component_type ON component_specifications(component_type);",
            "CREATE INDEX IF NOT EXISTS idx_component_specifications_part_number ON component_specifications(part_number);",
            "CREATE INDEX IF NOT EXISTS idx_component_specifications_specifications ON component_specifications USING GIN(specifications);"
        ]

        print("🔄 Creating indexes...")
        for i, index_sql in enumerate(indexes_sql, 1):
            try:
                supabase.rpc('exec_sql', {'sql': index_sql}).execute()
                print(f"✅ Index {i} created")
            except Exception as e:
                print(f"⚠️  Index {i} (non-critical): {e}")

        return True

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False


def verify_table():
    """Verify that the table was created successfully"""
    load_dotenv()

    try:
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )

        # Try to query the table
        result = supabase.table('component_specifications').select(
            'id').limit(1).execute()
        print("✅ component_specifications table exists and is accessible!")
        return True

    except Exception as e:
        print(f"❌ Table verification failed: {e}")
        return False


def main():
    """Main function"""
    print("🏗️  Creating FlexLink Component Table")
    print("=" * 40)

    if create_component_table():
        print("\n🔍 Verifying table...")
        if verify_table():
            print("\n🎉 Database table created successfully!")
            print("📝 You can now upload your components using:")
            print("   python upload_to_database.py --batch-size 10")
        else:
            print("\n⚠️  Table verification failed.")
            print("💡 Please create the table manually in the Supabase dashboard")
    else:
        print("\n❌ Failed to create table!")
        print("💡 Please run the SQL manually in the Supabase dashboard")


if __name__ == "__main__":
    main()
