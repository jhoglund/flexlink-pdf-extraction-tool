-- FlexLink Image Storage Database Schema
-- Run this in your Supabase SQL editor to create the product_images table

-- Create product_images table for storing blueprint drawings and product images
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_product_images_hash 
ON product_images(image_hash);

CREATE INDEX IF NOT EXISTS idx_product_images_product_code 
ON product_images(product_code);

CREATE INDEX IF NOT EXISTS idx_product_images_component_type 
ON product_images(component_type);

CREATE INDEX IF NOT EXISTS idx_product_images_page_number 
ON product_images(page_number);

CREATE INDEX IF NOT EXISTS idx_product_images_blueprint 
ON product_images(is_blueprint);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_product_images_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_product_images_updated_at 
    BEFORE UPDATE ON product_images 
    FOR EACH ROW 
    EXECUTE FUNCTION update_product_images_updated_at();

-- Create a view for easy querying of product images
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
    updated_at,
    -- Calculate image size in KB (approximate)
    LENGTH(image_data) / 1024 as image_size_kb
FROM product_images;

-- Create a function to search images by criteria
CREATE OR REPLACE FUNCTION search_product_images(
    p_product_code VARCHAR DEFAULT NULL,
    p_component_type VARCHAR DEFAULT NULL,
    p_is_blueprint BOOLEAN DEFAULT NULL,
    p_min_quality DECIMAL DEFAULT NULL,
    p_page_number INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR,
    page_number INTEGER,
    product_code VARCHAR,
    component_type VARCHAR,
    is_blueprint BOOLEAN,
    image_quality_score DECIMAL,
    associated_text TEXT,
    image_format VARCHAR,
    width DECIMAL,
    height DECIMAL
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
        pi.associated_text,
        pi.image_format,
        pi.width,
        pi.height
    FROM product_images pi
    WHERE 
        (p_product_code IS NULL OR pi.product_code = p_product_code)
        AND (p_component_type IS NULL OR pi.component_type = p_component_type)
        AND (p_is_blueprint IS NULL OR pi.is_blueprint = p_is_blueprint)
        AND (p_min_quality IS NULL OR pi.image_quality_score >= p_min_quality)
        AND (p_page_number IS NULL OR pi.page_number = p_page_number)
    ORDER BY pi.page_number, pi.product_code, pi.component_type;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get image statistics
CREATE OR REPLACE FUNCTION get_image_stats()
RETURNS TABLE (
    total_images BIGINT,
    blueprint_images BIGINT,
    products_with_images BIGINT,
    component_types_with_images BIGINT,
    avg_image_size_kb DECIMAL,
    avg_quality_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_images,
        COUNT(*) FILTER (WHERE is_blueprint = true) as blueprint_images,
        COUNT(DISTINCT product_code) FILTER (WHERE product_code IS NOT NULL) as products_with_images,
        COUNT(DISTINCT component_type) FILTER (WHERE component_type IS NOT NULL) as component_types_with_images,
        AVG(LENGTH(image_data) / 1024) as avg_image_size_kb,
        AVG(image_quality_score) as avg_quality_score
    FROM product_images;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get images for a specific product
CREATE OR REPLACE FUNCTION get_product_images(p_product_code VARCHAR)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR,
    page_number INTEGER,
    component_type VARCHAR,
    is_blueprint BOOLEAN,
    image_quality_score DECIMAL,
    associated_text TEXT,
    image_format VARCHAR,
    width DECIMAL,
    height DECIMAL,
    image_data TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.image_hash,
        pi.page_number,
        pi.component_type,
        pi.is_blueprint,
        pi.image_quality_score,
        pi.associated_text,
        pi.image_format,
        pi.width,
        pi.height,
        pi.image_data
    FROM product_images pi
    WHERE pi.product_code = p_product_code
    ORDER BY pi.page_number, pi.is_blueprint DESC, pi.image_quality_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get blueprint images for a component type
CREATE OR REPLACE FUNCTION get_blueprint_images(p_component_type VARCHAR)
RETURNS TABLE (
    id INTEGER,
    image_hash VARCHAR,
    page_number INTEGER,
    product_code VARCHAR,
    image_quality_score DECIMAL,
    associated_text TEXT,
    image_format VARCHAR,
    width DECIMAL,
    height DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.image_hash,
        pi.page_number,
        pi.product_code,
        pi.image_quality_score,
        pi.associated_text,
        pi.image_format,
        pi.width,
        pi.height
    FROM product_images pi
    WHERE pi.component_type = p_component_type AND pi.is_blueprint = true
    ORDER BY pi.image_quality_score DESC, pi.page_number;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON product_images TO authenticated;
-- GRANT USAGE ON SEQUENCE product_images_id_seq TO authenticated;

COMMENT ON TABLE product_images IS 'Stores extracted images and blueprint drawings from FlexLink catalog PDFs';
COMMENT ON COLUMN product_images.image_data IS 'Base64 encoded image data';
COMMENT ON COLUMN product_images.image_hash IS 'MD5 hash of image data for deduplication';
COMMENT ON COLUMN product_images.is_blueprint IS 'Whether the image is identified as a blueprint drawing';
COMMENT ON COLUMN product_images.image_quality_score IS 'Quality score for blueprint detection (0.0 to 1.0)'; 