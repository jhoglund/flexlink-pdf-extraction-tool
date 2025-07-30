# FlexLink PDF Extraction Tool

A comprehensive tool for extracting FlexLink component specifications from PDF catalogs and uploading them to Supabase. This repository focuses on data extraction and processing, while the configuration interface is handled in a separate Rails application.

## 🏗️ Project Structure

```
flexlink-pdf-extraction-tool/
├── data/                          # Extracted component data
│   ├── large_catalog_extraction/  # Main catalog extraction results
│   └── enhanced_components.json   # Components with application info
├── web/                           # Web interface for viewing data
│   └── index.html                 # Component viewer
├── extractors/                    # Core PDF extraction scripts
│   ├── component_extractor.py     # Main component extractor
│   ├── enhanced_component_extractor.py  # Enhanced with application info
│   ├── extract_large_catalog_offline.py # Large catalog processor
│   ├── extract_large_catalog.py   # Online catalog processor
│   ├── manual_extractor.py        # Manual extraction tool
│   ├── pdf_extractor.py           # PDF processing utilities
│   ├── process_main_catalog.py    # Main catalog processor
│   ├── simple_extractor.py        # Simple extraction tool
│   └── upload_to_database.py     # Database uploader
├── database/                      # Database schemas and migrations
│   ├── database_schema.sql        # Main database schema
│   ├── update_database_schema.sql # Application fields schema
│   ├── create_table_simple.sql    # Simple table creation
│   └── fix_database_schema.sql    # Schema fixes
├── utils/                         # Utility scripts
│   ├── advanced_extractor.py      # Advanced extraction utilities
│   ├── check_upload_status.py     # Upload status checker
│   ├── clear_database.py          # Database cleanup
│   ├── create_database_table.py   # Table creation utilities
│   ├── demo_application_filtering.py # Application filtering demo
│   ├── setup_database_schema.py   # Schema setup utilities
│   ├── setup_database.py          # Database setup
│   └── test_connection.py         # Connection testing
├── docs/                          # Documentation
│   ├── README_COMPONENT_EXTRACTION.md
│   └── USAGE_GUIDE.md
├── requirements.txt               # Python dependencies
├── setup.py                      # Installation script
└── README.md                     # Project documentation
```

## 🚀 Current Status

✅ **Completed:**
- 603 components extracted from FlexLink catalog
- All components uploaded to Supabase database
- Basic web interface for component viewing
- Resilient upload system with progress tracking

🔄 **In Progress:**
- Enhanced extraction with application information
- System-level intro text extraction
- Application filtering capabilities

🎯 **Next:**
- Rails-based guided configuration tool
- Step-by-step wizard interface
- 3D visualization and optimization

## 📊 Data Overview

**Extracted Components:**
- **603 total components** from 500+ page catalog
- **102 XH components** (hygienic system)
- **Multiple system types:** X45, XS, X65, X85, X180, X300, XH, XK
- **Component types:** Chains, Sprockets, Bearings, Tracks, Drive Units, Bends

**Database Schema:**
- `component_specifications` table in Supabase
- JSONB fields for flexible specifications
- Application flags for filtering
- Full text search capabilities

## 🛠️ Technology Stack

**Current:**
- **Python** - Data extraction and processing
- **Supabase** - PostgreSQL database
- **HTML/CSS/JavaScript** - Web interface
- **PyMuPDF/pdfplumber** - PDF processing

**Current:**
- **Python** - PDF processing and data extraction
- **Supabase** - Component database storage
- **PyMuPDF/pdfplumber** - PDF processing libraries
- **HTML/CSS/JavaScript** - Web interface for data viewing

**Related Project:**
- **Rails Application** - Separate repository for guided configuration tool

## 🔧 Setup Instructions

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/jhoglund/flexlink-pdf-extraction-tool.git
cd flexlink-pdf-extraction-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Set up Supabase credentials in .env file
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# Run database schema
# Copy database_schema.sql to Supabase SQL Editor and execute
```

### 3. Extract Components
```bash
# Extract from catalog
python extract_large_catalog_offline.py "path/to/catalog.pdf"

# Upload to database
python upload_to_database.py --batch-size 10
```

## 🎯 Guided Configuration Tool (Planned)

The Rails application will provide:

### Step 1: Challenge Definition
- Extending existing line
- New production line
- Replacing equipment

### Step 2: Environmental Requirements
- Cleanroom
- Washdown
- Standard
- ESD-safe

### Step 3: Solution Complexity
- Simple extension
- Custom configuration
- Complete system

### Step 4: Progressive Configuration
- Component selection based on requirements
- Automatic compatibility checking
- Cost optimization

### Step 5: 3D Visualization
- Interactive 3D model
- Optimization suggestions
- Export capabilities

## 📈 Application Filtering

Filter components by:
- **Washable** - Hygienic systems (XH)
- **Food Grade** - FDA approved components
- **Heavy Duty** - Industrial systems (X65, X85, X180, X300)
- **Chemical Resistant** - Corrosive environments (XK)
- **High Temperature** - Heat resistant applications

## 🔄 Resume Capability

All extraction and upload processes support:
- **Progress tracking** - Resume from interruptions
- **Batch processing** - Handle large catalogs
- **Error recovery** - Retry failed operations
- **Data persistence** - Local backup of all results

## 📝 Development Notes

**Current Data:**
- 603 components in Supabase
- All specifications and dimensions captured
- System codes and compatibility mapped
- Ready for Rails integration

**Next Steps:**
1. **Extract additional catalogs** and upload to Supabase
2. **Enhance extraction algorithms** for better accuracy
3. **Improve data validation** and error handling
4. **Create Rails application** (separate repository) for configuration interface
5. **Set up automated data sync** between extraction and Rails app

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

[Your License Here]

---

**Last Updated:** July 29, 2024  
**Status:** ✅ Core extraction complete, 🚧 Rails development pending 