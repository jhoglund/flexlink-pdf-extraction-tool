-- Update Database Schema for Application Information
-- Run this in your Supabase SQL Editor to add application fields

-- Add new columns for application information
ALTER TABLE component_specifications 
ADD COLUMN IF NOT EXISTS system_applications TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS system_features TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS washable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS food_grade BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS high_temperature BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS chemical_resistant BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS hygienic BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS heavy_duty BOOLEAN DEFAULT FALSE;

-- Create indexes for application filtering
CREATE INDEX IF NOT EXISTS idx_component_specifications_washable 
ON component_specifications(washable);

CREATE INDEX IF NOT EXISTS idx_component_specifications_food_grade 
ON component_specifications(food_grade);

CREATE INDEX IF NOT EXISTS idx_component_specifications_hygienic 
ON component_specifications(hygienic);

CREATE INDEX IF NOT EXISTS idx_component_specifications_heavy_duty 
ON component_specifications(heavy_duty);

-- Create a function to search components by application criteria
CREATE OR REPLACE FUNCTION search_components_by_application(
    p_washable BOOLEAN DEFAULT NULL,
    p_food_grade BOOLEAN DEFAULT NULL,
    p_hygienic BOOLEAN DEFAULT NULL,
    p_heavy_duty BOOLEAN DEFAULT NULL,
    p_high_temperature BOOLEAN DEFAULT NULL,
    p_chemical_resistant BOOLEAN DEFAULT NULL,
    p_system_code VARCHAR DEFAULT NULL
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
    description TEXT,
    washable BOOLEAN,
    food_grade BOOLEAN,
    hygienic BOOLEAN,
    heavy_duty BOOLEAN,
    high_temperature BOOLEAN,
    chemical_resistant BOOLEAN,
    system_applications TEXT[],
    system_features TEXT[]
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
        cs.description,
        cs.washable,
        cs.food_grade,
        cs.hygienic,
        cs.heavy_duty,
        cs.high_temperature,
        cs.chemical_resistant,
        cs.system_applications,
        cs.system_features
    FROM component_specifications cs
    WHERE 
        (p_washable IS NULL OR cs.washable = p_washable)
        AND (p_food_grade IS NULL OR cs.food_grade = p_food_grade)
        AND (p_hygienic IS NULL OR cs.hygienic = p_hygienic)
        AND (p_heavy_duty IS NULL OR cs.heavy_duty = p_heavy_duty)
        AND (p_high_temperature IS NULL OR cs.high_temperature = p_high_temperature)
        AND (p_chemical_resistant IS NULL OR cs.chemical_resistant = p_chemical_resistant)
        AND (p_system_code IS NULL OR cs.system_code = p_system_code)
    ORDER BY cs.system_code, cs.component_type, cs.name;
END;
$$ LANGUAGE plpgsql;

-- Add comments for the new fields
COMMENT ON COLUMN component_specifications.system_applications IS 'Array of applications this system is suitable for';
COMMENT ON COLUMN component_specifications.system_features IS 'Array of features this system provides';
COMMENT ON COLUMN component_specifications.washable IS 'Whether the component/system is washable';
COMMENT ON COLUMN component_specifications.food_grade IS 'Whether the component/system is food grade';
COMMENT ON COLUMN component_specifications.hygienic IS 'Whether the component/system is hygienic';
COMMENT ON COLUMN component_specifications.heavy_duty IS 'Whether the component/system is heavy duty';
COMMENT ON COLUMN component_specifications.high_temperature IS 'Whether the component/system is high temperature rated';
COMMENT ON COLUMN component_specifications.chemical_resistant IS 'Whether the component/system is chemical resistant'; 