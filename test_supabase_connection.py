#!/usr/bin/env python3
"""
Test Supabase connection for the web viewer
"""

import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = 'https://vpgawhkvfibhzafkdcsa.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZ2F3aGt2ZmliaHphZmtkY3NhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3Nzk0NjAsImV4cCI6MjA2OTM1NTQ2MH0.QjGdS6_Y4Dkud1E2wGBI11UE1UXljvMW5v0FQm1tJmc'


def test_connection():
    """Test basic connection to Supabase"""
    print("🔍 Testing Supabase Connection...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    print()

    # Test 1: Basic table access
    print("📊 Test 1: Basic table access")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/product_images?select=count",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Test 2: Get first few records
    print("📋 Test 2: Get first few records")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/product_images?select=*&limit=3",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} records")
            if data:
                print(f"First record keys: {list(data[0].keys())}")
                print(f"Sample data: {json.dumps(data[0], indent=2)[:300]}...")
        else:
            print(f"Error response: {response.text}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Test 3: Check RLS status
    print("🔒 Test 3: Check RLS and permissions")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/product_images?select=id&limit=1",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Prefer': 'count=exact'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()


def test_web_viewer_request():
    """Test the exact request the web viewer makes"""
    print("🌐 Test 4: Web viewer request simulation")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/product_images?select=*",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} images")
            if data:
                print(f"Sample image data:")
                sample = data[0]
                print(f"  - ID: {sample.get('id')}")
                print(f"  - Page: {sample.get('page_number')}")
                print(f"  - Product: {sample.get('product_code')}")
                print(f"  - Component: {sample.get('component_type')}")
                print(
                    f"  - Has image_data: {'Yes' if sample.get('image_data') else 'No'}")
        else:
            print(f"❌ Error: {response.text}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()


def main():
    print("🚀 Supabase Connection Test")
    print("=" * 40)
    print()

    test_connection()
    test_web_viewer_request()

    print("✅ Test completed!")


if __name__ == "__main__":
    main()
