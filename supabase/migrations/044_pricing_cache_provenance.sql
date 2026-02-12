-- Add provenance columns to pricing_cache
-- Round 24: Track source URLs and validation notes for Exa discovery + Claude interpretation

ALTER TABLE pricing_cache
ADD COLUMN IF NOT EXISTS source_urls JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS validation_notes JSONB DEFAULT '[]'::JSONB;

COMMENT ON COLUMN pricing_cache.source_urls IS 'Array of URLs used to acquire pricing (official page, corroboration sources)';
COMMENT ON COLUMN pricing_cache.validation_notes IS 'Array of validation notes from country-specific price checks';
