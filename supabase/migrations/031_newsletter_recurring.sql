-- Migration: 031_newsletter_recurring.sql
-- Purpose: Add recurring newsletter support to email system
-- Design: Morning Brew-style weekly digest with structured sections
--
-- Tables:
-- - email_sequences: Add recurrence fields
-- - newsletter_issues: Track individual newsletter editions

-- =============================================================================
-- EXTEND EMAIL SEQUENCES FOR RECURRENCE
-- =============================================================================

-- Add recurrence fields to email_sequences (PostgreSQL requires separate statements)
ALTER TABLE email_sequences ADD COLUMN IF NOT EXISTS recurrence_pattern TEXT CHECK (recurrence_pattern IN ('weekly', 'bi-weekly', 'monthly'));
ALTER TABLE email_sequences ADD COLUMN IF NOT EXISTS recurrence_day INTEGER CHECK (recurrence_day >= 0 AND recurrence_day <= 31);
ALTER TABLE email_sequences ADD COLUMN IF NOT EXISTS recurrence_time TIME DEFAULT '06:00';
ALTER TABLE email_sequences ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'America/Los_Angeles';

COMMENT ON COLUMN email_sequences.recurrence_pattern IS 'Recurring pattern: weekly, bi-weekly, monthly. NULL for one-time sequences';
COMMENT ON COLUMN email_sequences.recurrence_day IS 'Day to send: 0-6 for weekly (0=Sunday, 4=Thursday), 1-31 for monthly';
COMMENT ON COLUMN email_sequences.recurrence_time IS 'Time of day to send (in timezone)';
COMMENT ON COLUMN email_sequences.timezone IS 'Timezone for recurrence_time';

-- =============================================================================
-- NEWSLETTER ISSUES
-- Track individual newsletter editions with content and stats
-- =============================================================================
CREATE TABLE newsletter_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id UUID NOT NULL REFERENCES email_sequences(id) ON DELETE CASCADE,

    -- Issue metadata
    issue_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    preview_text TEXT,

    -- Content storage
    content_html TEXT,
    content_json JSONB NOT NULL DEFAULT '{}',  -- Structured sections for regeneration

    -- Status lifecycle
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'generating', 'scheduled', 'sending', 'sent', 'failed')),
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    generation_started_at TIMESTAMPTZ,
    generation_completed_at TIMESTAMPTZ,

    -- Statistics (populated after send via Resend webhooks)
    stats JSONB DEFAULT '{}'::JSONB,  -- {"recipients": 0, "delivered": 0, "opened": 0, "clicked": 0}

    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(sequence_id, issue_number)
);

CREATE INDEX idx_newsletter_issues_sequence ON newsletter_issues(sequence_id);
CREATE INDEX idx_newsletter_issues_status ON newsletter_issues(status);
CREATE INDEX idx_newsletter_issues_scheduled ON newsletter_issues(scheduled_for) WHERE status = 'scheduled';

-- =============================================================================
-- NEWSLETTER CONTENT SECTIONS
-- Individual sections that make up a newsletter issue
-- =============================================================================
CREATE TABLE newsletter_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES newsletter_issues(id) ON DELETE CASCADE,

    -- Section metadata
    section_type TEXT NOT NULL CHECK (section_type IN (
        'cold_open', 'new_resorts', 'trending', 'parent_hack',
        'pass_intel', 'community_photo', 'whats_next', 'referral_cta'
    )),
    display_order INTEGER NOT NULL DEFAULT 0,

    -- Content
    title TEXT,
    content_html TEXT,
    content_data JSONB DEFAULT '{}',  -- Type-specific structured data

    -- Source tracking
    source_type TEXT,  -- 'database', 'ai_generated', 'manual'
    source_ids JSONB DEFAULT '[]',  -- References to source data (resort IDs, etc.)

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(issue_id, section_type)
);

CREATE INDEX idx_newsletter_sections_issue ON newsletter_sections(issue_id);

-- =============================================================================
-- NEWSLETTER SENDS
-- Track individual sends for each newsletter issue
-- =============================================================================
CREATE TABLE newsletter_sends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES newsletter_issues(id) ON DELETE CASCADE,
    subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,

    -- Personalization applied
    personalized_content_hash TEXT,  -- Hash of personalized content for dedup

    -- Resend tracking
    resend_id TEXT,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')),

    -- Timestamps
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,

    -- Error tracking
    error_message TEXT,

    UNIQUE(issue_id, subscriber_id)
);

CREATE INDEX idx_newsletter_sends_issue ON newsletter_sends(issue_id);
CREATE INDEX idx_newsletter_sends_subscriber ON newsletter_sends(subscriber_id);
CREATE INDEX idx_newsletter_sends_status ON newsletter_sends(status);

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================
ALTER TABLE newsletter_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_sends ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY "service_role_full_access_issues" ON newsletter_issues FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_sections" ON newsletter_sections FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_sends" ON newsletter_sends FOR ALL TO service_role USING (true) WITH CHECK (true);

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Auto-update updated_at on newsletter_issues
CREATE TRIGGER update_newsletter_issues_timestamp
    BEFORE UPDATE ON newsletter_issues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Get next issue number for a sequence
CREATE OR REPLACE FUNCTION get_next_issue_number(p_sequence_id UUID)
RETURNS INTEGER AS $$
DECLARE
    max_issue INTEGER;
BEGIN
    SELECT COALESCE(MAX(issue_number), 0) INTO max_issue
    FROM newsletter_issues
    WHERE sequence_id = p_sequence_id;

    RETURN max_issue + 1;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- SEED WEEKLY NEWSLETTER SEQUENCE
-- =============================================================================
INSERT INTO email_sequences (
    name,
    trigger_event,
    trigger_conditions,
    status,
    recurrence_pattern,
    recurrence_day,
    recurrence_time,
    timezone
) VALUES (
    'weekly_newsletter',
    'recurring',
    '{"type": "newsletter", "version": "1.0"}'::JSONB,
    'active',
    'weekly',
    4,  -- Thursday
    '06:00',
    'America/Los_Angeles'
) ON CONFLICT (name) DO UPDATE SET
    recurrence_pattern = EXCLUDED.recurrence_pattern,
    recurrence_day = EXCLUDED.recurrence_day,
    recurrence_time = EXCLUDED.recurrence_time,
    timezone = EXCLUDED.timezone;

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE newsletter_issues IS 'Individual newsletter editions with content and stats';
COMMENT ON TABLE newsletter_sections IS 'Content sections within a newsletter issue';
COMMENT ON TABLE newsletter_sends IS 'Track individual subscriber sends for newsletters';
COMMENT ON FUNCTION get_next_issue_number IS 'Get the next issue number for a newsletter sequence';
