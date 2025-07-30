-- FlexLink Component Specifications Table
-- Copy and paste this into your Supabase SQL Editor

-- Create the main table
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

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON component_specifications TO authenticated;
GRANT USAGE ON SEQUENCE component_specifications_id_seq TO authenticated;

-- Add some helpful comments
COMMENT ON TABLE component_specifications IS 'Stores detailed specifications for FlexLink conveyor system components';
COMMENT ON COLUMN component_specifications.specifications IS 'JSON object containing component-specific technical specifications';
COMMENT ON COLUMN component_specifications.dimensions IS 'JSON object containing physical dimensions';
COMMENT ON COLUMN component_specifications.materials IS 'Array of materials used in the component';
COMMENT ON COLUMN component_specifications.compatibility IS 'Array of system codes this component is compatible with'; 