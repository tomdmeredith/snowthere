-- Migration: 009_quiz_metrics.sql
-- Purpose: Add columns needed for quiz scoring algorithm
-- Date: 2026-01-20

-- =============================================================================
-- PART 1: ADD QUIZ SCORING COLUMNS TO RESORT_FAMILY_METRICS
-- =============================================================================

-- Rename family_overall_score to family_score for consistency with quiz code
-- (Keep both for backwards compatibility during transition)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS family_score INTEGER CHECK (family_score BETWEEN 1 AND 10);

-- Update family_score from family_overall_score where null
UPDATE resort_family_metrics
SET family_score = family_overall_score
WHERE family_score IS NULL AND family_overall_score IS NOT NULL;

-- Ski school indicator (boolean - separate from min age)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS has_ski_school BOOLEAN DEFAULT true;

-- Update has_ski_school based on ski_school_min_age (if they have min age, they have school)
UPDATE resort_family_metrics
SET has_ski_school = (ski_school_min_age IS NOT NULL)
WHERE has_ski_school IS NULL;

-- Childcare available (already exists as has_childcare, add alias column)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS childcare_available BOOLEAN;

UPDATE resort_family_metrics
SET childcare_available = has_childcare
WHERE childcare_available IS NULL;

-- Terrain breakdown (more granular than kid_friendly_terrain_pct)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS beginner_terrain_pct INTEGER CHECK (beginner_terrain_pct BETWEEN 0 AND 100);

ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS intermediate_terrain_pct INTEGER CHECK (intermediate_terrain_pct BETWEEN 0 AND 100);

ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS advanced_terrain_pct INTEGER CHECK (advanced_terrain_pct BETWEEN 0 AND 100);

-- Default terrain distribution if not set
UPDATE resort_family_metrics
SET beginner_terrain_pct = COALESCE(kid_friendly_terrain_pct, 25)
WHERE beginner_terrain_pct IS NULL;

UPDATE resort_family_metrics
SET intermediate_terrain_pct = 50
WHERE intermediate_terrain_pct IS NULL;

UPDATE resort_family_metrics
SET advanced_terrain_pct = 100 - COALESCE(beginner_terrain_pct, 25) - COALESCE(intermediate_terrain_pct, 50)
WHERE advanced_terrain_pct IS NULL;

-- =============================================================================
-- PART 2: ADD QUIZ-SPECIFIC SCORES TO RESORT_FAMILY_METRICS
-- =============================================================================

-- Ski-in/ski-out availability
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS has_ski_in_out BOOLEAN DEFAULT false;

-- Nightlife/apres scene score (1-10)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS nightlife_score INTEGER CHECK (nightlife_score BETWEEN 1 AND 10);

-- Non-ski activities count/score (1-10)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS non_ski_activities INTEGER CHECK (non_ski_activities BETWEEN 1 AND 10);

-- English-friendly indicator (for European resorts)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS english_friendly BOOLEAN DEFAULT true;

-- Snow reliability score (1-10)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS snow_reliability INTEGER CHECK (snow_reliability BETWEEN 1 AND 10);

-- Village charm score (1-10)
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS village_charm INTEGER CHECK (village_charm BETWEEN 1 AND 10);

-- =============================================================================
-- PART 3: ADD PRICE LEVEL TO RESORT_COSTS
-- =============================================================================

-- Price level tier (for quick matching - $, $$, $$$, $$$$)
ALTER TABLE resort_costs
ADD COLUMN IF NOT EXISTS price_level VARCHAR(10) DEFAULT '$$';

-- Calculate price_level from existing cost data
UPDATE resort_costs
SET price_level = CASE
    WHEN lodging_mid_nightly < 150 THEN '$'
    WHEN lodging_mid_nightly < 300 THEN '$$'
    WHEN lodging_mid_nightly < 500 THEN '$$$'
    ELSE '$$$$'
END
WHERE price_level IS NULL OR price_level = '$$';

-- =============================================================================
-- PART 4: CREATE QUIZ RESULTS TABLE (OPTIONAL PERSISTENCE)
-- =============================================================================

-- Store quiz results for analytics (optional)
CREATE TABLE IF NOT EXISTS quiz_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100), -- Anonymous session tracking
    personality_type VARCHAR(50) NOT NULL,
    answers JSONB NOT NULL,
    top_match_resort_id UUID REFERENCES resorts(id) ON DELETE SET NULL,
    match_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for analytics queries
CREATE INDEX IF NOT EXISTS idx_quiz_results_personality ON quiz_results(personality_type);
CREATE INDEX IF NOT EXISTS idx_quiz_results_created ON quiz_results(created_at DESC);

-- RLS for quiz_results (service can write, no public read for privacy)
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service can manage quiz results"
    ON quiz_results FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- PART 5: SET DEFAULTS FOR EXISTING RESORTS
-- =============================================================================

-- Set reasonable defaults for quiz metrics on existing resorts
UPDATE resort_family_metrics
SET
    nightlife_score = COALESCE(nightlife_score, 5),
    non_ski_activities = COALESCE(non_ski_activities, 5),
    snow_reliability = COALESCE(snow_reliability, 7),
    village_charm = COALESCE(village_charm, 6)
WHERE nightlife_score IS NULL
   OR non_ski_activities IS NULL
   OR snow_reliability IS NULL
   OR village_charm IS NULL;

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- After running, verify columns exist:
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name = 'resort_family_metrics';
