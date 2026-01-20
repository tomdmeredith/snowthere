-- Migration: 010_guides.sql
-- Purpose: Create guides table for content hub
-- Date: 2026-01-20

-- =============================================================================
-- GUIDES TABLE
-- =============================================================================
-- Content hub for guides like:
-- - Comparison: "Best Resorts for Toddlers", "Best Budget Family Resorts"
-- - How-To: "Ultimate Family Ski Packing List", "First Ski Trip Checklist"
-- - Regional: "Austria Family Ski Guide", "Colorado Family Resorts"
-- - Pass: "Epic vs Ikon for Families"

CREATE TABLE IF NOT EXISTS guides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- URL and identification
    slug VARCHAR(200) UNIQUE NOT NULL,
    title VARCHAR(300) NOT NULL,

    -- Guide categorization
    guide_type VARCHAR(50) NOT NULL CHECK (guide_type IN (
        'comparison',  -- Resort comparisons/rankings
        'how-to',      -- Practical guides and checklists
        'regional',    -- Region/country-specific guides
        'pass',        -- Ski pass guides
        'seasonal',    -- Season-specific content
        'gear'         -- Equipment/packing guides
    )),

    -- Optional category for grouping (e.g., "toddlers", "budget", "beginners")
    category VARCHAR(100),

    -- Content
    excerpt TEXT,                -- Short description for listings
    content JSONB NOT NULL,      -- Structured content sections
    featured_image_url TEXT,     -- Hero image

    -- SEO
    seo_meta JSONB DEFAULT '{}'::JSONB,

    -- Related resorts (for comparison guides)
    featured_resort_ids UUID[] DEFAULT '{}',

    -- Publication
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    author VARCHAR(100) DEFAULT 'Snowthere Team',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Common query patterns
CREATE INDEX IF NOT EXISTS idx_guides_status ON guides(status);
CREATE INDEX IF NOT EXISTS idx_guides_type ON guides(guide_type);
CREATE INDEX IF NOT EXISTS idx_guides_category ON guides(category);
CREATE INDEX IF NOT EXISTS idx_guides_published ON guides(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_guides_slug ON guides(slug);

-- Full-text search on title and excerpt
CREATE INDEX IF NOT EXISTS idx_guides_title_search ON guides USING gin(to_tsvector('english', title));

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

ALTER TABLE guides ENABLE ROW LEVEL SECURITY;

-- Public can read published guides
CREATE POLICY "Public can read published guides"
    ON guides FOR SELECT
    USING (status = 'published');

-- Service can manage all guides
CREATE POLICY "Service can manage guides"
    ON guides FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE TRIGGER update_guides_updated_at
    BEFORE UPDATE ON guides
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- GUIDE-RESORT RELATIONSHIP TABLE (Many-to-Many)
-- =============================================================================
-- For guides that reference multiple resorts

CREATE TABLE IF NOT EXISTS guide_resorts (
    guide_id UUID NOT NULL REFERENCES guides(id) ON DELETE CASCADE,
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,
    display_order INTEGER DEFAULT 0,
    highlight_reason TEXT,  -- Why this resort is featured in the guide
    PRIMARY KEY (guide_id, resort_id)
);

CREATE INDEX IF NOT EXISTS idx_guide_resorts_guide ON guide_resorts(guide_id);
CREATE INDEX IF NOT EXISTS idx_guide_resorts_resort ON guide_resorts(resort_id);

-- RLS for guide_resorts
ALTER TABLE guide_resorts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read guide resorts"
    ON guide_resorts FOR SELECT
    USING (true);

CREATE POLICY "Service can manage guide resorts"
    ON guide_resorts FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- SAMPLE GUIDE CONTENT STRUCTURE
-- =============================================================================
-- The content JSONB follows this structure:
-- {
--   "sections": [
--     {
--       "type": "intro",
--       "title": "Introduction",
--       "content": "Text content here..."
--     },
--     {
--       "type": "list",
--       "title": "Top 5 Resorts",
--       "items": [
--         {"name": "Resort", "description": "Why it's great", "resort_slug": "park-city"}
--       ]
--     },
--     {
--       "type": "checklist",
--       "title": "Packing List",
--       "items": ["Ski jacket", "Gloves", ...]
--     },
--     {
--       "type": "comparison_table",
--       "title": "Resort Comparison",
--       "columns": ["Resort", "Price", "Family Score"],
--       "rows": [...]
--     },
--     {
--       "type": "faq",
--       "items": [
--         {"question": "Q?", "answer": "A."}
--       ]
--     }
--   ]
-- }

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- After running, verify:
-- SELECT * FROM guides LIMIT 1;
-- SELECT * FROM guide_resorts LIMIT 1;
