# FlexLink Component Specification Extractor

This tool extracts detailed component specifications from FlexLink catalog PDFs and formats them for database storage.

## Features

- **PDF Text Extraction**: Uses PyMuPDF and pdfplumber for robust text extraction
- **Intelligent Parsing**: Automatically detects component types and extracts specifications
- **Multiple Output Formats**: JSON, CSV, and direct database upload
- **Comprehensive Data**: Extracts specifications, dimensions, materials, compatibility, weights, and prices
- **Command Line Interface**: Easy-to-use CLI for batch processing

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** (create a `.env` file):
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. **Create database schema**:
   - Run the SQL commands in `database_schema.sql` in your Supabase SQL editor
   - This creates the `component_specifications` table with proper indexes and functions

## Usage

### Command Line Interface

The main tool is `extract_components.py`:

```bash
# Test with sample data
python extract_components.py --test

# Extract from a single PDF
python extract_components.py catalog.pdf --output components.json

# Extract from multiple PDFs and save to CSV
python extract_components.py *.pdf --format csv --output components.csv

# Extract and upload to database
python extract_components.py catalog.pdf --upload

# Verbose output
python extract_components.py catalog.pdf --verbose
```

### Python API

```python
from component_extractor import ComponentSpecificationExtractor

# Initialize extractor
extractor = ComponentSpecificationExtractor()

# Extract from PDF
components = extractor.extract_from_pdf('catalog.pdf')

# Save to files
extractor.save_to_json(components, 'output.json')
extractor.save_to_csv(components, 'output.csv')

# Upload to database
extractor.upload_to_database(components)
```

## Component Types Supported

The extractor recognizes and extracts specifications for:

### 1. **Chains**
- Pitch, width, max load, material, type
- Examples: Plain chain, cleated chain, steel top chain

### 2. **Sprockets**
- Teeth count, bore size, pitch, material, type
- Examples: Drive sprockets, idler sprockets, tension sprockets

### 3. **Bearings**
- Load rating, bore size, material, seals, type
- Examples: Roller bearings, ball bearings, needle bearings

### 4. **Tracks**
- Width, height, material, profile, length
- Examples: Aluminum tracks, guide rails, support brackets

### 5. **Drive Units**
- Power, voltage, speed, torque, type
- Examples: End drive units, intermediate drives, motors

### 6. **Bends**
- Radius, angle, type, direction
- Examples: Horizontal bends, vertical curves, spiral sections

## System Codes Supported

- **X45**: Small parts and components
- **XS**: Enhanced small parts system
- **X65**: Medium load applications
- **X85**: Heavy duty applications
- **XH/XK**: High load applications
- **X180**: Extra heavy duty
- **X300**: Maximum load capacity

## Data Structure

Each extracted component includes:

```python
ComponentSpecification(
    system_code="X45",                    # System code (X45, XS, etc.)
    component_type="chain",               # Type of component
    component_name="X45 Plain Chain",     # Full component name
    part_number="X45-PC-1000",           # Part number (if found)
    specifications={                      # Technical specifications
        "pitch": 25.4,
        "width": 43,
        "max_load": 2.5,
        "material": "steel",
        "type": "plain"
    },
    dimensions={                          # Physical dimensions
        "length": "1000mm",
        "width": "43mm",
        "height": "12mm"
    },
    materials=["Steel"],                  # Materials used
    compatibility=["X45"],                # Compatible systems
    weight_kg=0.85,                      # Weight in kg
    price_euro=45.50,                    # Price in euros
    description="Standard plain chain...", # Description
    page_reference=15                    # PDF page number
)
```

## Database Schema

The `component_specifications` table includes:

- **Primary fields**: system_code, component_type, name, part_number
- **JSON fields**: specifications, dimensions (for flexible data)
- **Array fields**: materials, compatibility
- **Numeric fields**: weight_kg, price_euro
- **Metadata**: created_at, updated_at, page_reference

## Advanced Features

### Custom Patterns

You can extend the extractor by adding custom patterns:

```python
extractor.component_patterns['custom_type'] = {
    'keywords': ['custom', 'special'],
    'spec_patterns': {
        'custom_spec': r'(\d+)\s*custom\s*unit',
        'special_feature': r'(feature1|feature2)'
    }
}
```

### Database Functions

The schema includes useful functions:

```sql
-- Search components by specifications
SELECT * FROM search_components('X45', 'chain', 2.0, 5.0, 'Steel');

-- Get component statistics
SELECT * FROM get_component_stats();

-- Use the view for easier querying
SELECT * FROM component_specifications_view WHERE system_code = 'X45';
```

## Troubleshooting

### Common Issues

1. **PDF libraries not installed**:
   ```bash
   pip install PyMuPDF pdfplumber
   ```

2. **No text extracted from PDF**:
   - Try different PDF processing libraries
   - Check if PDF is image-based (OCR may be needed)
   - Verify PDF is not password-protected

3. **Database connection failed**:
   - Check environment variables
   - Verify Supabase credentials
   - Ensure database schema is created

4. **Low extraction accuracy**:
   - Add custom patterns for your specific PDF format
   - Use verbose mode to see what's being extracted
   - Manually review and adjust patterns

### Improving Accuracy

1. **Add custom patterns** for your specific PDF format
2. **Use verbose mode** to see extraction details
3. **Review extracted data** and adjust patterns accordingly
4. **Combine multiple extraction methods** for better results

## Example Workflow

1. **Prepare PDFs**: Ensure catalogs are in PDF format
2. **Test extraction**: Run with `--test` to verify setup
3. **Extract data**: Process your PDF files
4. **Review results**: Check extracted data quality
5. **Upload to database**: Store in Supabase for web app use
6. **Verify in web app**: Check the Components tab

## Integration with Web App

The extracted component data integrates with your web app's Components tab:

- **Real-time display**: Components show in the detailed table
- **Filtering**: Filter by system, component type, specifications
- **Specifications**: Detailed technical data for each component
- **Compatibility**: See which systems each component works with

## Contributing

To improve the extractor:

1. **Add new component types** to the patterns
2. **Enhance extraction logic** for better accuracy
3. **Add support for new PDF formats**
4. **Improve error handling** and reporting
5. **Add unit tests** for reliability

## License

This tool is part of the FlexLink Configuration Tool project. 