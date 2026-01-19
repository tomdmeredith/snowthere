-- Trail Map Data Migration
-- Adds trail map data storage for OpenStreetMap piste information
-- Part of P3: Trail Map Primitive implementation

-- Add trail_map_data column to resorts table
-- Stores OSM piste/lift data as JSONB for flexibility
ALTER TABLE resorts
ADD COLUMN IF NOT EXISTS trail_map_data JSONB DEFAULT NULL;

-- Add index for querying resorts with/without trail data
CREATE INDEX IF NOT EXISTS idx_resorts_has_trail_map
ON resorts ((trail_map_data IS NOT NULL));

-- Comment for documentation
COMMENT ON COLUMN resorts.trail_map_data IS 'OpenStreetMap trail map data including pistes, lifts, and quality assessment. Structured as: {quality, piste_count, lift_count, center_coords, bbox, pistes: [...], lifts: [...], official_map_url, osm_attribution, confidence}';

-- Example structure stored in trail_map_data:
-- {
--   "quality": "full|partial|minimal|none",
--   "piste_count": 25,
--   "lift_count": 8,
--   "center_coords": [47.0833, 10.8333],
--   "bbox": [46.98, 10.73, 47.18, 10.93],
--   "official_map_url": "https://resort.com/trail-map",
--   "osm_attribution": "© OpenStreetMap contributors, ODbL",
--   "confidence": 0.85,
--   "difficulty_breakdown": {"easy": 10, "intermediate": 8, "advanced": 5, "expert": 2},
--   "pistes": [
--     {"osm_id": 123, "name": "Blue Run", "difficulty": "easy", "piste_type": "downhill"}
--   ],
--   "lifts": [
--     {"osm_id": 456, "name": "Main Gondola", "lift_type": "gondola", "capacity": 2400}
--   ],
--   "fetched_at": "2026-01-17T12:00:00Z"
-- }
