-- Migration: 026_email_system.sql
-- Purpose: Agent-native email system with Resend
-- Design: Atomic primitives, full CRUD, agents have parity with users
--
-- Tables:
-- - subscribers: Email list management
-- - email_templates: Reusable email templates
-- - email_sequences: Automated email flows (welcome, nurture)
-- - email_sequence_steps: Individual steps within sequences
-- - email_sends: Audit log of all emails sent

-- =============================================================================
-- SUBSCRIBERS
-- Core email list - subscribers from newsletter signup, lead magnets, etc.
-- =============================================================================
CREATE TABLE subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT,

    -- Acquisition tracking
    source TEXT NOT NULL DEFAULT 'website',  -- website, lead_magnet, referral, import
    source_detail TEXT,  -- specific page, magnet name, referrer code

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced', 'complained')),
    confirmed_at TIMESTAMPTZ,  -- Double opt-in confirmation
    unsubscribed_at TIMESTAMPTZ,

    -- Preferences (JSONB for flexibility)
    preferences JSONB DEFAULT '{}',  -- {"frequency": "weekly", "interests": ["deals", "tips"]}

    -- Referral tracking (Morning Brew style)
    referral_code TEXT UNIQUE,
    referred_by UUID REFERENCES subscribers(id),
    referral_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_subscribers_email ON subscribers(email);
CREATE INDEX idx_subscribers_status ON subscribers(status);
CREATE INDEX idx_subscribers_source ON subscribers(source);
CREATE INDEX idx_subscribers_referral_code ON subscribers(referral_code);
CREATE INDEX idx_subscribers_created_at ON subscribers(created_at);

-- =============================================================================
-- EMAIL TEMPLATES
-- Reusable templates for transactional and marketing emails
-- =============================================================================
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,  -- welcome_checklist, day_2_alps_vs_colorado

    -- Content
    subject TEXT NOT NULL,
    preview_text TEXT,  -- Email preview snippet
    body_html TEXT NOT NULL,
    body_text TEXT,  -- Plain text fallback

    -- Metadata
    category TEXT NOT NULL DEFAULT 'transactional' CHECK (category IN ('transactional', 'marketing', 'sequence')),
    variables JSONB DEFAULT '[]',  -- ["{{subscriber_name}}", "{{resort_name}}"]

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- EMAIL SEQUENCES
-- Automated email flows (welcome series, nurture, re-engagement)
-- =============================================================================
CREATE TABLE email_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,  -- welcome, nurture, winback

    -- Trigger conditions
    trigger_event TEXT NOT NULL,  -- on_subscribe, on_tag_add, manual
    trigger_conditions JSONB DEFAULT '{}',  -- {"source": "lead_magnet"}

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'draft')),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- EMAIL SEQUENCE STEPS
-- Individual emails within a sequence
-- =============================================================================
CREATE TABLE email_sequence_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id UUID NOT NULL REFERENCES email_sequences(id) ON DELETE CASCADE,

    -- Step configuration
    step_number INTEGER NOT NULL,
    template_id UUID NOT NULL REFERENCES email_templates(id),

    -- Timing
    delay_days INTEGER NOT NULL DEFAULT 0,  -- Days after previous step (0 = immediately)
    send_time TIME,  -- Preferred time of day (null = any time)

    -- Conditions (optional)
    skip_conditions JSONB DEFAULT '{}',  -- {"if_opened": "step_1"} = skip if opened step 1

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(sequence_id, step_number)
);

CREATE INDEX idx_sequence_steps_sequence ON email_sequence_steps(sequence_id);

-- =============================================================================
-- EMAIL SENDS
-- Audit log of all emails sent - critical for compliance and debugging
-- =============================================================================
CREATE TABLE email_sends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,

    -- What was sent
    template_id UUID REFERENCES email_templates(id),
    sequence_id UUID REFERENCES email_sequences(id),
    step_number INTEGER,

    -- Resend tracking
    resend_id TEXT,  -- Resend's message ID for tracking

    -- Delivery status
    status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('queued', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')),

    -- Engagement tracking
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX idx_email_sends_subscriber ON email_sends(subscriber_id);
CREATE INDEX idx_email_sends_template ON email_sends(template_id);
CREATE INDEX idx_email_sends_sequence ON email_sends(sequence_id, step_number);
CREATE INDEX idx_email_sends_status ON email_sends(status);
CREATE INDEX idx_email_sends_sent_at ON email_sends(sent_at);

-- =============================================================================
-- SUBSCRIBER SEQUENCE PROGRESS
-- Track where each subscriber is in each sequence
-- =============================================================================
CREATE TABLE subscriber_sequence_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
    sequence_id UUID NOT NULL REFERENCES email_sequences(id) ON DELETE CASCADE,

    -- Progress
    current_step INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_sent_at TIMESTAMPTZ,
    next_send_at TIMESTAMPTZ,

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    completed_at TIMESTAMPTZ,

    UNIQUE(subscriber_id, sequence_id)
);

CREATE INDEX idx_sequence_progress_subscriber ON subscriber_sequence_progress(subscriber_id);
CREATE INDEX idx_sequence_progress_next_send ON subscriber_sequence_progress(next_send_at) WHERE status = 'active';

-- =============================================================================
-- REFERRALS (Morning Brew style)
-- Track referral rewards and milestones
-- =============================================================================
CREATE TABLE referral_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,

    -- Milestone reached
    milestone INTEGER NOT NULL,  -- 1, 3, 5, 10, 25
    reward_type TEXT NOT NULL,  -- pdf, sticker, tote, gift_card
    reward_detail TEXT,  -- "Alps vs Colorado PDF", "$50 Booking.com"

    -- Fulfillment
    claimed_at TIMESTAMPTZ DEFAULT NOW(),
    fulfilled_at TIMESTAMPTZ,
    fulfillment_notes TEXT,

    UNIQUE(subscriber_id, milestone)
);

-- =============================================================================
-- ROW LEVEL SECURITY
-- Service role has full access, anon can only subscribe
-- =============================================================================
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequence_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sends ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriber_sequence_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_rewards ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY "service_role_full_access_subscribers" ON subscribers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_templates" ON email_templates FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_sequences" ON email_sequences FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_steps" ON email_sequence_steps FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_sends" ON email_sends FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_progress" ON subscriber_sequence_progress FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access_rewards" ON referral_rewards FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Anon can insert new subscribers (signup flow)
CREATE POLICY "anon_can_subscribe" ON subscribers FOR INSERT TO anon WITH CHECK (true);

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Generate unique referral code for new subscribers
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.referral_code IS NULL THEN
        NEW.referral_code := LOWER(SUBSTRING(MD5(NEW.id::TEXT || NOW()::TEXT) FROM 1 FOR 8));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_referral_code
    BEFORE INSERT ON subscribers
    FOR EACH ROW
    EXECUTE FUNCTION generate_referral_code();

-- Increment referral count when someone signs up with a referral code
CREATE OR REPLACE FUNCTION increment_referral_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.referred_by IS NOT NULL THEN
        UPDATE subscribers
        SET referral_count = referral_count + 1,
            updated_at = NOW()
        WHERE id = NEW.referred_by;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_referral_signup
    AFTER INSERT ON subscribers
    FOR EACH ROW
    EXECUTE FUNCTION increment_referral_count();

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_subscribers_timestamp
    BEFORE UPDATE ON subscribers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_templates_timestamp
    BEFORE UPDATE ON email_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sequences_timestamp
    BEFORE UPDATE ON email_sequences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE subscribers IS 'Email subscribers - core list for newsletter and sequences';
COMMENT ON TABLE email_templates IS 'Reusable email templates with variable substitution';
COMMENT ON TABLE email_sequences IS 'Automated email flows triggered by events';
COMMENT ON TABLE email_sequence_steps IS 'Individual steps/emails within a sequence';
COMMENT ON TABLE email_sends IS 'Audit log of all emails sent via Resend';
COMMENT ON TABLE subscriber_sequence_progress IS 'Track subscriber progress through sequences';
COMMENT ON TABLE referral_rewards IS 'Morning Brew style referral reward tracking';
