-- Discovery Candidates Table
-- Stores potential resorts identified through keyword research, gap analysis,
-- and trending topic discovery for future content creation.

-- Discovery candidates table
CREATE TABLE IF NOT EXISTS discovery_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Resort identification
    resort_name VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),

    -- Scoring
    opportunity_score FLOAT NOT NULL DEFAULT 0.0,
    search_volume_monthly INT,
    competitive_gap VARCHAR(20),  -- low, medium, high
    value_potential VARCHAR(20),  -- low, medium, high

    -- Discovery context
    discovery_source VARCHAR(50) NOT NULL,  -- keyword_research, gap_analysis, trending, exploration
    pass_networks JSONB DEFAULT '[]'::jsonb,  -- Pass affiliations: ["Epic", "Ikon"]

    -- Detailed signals
    signals JSONB NOT NULL DEFAULT '{}'::jsonb,  -- All discovery signals as JSON
    reasoning TEXT,  -- LLM reasoning for why this was identified

    -- Lifecycle
    status VARCHAR(20) DEFAULT 'pending',  -- pending, queued, researched, published, rejected
    priority_rank INT DEFAULT 0,  -- For sorting candidates

    -- Timestamps
    discovered_at TIMESTAMP DEFAULT NOW(),
    queued_at TIMESTAMP,
    processed_at TIMESTAMP,

    -- Prevent duplicates
    UNIQUE(resort_name, country)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_discovery_candidates_status
    ON discovery_candidates(status);

CREATE INDEX IF NOT EXISTS idx_discovery_candidates_score
    ON discovery_candidates(opportunity_score DESC);

CREATE INDEX IF NOT EXISTS idx_discovery_candidates_source
    ON discovery_candidates(discovery_source);

CREATE INDEX IF NOT EXISTS idx_discovery_candidates_country
    ON discovery_candidates(country);

-- Discovery runs audit table
CREATE TABLE IF NOT EXISTS discovery_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Run configuration
    mode VARCHAR(50) NOT NULL,  -- keyword_research, gap_discovery, trending, exploration, full
    config JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Results summary
    candidates_found INT DEFAULT 0,
    candidates_new INT DEFAULT 0,
    candidates_updated INT DEFAULT 0,

    -- Execution details
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',  -- running, completed, failed
    error TEXT,

    -- Cost tracking
    api_cost FLOAT DEFAULT 0.0,
    tokens_used INT DEFAULT 0,

    -- Reasoning and observations
    reasoning TEXT,
    patterns_discovered JSONB DEFAULT '[]'::jsonb
);

-- Index for recent runs
CREATE INDEX IF NOT EXISTS idx_discovery_runs_started
    ON discovery_runs(started_at DESC);

-- Comments for documentation
COMMENT ON TABLE discovery_candidates IS 'Potential ski resorts identified through search demand analysis and gap detection';
COMMENT ON COLUMN discovery_candidates.opportunity_score IS 'Weighted score: search_demand(0.25) + competitive_gap(0.30) + value_potential(0.20) + coverage(0.15) + exploration(0.10)';
COMMENT ON COLUMN discovery_candidates.signals IS 'Raw discovery signals: {keyword_data, trending_score, coverage_gap, related_resorts, etc.}';
COMMENT ON COLUMN discovery_candidates.discovery_source IS 'How this candidate was found: keyword_research, gap_analysis, trending, or exploration';

COMMENT ON TABLE discovery_runs IS 'Audit trail for discovery agent executions';
