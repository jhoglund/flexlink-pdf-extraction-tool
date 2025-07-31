#!/usr/bin/env python3
"""
Generate SQL commands for manual execution in Supabase SQL Editor
"""


def generate_sql_commands():
    """Generate the SQL commands to create the product_images table"""

    sql_commands = """
-- FlexLink Product Images Table
-- Run these commands in your Supabase SQL Editor

-- 1. Create the product_images table
CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    image_hash VARCHAR(64) UNIQUE NOT NULL,
    page_number INTEGER NOT NULL,
    x_coord DECIMAL(10,2),
    y_coord DECIMAL(10,2),
    width DECIMAL(10,2),
    height DECIMAL(10,2),
    image_format VARCHAR(10) DEFAULT 'png',
    image_data TEXT NOT NULL, -- Base64 encoded image data
    associated_text TEXT,
    product_code VARCHAR(50),
    component_type VARCHAR(50),
    is_blueprint BOOLEAN DEFAULT false,
    image_quality_score DECIMAL(3,2),
    extraction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_product_images_hash ON product_images(image_hash);
CREATE INDEX IF NOT EXISTS idx_product_images_product_code ON product_images(product_code);
CREATE INDEX IF NOT EXISTS idx_product_images_component_type ON product_images(component_type);
CREATE INDEX IF NOT EXISTS idx_product_images_page_number ON product_images(page_number);
CREATE INDEX IF NOT EXISTS idx_product_images_is_blueprint ON product_images(is_blueprint);

-- 3. Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_product_images_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Create trigger to automatically update updated_at
CREATE TRIGGER update_product_images_updated_at 
    BEFORE UPDATE ON product_images 
    FOR EACH ROW 
    EXECUTE FUNCTION update_product_images_updated_at();

-- 5. Create a view for easy querying
CREATE OR REPLACE VIEW product_images_view AS
SELECT 
    id,
    image_hash,
    page_number,
    x_coord,
    y_coord,
    width,
    height,
    image_format,
    associated_text,
    product_code,
    component_type,
    is_blueprint,
    image_quality_score,
    extraction_date,
    created_at,
    updated_at
FROM product_images;

-- 6. Create a function to search images by criteria
CREATE OR REPLACE FUNCTION search_product_images(
    p_product_code VARCHAR DEFAULT NULL,
    p_component_type VARCHAR DEFAULT NULL,
    p_is_blueprint BOOLEAN DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR(64),
    page_number INTEGER,
    product_code VARCHAR(50),
    component_type VARCHAR(50),
    is_blueprint BOOLEAN,
    image_quality_score DECIMAL(3,2),
    extraction_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.image_hash,
        pi.page_number,
        pi.product_code,
        pi.component_type,
        pi.is_blueprint,
        pi.image_quality_score,
        pi.extraction_date
    FROM product_images pi
    WHERE (p_product_code IS NULL OR pi.product_code = p_product_code)
      AND (p_component_type IS NULL OR pi.component_type = p_component_type)
      AND (p_is_blueprint IS NULL OR pi.is_blueprint = p_is_blueprint)
    ORDER BY pi.page_number, pi.id;
END;
$$ LANGUAGE plpgsql;

-- 7. Create a function to get image statistics
CREATE OR REPLACE FUNCTION get_image_stats()
RETURNS TABLE (
    total_images BIGINT,
    blueprint_images BIGINT,
    unique_product_codes BIGINT,
    unique_component_types BIGINT,
    avg_quality_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_images,
        COUNT(*) FILTER (WHERE is_blueprint = true) as blueprint_images,
        COUNT(DISTINCT product_code) FILTER (WHERE product_code IS NOT NULL) as unique_product_codes,
        COUNT(DISTINCT component_type) FILTER (WHERE component_type IS NOT NULL) as unique_component_types,
        ROUND(AVG(image_quality_score)::DECIMAL, 2) as avg_quality_score
    FROM product_images;
END;
$$ LANGUAGE plpgsql;

-- 8. Create a function to get images for a specific product
CREATE OR REPLACE FUNCTION get_product_images(p_product_code VARCHAR)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR(64),
    page_number INTEGER,
    component_type VARCHAR(50),
    is_blueprint BOOLEAN,
    image_quality_score DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.image_hash,
        pi.page_number,
        pi.component_type,
        pi.is_blueprint,
        pi.image_quality_score
    FROM product_images pi
    WHERE pi.product_code = p_product_code
    ORDER BY pi.page_number, pi.id;
END;
$$ LANGUAGE plpgsql;

-- 9. Create a function to get blueprint images for a component type
CREATE OR REPLACE FUNCTION get_blueprint_images(p_component_type VARCHAR)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR(64),
    page_number INTEGER,
    product_code VARCHAR(50),
    image_quality_score DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.image_hash,
        pi.page_number,
        pi.product_code,
        pi.image_quality_score
    FROM product_images pi
    WHERE pi.component_type = p_component_type
      AND pi.is_blueprint = true
    ORDER BY pi.page_number, pi.id;
END;
$$ LANGUAGE plpgsql;

-- 10. Enable Row Level Security (RLS) - Optional
-- ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;

-- 11. Create a policy for public read access - Optional
-- CREATE POLICY "Allow public read access" ON product_images
--     FOR SELECT USING (true);

-- 12. Create a policy for authenticated insert access - Optional
-- CREATE POLICY "Allow authenticated insert" ON product_images
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
"""

    return sql_commands


def main():
    print("🔧 FlexLink Database Setup")
    print("=" * 50)
    print()
    print("📋 Instructions:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL commands below")
    print("4. Execute the commands")
    print()
    print("📄 SQL Commands to Execute:")
    print("=" * 50)
    print(generate_sql_commands())
    print("=" * 50)
    print()
    print("✅ After running these commands, your database will be ready!")
    print("You can then upload images using the extraction tool.")


if __name__ == "__main__":
    main()
