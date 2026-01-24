-- Pricing cache table for multi-strategy cost acquisition
-- Round 5.9.2: Cache pricing results to avoid repeated API calls

CREATE TABLE IF NOT EXISTS pricing_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resort_name VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,
    costs JSONB NOT NULL,
    currency VARCHAR(3),
    source VARCHAR(50) NOT NULL,  -- 'tavily', 'scrape', 'claude', 'pass_network', 'manual'
    confidence DECIMAL(3,2) CHECK (confidence BETWEEN 0 AND 1),
    official_website_url TEXT,    -- Store discovered URL for future scraping
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Unique constraint on resort + country (one cache entry per resort)
    CONSTRAINT uq_pricing_cache_resort UNIQUE(resort_name, country)
);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_pricing_cache_expires ON pricing_cache(expires_at)
WHERE expires_at IS NOT NULL;

-- Index for source analysis
CREATE INDEX IF NOT EXISTS idx_pricing_cache_source ON pricing_cache(source);

-- RLS policies
ALTER TABLE pricing_cache ENABLE ROW LEVEL SECURITY;

-- Service role can manage pricing cache
CREATE POLICY "Service role manages pricing cache"
ON pricing_cache
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Anon users can read pricing cache (for potential frontend use)
CREATE POLICY "Anon can read pricing cache"
ON pricing_cache
FOR SELECT
TO anon
USING (true);

COMMENT ON TABLE pricing_cache IS 'Cache for pricing data acquired via multi-strategy system (30-day TTL)';
COMMENT ON COLUMN pricing_cache.source IS 'Acquisition strategy used: tavily, scrape, claude, pass_network, manual';
COMMENT ON COLUMN pricing_cache.confidence IS 'Confidence score 0-1 based on source reliability';
