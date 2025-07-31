-- Database Migration Script for FlexLink Project
-- This script shows all changes made to the Supabase database

-- =====================================================
-- 1. CREATE NEW SYSTEMS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS systems (
    id SERIAL PRIMARY KEY,
    system_code VARCHAR(10) UNIQUE NOT NULL,
    system_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    key_features TEXT[],
    applications TEXT[],
    advantages TEXT[],
    technical_specs JSONB,
    materials TEXT[],
    load_capacity VARCHAR(50),
    speed_range VARCHAR(50),
    precision_level VARCHAR(20),
    chain_pitch VARCHAR(20),
    chain_width VARCHAR(50),
    max_load VARCHAR(100),
    temperature_range VARCHAR(50),
    page_reference INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. RENAME EXISTING TABLES (ARCHIVE)
-- =====================================================

-- Archive old components table
ALTER TABLE IF EXISTS components RENAME TO archived_components;

-- Archive old conveyor_systems table  
ALTER TABLE IF EXISTS conveyor_systems RENAME TO archived_conveyor_systems;

-- Rename component_specifications to components
ALTER TABLE IF EXISTS component_specifications RENAME TO components;

-- =====================================================
-- 3. ADD INDEXES FOR PERFORMANCE
-- =====================================================

-- Systems table indexes
CREATE INDEX IF NOT EXISTS idx_systems_category ON systems(category);
CREATE INDEX IF NOT EXISTS idx_systems_load_capacity ON systems(load_capacity);
CREATE INDEX IF NOT EXISTS idx_systems_system_code ON systems(system_code);

-- Components table indexes
CREATE INDEX IF NOT EXISTS idx_components_system_code ON components(system_code);
CREATE INDEX IF NOT EXISTS idx_components_type ON components(component_type);

-- Product images indexes (if not exists)
CREATE INDEX IF NOT EXISTS idx_product_images_system_code ON product_images(system_code);

-- =====================================================
-- 4. CREATE VIEWS FOR EASY QUERYING
-- =====================================================

-- System overview view
CREATE OR REPLACE VIEW system_overview AS
SELECT 
    system_code,
    system_name,
    category,
    load_capacity,
    speed_range,
    precision_level,
    chain_width,
    max_load
FROM systems
ORDER BY system_code;

-- Component compatibility view
CREATE OR REPLACE VIEW component_compatibility AS
SELECT 
    c.*,
    s.system_name,
    s.category,
    s.load_capacity
FROM components c
JOIN systems s ON c.system_code = s.system_code;

-- System statistics view
CREATE OR REPLACE VIEW system_stats AS
SELECT 
    COUNT(*) as total_systems,
    COUNT(DISTINCT category) as category_count,
    COUNT(DISTINCT load_capacity) as load_types,
    AVG(CASE 
        WHEN load_capacity LIKE '%Light%' THEN 1
        WHEN load_capacity LIKE '%Medium%' THEN 2
        WHEN load_capacity LIKE '%Heavy%' THEN 3
        ELSE 1
    END) as avg_load_score
FROM systems;

-- =====================================================
-- 5. CREATE FUNCTIONS FOR ADVANCED QUERIES
-- =====================================================

-- Search systems function
CREATE OR REPLACE FUNCTION search_systems(
    search_term TEXT DEFAULT NULL,
    category_filter TEXT DEFAULT NULL,
    load_filter TEXT DEFAULT NULL
)
RETURNS TABLE(
    system_code VARCHAR(10),
    system_name VARCHAR(255),
    category VARCHAR(100),
    load_capacity VARCHAR(50),
    speed_range VARCHAR(50),
    match_score INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.system_code,
        s.system_name,
        s.category,
        s.load_capacity,
        s.speed_range,
        CASE 
            WHEN search_term IS NOT NULL AND (
                s.system_name ILIKE '%' || search_term || '%' OR
                s.description ILIKE '%' || search_term || '%'
            ) THEN 100
            ELSE 50
        END as match_score
    FROM systems s
    WHERE (category_filter IS NULL OR s.category = category_filter)
    AND (load_filter IS NULL OR s.load_capacity ILIKE '%' || load_filter || '%')
    ORDER BY match_score DESC, s.system_code;
END;
$$;

-- Get system statistics function
CREATE OR REPLACE FUNCTION get_system_stats()
RETURNS TABLE(
    total_systems INTEGER,
    categories TEXT[],
    avg_load_capacity TEXT,
    total_components INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM systems) as total_systems,
        (SELECT ARRAY_AGG(DISTINCT category) FROM systems) as categories,
        (SELECT 
            CASE 
                WHEN AVG(CASE 
                    WHEN load_capacity LIKE '%Light%' THEN 1
                    WHEN load_capacity LIKE '%Medium%' THEN 2
                    WHEN load_capacity LIKE '%Heavy%' THEN 3
                    ELSE 1
                END) < 1.5 THEN 'Light Duty'
                WHEN AVG(CASE 
                    WHEN load_capacity LIKE '%Light%' THEN 1
                    WHEN load_capacity LIKE '%Medium%' THEN 2
                    WHEN load_capacity LIKE '%Heavy%' THEN 3
                    ELSE 1
                END) < 2.5 THEN 'Medium Duty'
                ELSE 'Heavy Duty'
            END
        FROM systems) as avg_load_capacity,
        (SELECT COUNT(*) FROM components) as total_components;
END;
$$;

-- =====================================================
-- 6. DATA QUALITY FIXES
-- =====================================================

-- Standardize system codes to uppercase
UPDATE components 
SET system_code = UPPER(system_code) 
WHERE system_code != UPPER(system_code);

-- Fix orphaned component references
UPDATE components 
SET system_code = 'X180' 
WHERE system_code = 'x180';

-- =====================================================
-- 7. INSERT SAMPLE SYSTEMS DATA
-- =====================================================

-- Note: This is a sample of the 17 systems that were added
-- The full data insertion was done via the create_systems_table.sql script

INSERT INTO systems (system_code, system_name, category, description, load_capacity, speed_range, precision_level) 
VALUES 
('X45', 'X45 Chain System', 'Chain Conveyor', 'Compact chain conveyor system for space-constrained applications', 'Light duty', 'Up to 20 m/min', 'Standard'),
('XS', 'XS Chain System', 'Chain Conveyor', 'Ultra-compact design for maximum space efficiency', 'Very light duty', 'Up to 15 m/min', 'Standard'),
('X65', 'X65 Chain System', 'Chain Conveyor', 'Standard chain conveyor for versatile applications', 'Medium', 'Up to 30 m/min', 'Standard')
ON CONFLICT (system_code) DO NOTHING;

-- =====================================================
-- 8. GRANT PERMISSIONS (if needed)
-- =====================================================

-- Grant select permissions on views
GRANT SELECT ON system_overview TO anon, authenticated;
GRANT SELECT ON component_compatibility TO anon, authenticated;
GRANT SELECT ON system_stats TO anon, authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION search_systems TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_system_stats TO anon, authenticated;

-- =====================================================
-- 9. VERIFICATION QUERIES
-- =====================================================

-- Check table structure
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('systems', 'components', 'product_images')
ORDER BY table_name, ordinal_position;

-- Check data counts
SELECT 
    'systems' as table_name,
    COUNT(*) as record_count
FROM systems
UNION ALL
SELECT 
    'components' as table_name,
    COUNT(*) as record_count
FROM components
UNION ALL
SELECT 
    'product_images' as table_name,
    COUNT(*) as record_count
FROM product_images;

-- Check system codes
SELECT DISTINCT system_code FROM systems ORDER BY system_code; 