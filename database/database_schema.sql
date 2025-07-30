-- FlexLink Component Specifications Database Schema
-- Run this in your Supabase SQL editor to create the component_specifications table

-- Create component_specifications table
CREATE TABLE IF NOT EXISTS component_specifications (
    id SERIAL PRIMARY KEY,
    system_code VARCHAR(20) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    part_number VARCHAR(100),
    specifications JSONB DEFAULT '{}',
    dimensions JSONB DEFAULT '{}',
    materials TEXT[] DEFAULT '{}',
    compatibility TEXT[] DEFAULT '{}',
    weight_kg DECIMAL(8,3),
    price_euro DECIMAL(10,2),
    description TEXT,
    image_url TEXT,
    page_reference INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_component_specifications_system_code 
ON component_specifications(system_code);

CREATE INDEX IF NOT EXISTS idx_component_specifications_component_type 
ON component_specifications(component_type);

CREATE INDEX IF NOT EXISTS idx_component_specifications_part_number 
ON component_specifications(part_number);

CREATE INDEX IF NOT EXISTS idx_component_specifications_specifications 
ON component_specifications USING GIN(specifications);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_component_specifications_updated_at 
    BEFORE UPDATE ON component_specifications 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create a view for easy querying of component specifications
CREATE OR REPLACE VIEW component_specifications_view AS
SELECT 
    id,
    system_code,
    component_type,
    name,
    part_number,
    specifications,
    dimensions,
    materials,
    compatibility,
    weight_kg,
    price_euro,
    description,
    image_url,
    page_reference,
    created_at,
    updated_at,
    -- Extract common specifications for easier querying
    specifications->>'pitch' as pitch_mm,
    specifications->>'width' as width_mm,
    specifications->>'max_load' as max_load_kg,
    specifications->>'teeth' as teeth_count,
    specifications->>'bore' as bore_mm,
    specifications->>'power' as power_kw,
    specifications->>'voltage' as voltage_v,
    specifications->>'material' as material_type,
    specifications->>'type' as component_subtype
FROM component_specifications;

-- Create a function to search components by specifications
CREATE OR REPLACE FUNCTION search_components(
    p_system_code VARCHAR DEFAULT NULL,
    p_component_type VARCHAR DEFAULT NULL,
    p_min_load DECIMAL DEFAULT NULL,
    p_max_load DECIMAL DEFAULT NULL,
    p_material VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    system_code VARCHAR,
    component_type VARCHAR,
    name VARCHAR,
    part_number VARCHAR,
    specifications JSONB,
    dimensions JSONB,
    materials TEXT[],
    compatibility TEXT[],
    weight_kg DECIMAL,
    price_euro DECIMAL,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cs.id,
        cs.system_code,
        cs.component_type,
        cs.name,
        cs.part_number,
        cs.specifications,
        cs.dimensions,
        cs.materials,
        cs.compatibility,
        cs.weight_kg,
        cs.price_euro,
        cs.description
    FROM component_specifications cs
    WHERE 
        (p_system_code IS NULL OR cs.system_code = p_system_code)
        AND (p_component_type IS NULL OR cs.component_type = p_component_type)
        AND (p_min_load IS NULL OR (cs.specifications->>'max_load')::DECIMAL >= p_min_load)
        AND (p_max_load IS NULL OR (cs.specifications->>'max_load')::DECIMAL <= p_max_load)
        AND (p_material IS NULL OR p_material = ANY(cs.materials))
    ORDER BY cs.system_code, cs.component_type, cs.name;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data for testing
INSERT INTO component_specifications (
    system_code, 
    component_type, 
    name, 
    part_number, 
    specifications, 
    dimensions, 
    materials, 
    compatibility, 
    weight_kg, 
    price_euro, 
    description
) VALUES 
(
    'X45',
    'chain',
    'X45 Plain Chain',
    'X45-PC-1000',
    '{"pitch": 25.4, "width": 43, "max_load": 2.5, "material": "steel", "type": "plain"}',
    '{"length": "1000mm", "width": "43mm", "height": "12mm"}',
    ARRAY['Steel'],
    ARRAY['X45'],
    0.85,
    45.50,
    'Standard plain chain for X45 system'
),
(
    'X45',
    'sprocket',
    'X45 Drive Sprocket 16T',
    'X45-DS-16',
    '{"teeth": 16, "bore": 25, "pitch": 25.4, "material": "steel", "type": "drive"}',
    '{"diameter": "130mm", "width": "20mm"}',
    ARRAY['Steel'],
    ARRAY['X45'],
    0.45,
    28.75,
    '16-tooth drive sprocket for X45 system'
),
(
    'XS',
    'chain',
    'XS Cleated Chain',
    'XS-CC-1000',
    '{"pitch": 25.4, "width": 44, "max_load": 3.0, "material": "steel", "type": "cleated"}',
    '{"length": "1000mm", "width": "44mm", "height": "15mm"}',
    ARRAY['Steel'],
    ARRAY['XS'],
    1.2,
    52.30,
    'Cleated chain for XS system with enhanced grip'
),
(
    'X65',
    'bearing',
    'X65 Chain Bearings',
    'X65-CB-100',
    '{"load_rating": 500, "bore": 12, "material": "steel", "seals": "double lip", "type": "roller"}',
    '{"outer_diameter": "32mm", "width": "10mm"}',
    ARRAY['Steel'],
    ARRAY['X65'],
    0.08,
    12.50,
    'Roller bearings for X65 chain system'
)
ON CONFLICT DO NOTHING;

-- Create a function to get component statistics
CREATE OR REPLACE FUNCTION get_component_stats()
RETURNS TABLE (
    total_components BIGINT,
    systems_count BIGINT,
    component_types_count BIGINT,
    avg_price DECIMAL,
    total_weight DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_components,
        COUNT(DISTINCT system_code) as systems_count,
        COUNT(DISTINCT component_type) as component_types_count,
        AVG(price_euro) as avg_price,
        SUM(weight_kg) as total_weight
    FROM component_specifications;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON component_specifications TO authenticated;
-- GRANT USAGE ON SEQUENCE component_specifications_id_seq TO authenticated;

COMMENT ON TABLE component_specifications IS 'Stores detailed specifications for FlexLink conveyor system components';
COMMENT ON COLUMN component_specifications.specifications IS 'JSON object containing component-specific technical specifications';
COMMENT ON COLUMN component_specifications.dimensions IS 'JSON object containing physical dimensions';
COMMENT ON COLUMN component_specifications.materials IS 'Array of materials used in the component';
COMMENT ON COLUMN component_specifications.compatibility IS 'Array of system codes this component is compatible with'; 