-- Migration: Resort Entities (first-class entity atoms)
-- Created: 2026-02-02
-- Purpose: Store extracted entities as persistent atoms. Links become molecules
--          computed from entity atoms + resolution data + affiliate rules.
-- Part of: Entity Link Coverage Overhaul

CREATE TABLE IF NOT EXISTS resort_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,

    -- Entity identification
    name TEXT NOT NULL,
    name_normalized TEXT NOT NULL,
    entity_type TEXT NOT NULL,

    -- Provenance
    source TEXT NOT NULL DEFAULT 'extraction',  -- extraction, research, generation, manual
    source_url TEXT,                             -- Pre-resolved URL from research/generation

    -- Content context
    sections TEXT[] DEFAULT '{}',                -- Which content sections reference this
    editorial_role TEXT DEFAULT 'mentioned',     -- mentioned, recommended, warned_about

    -- Resolution state
    resolution_status TEXT DEFAULT 'pending',    -- pending, resolved, failed, brand
    resolved_url TEXT,                           -- Final chosen URL
    google_place_id TEXT,
    maps_url TEXT,
    confidence FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One entity per resort per normalized name + type
    UNIQUE(resort_id, name_normalized, entity_type)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_resort_entities_resort
ON resort_entities(resort_id);

CREATE INDEX IF NOT EXISTS idx_resort_entities_type
ON resort_entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_resort_entities_resolution
ON resort_entities(resolution_status);

CREATE INDEX IF NOT EXISTS idx_resort_entities_name
ON resort_entities(name_normalized);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_resort_entities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resort_entities_updated_at
    BEFORE UPDATE ON resort_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_resort_entities_updated_at();

-- RLS Policies
ALTER TABLE resort_entities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access for resort_entities"
ON resort_entities FOR SELECT
USING (true);

CREATE POLICY "Service role insert for resort_entities"
ON resort_entities FOR INSERT
WITH CHECK (true);

CREATE POLICY "Service role update for resort_entities"
ON resort_entities FOR UPDATE
USING (true);

CREATE POLICY "Service role delete for resort_entities"
ON resort_entities FOR DELETE
USING (true);

-- Valid entity types
ALTER TABLE resort_entities
ADD CONSTRAINT valid_resort_entity_type CHECK (
    entity_type IN (
        'hotel', 'restaurant', 'ski_school', 'rental', 'activity', 'grocery',
        'childcare', 'airport', 'transport', 'bar', 'cafe', 'retail', 'village'
    )
);

-- Valid resolution statuses
ALTER TABLE resort_entities
ADD CONSTRAINT valid_resolution_status CHECK (
    resolution_status IN ('pending', 'resolved', 'failed', 'brand')
);

-- Valid sources
ALTER TABLE resort_entities
ADD CONSTRAINT valid_entity_source CHECK (
    source IN ('extraction', 'research', 'generation', 'manual')
);

-- Valid editorial roles
ALTER TABLE resort_entities
ADD CONSTRAINT valid_editorial_role CHECK (
    editorial_role IN ('mentioned', 'recommended', 'warned_about')
);

COMMENT ON TABLE resort_entities IS 'First-class entity atoms extracted from resort content. Links are molecules computed from these atoms.';
COMMENT ON COLUMN resort_entities.name_normalized IS 'Lowercase, whitespace-normalized entity name for dedup';
COMMENT ON COLUMN resort_entities.source IS 'How this entity was discovered: extraction (from content), research (from sources), generation (during content gen), manual';
COMMENT ON COLUMN resort_entities.resolution_status IS 'Link resolution state: pending (not yet resolved), resolved (has confident URL), failed (could not resolve), brand (well-known brand with canonical URL)';
