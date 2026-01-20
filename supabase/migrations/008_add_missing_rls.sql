-- Migration: 008_add_missing_rls.sql
-- Purpose: Add RLS policies to tables created in migrations 005-007
-- Date: 2026-01-20

-- =============================================================================
-- PART 1: ROW LEVEL SECURITY POLICIES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- resort_images (from 005_resort_images.sql)
-- Public can read images for published resorts only
-- -----------------------------------------------------------------------------
ALTER TABLE resort_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read resort images"
    ON resort_images FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts
        WHERE resorts.id = resort_images.resort_id
        AND resorts.status = 'published'
    ));

CREATE POLICY "Service can manage resort images"
    ON resort_images FOR ALL
    USING (true)
    WITH CHECK (true);

-- -----------------------------------------------------------------------------
-- discovery_candidates (from 006_discovery_candidates.sql)
-- Service-only table for pipeline use
-- -----------------------------------------------------------------------------
ALTER TABLE discovery_candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service can manage discovery candidates"
    ON discovery_candidates FOR ALL
    USING (true)
    WITH CHECK (true);

-- -----------------------------------------------------------------------------
-- discovery_runs (from 006_discovery_candidates.sql)
-- Service-only table for pipeline use
-- -----------------------------------------------------------------------------
ALTER TABLE discovery_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service can manage discovery runs"
    ON discovery_runs FOR ALL
    USING (true)
    WITH CHECK (true);

-- -----------------------------------------------------------------------------
-- resort_similarities (from 007_resort_similarities.sql)
-- Public can read all similarities (used for "Similar Resorts" section)
-- -----------------------------------------------------------------------------
ALTER TABLE resort_similarities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read resort similarities"
    ON resort_similarities FOR SELECT
    USING (true);

CREATE POLICY "Service can manage resort similarities"
    ON resort_similarities FOR ALL
    USING (true)
    WITH CHECK (true);

-- -----------------------------------------------------------------------------
-- resort_internal_links (from 007_resort_similarities.sql)
-- Public can read all internal links (used for SEO/navigation)
-- -----------------------------------------------------------------------------
ALTER TABLE resort_internal_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read internal links"
    ON resort_internal_links FOR SELECT
    USING (true);

CREATE POLICY "Service can manage internal links"
    ON resort_internal_links FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- PART 2: PERFORMANCE INDEXES
-- =============================================================================

-- Content queue: frequent lookups by resort
CREATE INDEX IF NOT EXISTS idx_content_queue_resort
    ON content_queue(resort_id);

-- Agent audit log: frequent queries by agent name for debugging
CREATE INDEX IF NOT EXISTS idx_agent_audit_log_agent
    ON agent_audit_log(agent_name);

-- Newsletter subscribers: ordered by subscription date
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_subscribed
    ON newsletter_subscribers(subscribed_at);

-- Resort similarities: lookup by calculation freshness
CREATE INDEX IF NOT EXISTS idx_resort_similarities_calculated
    ON resort_similarities(calculated_at);

-- Discovery candidates: lookup by status and priority
CREATE INDEX IF NOT EXISTS idx_discovery_candidates_status
    ON discovery_candidates(status, priority DESC);

-- Discovery runs: lookup by run date
CREATE INDEX IF NOT EXISTS idx_discovery_runs_started
    ON discovery_runs(started_at DESC);

-- Resort images: lookup by resort and image type
CREATE INDEX IF NOT EXISTS idx_resort_images_resort_type
    ON resort_images(resort_id, image_type);

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- After running this migration, verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
