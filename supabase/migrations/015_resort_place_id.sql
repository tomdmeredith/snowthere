-- Add Google Place ID column to resorts table for UGC photo caching
-- This stores the Google Places API place_id after first successful lookup
-- to avoid redundant API calls on subsequent photo fetches

ALTER TABLE resorts
ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255);

-- Index for fast lookups when checking if we already have a place_id
CREATE INDEX IF NOT EXISTS idx_resorts_google_place_id
ON resorts(google_place_id) WHERE google_place_id IS NOT NULL;

COMMENT ON COLUMN resorts.google_place_id IS
'Cached Google Places ID for UGC photo fetching - saves API calls';
