# FlexLink Component Extraction - Usage Guide

## Quick Start

### 1. Test the Component Extractor

```bash
# Activate virtual environment
source venv/bin/activate

# Test with sample data
python extract_components.py --test
```

This will create:
- `data/test_components.json` - Structured component data
- `data/test_components.csv` - Tabular format for analysis

### 2. Extract from PDF Files

```bash
# Extract from a single PDF
python extract_components.py catalog.pdf --output my_components.json

# Extract from multiple PDFs
python extract_components.py *.pdf --format csv --output all_components.csv

# Extract and upload to database (if configured)
python extract_components.py catalog.pdf --upload
```

### 3. Use the Python API

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

## What Gets Extracted

The tool automatically extracts:

### Component Types
- **Chains**: Pitch, width, max load, material, type
- **Sprockets**: Teeth count, bore size, pitch, material, type  
- **Bearings**: Load rating, bore size, material, seals, type
- **Tracks**: Width, height, material, profile, length
- **Drive Units**: Power, voltage, speed, torque, type
- **Bends**: Radius, angle, type, direction

### Data Fields
- System code (X45, XS, X65, etc.)
- Component name and part number
- Technical specifications (JSON format)
- Physical dimensions
- Materials used
- Compatibility information
- Weight and price (if available)
- Description and page reference

## Database Integration

### 1. Set up Database Schema

Run the SQL commands in `database_schema.sql` in your Supabase SQL editor to create the `component_specifications` table.

### 2. Configure Environment

Create a `.env` file:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Upload Data

```bash
python extract_components.py catalog.pdf --upload
```

## Output Formats

### JSON Format
```json
{
  "system_code": "X45",
  "component_type": "chain",
  "component_name": "X45 Plain Chain",
  "part_number": "X45-PC-1000",
  "specifications": {
    "pitch": 25.4,
    "width": 43,
    "max_load": 2.5,
    "material": "steel",
    "type": "plain"
  },
  "dimensions": {
    "length": "1000mm",
    "width": "43mm",
    "height": "12mm"
  },
  "materials": ["Steel"],
  "compatibility": ["X45"],
  "weight_kg": 0.85,
  "price_euro": 45.50
}
```

### CSV Format
- Flattened structure with all specifications as columns
- Easy to import into Excel or other analysis tools
- Compatible with database import tools

## Integration with Web App

The extracted component data integrates with your web app's Components tab:

1. **Upload to Database**: Use `--upload` flag
2. **View in Web App**: Components appear in the detailed table
3. **Filter and Search**: Use the web interface to find specific components
4. **Specifications**: View detailed technical data for each component

## Troubleshooting

### Common Issues

1. **PDF libraries not installed**:
   ```bash
   pip install PyMuPDF pdfplumber
   ```

2. **No components extracted**:
   - Check if PDF contains text (not just images)
   - Verify PDF is not password-protected
   - Try different PDF processing libraries

3. **Database connection failed**:
   - Check environment variables
   - Verify Supabase credentials
   - Ensure database schema is created

### Improving Accuracy

1. **Add custom patterns** for your specific PDF format
2. **Use verbose mode** to see extraction details
3. **Review extracted data** and adjust patterns
4. **Combine multiple extraction methods** for better results

## Example Workflow

1. **Prepare PDFs**: Ensure catalogs are in PDF format
2. **Test extraction**: Run with `--test` to verify setup
3. **Extract data**: Process your PDF files
4. **Review results**: Check extracted data quality
5. **Upload to database**: Store in Supabase for web app use
6. **Verify in web app**: Check the Components tab

## Command Line Options

```bash
python extract_components.py --help
```

Available options:
- `--output, -o`: Output file path
- `--format`: Output format (json or csv)
- `--upload`: Upload to database
- `--test`: Test with sample data
- `--verbose, -v`: Verbose output

## Next Steps

1. **Install PDF libraries** for full functionality
2. **Set up database** for persistent storage
3. **Process your catalogs** to extract component data
4. **Integrate with web app** for user-friendly access
5. **Customize patterns** for better extraction accuracy 