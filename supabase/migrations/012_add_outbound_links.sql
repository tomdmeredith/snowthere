-- Migration: Resort Outbound Links Table
-- Created: 2026-01-21
-- Purpose: Store helpful outbound links for each resort with UTM tracking support

CREATE TABLE IF NOT EXISTS resort_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,

    -- Link information
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,

    -- Categorization
    category TEXT NOT NULL,  -- 'official', 'lodging', 'dining', 'activity', 'transport', 'rental'

    -- Affiliate tracking (future use)
    is_affiliate BOOLEAN DEFAULT FALSE,
    affiliate_url TEXT,

    -- Metadata
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_category CHECK (
        category IN ('official', 'lodging', 'dining', 'activity', 'transport', 'rental', 'ski_school', 'childcare')
    )
);

-- Index for efficient resort lookups
CREATE INDEX IF NOT EXISTS idx_resort_links_resort_id
ON resort_links(resort_id);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS idx_resort_links_category
ON resort_links(resort_id, category);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_resort_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resort_links_updated_at
    BEFORE UPDATE ON resort_links
    FOR EACH ROW
    EXECUTE FUNCTION update_resort_links_updated_at();

-- RLS Policies
ALTER TABLE resort_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access for resort_links"
ON resort_links FOR SELECT
USING (true);

CREATE POLICY "Service role insert for resort_links"
ON resort_links FOR INSERT
WITH CHECK (true);

CREATE POLICY "Service role update for resort_links"
ON resort_links FOR UPDATE
USING (true);

CREATE POLICY "Service role delete for resort_links"
ON resort_links FOR DELETE
USING (true);

COMMENT ON TABLE resort_links IS 'Helpful outbound links for ski resorts with UTM tracking support';
COMMENT ON COLUMN resort_links.category IS 'Link category: official, lodging, dining, activity, transport, rental, ski_school, childcare';
COMMENT ON COLUMN resort_links.is_affiliate IS 'Whether this link should use affiliate URL when available';
