#!/usr/bin/env python3
"""
Command-line browser for FlexLink images with product associations
"""

import requests
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = 'https://vpgawhkvfibhzafkdcsa.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZ2F3aGt2ZmliaHphZmtkY3NhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3Nzk0NjAsImV4cCI6MjA2OTM1NTQ2MH0.QjGdS6_Y4Dkud1E2wGBI11UE1UXljvMW5v0FQm1tJmc'


class FlexLinkImageBrowser:
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1/product_images"
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }

    def get_images(self, limit: int = 20, product_code: str = None,
                   component_type: str = None, is_blueprint: bool = None) -> List[Dict[str, Any]]:
        """Get images from database with optional filters"""
        url = f"{self.base_url}?select=*&limit={limit}"

        filters = []
        if product_code:
            filters.append(f"product_code=eq.{product_code}")
        if component_type:
            filters.append(f"component_type=eq.{component_type}")
        if is_blueprint is not None:
            filters.append(f"is_blueprint=eq.{str(is_blueprint).lower()}")

        if filters:
            url += '&' + '&'.join(filters)

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/get_image_stats",
                headers={**self.headers, 'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                return response.json()[0] if response.json() else {}
            else:
                print(f"❌ Error getting stats: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}

    def display_images(self, images: List[Dict[str, Any]]):
        """Display images in a formatted way"""
        if not images:
            print("📭 No images found matching your criteria.")
            return

        print(f"\n📋 Found {len(images)} images:")
        print("=" * 80)

        for i, image in enumerate(images, 1):
            print(f"\n🖼️  Image {i}:")
            print(f"   📄 Page: {image.get('page_number', 'N/A')}")
            print(
                f"   🏷️  Product: {image.get('product_code', 'Not specified')}")
            print(
                f"   🔧 Component: {image.get('component_type', 'Not specified')}")
            print(f"   📐 Quality: {image.get('image_quality_score', 'N/A')}")
            print(
                f"   🔧 Blueprint: {'Yes' if image.get('is_blueprint') else 'No'}")
            print(f"   📅 Date: {image.get('extraction_date', 'N/A')}")

            if image.get('associated_text'):
                text = image['associated_text'][:100] + "..." if len(
                    image['associated_text']) > 100 else image['associated_text']
                print(f"   📝 Text: {text}")

            if i < len(images):
                print("   " + "-" * 60)

    def display_statistics(self, stats: Dict[str, Any]):
        """Display database statistics"""
        print("\n📊 Database Statistics:")
        print("=" * 40)
        print(f"📸 Total Images: {stats.get('total_images', 0)}")
        print(f"🔧 Blueprint Images: {stats.get('blueprint_images', 0)}")
        print(
            f"🏷️  Unique Product Codes: {stats.get('unique_product_codes', 0)}")
        print(
            f"🔧 Unique Component Types: {stats.get('unique_component_types', 0)}")
        print(
            f"⭐ Average Quality Score: {stats.get('avg_quality_score', 0):.2f}")

    def interactive_menu(self):
        """Interactive menu for browsing images"""
        while True:
            print("\n" + "=" * 60)
            print("🔧 FlexLink Image Browser")
            print("=" * 60)
            print("1. 📋 Show recent images (last 20)")
            print("2. 🔍 Search by product code")
            print("3. 🔧 Search by component type")
            print("4. 🔧 Show blueprint images only")
            print("5. 📊 Show database statistics")
            print("6. 🌐 Open web viewer")
            print("0. ❌ Exit")
            print("-" * 60)

            choice = input("Choose an option (0-6): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                images = self.get_images(limit=20)
                self.display_images(images)
            elif choice == "2":
                product_code = input(
                    "Enter product code (e.g., X45, X65): ").strip()
                if product_code:
                    images = self.get_images(
                        limit=50, product_code=product_code)
                    self.display_images(images)
                else:
                    print("❌ Please enter a product code.")
            elif choice == "3":
                print("Available component types:")
                print("  - chain, sprocket, motor, drive, gear, wheel")
                print("  - roller, guide, plate, bracket, support, track, link")
                component_type = input(
                    "Enter component type: ").strip().lower()
                if component_type:
                    images = self.get_images(
                        limit=50, component_type=component_type)
                    self.display_images(images)
                else:
                    print("❌ Please enter a component type.")
            elif choice == "4":
                images = self.get_images(limit=50, is_blueprint=True)
                self.display_images(images)
            elif choice == "5":
                stats = self.get_statistics()
                self.display_statistics(stats)
            elif choice == "6":
                print("🌐 Opening web viewer...")
                import subprocess
                try:
                    subprocess.run(
                        ["python3", "open_web_viewer.py"], check=True)
                except Exception as e:
                    print(f"❌ Error opening web viewer: {e}")
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    print("🚀 FlexLink Image Browser")
    print("=" * 40)

    browser = FlexLinkImageBrowser()

    # Test connection
    print("🔍 Testing database connection...")
    test_images = browser.get_images(limit=1)
    if test_images:
        print("✅ Connected to database successfully!")
        browser.interactive_menu()
    else:
        print("❌ Failed to connect to database. Please check your configuration.")


if __name__ == "__main__":
    main()
