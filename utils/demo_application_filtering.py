#!/usr/bin/env python3
"""
Demonstration of Application Filtering for FlexLink Components
Shows how to filter components by application criteria like "washable", "food grade", etc.
"""

import json
from typing import List, Dict, Any


def load_components(file_path: str) -> List[Dict[str, Any]]:
    """Load components from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def filter_components_by_application(components: List[Dict[str, Any]],
                                     washable: bool = None,
                                     food_grade: bool = None,
                                     hygienic: bool = None,
                                     heavy_duty: bool = None,
                                     system_code: str = None) -> List[Dict[str, Any]]:
    """Filter components by application criteria"""
    filtered = []

    for component in components:
        # Check system code
        if system_code and component.get('system_code') != system_code:
            continue

        # Check application flags (if they exist)
        if washable is not None and component.get('washable') != washable:
            continue
        if food_grade is not None and component.get('food_grade') != food_grade:
            continue
        if hygienic is not None and component.get('hygienic') != hygienic:
            continue
        if heavy_duty is not None and component.get('heavy_duty') != heavy_duty:
            continue

        # Check system applications and features
        system_apps = component.get('system_applications', [])
        system_features = component.get('system_features', [])

        # Check for keywords in component name and description
        component_text = f"{component.get('component_name', '')} {component.get('description', '')}".lower(
        )

        # Apply filters based on keywords
        if washable and 'washable' not in component_text and 'hygienic' not in component_text:
            continue
        if food_grade and 'food' not in component_text and 'hygienic' not in component_text:
            continue
        if hygienic and 'hygienic' not in component_text and 'sanitary' not in component_text:
            continue
        if heavy_duty and 'heavy' not in component_text and 'industrial' not in component_text:
            continue

        filtered.append(component)

    return filtered


def demonstrate_filtering():
    """Demonstrate application filtering with sample data"""
    print("🔍 FlexLink Application Filtering Demo")
    print("=" * 50)

    # Load existing components
    try:
        components = load_components(
            'data/large_catalog_extraction/all_components.json')
        print(f"📊 Loaded {len(components)} components")
    except FileNotFoundError:
        print("❌ No components file found. Using sample data.")
        components = [
            {
                "system_code": "XH",
                "component_type": "chain",
                "component_name": "XH Hygienic Chain",
                "description": "Stainless steel hygienic chain for food grade applications",
                "system_applications": ["hygienic", "food grade", "washable"],
                "system_features": ["hygienic", "food grade", "washable", "stainless steel"],
                "washable": True,
                "food_grade": True,
                "hygienic": True,
                "heavy_duty": False
            },
            {
                "system_code": "X45",
                "component_type": "chain",
                "component_name": "X45 Standard Chain",
                "description": "General purpose modular chain",
                "system_applications": ["general purpose", "light duty", "modular"],
                "system_features": ["modular", "flexible", "easy assembly"],
                "washable": False,
                "food_grade": False,
                "hygienic": False,
                "heavy_duty": False
            },
            {
                "system_code": "X65",
                "component_type": "chain",
                "component_name": "X65 Heavy Duty Chain",
                "description": "Industrial heavy duty chain for high load applications",
                "system_applications": ["heavy duty", "industrial", "robust"],
                "system_features": ["heavy duty", "robust", "industrial"],
                "washable": False,
                "food_grade": False,
                "hygienic": False,
                "heavy_duty": True
            }
        ]

    # Demo 1: Find washable components
    print("\n🧼 Washable Components:")
    washable_components = filter_components_by_application(
        components, washable=True)
    for comp in washable_components[:5]:  # Show first 5
        print(f"  • {comp.get('system_code')} - {comp.get('component_name')}")
    print(f"  Found {len(washable_components)} washable components")

    # Demo 2: Find food grade components
    print("\n🍽️  Food Grade Components:")
    food_grade_components = filter_components_by_application(
        components, food_grade=True)
    for comp in food_grade_components[:5]:
        print(f"  • {comp.get('system_code')} - {comp.get('component_name')}")
    print(f"  Found {len(food_grade_components)} food grade components")

    # Demo 3: Find heavy duty components
    print("\n🏭 Heavy Duty Components:")
    heavy_duty_components = filter_components_by_application(
        components, heavy_duty=True)
    for comp in heavy_duty_components[:5]:
        print(f"  • {comp.get('system_code')} - {comp.get('component_name')}")
    print(f"  Found {len(heavy_duty_components)} heavy duty components")

    # Demo 4: Find XH system components (typically hygienic)
    print("\n🧽 XH System Components (Hygienic):")
    xh_components = filter_components_by_application(
        components, system_code="XH")
    for comp in xh_components[:5]:
        print(f"  • {comp.get('component_name')}")
    print(f"  Found {len(xh_components)} XH components")

    # Demo 5: Find components that are both washable AND food grade
    print("\n🧼🍽️  Washable AND Food Grade Components:")
    washable_food_components = filter_components_by_application(
        components, washable=True, food_grade=True
    )
    for comp in washable_food_components[:5]:
        print(f"  • {comp.get('system_code')} - {comp.get('component_name')}")
    print(
        f"  Found {len(washable_food_components)} washable and food grade components")


def show_system_applications():
    """Show what applications each system is suitable for"""
    print("\n📋 System Applications Guide:")
    print("=" * 40)

    system_apps = {
        "XH": {
            "applications": ["Food & Beverage", "Pharmaceutical", "Cosmetics"],
            "features": ["Hygienic", "Washable", "Stainless Steel", "FDA Approved"],
            "description": "Hygienic system for food grade applications"
        },
        "XK": {
            "applications": ["Chemical Industry", "Corrosive Environments"],
            "features": ["Chemical Resistant", "Corrosive Resistant", "Acid Resistant"],
            "description": "Chemical resistant system for harsh environments"
        },
        "X45": {
            "applications": ["General Manufacturing", "Assembly Lines", "Packaging"],
            "features": ["Modular", "Flexible", "Easy Assembly", "Cost Effective"],
            "description": "General purpose modular system"
        },
        "X65": {
            "applications": ["Heavy Industry", "High Load Applications", "Automotive"],
            "features": ["Heavy Duty", "High Load Capacity", "Industrial Grade"],
            "description": "Heavy duty system for industrial applications"
        },
        "X85/X180/X300": {
            "applications": ["Heavy Industry", "Mining", "Construction"],
            "features": ["Ultra Heavy Duty", "Extreme Load Capacity", "Rugged"],
            "description": "Ultra heavy duty systems for extreme applications"
        }
    }

    for system, info in system_apps.items():
        print(f"\n🔧 {system} System:")
        print(f"   Applications: {', '.join(info['applications'])}")
        print(f"   Features: {', '.join(info['features'])}")
        print(f"   Description: {info['description']}")


if __name__ == "__main__":
    demonstrate_filtering()
    show_system_applications()

    print("\n💡 To implement this in your web app:")
    print("   1. Update database schema with application fields")
    print("   2. Extract system descriptions from catalog")
    print("   3. Add filter checkboxes to web interface")
    print("   4. Query database by application criteria")
