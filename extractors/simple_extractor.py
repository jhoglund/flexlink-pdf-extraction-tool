#!/usr/bin/env python3
"""
Simple FlexLink Data Extractor using REST API
Bypasses Python client dependency issues
"""

import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SimpleFlexLinkExtractor:
    def __init__(self):
        """Initialize with Supabase REST API"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return

        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test the REST API connection"""
        try:
            url = f"{self.supabase_url}/rest/v1/conveyor_systems?select=count"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print("✅ Connected to Supabase REST API")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def insert_components_batch(self, components: List[Dict]) -> bool:
        """Insert components using REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/components"

            # Insert in smaller batches to avoid API limits
            batch_size = 5
            total_inserted = 0

            for i in range(0, len(components), batch_size):
                batch = components[i:i + batch_size]

                response = requests.post(url, headers=self.headers, json=batch)

                if response.status_code in [201, 200]:
                    total_inserted += len(batch)
                    print(
                        f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} components")
                else:
                    print(
                        f"❌ Batch {i//batch_size + 1} failed: {response.status_code}")
                    print(f"Error: {response.text}")
                    return False

            print(f"🎉 Successfully inserted {total_inserted} components")
            return True

        except Exception as e:
            print(f"❌ Error inserting components: {e}")
            return False

    def get_sample_components(self) -> List[Dict]:
        """Get a focused set of essential components"""

        components = [
            # X45 Essential Components
            {
                "system_code": "X45",
                "name": "X45 End drive unit 24V",
                "component_type": "drive_unit",
                "specifications": {
                    "voltage": "24V",
                    "max_traction_force_n": 300,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["X45"]
            },
            {
                "system_code": "X45",
                "name": "X45 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM"
                },
                "compatibility": ["X45"]
            },
            {
                "system_code": "X45",
                "name": "X45 Idler end unit",
                "component_type": "idler_unit",
                "specifications": {
                    "type": "end_idler"
                },
                "compatibility": ["X45"]
            },

            # XS Essential Components
            {
                "system_code": "XS",
                "name": "XS End drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "max_traction_force_n": 700,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["XS"]
            },
            {
                "system_code": "XS",
                "name": "XS Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM"
                },
                "compatibility": ["XS"]
            },

            # X65 Essential Components
            {
                "system_code": "X65",
                "name": "X65 Medium drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "medium",
                    "max_traction_force_n": 800,
                    "teeth_count": 11,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["X65"]
            },
            {
                "system_code": "X65",
                "name": "X65 Heavy drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "heavy",
                    "max_traction_force_n": 1250,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["X65"]
            },
            {
                "system_code": "X65",
                "name": "X65 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM"
                },
                "compatibility": ["X65"]
            },
            {
                "system_code": "X65",
                "name": "X65 Cleated chain Type A",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "cleated_a",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "cleat_height_mm": 12
                },
                "compatibility": ["X65"]
            },

            # X85 Essential Components
            {
                "system_code": "X85",
                "name": "X85 Standard drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "standard",
                    "max_traction_force_n": 1250,
                    "teeth_count": 9,
                    "chain_pitch_mm": 33.5
                },
                "compatibility": ["X85"]
            },
            {
                "system_code": "X85",
                "name": "X85 Roller top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "roller_top",
                    "pitch_mm": 33.5,
                    "material": "POM"
                },
                "compatibility": ["X85"]
            },

            # XK Essential Components
            {
                "system_code": "XK",
                "name": "XK Heavy drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "heavy",
                    "max_traction_force_n": 2500,
                    "teeth_count": 11,
                    "chain_pitch_mm": 38.1
                },
                "compatibility": ["XK", "XKP"]
            },
            {
                "system_code": "XK",
                "name": "XK Wheel bend 90°",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "wheel",
                    "angle_degrees": 90
                },
                "compatibility": ["XK", "XKP"]
            },

            # Guide Rails
            {
                "system_code": "X65",
                "name": "X65 Fixed guide rail bracket",
                "component_type": "guide_rail_bracket",
                "specifications": {
                    "bracket_type": "fixed",
                    "material": "aluminium"
                },
                "compatibility": ["X65"]
            },
            {
                "system_code": "X85",
                "name": "X85 Adjustable guide rail bracket",
                "component_type": "guide_rail_bracket",
                "specifications": {
                    "bracket_type": "adjustable",
                    "material": "aluminium",
                    "adjustment_range_mm": "50-200"
                },
                "compatibility": ["X85"]
            }
        ]

        return components

    def populate_components(self):
        """Main function to populate component data"""
        print("🚀 Starting FlexLink component population...")
        print("=" * 50)

        # Get sample components
        components = self.get_sample_components()

        print(f"📦 Preparing to insert {len(components)} components:")
        component_types = {}
        for comp in components:
            comp_type = comp['component_type']
            component_types[comp_type] = component_types.get(comp_type, 0) + 1

        for comp_type, count in component_types.items():
            print(f"   • {comp_type}: {count}")

        # Insert components
        print(f"\n💾 Inserting components...")
        success = self.insert_components_batch(components)

        if success:
            print("\n🎉 Component population completed!")
            print("\n📋 Next steps:")
            print("1. Refresh your web interface")
            print("2. Check that components appear in the database")
            print("3. Test component filtering and selection")
            print("4. Add more component types as needed")
        else:
            print("\n❌ Component population failed")

    def check_current_data(self):
        """Check what's currently in the database"""
        try:
            # Check systems
            systems_url = f"{self.supabase_url}/rest/v1/conveyor_systems?select=code,name"
            systems_response = requests.get(systems_url, headers=self.headers)

            if systems_response.status_code == 200:
                systems = systems_response.json()
                print(f"✅ Found {len(systems)} conveyor systems:")
                for system in systems[:5]:  # Show first 5
                    print(f"   • {system['code']}: {system['name']}")

            # Check components
            components_url = f"{self.supabase_url}/rest/v1/components?select=system_code,component_type&limit=10"
            components_response = requests.get(
                components_url, headers=self.headers)

            if components_response.status_code == 200:
                components = components_response.json()
                print(
                    f"\n✅ Found {len(components)} components (showing first 10)")

                if len(components) == 0:
                    print("   No components found - ready to populate!")
                else:
                    for comp in components:
                        print(
                            f"   • {comp['system_code']}: {comp['component_type']}")

        except Exception as e:
            print(f"❌ Error checking data: {e}")


def main():
    print("🔧 Simple FlexLink Data Extractor")
    print("=" * 40)

    extractor = SimpleFlexLinkExtractor()

    print("\nWhat would you like to do?")
    print("1. Check current database contents")
    print("2. Add sample components")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        extractor.check_current_data()
    elif choice == "2":
        extractor.populate_components()
    elif choice == "3":
        extractor.check_current_data()
        print("\n" + "="*50)
        extractor.populate_components()
    else:
        print("Invalid choice, running both...")
        extractor.check_current_data()
        print("\n" + "="*50)
        extractor.populate_components()


if __name__ == "__main__":
    main()
