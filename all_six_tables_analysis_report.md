# Complete FlexLink Database Analysis - All 6 Tables

Generated on: 2025-07-31 14:29:37

## Database Overview

- **Total Tables**: 6
- **Tables**: component_specifications, components, conveyor_systems, product_images, system_compatibility, systems

## Detailed Table Analysis

### component_specifications
- **Status**: ✅ Active
- **Row Count**: 612
- **Columns**: 24
- **Column Names**: id, system_code, component_type, name, part_number, specifications, dimensions, materials...

### components
- **Status**: ✅ Active
- **Row Count**: 11
- **Columns**: 9
- **Column Names**: id, system_code, name, component_type, specifications, compatibility, image_url, is_active...

### conveyor_systems
- **Status**: ✅ Active
- **Row Count**: 15
- **Columns**: 11
- **Column Names**: id, code, name, description, chain_width_mm, max_load_per_link_kg, features, applications...

### product_images
- **Status**: ❌ Error
- **Error**: {'message': 'canceling statement due to statement timeout', 'code': '57014', 'hint': None, 'details': None}

### system_compatibility
- **Status**: ✅ Active
- **Row Count**: 14
- **Columns**: 5
- **Column Names**: id, system_a, system_b, compatible, notes

### systems
- **Status**: ✅ Active
- **Row Count**: 17
- **Columns**: 20
- **Column Names**: id, system_code, system_name, category, description, key_features, applications, advantages...

## Table Categories

### System Data
- **conveyor_systems**: 15 rows
- **systems**: 17 rows

### Component Data
- **component_specifications**: 612 rows
- **components**: 11 rows

### Compatibility Data
- **system_compatibility**: 14 rows

## Table Relationships

### Common Columns Across Tables
- **updated_at**: component_specifications, product_images, systems
- **is_active**: components, conveyor_systems
- **compatibility**: component_specifications, components
- **materials**: component_specifications, systems
- **description**: component_specifications, conveyor_systems, systems
- **id**: component_specifications, components, conveyor_systems, product_images, system_compatibility, systems
- **image_url**: component_specifications, components, conveyor_systems
- **system_code**: component_specifications, components, systems
- **applications**: conveyor_systems, systems
- **component_type**: component_specifications, components, product_images
- **specifications**: component_specifications, components
- **name**: component_specifications, components, conveyor_systems
- **page_reference**: component_specifications, systems
- **created_at**: component_specifications, components, conveyor_systems, product_images, systems

### Potential Foreign Keys
#### component_specifications
- **Potential Foreign Keys**: id, system_code, component_type, compatibility, system_applications, system_features
#### components
- **Potential Foreign Keys**: id, system_code, component_type, compatibility
#### conveyor_systems
- **Potential Foreign Keys**: id, code, chain_width_mm
#### product_images
- **Potential Foreign Keys**: id, width, product_code, component_type
#### system_compatibility
- **Potential Foreign Keys**: id, system_a, system_b
#### systems
- **Potential Foreign Keys**: id, system_code, system_name, chain_width

## Data Overlap Analysis

### System Codes Distribution
- **systems**: 17 system codes
- **component_specifications**: 612 system codes
- **components**: 11 system codes

### Component Data Overlap
- **component_specifications**: 612 rows, 24 columns
- **components**: 11 rows, 9 columns

### Conveyor System Data Overlap
- **conveyor_systems**: 15 rows, 11 columns
- **systems**: 17 rows, 20 columns

## Recommendations

⚠️ **Multiple component tables found** - Check for redundancy between component tables
⚠️ **Multiple system tables found** - Check for redundancy between system tables

## Summary

- **Total Tables**: 6
- **Active Tables**: 5
- **Empty Tables**: 0
- **Categories**: 3
