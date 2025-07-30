#!/usr/bin/env python3
"""
Advanced FlexLink Data Extractor
Extracts detailed component and system data from the FlexLink catalog
Run this in Cursor to populate your database with comprehensive data
"""

import os
import json
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FlexLinkDataExtractor:
    def __init__(self):
        """Initialize with Supabase credentials"""
        try:
            self.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
            print("✅ Connected to Supabase")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return

    def extract_drive_units_data(self) -> List[Dict]:
        """Extract comprehensive drive unit data from catalog"""

        drive_units = [
            # X45 Drive Units
            {
                "system_code": "X45",
                "name": "X45 End drive unit 24V",
                "component_type": "drive_unit",
                "specifications": {
                    "voltage": "24V",
                    "type": "end_drive",
                    "max_traction_force_n": 300,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4,
                    "temperature_range": "-20°C to +60°C"
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "X45",
                "name": "X45 End drive unit 400V",
                "component_type": "drive_unit",
                "specifications": {
                    "voltage": "400V",
                    "type": "end_drive",
                    "max_traction_force_n": 500,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4,
                    "temperature_range": "-20°C to +60°C"
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "X45",
                "name": "X45 Intermediate drive unit 24V",
                "component_type": "drive_unit",
                "specifications": {
                    "voltage": "24V",
                    "type": "intermediate",
                    "max_traction_force_n": 300,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "X45",
                "name": "X45 Idler end unit",
                "component_type": "idler_unit",
                "specifications": {
                    "type": "end_idler",
                    "compatible_chains": ["plain", "cleated", "steel_top"]
                },
                "compatibility": ["X45"],
                "image_url": None
            },

            # XS Drive Units
            {
                "system_code": "XS",
                "name": "XS End drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "max_traction_force_n": 700,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4,
                    "type": "end_drive"
                },
                "compatibility": ["XS"],
                "image_url": None
            },
            {
                "system_code": "XS",
                "name": "XS Double drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "double",
                    "max_traction_force_n": 500,
                    "teeth_count": 16,
                    "chain_pitch_mm": 25.4,
                    "center_distance_options": ["55mm", "90-350mm"]
                },
                "compatibility": ["XS"],
                "image_url": None
            },

            # X65 Drive Units
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
                "compatibility": ["X65"],
                "image_url": None
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
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Catenary drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "catenary",
                    "max_traction_force_n": 200,
                    "teeth_count": 11,
                    "chain_pitch_mm": 25.4
                },
                "compatibility": ["X65"],
                "image_url": None
            },

            # X85 Drive Units
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
                "compatibility": ["X85"],
                "image_url": None
            },
            {
                "system_code": "X85",
                "name": "X85 Heavy drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "heavy",
                    "max_traction_force_n": 1250,
                    "teeth_count": 12,
                    "chain_pitch_mm": 33.5
                },
                "compatibility": ["X85"],
                "image_url": None
            },

            # XH Drive Units
            {
                "system_code": "XH",
                "name": "XH Synchronous drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "synchronous",
                    "max_traction_force_n": 1250,
                    "teeth_count": 12,
                    "chain_pitch_mm": 35.5
                },
                "compatibility": ["XH"],
                "image_url": None
            },

            # XK Drive Units
            {
                "system_code": "XK",
                "name": "XK Standard drive unit",
                "component_type": "drive_unit",
                "specifications": {
                    "type": "standard",
                    "max_traction_force_n": 1250,
                    "teeth_count": 11,
                    "chain_pitch_mm": 38.1
                },
                "compatibility": ["XK", "XKP"],
                "image_url": None
            },
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
                "compatibility": ["XK", "XKP"],
                "image_url": None
            },

            # WL Drive Units
            {
                "system_code": "WL322",
                "name": "WL End drive unit (5 sprockets)",
                "component_type": "drive_unit",
                "specifications": {
                    "sprocket_count": 5,
                    "belt_pitch_mm": 25.4,
                    "width_mm": 322
                },
                "compatibility": ["WL322", "WL424", "WL626"],
                "image_url": None
            }
        ]

        return drive_units

    def extract_chain_data(self) -> List[Dict]:
        """Extract comprehensive chain data from catalog"""

        chains = [
            # X45 Chains
            {
                "system_code": "X45",
                "name": "X45 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 300,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "X45",
                "name": "X45 Steel top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "steel_top",
                    "pitch_mm": 25.4,
                    "material": "POM + steel",
                    "max_working_tension_n": 300,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "X45",
                "name": "X45 Friction top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "friction_top",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 300,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X45"],
                "image_url": None
            },

            # XS Chains
            {
                "system_code": "XS",
                "name": "XS Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 500,
                    "pivot_material": "PA66"
                },
                "compatibility": ["XS"],
                "image_url": None
            },
            {
                "system_code": "XS",
                "name": "XS Friction top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "friction_top",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 500,
                    "pivot_material": "PA66"
                },
                "compatibility": ["XS"],
                "image_url": None
            },

            # X65 Chains
            {
                "system_code": "X65",
                "name": "X65 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 1000,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Universal chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "universal",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 1000,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Cleated chain Type A",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "cleated_a",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 1000,
                    "pivot_material": "PA66",
                    "cleat_height_mm": 12
                },
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Flexible cleat chain Type B",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "flexible_cleat_b",
                    "pitch_mm": 25.4,
                    "material": "POM",
                    "max_working_tension_n": 1000,
                    "pivot_material": "PA66",
                    "cleat_flexibility": "high"
                },
                "compatibility": ["X65"],
                "image_url": None
            },

            # X85 Chains
            {
                "system_code": "X85",
                "name": "X85 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 33.5,
                    "material": "POM",
                    "max_working_tension_n": 1250,
                    "pivot_material": "PA66"
                },
                "compatibility": ["X85"],
                "image_url": None
            },
            {
                "system_code": "X85",
                "name": "X85 Roller top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "roller_top",
                    "pitch_mm": 33.5,
                    "material": "POM",
                    "max_working_tension_n": 1250,
                    "pivot_material": "PA66",
                    "roller_type": "low_friction"
                },
                "compatibility": ["X85"],
                "image_url": None
            },
            {
                "system_code": "X85",
                "name": "X85 Roller cleat chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "roller_cleat",
                    "pitch_mm": 33.5,
                    "material": "POM",
                    "max_working_tension_n": 1250,
                    "pivot_material": "PA66",
                    "roller_type": "low_friction",
                    "cleat_height_mm": 16
                },
                "compatibility": ["X85"],
                "image_url": None
            },

            # X180/X300 Chains
            {
                "system_code": "X180",
                "name": "X180 Plain chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "plain",
                    "pitch_mm": 33.5,
                    "material": "POM",
                    "max_working_tension_n": 1250,
                    "pivot_material": "PA66",
                    "slide_rails": 4
                },
                "compatibility": ["X180", "X300"],
                "image_url": None
            },
            {
                "system_code": "X300",
                "name": "X300 Friction top chain",
                "component_type": "chain",
                "specifications": {
                    "chain_type": "friction_top",
                    "pitch_mm": 33.5,
                    "material": "POM",
                    "max_working_tension_n": 1250,
                    "pivot_material": "PA66",
                    "slide_rails": 4
                },
                "compatibility": ["X180", "X300"],
                "image_url": None
            }
        ]

        return chains

    def extract_bend_components(self) -> List[Dict]:
        """Extract bend component data"""

        bends = [
            # Standard bends for different systems
            {
                "system_code": "X45",
                "name": "X45 Plain bend 90°",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "plain",
                    "angle_degrees": 90,
                    "bend_factor": 1.6,
                    "recommended_use": "exceptional_cases"
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "XS",
                "name": "XS Wheel bend 90°",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "wheel",
                    "angle_degrees": 90,
                    "bend_factor": 1.0,
                    "recommended_use": "normal_applications"
                },
                "compatibility": ["XS"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Vertical bend",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "vertical",
                    "angle_degrees": 90,
                    "bend_factor": 1.6,
                    "direction": "up_down"
                },
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X85",
                "name": "X85 Wheel bend 45°",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "wheel",
                    "angle_degrees": 45,
                    "bend_factor": 1.0,
                    "recommended_use": "normal_applications"
                },
                "compatibility": ["X85"],
                "image_url": None
            },
            {
                "system_code": "XK",
                "name": "XK Wheel bend variable",
                "component_type": "bend",
                "specifications": {
                    "bend_type": "wheel",
                    "angle_options": [30, 45, 60, 90],
                    "bend_factor": 1.0,
                    "recommended_use": "normal_applications"
                },
                "compatibility": ["XK", "XKP"],
                "image_url": None
            }
        ]

        return bends

    def extract_guide_rail_components(self) -> List[Dict]:
        """Extract guide rail component data"""

        guide_rails = [
            {
                "system_code": "X45",
                "name": "X45 Fixed guide rail bracket (aluminium)",
                "component_type": "guide_rail_bracket",
                "specifications": {
                    "bracket_type": "fixed",
                    "material": "aluminium",
                    "adjustable": False
                },
                "compatibility": ["X45"],
                "image_url": None
            },
            {
                "system_code": "XS",
                "name": "XS Adjustable guide rail bracket (aluminium)",
                "component_type": "guide_rail_bracket",
                "specifications": {
                    "bracket_type": "adjustable",
                    "material": "aluminium",
                    "adjustable": True,
                    "adjustment_range_mm": "50-200"
                },
                "compatibility": ["XS"],
                "image_url": None
            },
            {
                "system_code": "X65",
                "name": "X65 Guide rail profile",
                "component_type": "guide_rail",
                "specifications": {
                    "profile_type": "standard",
                    "material": "aluminium",
                    "length_options_mm": [500, 1000, 2000, 3000]
                },
                "compatibility": ["X65"],
                "image_url": None
            },
            {
                "system_code": "X85",
                "name": "X85 Flexible roller guide rail",
                "component_type": "guide_rail",
                "specifications": {
                    "profile_type": "flexible_roller",
                    "material": "aluminium_with_rollers",
                    "flexibility": "high",
                    "roller_count_per_meter": 20
                },
                "compatibility": ["X85"],
                "image_url": None
            }
        ]

        return guide_rails

    def add_components_batch(self, components: List[Dict]) -> bool:
        """Add components to database in batches"""
        try:
            # Insert in batches of 10 to avoid API limits
            batch_size = 10
            total_inserted = 0

            for i in range(0, len(components), batch_size):
                batch = components[i:i + batch_size]

                result = self.supabase.table(
                    "components").insert(batch).execute()
                total_inserted += len(batch)

                print(
                    f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} components")

            print(f"🎉 Successfully inserted {total_inserted} components total")
            return True

        except Exception as e:
            print(f"❌ Error inserting components: {e}")
            return False

    def populate_all_components(self):
        """Main function to populate all component data"""
        print("🚀 Starting FlexLink component data extraction...")
        print("=" * 60)

        # Extract all component types
        print("📦 Extracting drive units...")
        drive_units = self.extract_drive_units_data()

        print("⛓️ Extracting chains...")
        chains = self.extract_chain_data()

        print("🔄 Extracting bends...")
        bends = self.extract_bend_components()

        print("🛤️ Extracting guide rails...")
        guide_rails = self.extract_guide_rail_components()

        # Combine all components
        all_components = drive_units + chains + bends + guide_rails

        print(f"\n📊 Summary:")
        print(f"   • Drive units: {len(drive_units)}")
        print(f"   • Chains: {len(chains)}")
        print(f"   • Bends: {len(bends)}")
        print(f"   • Guide rails: {len(guide_rails)}")
        print(f"   • Total components: {len(all_components)}")

        # Insert into database
        print(
            f"\n💾 Inserting {len(all_components)} components into database...")
        success = self.add_components_batch(all_components)

        if success:
            print("\n🎉 Component extraction completed successfully!")
            print("\n📋 Next steps:")
            print("1. Refresh your web interface to see the new components")
            print("2. Add more systems from other catalogs")
            print("3. Implement component compatibility logic")
            print("4. Add pricing and availability data")
        else:
            print("\n❌ Component extraction failed. Check the errors above.")

    def export_to_json(self):
        """Export all data to JSON for backup"""
        try:
            # Create data directory
            os.makedirs("data", exist_ok=True)

            # Get all data from database
            systems = self.supabase.table(
                "conveyor_systems").select("*").execute()
            components = self.supabase.table(
                "components").select("*").execute()
            configurations = self.supabase.table(
                "user_configurations").select("*").execute()

            # Export to JSON files
            with open("data/systems_backup.json", "w") as f:
                json.dump(systems.data, f, indent=2, default=str)

            with open("data/components_backup.json", "w") as f:
                json.dump(components.data, f, indent=2, default=str)

            with open("data/configurations_backup.json", "w") as f:
                json.dump(configurations.data, f, indent=2, default=str)

            print("✅ Data exported to JSON files in 'data/' folder")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False


if __name__ == "__main__":
    print("🔧 FlexLink Advanced Data Extractor")
    print("=" * 50)

    extractor = FlexLinkDataExtractor()

    # Menu
    print("\nChoose an option:")
    print("1. Populate all components (recommended)")
    print("2. Export current data to JSON")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        extractor.populate_all_components()
    elif choice == "2":
        extractor.export_to_json()
    elif choice == "3":
        extractor.populate_all_components()
        extractor.export_to_json()
    else:
        print("Invalid choice. Running full population...")
        extractor.populate_all_components()
