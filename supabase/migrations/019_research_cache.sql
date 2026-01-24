-- Research Cache: Store search API results for reuse and citation tracking
-- This enables:
-- 1. Avoiding redundant API calls (cost savings)
-- 2. Tracking which sources were used per resort
-- 3. Foundation for citation tracking in generated content

CREATE TABLE IF NOT EXISTS research_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Resort identification (nullable for non-resort queries)
    resort_name VARCHAR(200),
    country VARCHAR(100),

    -- Query details
    query_type VARCHAR(50) NOT NULL,        -- family_reviews, lift_prices, etc.
    query_text TEXT NOT NULL,               -- Actual query string
    api_source VARCHAR(20) NOT NULL,        -- exa, brave, tavily

    -- Results
    results JSONB NOT NULL DEFAULT '[]',    -- Array of search results
    result_count INTEGER DEFAULT 0,

    -- Tavily-specific (stores AI-generated answer)
    ai_answer TEXT,

    -- Metadata
    latency_ms INTEGER,
    error TEXT,                             -- Store errors for debugging

    -- Timestamps
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,    -- When this cache entry should be refreshed

    -- Usage tracking
    use_count INTEGER DEFAULT 0,            -- How many times this cache was used
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Composite unique constraint
    CONSTRAINT unique_resort_query_api UNIQUE (resort_name, country, query_type, api_source)
);

-- Indexes for common queries
CREATE INDEX idx_research_cache_resort ON research_cache(resort_name, country);
CREATE INDEX idx_research_cache_query_type ON research_cache(query_type);
CREATE INDEX idx_research_cache_api ON research_cache(api_source);
CREATE INDEX idx_research_cache_expires ON research_cache(expires_at);
CREATE INDEX idx_research_cache_fetched ON research_cache(fetched_at DESC);

-- Function to check if cache is valid (not expired)
CREATE OR REPLACE FUNCTION is_cache_valid(cache_row research_cache)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN cache_row.expires_at IS NULL OR cache_row.expires_at > NOW();
END;
$$ LANGUAGE plpgsql;

-- Research sources per resort (denormalized for fast access)
-- Links to research_cache entries used when generating content
CREATE TABLE IF NOT EXISTS resort_research_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resort_id UUID REFERENCES resorts(id) ON DELETE CASCADE,

    -- Source details
    url TEXT NOT NULL,
    title TEXT,
    snippet TEXT,
    api_source VARCHAR(20) NOT NULL,        -- exa, brave, tavily
    query_type VARCHAR(50),                 -- Which query found this

    -- Quality indicators
    relevance_score FLOAT,                  -- From search API
    was_cited BOOLEAN DEFAULT FALSE,        -- Did content generation use this?
    cited_in_sections TEXT[],               -- Which sections cited this source

    -- Timestamps
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Prevent duplicates
    CONSTRAINT unique_resort_source UNIQUE (resort_id, url)
);

CREATE INDEX idx_resort_sources_resort ON resort_research_sources(resort_id);
CREATE INDEX idx_resort_sources_cited ON resort_research_sources(was_cited);

-- Add research_sources_metadata to resort_content for quick reference
ALTER TABLE resort_content
ADD COLUMN IF NOT EXISTS research_metadata JSONB DEFAULT '{}';

COMMENT ON COLUMN resort_content.research_metadata IS
'Metadata about research used to generate this content: source counts, APIs used, cache hits, etc.';

-- View for cache statistics
CREATE OR REPLACE VIEW research_cache_stats AS
SELECT
    api_source,
    query_type,
    COUNT(*) as total_entries,
    COUNT(*) FILTER (WHERE expires_at > NOW()) as valid_entries,
    SUM(use_count) as total_uses,
    AVG(latency_ms) as avg_latency_ms,
    COUNT(*) FILTER (WHERE error IS NOT NULL) as error_count
FROM research_cache
GROUP BY api_source, query_type;
