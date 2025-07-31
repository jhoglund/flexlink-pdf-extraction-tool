-- Create Systems Table for FlexLink System Summaries
-- Run this in your Supabase SQL Editor to create the systems table

-- Create systems table to store system-level information
CREATE TABLE IF NOT EXISTS systems (
    id SERIAL PRIMARY KEY,
    system_code VARCHAR(20) UNIQUE NOT NULL,
    system_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    key_features TEXT[] DEFAULT '{}',
    applications TEXT[] DEFAULT '{}',
    advantages TEXT[] DEFAULT '{}',
    technical_specs JSONB DEFAULT '{}',
    materials TEXT[] DEFAULT '{}',
    load_capacity VARCHAR(50),
    speed_range VARCHAR(100),
    precision_level VARCHAR(100),
    chain_pitch VARCHAR(50),
    chain_width VARCHAR(100),
    max_load VARCHAR(100),
    temperature_range VARCHAR(100),
    page_reference INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_systems_system_code 
ON systems(system_code);

CREATE INDEX IF NOT EXISTS idx_systems_category 
ON systems(category);

CREATE INDEX IF NOT EXISTS idx_systems_load_capacity 
ON systems(load_capacity);

CREATE INDEX IF NOT EXISTS idx_systems_technical_specs 
ON systems USING GIN(technical_specs);

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_systems_updated_at 
    BEFORE UPDATE ON systems 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert all FlexLink systems with their summaries
INSERT INTO systems (
    system_code, 
    system_name, 
    category, 
    description, 
    key_features, 
    applications, 
    advantages, 
    technical_specs, 
    materials, 
    load_capacity, 
    speed_range, 
    precision_level, 
    chain_pitch, 
    chain_width, 
    max_load, 
    temperature_range, 
    page_reference
) VALUES 
-- Chain Conveyor Systems
(
    'X45',
    'X45 Chain System',
    'Chain Conveyor',
    'The X45 is FlexLink''s compact chain conveyor system, designed for space-constrained applications requiring reliable material handling in limited environments. It features a smaller footprint while maintaining the modular design philosophy, making it ideal for applications where space efficiency is critical.',
    ARRAY['Compact design for space-constrained applications', '25.4 mm pitch chain system', 'Reduced profile components', 'Modular design for easy customization', 'Light-duty applications', 'Easy installation and maintenance'],
    ARRAY['Small assembly operations', 'Compact production lines', 'Space-limited installations', 'Light material handling', 'Miniature product transport'],
    ARRAY['Minimal space requirements', 'Cost-effective for small applications', 'Easy integration into existing systems', 'Lightweight construction', 'Quick installation'],
    '{"chain_pitch": "25.4 mm", "max_load": "Light duty", "chain_width": "50-150 mm", "speed": "Up to 20 m/min"}',
    ARRAY['Plastic chain', 'Aluminum frame', 'Steel components'],
    'Light',
    'Up to 20 m/min',
    'Standard',
    '25.4 mm',
    '50-150 mm',
    'Light duty',
    '-20°C to +80°C',
    3
),
(
    'XS',
    'XS Chain System',
    'Chain Conveyor',
    'The XS Chain System represents FlexLink''s super-compact conveyor solution, designed for applications requiring maximum space efficiency and minimal footprint. This system features an ultra-compact design with reduced chain pitch and minimal component profiles.',
    ARRAY['Ultra-compact design', 'Minimal component profiles', 'Reduced chain pitch', 'Maximum space efficiency', 'Modular construction', 'Light-duty applications'],
    ARRAY['Micro-assembly operations', 'Compact production lines', 'Space-critical installations', 'Small component handling', 'Miniature product transport'],
    ARRAY['Maximum space efficiency', 'Minimal footprint', 'Easy integration', 'Lightweight design', 'Quick setup'],
    '{"chain_pitch": "12.7 mm", "max_load": "Very light duty", "chain_width": "30-100 mm", "speed": "Up to 15 m/min"}',
    ARRAY['Plastic chain', 'Aluminum frame', 'Lightweight components'],
    'Very Light',
    'Up to 15 m/min',
    'Standard',
    '12.7 mm',
    '30-100 mm',
    'Very light duty',
    '-10°C to +60°C',
    3
),
(
    'X65',
    'X65 Chain System',
    'Chain Conveyor',
    'The X65 is FlexLink''s standard chain conveyor system, designed for versatile applications across various industries. It features a modular plastic chain design that provides reliable transportation of products with different shapes and sizes.',
    ARRAY['Modular plastic chain design for flexibility', 'Standard pitch chain system for general applications', 'Compatible with various accessories and components', 'Suitable for light to medium duty applications', 'Easy installation and maintenance', 'Wide range of chain types'],
    ARRAY['General material handling', 'Assembly line operations', 'Packaging and sorting applications', 'Light manufacturing processes', 'Product accumulation and buffering'],
    ARRAY['Cost-effective solution for standard applications', 'High flexibility in configuration', 'Extensive accessory range', 'Proven reliability in various industries', 'Easy to modify and expand'],
    '{"chain_pitch": "25.4 mm", "max_load": "Varies by configuration", "chain_width": "50-200 mm", "speed": "Up to 30 m/min"}',
    ARRAY['Plastic chain', 'Aluminum frame', 'Steel components'],
    'Medium',
    'Up to 30 m/min',
    'Standard',
    '25.4 mm',
    '50-200 mm',
    'Varies by configuration',
    '-20°C to +80°C',
    3
),
(
    'X85',
    'X85 Chain System',
    'Chain Conveyor',
    'The X85 is FlexLink''s heavy-duty chain conveyor system, designed for demanding applications requiring higher load capacities and more robust construction. It features enhanced chain design and reinforced components for industrial applications.',
    ARRAY['Heavy-duty chain design for high load capacity', 'Reinforced frame construction', 'Enhanced wear resistance', 'Suitable for harsh industrial environments', 'High-speed operation capability', 'Advanced chain lubrication systems'],
    ARRAY['Heavy manufacturing operations', 'Automotive industry applications', 'Metal processing and handling', 'High-speed production lines', 'Industrial material handling'],
    ARRAY['Superior load capacity compared to X65', 'Enhanced durability and longevity', 'Better performance in demanding environments', 'Reduced maintenance requirements', 'Higher speed capabilities'],
    '{"chain_pitch": "38.1 mm", "max_load": "Up to 2000 N per link", "chain_width": "75-300 mm", "speed": "Up to 60 m/min"}',
    ARRAY['Steel chain', 'Reinforced aluminum frame', 'Hardened steel components'],
    'High',
    'Up to 60 m/min',
    'Standard',
    '38.1 mm',
    '75-300 mm',
    'Up to 2000 N',
    '-40°C to +120°C',
    3
),
(
    'XH',
    'XH Chain System',
    'Chain Conveyor',
    'The XH Chain System represents FlexLink''s high-performance conveyor solution, designed for applications requiring enhanced speed and precision while maintaining the reliability of the X85 platform.',
    ARRAY['High-speed operation capabilities', 'Enhanced precision and accuracy', 'Advanced chain technology', 'Optimized for speed applications', 'Robust construction for demanding environments', 'Advanced control integration'],
    ARRAY['High-speed production lines', 'Precision manufacturing', 'Automated assembly operations', 'Fast-paced industrial applications', 'Speed-critical operations'],
    ARRAY['Superior speed capabilities', 'Enhanced precision', 'Advanced technology integration', 'Robust performance', 'High throughput capacity'],
    '{"chain_pitch": "38.1 mm", "max_load": "Up to 2500 N per link", "chain_width": "75-300 mm", "speed": "Up to 80 m/min"}',
    ARRAY['High-performance steel chain', 'Reinforced aluminum frame', 'Precision components'],
    'High',
    'Up to 80 m/min',
    'High',
    '38.1 mm',
    '75-300 mm',
    'Up to 2500 N',
    '-40°C to +120°C',
    3
),
(
    'X180',
    'X180 Chain System',
    'Chain Conveyor',
    'The X180 Chain System is FlexLink''s specialized conveyor solution designed for applications requiring enhanced load capacity and extended chain pitch. This system features a 180 mm chain pitch that provides superior load distribution.',
    ARRAY['Extended 180 mm chain pitch', 'Enhanced load distribution', 'Superior stability for heavy loads', 'Specialized for heavy-duty applications', 'Robust construction', 'Advanced load handling capabilities'],
    ARRAY['Heavy material handling', 'Large component transport', 'Industrial manufacturing', 'Heavy-duty assembly operations', 'Large product handling'],
    ARRAY['Superior load distribution', 'Enhanced stability', 'Heavy-duty performance', 'Robust construction', 'Specialized load handling'],
    '{"chain_pitch": "180 mm", "max_load": "Up to 5000 N per link", "chain_width": "100-400 mm", "speed": "Up to 40 m/min"}',
    ARRAY['Heavy-duty steel chain', 'Reinforced frame', 'Industrial-grade components'],
    'Very High',
    'Up to 40 m/min',
    'Standard',
    '180 mm',
    '100-400 mm',
    'Up to 5000 N',
    '-40°C to +120°C',
    3
),
(
    'X300',
    'X300 Chain System',
    'Chain Conveyor',
    'The X300 Chain System represents FlexLink''s ultra-heavy-duty conveyor solution, designed for the most demanding industrial applications requiring maximum load capacity and extreme durability.',
    ARRAY['Ultra-heavy-duty design', '300 mm chain pitch for maximum load distribution', 'Extreme durability and longevity', 'Specialized for maximum load applications', 'Industrial-grade construction', 'Advanced load handling technology'],
    ARRAY['Ultra-heavy material handling', 'Large industrial components', 'Heavy manufacturing operations', 'Extreme load applications', 'Industrial heavy-duty operations'],
    ARRAY['Maximum load capacity', 'Extreme durability', 'Superior load distribution', 'Industrial-grade performance', 'Specialized heavy-duty design'],
    '{"chain_pitch": "300 mm", "max_load": "Up to 10000 N per link", "chain_width": "150-500 mm", "speed": "Up to 30 m/min"}',
    ARRAY['Ultra-heavy-duty steel chain', 'Reinforced industrial frame', 'Heavy-duty components'],
    'Ultra High',
    'Up to 30 m/min',
    'Standard',
    '300 mm',
    '150-500 mm',
    'Up to 10000 N',
    '-40°C to +120°C',
    3
),
-- Pallet Conveyor Systems
(
    'XK',
    'XK Pallet System',
    'Pallet Conveyor',
    'The XK Pallet System is FlexLink''s precision pallet handling solution, designed for applications requiring accurate positioning and flexible routing of pallets. It features advanced control capabilities and precise positioning technology.',
    ARRAY['Precision pallet positioning', 'Flexible routing capabilities', 'Advanced control systems', 'Modular pallet design', 'High accuracy positioning', 'Integrated safety features'],
    ARRAY['Precision assembly operations', 'Automated manufacturing', 'Flexible production systems', 'Pallet-based material handling', 'High-precision applications'],
    ARRAY['Exceptional positioning accuracy', 'Flexible routing and sorting', 'Advanced automation capabilities', 'Reduced setup time', 'High throughput capacity'],
    '{"pallet_size": "200x200 mm to 600x600 mm", "positioning_accuracy": "±0.1 mm", "max_load": "50 kg per pallet", "speed": "Up to 60 m/min", "pallet_spacing": "25.4 mm"}',
    ARRAY['Aluminum pallets', 'Steel chain', 'Precision bearings'],
    'Medium',
    'Up to 60 m/min',
    'High (±0.1mm)',
    '25.4 mm',
    'N/A',
    '50 kg per pallet',
    'Standard range',
    147
),
(
    'XT',
    'XT Pallet System',
    'Pallet Conveyor',
    'The XT Pallet System is FlexLink''s twin-track pallet solution, offering advanced control and high precision for complex manufacturing applications. It features dual-track technology for enhanced stability and control.',
    ARRAY['Twin-track design for enhanced stability', 'Advanced control and positioning', 'High precision movement', 'Complex routing capabilities', 'Integrated safety systems', 'Modular design for easy expansion'],
    ARRAY['Complex assembly operations', 'Multi-station manufacturing', 'High-precision applications', 'Automated production lines', 'Flexible manufacturing systems'],
    ARRAY['Superior stability and control', 'Advanced automation features', 'High precision and repeatability', 'Complex routing capabilities', 'Enhanced safety features'],
    '{"pallet_size": "300x300 mm to 800x800 mm", "positioning_accuracy": "±0.05 mm", "max_load": "100 kg per pallet", "speed": "Up to 80 m/min", "track_spacing": "50.8 mm"}',
    ARRAY['Reinforced aluminum pallets', 'Precision steel tracks', 'Advanced control components'],
    'High',
    'Up to 80 m/min',
    'Very High (±0.05mm)',
    '50.8 mm',
    'N/A',
    '100 kg per pallet',
    'Standard range',
    257
),
(
    'HU',
    'HU Pallet System',
    'Pallet Conveyor',
    'The HU Pallet System is FlexLink''s specialized pallet handling solution designed for unique applications requiring custom pallet configurations and specialized handling capabilities.',
    ARRAY['Custom pallet configurations', 'Specialized handling capabilities', 'Advanced pallet technology', 'Flexible configuration options', 'Specialized application support', 'Custom integration capabilities'],
    ARRAY['Specialized manufacturing', 'Custom pallet applications', 'Unique handling requirements', 'Specialized assembly operations', 'Custom automation solutions'],
    ARRAY['Custom configuration options', 'Specialized capabilities', 'Flexible design', 'Custom integration', 'Application-specific solutions'],
    '{"pallet_size": "Custom", "positioning_accuracy": "Custom", "max_load": "Custom", "speed": "Custom", "track_spacing": "Custom"}',
    ARRAY['Custom materials based on application requirements'],
    'Custom',
    'Custom',
    'Custom',
    'Custom',
    'Custom',
    'Custom',
    'Custom',
    407
),
-- Belt Conveyor Systems
(
    'WL',
    'WL Modular Belt System',
    'Belt Conveyor',
    'The WL Modular Belt System is FlexLink''s wide-load belt conveyor solution, designed for applications requiring gentle handling of large or wide products. This system features a modular plastic belt design with wide belt options.',
    ARRAY['Wide belt options for large products', 'Gentle handling capabilities', 'Modular belt design', 'Stable support for bulky items', 'Easy cleaning and maintenance', 'Food-grade options available'],
    ARRAY['Large product handling', 'Bulky item transport', 'Food and beverage industry', 'Packaging operations', 'Gentle material handling'],
    ARRAY['Wide belt support', 'Gentle handling', 'Stable product support', 'Easy maintenance', 'Hygienic design options'],
    '{"belt_width": "300-1200 mm", "max_load": "Varies by belt type", "speed": "Up to 30 m/min", "temperature_range": "-10°C to +80°C", "belt_pitch": "12.7 mm"}',
    ARRAY['Polyethylene belt modules', 'Aluminum frame', 'Stainless steel components'],
    'Medium',
    'Up to 30 m/min',
    'Standard',
    '12.7 mm',
    '300-1200 mm',
    'Varies by belt type',
    '-10°C to +80°C',
    441
),
(
    'WK',
    'WK Modular Belt System',
    'Belt Conveyor',
    'The WK Modular Belt System is FlexLink''s compact belt conveyor solution, designed for applications requiring gentle handling in space-constrained environments.',
    ARRAY['Compact belt design', 'Gentle handling capabilities', 'Modular belt construction', 'Space-efficient design', 'Easy cleaning and maintenance', 'Accumulation capabilities'],
    ARRAY['Small product handling', 'Compact production lines', 'Gentle material handling', 'Accumulation applications', 'Space-constrained installations'],
    ARRAY['Compact design', 'Gentle handling', 'Space efficiency', 'Easy maintenance', 'Accumulation capabilities'],
    '{"belt_width": "150-600 mm", "max_load": "Varies by belt type", "speed": "Up to 25 m/min", "temperature_range": "-10°C to +80°C", "belt_pitch": "12.7 mm"}',
    ARRAY['Polyethylene belt modules', 'Aluminum frame', 'Stainless steel components'],
    'Medium',
    'Up to 25 m/min',
    'Standard',
    '12.7 mm',
    '150-600 mm',
    'Varies by belt type',
    '-10°C to +80°C',
    441
),
-- Support Systems
(
    'XC',
    'XC Structural System',
    'Support System',
    'The XC Structural System is FlexLink''s compact structural support solution, designed for applications requiring minimal space requirements while maintaining robust support capabilities.',
    ARRAY['Compact frame design', 'Minimal space requirements', 'Robust support capabilities', 'Easy installation and adjustment', 'Compatible with compact systems', 'Lightweight construction'],
    ARRAY['Compact conveyor support', 'Space-constrained installations', 'Light-duty structural support', 'Modular system construction', 'Flexible layout configurations'],
    ARRAY['Minimal space requirements', 'Easy installation', 'Lightweight design', 'Flexible configuration', 'Cost-effective solution'],
    '{"height_range": "300-800 mm", "load_capacity": "Up to 2000 N per leg", "frame_profiles": "30x30 mm to 60x60 mm", "material": "Aluminum profiles", "surface_finish": "Anodized"}',
    ARRAY['Aluminum profiles', 'Steel fasteners', 'Adjustable feet'],
    'Light',
    'N/A',
    'N/A',
    'N/A',
    'N/A',
    'Up to 2000 N per leg',
    'Standard range',
    5
),
(
    'XF',
    'XF Structural System',
    'Support System',
    'The XF Structural System is FlexLink''s flexible structural support solution, designed for applications requiring adjustable and reconfigurable support structures.',
    ARRAY['Flexible frame design', 'Adjustable configuration', 'Reconfigurable support', 'Easy modification capabilities', 'Modular construction', 'Versatile application support'],
    ARRAY['Flexible conveyor support', 'Adjustable height requirements', 'Reconfigurable layouts', 'Modular system construction', 'Variable application support'],
    ARRAY['Flexible configuration', 'Easy adjustment', 'Reconfigurable design', 'Versatile application', 'Modular construction'],
    '{"height_range": "400-1000 mm", "load_capacity": "Up to 3000 N per leg", "frame_profiles": "40x40 mm to 70x70 mm", "material": "Aluminum profiles", "surface_finish": "Anodized"}',
    ARRAY['Aluminum profiles', 'Steel fasteners', 'Adjustable feet'],
    'Medium',
    'N/A',
    'N/A',
    'N/A',
    'N/A',
    'Up to 3000 N per leg',
    'Standard range',
    5
),
(
    'XD',
    'XD Structural System',
    'Support System',
    'The XD Structural System is FlexLink''s heavy-duty structural support solution, designed for applications requiring maximum load capacity and robust support capabilities.',
    ARRAY['Heavy-duty frame design', 'Maximum load capacity', 'Robust support capabilities', 'Industrial-grade construction', 'Enhanced durability', 'Superior load handling'],
    ARRAY['Heavy conveyor support', 'Industrial installations', 'High-load applications', 'Demanding environments', 'Heavy-duty structural support'],
    ARRAY['Maximum load capacity', 'Robust construction', 'Enhanced durability', 'Industrial-grade performance', 'Superior load handling'],
    '{"height_range": "500-1200 mm", "load_capacity": "Up to 8000 N per leg", "frame_profiles": "60x60 mm to 100x100 mm", "material": "Aluminum profiles", "surface_finish": "Anodized"}',
    ARRAY['Heavy-duty aluminum profiles', 'Reinforced steel fasteners', 'Industrial-grade feet'],
    'High',
    'N/A',
    'N/A',
    'N/A',
    'N/A',
    'Up to 8000 N per leg',
    'Standard range',
    5
),
(
    'GR',
    'Guide Rail System',
    'Support System',
    'The Guide Rail System provides product guidance and positioning support for various conveyor applications. It ensures proper product alignment and prevents product damage during transportation.',
    ARRAY['Adjustable width settings', 'Curved section support', 'Product guidance capabilities', 'Easy installation and adjustment', 'Compatible with multiple systems', 'Wear-resistant materials'],
    ARRAY['Product alignment and guidance', 'Curve section support', 'Width adjustment systems', 'Product positioning', 'Quality control applications'],
    ARRAY['Flexible width adjustment', 'Easy installation and maintenance', 'Compatible with multiple systems', 'Cost-effective solution', 'Reliable performance'],
    '{"width_adjustment": "50-800 mm", "height_adjustment": "20-100 mm", "material_thickness": "2-6 mm", "surface_finish": "Various options", "installation": "Tool-free adjustment"}',
    ARRAY['Aluminum', 'Steel', 'Plastic components'],
    'N/A',
    'N/A',
    'N/A',
    'N/A',
    '50-800 mm',
    'N/A',
    'Standard range',
    67
),
(
    'CS',
    'Conveyor Support System',
    'Support System',
    'The Conveyor Support System provides comprehensive support infrastructure for FlexLink conveyor systems, including mounting brackets, support beams, and structural components.',
    ARRAY['Comprehensive support infrastructure', 'Mounting brackets and support beams', 'Structural alignment components', 'Easy installation and adjustment', 'Compatible with all FlexLink systems', 'Modular support design'],
    ARRAY['Conveyor system support', 'Structural alignment', 'Mounting and installation', 'System stability', 'Infrastructure support'],
    ARRAY['Comprehensive support', 'Easy installation', 'Modular design', 'Compatible with all systems', 'Reliable performance'],
    '{"support_capacity": "Varies by configuration", "adjustment_range": "20-200 mm", "material": "Steel and aluminum", "surface_finish": "Various options", "installation": "Tool-free adjustment"}',
    ARRAY['Steel brackets', 'Aluminum beams', 'Support components'],
    'Varies',
    'N/A',
    'N/A',
    'N/A',
    'N/A',
    'Varies',
    'Standard range',
    5
)
ON CONFLICT (system_code) DO UPDATE SET
    system_name = EXCLUDED.system_name,
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    key_features = EXCLUDED.key_features,
    applications = EXCLUDED.applications,
    advantages = EXCLUDED.advantages,
    technical_specs = EXCLUDED.technical_specs,
    materials = EXCLUDED.materials,
    load_capacity = EXCLUDED.load_capacity,
    speed_range = EXCLUDED.speed_range,
    precision_level = EXCLUDED.precision_level,
    chain_pitch = EXCLUDED.chain_pitch,
    chain_width = EXCLUDED.chain_width,
    max_load = EXCLUDED.max_load,
    temperature_range = EXCLUDED.temperature_range,
    page_reference = EXCLUDED.page_reference,
    updated_at = NOW();

-- Create a view for easy querying of systems
CREATE OR REPLACE VIEW systems_view AS
SELECT 
    id,
    system_code,
    system_name,
    category,
    description,
    key_features,
    applications,
    advantages,
    technical_specs,
    materials,
    load_capacity,
    speed_range,
    precision_level,
    chain_pitch,
    chain_width,
    max_load,
    temperature_range,
    page_reference,
    created_at,
    updated_at
FROM systems;

-- Create a function to search systems by criteria
CREATE OR REPLACE FUNCTION search_systems(
    p_category VARCHAR DEFAULT NULL,
    p_load_capacity VARCHAR DEFAULT NULL,
    p_min_speed VARCHAR DEFAULT NULL,
    p_material VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    system_code VARCHAR,
    system_name VARCHAR,
    category VARCHAR,
    description TEXT,
    key_features TEXT[],
    applications TEXT[],
    advantages TEXT[],
    technical_specs JSONB,
    materials TEXT[],
    load_capacity VARCHAR,
    speed_range VARCHAR,
    precision_level VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.system_code,
        s.system_name,
        s.category,
        s.description,
        s.key_features,
        s.applications,
        s.advantages,
        s.technical_specs,
        s.materials,
        s.load_capacity,
        s.speed_range,
        s.precision_level
    FROM systems s
    WHERE 
        (p_category IS NULL OR s.category = p_category)
        AND (p_load_capacity IS NULL OR s.load_capacity = p_load_capacity)
        AND (p_min_speed IS NULL OR s.speed_range LIKE '%' || p_min_speed || '%')
        AND (p_material IS NULL OR p_material = ANY(s.materials))
    ORDER BY s.category, s.system_code;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get system statistics
CREATE OR REPLACE FUNCTION get_system_stats()
RETURNS TABLE (
    total_systems BIGINT,
    categories_count BIGINT,
    chain_conveyors BIGINT,
    pallet_conveyors BIGINT,
    belt_conveyors BIGINT,
    support_systems BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_systems,
        COUNT(DISTINCT category) as categories_count,
        COUNT(*) FILTER (WHERE category = 'Chain Conveyor') as chain_conveyors,
        COUNT(*) FILTER (WHERE category = 'Pallet Conveyor') as pallet_conveyors,
        COUNT(*) FILTER (WHERE category = 'Belt Conveyor') as belt_conveyors,
        COUNT(*) FILTER (WHERE category = 'Support System') as support_systems
    FROM systems;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE systems IS 'Stores comprehensive information about FlexLink conveyor systems';
COMMENT ON COLUMN systems.technical_specs IS 'JSON object containing technical specifications for the system';
COMMENT ON COLUMN systems.key_features IS 'Array of key features and capabilities of the system';
COMMENT ON COLUMN systems.applications IS 'Array of applications the system is suitable for';
COMMENT ON COLUMN systems.advantages IS 'Array of advantages and benefits of the system'; 