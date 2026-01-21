-- Add tagline column to resort_content table
-- Stores unique 8-12 word taglines for each resort

ALTER TABLE resort_content ADD COLUMN IF NOT EXISTS tagline TEXT;

COMMENT ON COLUMN resort_content.tagline IS 'Unique 8-12 word tagline capturing resort personality';
