# FlexLink Database Analysis Report

Generated on: 2025-07-31 14:11:50

## Table Analysis

### systems
- **Status**: ✅ Active
- **Row Count**: 17
- **Columns**: 20
- **Column Names**: id, system_code, system_name, category, description...

### component_specifications
- **Status**: ✅ Active
- **Row Count**: 612
- **Columns**: 24
- **Column Names**: id, system_code, component_type, name, part_number...

### images
- **Status**: ❌ Not found or error
- **Error**: {'message': "Could not find the table 'public.images' in the schema cache", 'code': 'PGRST205', 'hint': "Perhaps you meant the table 'public.product_images'", 'details': None}

### extracted_images
- **Status**: ❌ Not found or error
- **Error**: {'message': "Could not find the table 'public.extracted_images' in the schema cache", 'code': 'PGRST205', 'hint': "Perhaps you meant the table 'public.product_images'", 'details': None}

## System Data Overlap Analysis

- **Systems in Systems Table**: 17
- **Components in Components Table**: 612
- **Overlapping Systems**: 17
- **Systems Only**: 0
- **Components Only**: 1

**Systems only in components table**: x180

## Duplicate Data Analysis

- **Duplicate System Codes (Systems Table)**: 0
- **Duplicate System Codes (Components Table)**: 8

**Found Duplicates**:
- component_system_codes: ['X45', 'X180', 'XS', 'X65', 'X300', 'XH', 'XK', 'X85']

## Table Relationships Analysis

- **Valid Relationships**: 17
- **Orphaned Components**: 1
- **Unused Systems**: 0

**Orphaned Components**: x180

## Image Tables Analysis

### images_table
- **Status**: ❌ Not found or error
- **Error**: {'message': "Could not find the table 'public.images' in the schema cache", 'code': 'PGRST205', 'hint': "Perhaps you meant the table 'public.product_images'", 'details': None}

### extracted_images_table
- **Status**: ❌ Not found or error
- **Error**: {'message': "Could not find the table 'public.extracted_images' in the schema cache", 'code': 'PGRST205', 'hint': "Perhaps you meant the table 'public.product_images'", 'details': None}

## Recommendations

✅ **Systems and Components tables are complementary** - Both contain valuable data
⚠️ **Orphaned components found** - Components reference non-existent systems
