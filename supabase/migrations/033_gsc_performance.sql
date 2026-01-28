-- Migration: Google Search Console performance data
-- Purpose: Store daily GSC metrics for SEO optimization
-- Range: Per-page, per-query performance tracking

-- GSC Performance Data Table
CREATE TABLE gsc_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Page and query identifiers
    page_url TEXT NOT NULL,           -- Full URL from GSC (e.g., https://www.snowthere.com/resorts/austria/kitzbuhel)
    query TEXT,                        -- Search query (nullable for page-level aggregates)

    -- Performance metrics
    impressions INTEGER DEFAULT 0,    -- Number of times page appeared in search
    clicks INTEGER DEFAULT 0,         -- Number of clicks from search
    ctr DECIMAL(5,4),                 -- Click-through rate (0.0000 to 1.0000)
    position DECIMAL(5,2),            -- Average position in search results

    -- Time tracking
    date DATE NOT NULL,               -- The date this data is for
    fetched_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint: one row per page+query+date
    UNIQUE(page_url, query, date)
);

-- Indexes for common queries
CREATE INDEX idx_gsc_date ON gsc_performance(date DESC);
CREATE INDEX idx_gsc_page ON gsc_performance(page_url);
CREATE INDEX idx_gsc_impressions ON gsc_performance(impressions DESC) WHERE impressions > 0;
CREATE INDEX idx_gsc_ctr ON gsc_performance(ctr) WHERE impressions >= 100;

-- Comments
COMMENT ON TABLE gsc_performance IS 'Daily Google Search Console performance data for SEO optimization';
COMMENT ON COLUMN gsc_performance.page_url IS 'Full URL from GSC API';
COMMENT ON COLUMN gsc_performance.query IS 'Search query (null for page-level aggregates)';
COMMENT ON COLUMN gsc_performance.ctr IS 'Click-through rate as decimal (0.0523 = 5.23%)';
COMMENT ON COLUMN gsc_performance.position IS 'Average position (1.0 = first result)';

-- RLS (Row Level Security) - enable for service role only
ALTER TABLE gsc_performance ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "Service role full access on gsc_performance"
    ON gsc_performance
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Anon users can read (for public dashboards if needed)
CREATE POLICY "Anon can read gsc_performance"
    ON gsc_performance
    FOR SELECT
    TO anon
    USING (true);
