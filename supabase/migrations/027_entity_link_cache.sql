-- Migration: Entity Link Cache
-- Created: 2026-01-26
-- Purpose: Cache resolved external entity links (Google Places, affiliates)
-- Part of Round 7: External Linking & Affiliate System

-- Entity link cache for Google Places and affiliate lookups
CREATE TABLE IF NOT EXISTS entity_link_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Entity identification
    name_normalized TEXT NOT NULL,       -- Lowercase, trimmed entity name
    entity_type TEXT NOT NULL,           -- 'hotel', 'restaurant', 'ski_school', 'rental', 'activity'
    location_context TEXT NOT NULL,      -- Country or "Resort, Country" for disambiguation

    -- Google Places data
    google_place_id TEXT,                -- Stable identifier (cache indefinitely)
    resolved_name TEXT,                  -- Official name from Google
    direct_url TEXT,                     -- Official website
    maps_url TEXT,                       -- Google Maps link

    -- Affiliate data
    affiliate_url TEXT,                  -- Affiliate link if available
    affiliate_program TEXT,              -- 'booking.com', 'ski.com', etc.

    -- Metadata
    resolution_source TEXT,              -- 'google_places', 'manual', 'affiliate_lookup'
    confidence FLOAT,                    -- 0-1 confidence in the match

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,              -- For non-place_id data (website, hours change)

    -- Unique constraint on entity identification
    CONSTRAINT entity_link_cache_unique
        UNIQUE(name_normalized, entity_type, location_context)
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_entity_link_cache_lookup
ON entity_link_cache(name_normalized, entity_type, location_context);

CREATE INDEX IF NOT EXISTS idx_entity_link_cache_place_id
ON entity_link_cache(google_place_id) WHERE google_place_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_entity_link_cache_expires
ON entity_link_cache(expires_at) WHERE expires_at IS NOT NULL;

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_entity_link_cache_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER entity_link_cache_updated_at
    BEFORE UPDATE ON entity_link_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_entity_link_cache_updated_at();

-- RLS Policies
ALTER TABLE entity_link_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access for entity_link_cache"
ON entity_link_cache FOR SELECT
USING (true);

CREATE POLICY "Service role insert for entity_link_cache"
ON entity_link_cache FOR INSERT
WITH CHECK (true);

CREATE POLICY "Service role update for entity_link_cache"
ON entity_link_cache FOR UPDATE
USING (true);

CREATE POLICY "Service role delete for entity_link_cache"
ON entity_link_cache FOR DELETE
USING (true);

-- Valid entity types constraint
ALTER TABLE entity_link_cache
ADD CONSTRAINT valid_entity_type CHECK (
    entity_type IN ('hotel', 'restaurant', 'ski_school', 'rental', 'activity', 'grocery', 'transport', 'official')
);

COMMENT ON TABLE entity_link_cache IS 'Cache for resolved external entity links (Google Places, affiliates)';
COMMENT ON COLUMN entity_link_cache.google_place_id IS 'Google Places ID - stable, cache indefinitely';
COMMENT ON COLUMN entity_link_cache.expires_at IS 'Expiration for volatile data like websites/hours (90 days recommended)';
