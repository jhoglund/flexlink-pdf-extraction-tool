#!/usr/bin/env python3
"""
FlexLink Configuration Tool - One-Click Setup
Run this script to create all project files automatically
"""

import os


def create_project_structure():
    """Create the complete FlexLink project structure"""

    print("🚀 Setting up FlexLink Configuration Tool...")

    # Create directories
    os.makedirs("web", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Create .env file
    env_content = """SUPABASE_URL=https://vpgawhkvfibhzafkdcsa.supabase.co
SUPABASE_ANON_KEY=sb_publishable_f2c0fviCPr30-WvxPQvDOw_BT061Zxc"""

    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created .env")

    # Create requirements.txt
    requirements_content = """supabase==2.3.0
python-dotenv==1.0.0
requests==2.31.0"""

    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt")

    # Create .gitignore
    gitignore_content = """.env
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.vscode/
.cursor/
.DS_Store
Thumbs.db
*.log"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")

    # Create README.md
    readme_content = """# FlexLink Configuration Tool

A prototype configuration tool for FlexLink conveyor systems.

## Quick Start

1. **Setup:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test connection:**
   ```bash
   python test_connection.py
   ```

3. **Run manager:**
   ```bash
   python flexlink_manager.py
   ```

4. **Open web interface:**
   - Open `web/index.html` in browser
   - Or: `python -m http.server 8000` then go to `http://localhost:8000/web/`

## Files Overview

- `test_connection.py` - Test your Supabase connection
- `flexlink_manager.py` - Interactive command-line tool
- `web/index.html` - Web-based configuration interface  
- `supabase_schema.sql` - Run this in Supabase SQL Editor first

## Next Steps

1. Run the SQL schema in Supabase
2. Test the connection
3. Use either the Python CLI or web interface
4. Extend with more components and features"""

    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")

    # Create test_connection.py
    test_connection_content = '''#!/usr/bin/env python3
"""
Quick test to verify Supabase connection works
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_supabase_connection():
    print("🚀 Testing FlexLink Supabase Connection")
    print("=" * 50)
    
    # Get credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    # Check if credentials exist
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
        
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY not found in .env file") 
        return False
    
    print(f"✅ Found SUPABASE_URL: {supabase_url}")
    print(f"✅ Found SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test database connection by counting systems
        result = supabase.table("conveyor_systems").select("count", count="exact").execute()
        system_count = result.count
        
        print(f"✅ Database connected! Found {system_count} conveyor systems")
        
        # Show a few systems as example
        systems = supabase.table("conveyor_systems").select("code, name").limit(3).execute()
        
        print("\\n📋 Sample systems in database:")
        for system in systems.data:
            print(f"   • {system['code']}: {system['name']}")
            
        print(f"\\n🎉 Connection test successful!")
        print("You're ready to run the full data extractor.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\\nTroubleshooting:")
        print("1. Check that you've run the SQL schema in Supabase SQL Editor")
        print("2. Verify your publishable key is correct")
        print("3. Make sure your .env file is in the same folder as this script")
        return False

if __name__ == "__main__":
    test_supabase_connection()'''

    with open("test_connection.py", "w") as f:
        f.write(test_connection_content)
    print("✅ Created test_connection.py")

    # Create placeholder files that need manual content
    placeholder_files = {
        "supabase_schema.sql": "-- Copy the SQL schema from the artifacts above",
        "flexlink_manager.py": "# Copy the FlexLink Manager script from the artifacts above",
        "web/index.html": "<!-- Copy the complete web interface from the artifacts above -->"
    }

    for filename, placeholder in placeholder_files.items():
        with open(filename, "w") as f:
            f.write(placeholder)
        print(f"⚠️  Created {filename} (needs content from artifacts)")

    print("\n" + "="*60)
    print("🎉 Project structure created successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Copy content from the artifacts above into these files:")
    print("   - supabase_schema.sql")
    print("   - flexlink_manager.py")
    print("   - web/index.html")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Run the SQL schema in your Supabase dashboard")
    print("\n4. Test connection:")
    print("   python test_connection.py")
    print("\n5. Open in Cursor:")
    print("   cursor .")


if __name__ == "__main__":
    create_project_structure()'''
    
    with open("setup.py", "w") as f:
        f.write(setup_script_content)
    print("✅ Created setup.py")

setup_script_content = '''  # !/usr/bin/env python3
"""
FlexLink Configuration Tool - One-Click Setup
Run this script to create all project files automatically
"""


def create_project_structure():
    """Create the complete FlexLink project structure"""

    print("🚀 Setting up FlexLink Configuration Tool...")

    # Create directories
    os.makedirs("web", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Create .env file
    env_content = """SUPABASE_URL=https://vpgawhkvfibhzafkdcsa.supabase.co
SUPABASE_ANON_KEY=sb_publishable_f2c0fviCPr30-WvxPQvDOw_BT061Zxc"""

    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created .env")

    # Create requirements.txt
    requirements_content = """supabase==2.3.0
python-dotenv==1.0.0
requests==2.31.0"""

    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt")

    # Create .gitignore
    gitignore_content = """.env
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.vscode/
.cursor/
.DS_Store
Thumbs.db
*.log"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")

    # Create README.md
    readme_content = """# FlexLink Configuration Tool

A prototype configuration tool for FlexLink conveyor systems.

## Quick Start

1. **Setup:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test connection:**
   ```bash
   python test_connection.py
   ```

3. **Run manager:**
   ```bash
   python flexlink_manager.py
   ```

4. **Open web interface:**
   - Open `web/index.html` in browser
   - Or: `python -m http.server 8000` then go to `http://localhost:8000/web/`

## Files Overview

- `test_connection.py` - Test your Supabase connection
- `flexlink_manager.py` - Interactive command-line tool
- `web/index.html` - Web-based configuration interface  
- `supabase_schema.sql` - Run this in Supabase SQL Editor first

## Next Steps

1. Run the SQL schema in Supabase
2. Test the connection
3. Use either the Python CLI or web interface
4. Extend with more components and features"""

    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")

    print("\\n" + "="*60)
    print("🎉 Basic project structure created!")
    print("="*60)
    print("\\n📋 You still need to copy these from the artifacts above:")
    print("   - supabase_schema.sql (Complete Supabase Schema)")
    print("   - test_connection.py (Quick Connection Test)")
    print("   - flexlink_manager.py (FlexLink Manager - Complete Script)")
    print("   - web/index.html (Complete Web Interface)")
    print("\\n🚀 Then run: pip install -r requirements.txt")


if __name__ == "__main__":
    create_project_structure()
