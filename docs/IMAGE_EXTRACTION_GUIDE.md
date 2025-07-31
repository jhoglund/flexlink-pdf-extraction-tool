# FlexLink Image Extraction Guide

This guide explains how to use the FlexLink image extraction system to extract blueprint drawings and product images from PDF catalogs and store them in the database.

## Overview

The image extraction system consists of several components:

1. **Image Extractor** (`extractors/image_extractor.py`) - Extracts images from PDF files
2. **Database Uploader** (`extractors/upload_images_to_database.py`) - Uploads images to the database
3. **Combined Processor** (`extractors/extract_and_upload_images.py`) - Complete pipeline
4. **Web Viewer** (`web/image_viewer.html`) - Web interface to browse images
5. **Database Schema** (`database/create_images_table.sql`) - Database structure for images

## Features

- 🔍 **Smart Image Detection**: Automatically identifies blueprint drawings vs. regular images
- 📋 **Product Association**: Links images to product codes and component types
- 💾 **Database Storage**: Stores images as base64 data with metadata
- 🔍 **Advanced Search**: Search by product code, component type, and image type
- 📊 **Statistics**: Track image quality and database statistics
- 🌐 **Web Interface**: Beautiful web viewer for browsing images

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The system requires these additional libraries:
- `Pillow` - For image processing
- `PyMuPDF` - For PDF processing
- `supabase` - For database operations

### 2. Set Up Database

Run the database schema in your Supabase SQL editor:

```sql
-- Run the contents of database/create_images_table.sql
```

This creates:
- `product_images` table for storing images
- Indexes for performance
- Helper functions for searching and statistics
- Views for easy querying

### 3. Configure Environment

Create a `.env` file with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Usage

### Command Line Interface

#### Process a Single PDF

```bash
# Basic usage
python extractors/extract_and_upload_images.py --pdf path/to/catalog.pdf

# Save images locally as well
python extractors/extract_and_upload_images.py --pdf path/to/catalog.pdf --output-dir extracted_images

# Don't save locally (database only)
python extractors/extract_and_upload_images.py --pdf path/to/catalog.pdf --no-save-local
```

#### Process Multiple PDFs

```bash
# Process all PDFs in a directory
python extractors/extract_and_upload_images.py --directory path/to/pdf/folder
```

#### Search Images

```bash
# Search by product code
python extractors/extract_and_upload_images.py --search --product-code X45

# Search by component type
python extractors/extract_and_upload_images.py --search --component-type chain

# Search only blueprints
python extractors/extract_and_upload_images.py --search --blueprint-only

# Show database statistics
python extractors/extract_and_upload_images.py --stats
```

### Interactive Mode

Run without arguments for interactive mode:

```bash
python extractors/extract_and_upload_images.py
```

This provides a menu-driven interface for:
1. Processing single PDFs
2. Processing directories of PDFs
3. Searching images in database
4. Viewing database statistics

### Individual Components

#### Image Extractor Only

```bash
python extractors/image_extractor.py
```

This runs the image extractor in isolation for testing.

#### Database Uploader Only

```bash
python extractors/upload_images_to_database.py
```

This provides a menu for database operations.

## Web Interface

### Setup

1. Update the Supabase credentials in `web/image_viewer.html`:
   ```javascript
   const SUPABASE_URL = 'your_supabase_url';
   const SUPABASE_KEY = 'your_supabase_anon_key';
   ```

2. Open the file in a web browser or serve it with a local server.

### Features

- **Search Interface**: Filter by product code, component type, and image type
- **Image Grid**: Browse all extracted images with metadata
- **Image Details**: Click images to view full details and larger versions
- **Statistics**: View database statistics and image metrics
- **Responsive Design**: Works on desktop and mobile devices

## Database Schema

### Product Images Table

```sql
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    image_hash VARCHAR(64) UNIQUE NOT NULL,
    page_number INTEGER NOT NULL,
    x_coord DECIMAL(10,2),
    y_coord DECIMAL(10,2),
    width DECIMAL(10,2),
    height DECIMAL(10,2),
    image_format VARCHAR(10) DEFAULT 'png',
    image_data TEXT NOT NULL, -- Base64 encoded
    associated_text TEXT,
    product_code VARCHAR(50),
    component_type VARCHAR(50),
    is_blueprint BOOLEAN DEFAULT false,
    image_quality_score DECIMAL(3,2),
    extraction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Key Fields

- `image_hash`: MD5 hash for deduplication
- `image_data`: Base64 encoded image data
- `product_code`: Associated product code (e.g., X45, XS)
- `component_type`: Component type (e.g., chain, sprocket, bearing)
- `is_blueprint`: Whether the image is identified as a blueprint drawing
- `image_quality_score`: Quality score for blueprint detection (0.0-1.0)

## Blueprint Detection

The system uses several criteria to identify blueprint drawings:

1. **Technical Text Analysis**: Looks for technical terms in surrounding text
2. **Image Characteristics**: Analyzes contrast, aspect ratio, and brightness
3. **Quality Scoring**: Combines multiple factors into a quality score
4. **Threshold Filtering**: Only keeps images above a quality threshold

### Detection Criteria

- Technical terms in associated text (dimension, mm, drawing, etc.)
- Appropriate aspect ratios (0.5-2.0)
- Good contrast (edge pixel ratio > 0.1)
- Appropriate brightness (50-180 average pixel value)
- Minimum quality score (default: 0.7)

## API Functions

The database includes several helper functions:

### Search Functions

```sql
-- Search images by criteria
SELECT * FROM search_product_images(
    p_product_code := 'X45',
    p_component_type := 'chain',
    p_is_blueprint := true
);

-- Get images for a specific product
SELECT * FROM get_product_images('X45');

-- Get blueprint images for a component type
SELECT * FROM get_blueprint_images('chain');
```

### Statistics Functions

```sql
-- Get comprehensive statistics
SELECT * FROM get_image_stats();
```

## Troubleshooting

### Common Issues

1. **No images extracted**
   - Check if PDF contains images
   - Verify PDF is not corrupted
   - Adjust quality threshold in image extractor

2. **Database upload errors**
   - Verify Supabase credentials
   - Check database schema is installed
   - Ensure image data is not too large

3. **Web interface not working**
   - Update Supabase credentials in HTML file
   - Check browser console for errors
   - Verify CORS settings in Supabase

### Performance Tips

1. **Large PDFs**: Process in smaller chunks or increase memory limits
2. **Image Quality**: Adjust quality threshold for better/faster processing
3. **Database**: Use indexes for better query performance
4. **Storage**: Monitor database size as images can be large

### Debugging

Enable verbose logging by modifying the extractor classes:

```python
# In image_extractor.py
self.debug = True  # Add this to __init__ method
```

## Examples

### Example 1: Process a Catalog PDF

```bash
# Extract images and upload to database
python extractors/extract_and_upload_images.py --pdf flexlink_catalog.pdf

# Output:
# 🔄 Starting complete image processing pipeline
# 📄 PDF: flexlink_catalog.pdf
# 📋 Step 1: Extracting images from PDF...
# ✅ Extracted 45 images from PDF
# 🔍 Identified 23 blueprint images out of 45 total images
# 📋 Step 2: Uploading 23 images to database...
# ✅ Uploaded image 1/23: X45
# ...
# 📊 PROCESSING SUMMARY
# 📄 PDF Processing:
#    Total images found: 45
#    Blueprint images identified: 23
# 💾 Database Upload:
#    Images uploaded successfully: 23
#    Upload errors: 0
```

### Example 2: Search for Chain Images

```bash
python extractors/extract_and_upload_images.py --search --component-type chain --blueprint-only
```

### Example 3: Web Interface Usage

1. Open `web/image_viewer.html` in browser
2. Enter "X45" in Product Code field
3. Select "chain" from Component Type dropdown
4. Click "Search Images"
5. Click on any image to view details

## Advanced Usage

### Custom Blueprint Detection

Modify the detection criteria in `image_extractor.py`:

```python
def _is_blueprint_drawing(self, image: Image.Image, associated_text: str) -> bool:
    # Add your custom detection logic here
    # Return True for blueprint, False for regular image
```

### Batch Processing Script

Create a script for processing multiple catalogs:

```python
from extractors.extract_and_upload_images import FlexLinkImageProcessor

processor = FlexLinkImageProcessor()

# Process multiple catalogs
catalogs = [
    "catalog_2023.pdf",
    "catalog_2024.pdf",
    "technical_drawings.pdf"
]

for catalog in catalogs:
    print(f"Processing {catalog}...")
    result = processor.process_pdf_and_upload(catalog)
    print(f"Result: {result['success']}")
```

### Database Maintenance

```sql
-- Clean up duplicate images
DELETE FROM product_images 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM product_images 
    GROUP BY image_hash
);

-- Get storage usage
SELECT 
    COUNT(*) as total_images,
    SUM(LENGTH(image_data)) / 1024 / 1024 as total_size_mb
FROM product_images;
```

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Test with a small PDF first
4. Verify database connectivity and permissions

The system is designed to be robust and handle various PDF formats and image types commonly found in technical catalogs. 