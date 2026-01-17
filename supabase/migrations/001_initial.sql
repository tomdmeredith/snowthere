-- Family Ski Directory Database Schema
-- Initial migration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CORE TABLES
-- ============================================

-- Resorts: Core resort information
CREATE TABLE resorts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_refreshed TIMESTAMP WITH TIME ZONE
);

-- Index for common queries
CREATE INDEX idx_resorts_status ON resorts(status);
CREATE INDEX idx_resorts_country ON resorts(country);
CREATE INDEX idx_resorts_country_slug ON resorts(country, slug);

-- ============================================
-- FAMILY METRICS
-- ============================================

-- Resort family metrics: Kid-specific data
CREATE TABLE resort_family_metrics (
    resort_id UUID PRIMARY KEY REFERENCES resorts(id) ON DELETE CASCADE,
    family_overall_score INTEGER CHECK (family_overall_score BETWEEN 1 AND 10),
    best_age_min INTEGER,
    best_age_max INTEGER,
    kid_friendly_terrain_pct INTEGER CHECK (kid_friendly_terrain_pct BETWEEN 0 AND 100),
    has_childcare BOOLEAN,
    childcare_min_age INTEGER, -- in months
    ski_school_min_age INTEGER, -- in years
    kids_ski_free_age INTEGER,
    has_magic_carpet BOOLEAN,
    has_terrain_park_kids BOOLEAN,
    perfect_if TEXT[],
    skip_if TEXT[]
);

-- ============================================
-- CONTENT
-- ============================================

-- Resort content: All written content for the resort page
CREATE TABLE resort_content (
    resort_id UUID PRIMARY KEY REFERENCES resorts(id) ON DELETE CASCADE,
    quick_take TEXT,
    getting_there TEXT,
    where_to_stay TEXT,
    lift_tickets TEXT,
    on_mountain TEXT,
    off_mountain TEXT,
    parent_reviews_summary TEXT,
    faqs JSONB DEFAULT '[]'::JSONB,
    llms_txt TEXT,
    seo_meta JSONB DEFAULT '{}'::JSONB,
    content_version INTEGER DEFAULT 1
);

-- ============================================
-- COSTS
-- ============================================

-- Resort costs: Pricing information
CREATE TABLE resort_costs (
    resort_id UUID PRIMARY KEY REFERENCES resorts(id) ON DELETE CASCADE,
    currency VARCHAR(3) DEFAULT 'USD',
    lift_adult_daily DECIMAL(10,2),
    lift_child_daily DECIMAL(10,2),
    lift_family_daily DECIMAL(10,2),
    lodging_budget_nightly DECIMAL(10,2),
    lodging_mid_nightly DECIMAL(10,2),
    lodging_luxury_nightly DECIMAL(10,2),
    meal_family_avg DECIMAL(10,2),
    estimated_family_daily DECIMAL(10,2)
);

-- ============================================
-- CALENDAR
-- ============================================

-- Ski quality calendar: Monthly conditions and recommendations
CREATE TABLE ski_quality_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    snow_quality_score INTEGER CHECK (snow_quality_score BETWEEN 1 AND 5),
    crowd_level VARCHAR(20) CHECK (crowd_level IN ('low', 'medium', 'high')),
    family_recommendation INTEGER CHECK (family_recommendation BETWEEN 1 AND 10),
    notes TEXT,
    UNIQUE(resort_id, month)
);

CREATE INDEX idx_calendar_resort ON ski_quality_calendar(resort_id);

-- ============================================
-- SKI PASSES
-- ============================================

-- Ski passes: Epic, Ikon, regional passes, etc.
CREATE TABLE ski_passes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50), -- mega, regional, single
    website_url TEXT,
    purchase_url TEXT
);

-- Many-to-many: Which passes work at which resorts
CREATE TABLE resort_passes (
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,
    pass_id UUID NOT NULL REFERENCES ski_passes(id) ON DELETE CASCADE,
    access_type VARCHAR(50), -- full, limited, blackout
    PRIMARY KEY (resort_id, pass_id)
);

CREATE INDEX idx_resort_passes_resort ON resort_passes(resort_id);
CREATE INDEX idx_resort_passes_pass ON resort_passes(pass_id);

-- ============================================
-- CONTENT QUEUE (Agent Pipeline)
-- ============================================

-- Content queue: Task queue for agent pipeline
CREATE TABLE content_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resort_id UUID REFERENCES resorts(id) ON DELETE SET NULL,
    task_type VARCHAR(50) NOT NULL, -- discover, research, generate, geo_optimize, validate, publish
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    priority INTEGER DEFAULT 5,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_queue_status ON content_queue(status);
CREATE INDEX idx_queue_priority ON content_queue(priority DESC, created_at ASC);

-- ============================================
-- AUDIT LOG (Agent Observability)
-- ============================================

-- Agent audit log: Track reasoning and decisions
CREATE TABLE agent_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES content_queue(id) ON DELETE SET NULL,
    resort_id UUID REFERENCES resorts(id) ON DELETE SET NULL,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    reasoning TEXT,
    input_data JSONB,
    output_data JSONB,
    api_costs JSONB, -- Track API usage per action
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_task ON agent_audit_log(task_id);
CREATE INDEX idx_audit_resort ON agent_audit_log(resort_id);
CREATE INDEX idx_audit_created ON agent_audit_log(created_at DESC);

-- ============================================
-- NEWSLETTER SUBSCRIBERS
-- ============================================

CREATE TABLE newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(100), -- Which page they signed up from
    confirmed BOOLEAN DEFAULT FALSE,
    unsubscribed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscribers_email ON newsletter_subscribers(email);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_resorts_updated_at
    BEFORE UPDATE ON resorts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS
ALTER TABLE resorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE resort_family_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE resort_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE resort_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ski_quality_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE ski_passes ENABLE ROW LEVEL SECURITY;
ALTER TABLE resort_passes ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Public read access for published resorts
CREATE POLICY "Public can read published resorts"
    ON resorts FOR SELECT
    USING (status = 'published');

CREATE POLICY "Public can read resort metrics"
    ON resort_family_metrics FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts WHERE resorts.id = resort_family_metrics.resort_id AND resorts.status = 'published'
    ));

CREATE POLICY "Public can read resort content"
    ON resort_content FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts WHERE resorts.id = resort_content.resort_id AND resorts.status = 'published'
    ));

CREATE POLICY "Public can read resort costs"
    ON resort_costs FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts WHERE resorts.id = resort_costs.resort_id AND resorts.status = 'published'
    ));

CREATE POLICY "Public can read calendar"
    ON ski_quality_calendar FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts WHERE resorts.id = ski_quality_calendar.resort_id AND resorts.status = 'published'
    ));

CREATE POLICY "Public can read ski passes"
    ON ski_passes FOR SELECT
    USING (true);

CREATE POLICY "Public can read resort passes"
    ON resort_passes FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM resorts WHERE resorts.id = resort_passes.resort_id AND resorts.status = 'published'
    ));

-- Newsletter: Public can insert (sign up)
CREATE POLICY "Public can subscribe to newsletter"
    ON newsletter_subscribers FOR INSERT
    WITH CHECK (true);

-- Service role has full access (for agents)
-- Note: Service role bypasses RLS by default
