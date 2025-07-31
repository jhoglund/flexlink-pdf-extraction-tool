# Complete FlexLink Database Analysis Report

Generated on: 2025-07-31 14:24:57

## Database Overview

- **Total Tables**: 4
- **Tables**: systems, component_specifications, product_images, components

## Detailed Table Analysis

### systems
- **Status**: ✅ Active
- **Row Count**: 17
- **Columns**: 20
- **Column Names**: id, system_code, system_name, category, description, key_features, applications, advantages...

### component_specifications
- **Status**: ✅ Active
- **Row Count**: 612
- **Columns**: 24
- **Column Names**: id, system_code, component_type, name, part_number, specifications, dimensions, materials...

### product_images
- **Status**: ❌ Error
- **Error**: {'message': 'canceling statement due to statement timeout', 'code': '57014', 'hint': None, 'details': None}

### components
- **Status**: ✅ Active
- **Row Count**: 11
- **Columns**: 9
- **Column Names**: id, system_code, name, component_type, specifications, compatibility, image_url, is_active...

## Table Categories

### System Data
- **systems**: 17 rows

### Component Data
- **component_specifications**: 612 rows
- **components**: 11 rows

## Table Relationships

### Common Columns Across Tables
- **id**: systems, component_specifications, product_images, components
- **name**: component_specifications, components
- **component_type**: component_specifications, product_images, components
- **system_code**: systems, component_specifications, components
- **updated_at**: systems, component_specifications, product_images
- **specifications**: component_specifications, components
- **page_reference**: systems, component_specifications
- **image_url**: component_specifications, components
- **materials**: systems, component_specifications
- **created_at**: systems, component_specifications, product_images, components
- **description**: systems, component_specifications
- **compatibility**: component_specifications, components

### Potential Foreign Keys
#### systems
- **Potential Foreign Keys**: id, system_code, system_name, chain_width
#### component_specifications
- **Potential Foreign Keys**: id, system_code, component_type, system_applications, system_features
#### product_images
- **Potential Foreign Keys**: id, width, product_code, component_type
#### components
- **Potential Foreign Keys**: id, system_code, component_type

## Data Overlap Analysis

### System Codes Distribution
- **systems**: 17 system codes
- **component_specifications**: 612 system codes
- **components**: 11 system codes

### Component Data Overlap
- **component_specifications**: 612 rows, 24 columns
- **components**: 11 rows, 9 columns

## Recommendations

⚠️ **Multiple component tables found** - Check for redundancy between `component_specifications` and `components`
⚠️ **Potential component data duplication** - Both `component_specifications` and `components` contain data

## Summary

- **Total Tables**: 4
- **Active Tables**: 3
- **Empty Tables**: 0
- **Categories**: 2
