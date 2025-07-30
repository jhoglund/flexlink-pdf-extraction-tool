-- Fix Database Schema for Larger Weight Values
-- Run this in your Supabase SQL Editor to fix the weight_kg field

-- Alter the weight_kg column to handle larger values
ALTER TABLE component_specifications 
ALTER COLUMN weight_kg TYPE DECIMAL(10,3);

-- Also increase the price field for larger values
ALTER TABLE component_specifications 
ALTER COLUMN price_euro TYPE DECIMAL(12,2);

-- Add a comment explaining the change
COMMENT ON COLUMN component_specifications.weight_kg IS 'Weight in kg (supports values up to 9999999.999)';
COMMENT ON COLUMN component_specifications.price_euro IS 'Price in euros (supports values up to 99999999999.99)'; 