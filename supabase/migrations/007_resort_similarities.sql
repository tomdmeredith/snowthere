-- Resort Similarities Table
-- Stores pre-computed similarity scores between resorts for "Similar Resorts" feature
-- Part of P7: Link Primitives implementation

-- ============================================================================
-- RESORT SIMILARITIES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS resort_similarities (
    -- Composite primary key ensures uniqueness and efficient lookups
    resort_a_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,
    resort_b_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,

    -- Overall similarity score (0.0 - 1.0)
    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),

    -- Component scores for debugging and explanation
    family_score_similarity FLOAT,      -- Weight: 25%
    price_tier_similarity FLOAT,        -- Weight: 20%
    region_similarity FLOAT,            -- Weight: 15%
    age_range_similarity FLOAT,         -- Weight: 15%
    pass_network_similarity FLOAT,      -- Weight: 10%
    terrain_mix_similarity FLOAT,       -- Weight: 15%

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    algorithm_version VARCHAR(20) DEFAULT 'v1',

    -- Ensure A < B to avoid duplicate pairs (we only store one direction)
    PRIMARY KEY (resort_a_id, resort_b_id),
    CHECK (resort_a_id < resort_b_id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for finding similar resorts to a given resort
CREATE INDEX IF NOT EXISTS idx_similarities_resort_a
    ON resort_similarities(resort_a_id, similarity_score DESC);

CREATE INDEX IF NOT EXISTS idx_similarities_resort_b
    ON resort_similarities(resort_b_id, similarity_score DESC);

-- Index for finding highest similarity scores
CREATE INDEX IF NOT EXISTS idx_similarities_score
    ON resort_similarities(similarity_score DESC);

-- Index for stale calculation detection
CREATE INDEX IF NOT EXISTS idx_similarities_calculated_at
    ON resort_similarities(calculated_at);

-- ============================================================================
-- INTERNAL LINKS TABLE
-- ============================================================================
-- Tracks internal links between resort pages for SEO and navigation

CREATE TABLE IF NOT EXISTS resort_internal_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source and target resorts
    source_resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,
    target_resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,

    -- Link type for different contexts
    link_type VARCHAR(50) NOT NULL CHECK (link_type IN (
        'similar',           -- Similar resorts section
        'same_pass',         -- Same ski pass network
        'same_region',       -- Same geographic region
        'same_country',      -- Same country
        'comparison',        -- Used in comparison content
        'alternative',       -- Budget/luxury alternative
        'nearby'             -- Geographically nearby
    )),

    -- Link context and metadata
    anchor_text TEXT,                    -- Suggested anchor text
    context_snippet TEXT,                -- Where/how to use this link
    relevance_score FLOAT,               -- How relevant this link is

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Prevent duplicate links
    UNIQUE (source_resort_id, target_resort_id, link_type)
);

-- ============================================================================
-- INDEXES FOR INTERNAL LINKS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_internal_links_source
    ON resort_internal_links(source_resort_id);

CREATE INDEX IF NOT EXISTS idx_internal_links_target
    ON resort_internal_links(target_resort_id);

CREATE INDEX IF NOT EXISTS idx_internal_links_type
    ON resort_internal_links(link_type);

-- ============================================================================
-- HELPER VIEW: Get similar resorts for any resort
-- ============================================================================

CREATE OR REPLACE VIEW v_similar_resorts AS
SELECT
    r.id AS resort_id,
    r.name AS resort_name,
    r.country AS resort_country,
    r.slug AS resort_slug,
    similar.id AS similar_resort_id,
    similar.name AS similar_name,
    similar.country AS similar_country,
    similar.slug AS similar_slug,
    COALESCE(
        s1.similarity_score,
        s2.similarity_score
    ) AS similarity_score,
    COALESCE(
        s1.calculated_at,
        s2.calculated_at
    ) AS calculated_at
FROM resorts r
LEFT JOIN resort_similarities s1 ON r.id = s1.resort_a_id
LEFT JOIN resorts similar ON s1.resort_b_id = similar.id
LEFT JOIN resort_similarities s2 ON r.id = s2.resort_b_id
LEFT JOIN resorts similar2 ON s2.resort_a_id = similar2.id
WHERE similar.id IS NOT NULL OR similar2.id IS NOT NULL;

-- ============================================================================
-- FUNCTION: Get top N similar resorts for a given resort
-- ============================================================================

CREATE OR REPLACE FUNCTION get_similar_resorts(
    p_resort_id UUID,
    p_limit INTEGER DEFAULT 5,
    p_min_score FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    resort_id UUID,
    name VARCHAR(200),
    country VARCHAR(100),
    slug VARCHAR(100),
    similarity_score FLOAT,
    family_overall_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH similar AS (
        -- Get similarities where this resort is resort_a
        SELECT
            s.resort_b_id AS similar_id,
            s.similarity_score
        FROM resort_similarities s
        WHERE s.resort_a_id = p_resort_id
          AND s.similarity_score >= p_min_score

        UNION ALL

        -- Get similarities where this resort is resort_b
        SELECT
            s.resort_a_id AS similar_id,
            s.similarity_score
        FROM resort_similarities s
        WHERE s.resort_b_id = p_resort_id
          AND s.similarity_score >= p_min_score
    )
    SELECT
        r.id AS resort_id,
        r.name,
        r.country,
        r.slug,
        sim.similarity_score,
        fm.family_overall_score
    FROM similar sim
    JOIN resorts r ON r.id = sim.similar_id
    LEFT JOIN resort_family_metrics fm ON fm.resort_id = r.id
    WHERE r.status = 'published'  -- Only return published resorts
    ORDER BY sim.similarity_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: Get internal link suggestions for a resort
-- ============================================================================

CREATE OR REPLACE FUNCTION get_link_suggestions(
    p_resort_id UUID,
    p_link_type VARCHAR(50) DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    target_resort_id UUID,
    target_name VARCHAR(200),
    target_country VARCHAR(100),
    target_slug VARCHAR(100),
    link_type VARCHAR(50),
    anchor_text TEXT,
    relevance_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        il.target_resort_id,
        r.name AS target_name,
        r.country AS target_country,
        r.slug AS target_slug,
        il.link_type,
        il.anchor_text,
        il.relevance_score
    FROM resort_internal_links il
    JOIN resorts r ON r.id = il.target_resort_id
    WHERE il.source_resort_id = p_resort_id
      AND r.status = 'published'
      AND (p_link_type IS NULL OR il.link_type = p_link_type)
    ORDER BY il.relevance_score DESC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE resort_similarities IS 'Pre-computed similarity scores between resort pairs for Similar Resorts feature';
COMMENT ON TABLE resort_internal_links IS 'Internal linking suggestions between resorts for SEO and navigation';
COMMENT ON FUNCTION get_similar_resorts IS 'Returns top N similar resorts for a given resort, filtered by minimum score';
COMMENT ON FUNCTION get_link_suggestions IS 'Returns internal link suggestions for a given resort';
