-- Migration: Affiliate Configuration
-- Created: 2026-01-26
-- Purpose: Store affiliate program settings and URL templates
-- Part of Round 7: External Linking & Affiliate System

-- Affiliate program configuration
CREATE TABLE IF NOT EXISTS affiliate_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Program identification
    program_name TEXT NOT NULL UNIQUE,   -- 'booking.com', 'ski.com', 'liftopia'
    display_name TEXT NOT NULL,          -- 'Booking.com', 'Ski.com', 'Liftopia'

    -- URL configuration
    url_template TEXT,                   -- Template with {url}, {aid}, etc.
    affiliate_id TEXT,                   -- Our affiliate ID for this program
    tracking_param TEXT,                 -- 'aid', 'ref', etc.

    -- Domain matching
    domains TEXT[],                      -- ['booking.com', 'www.booking.com']

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    commission_rate TEXT,                -- '4-6%', '5%' for documentation

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Link click tracking for analytics
CREATE TABLE IF NOT EXISTS link_click_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Click context
    resort_id UUID REFERENCES resorts(id) ON DELETE SET NULL,
    link_url TEXT NOT NULL,
    link_category TEXT,                  -- 'lodging', 'dining', etc.

    -- Affiliate tracking
    is_affiliate BOOLEAN DEFAULT FALSE,
    affiliate_program TEXT,              -- Which program

    -- Session data
    session_id TEXT,                     -- For deduplication
    referrer TEXT,                       -- Where they came from
    user_agent TEXT,

    -- Timestamp
    clicked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_link_click_log_resort
ON link_click_log(resort_id, clicked_at);

CREATE INDEX IF NOT EXISTS idx_link_click_log_affiliate
ON link_click_log(affiliate_program, clicked_at)
WHERE is_affiliate = TRUE;

CREATE INDEX IF NOT EXISTS idx_link_click_log_time
ON link_click_log(clicked_at);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_affiliate_config_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER affiliate_config_updated_at
    BEFORE UPDATE ON affiliate_config
    FOR EACH ROW
    EXECUTE FUNCTION update_affiliate_config_updated_at();

-- RLS Policies
ALTER TABLE affiliate_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE link_click_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access for affiliate_config"
ON affiliate_config FOR SELECT
USING (true);

CREATE POLICY "Service role all for affiliate_config"
ON affiliate_config FOR ALL
USING (true);

CREATE POLICY "Service role insert for link_click_log"
ON link_click_log FOR INSERT
WITH CHECK (true);

CREATE POLICY "Service role select for link_click_log"
ON link_click_log FOR SELECT
USING (true);

COMMENT ON TABLE affiliate_config IS 'Affiliate program settings and URL templates';
COMMENT ON TABLE link_click_log IS 'Track outbound link clicks for analytics';

-- Seed initial affiliate configurations (placeholders - update with real IDs)
INSERT INTO affiliate_config (program_name, display_name, url_template, domains, commission_rate, notes)
VALUES
    ('booking.com', 'Booking.com', 'https://www.booking.com/hotel/{slug}.html?aid={aid}', ARRAY['booking.com', 'www.booking.com'], '4-6%', 'Apply at booking.com/affiliate'),
    ('ski.com', 'Ski.com', 'https://www.ski.com/{path}?ref={aid}', ARRAY['ski.com', 'www.ski.com'], '5-8%', 'Gear rentals and packages'),
    ('liftopia', 'Liftopia', 'https://www.liftopia.com/{path}?partner={aid}', ARRAY['liftopia.com', 'www.liftopia.com'], '3-5%', 'Lift ticket deals')
ON CONFLICT (program_name) DO NOTHING;
