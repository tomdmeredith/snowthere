-- Migration: Decimal scores for better differentiation
-- Range: 1.0 - 10.0 (90 discrete values vs 10)
-- Purpose: Enable scoring differentiation (7.2 vs 7.8) instead of clustered integers

-- ============================================
-- STEP 1: Drop existing CHECK constraints
-- ============================================

ALTER TABLE resort_family_metrics
DROP CONSTRAINT IF EXISTS resort_family_metrics_family_overall_score_check;

ALTER TABLE resort_family_metrics
DROP CONSTRAINT IF EXISTS resort_family_metrics_nightlife_score_check;

ALTER TABLE resort_family_metrics
DROP CONSTRAINT IF EXISTS resort_family_metrics_non_ski_activities_check;

ALTER TABLE resort_family_metrics
DROP CONSTRAINT IF EXISTS resort_family_metrics_snow_reliability_check;

ALTER TABLE resort_family_metrics
DROP CONSTRAINT IF EXISTS resort_family_metrics_village_charm_check;

-- ============================================
-- STEP 2: Convert INTEGER columns to DECIMAL(3,1)
-- ============================================
-- Existing values like 8 become 8.0 automatically

ALTER TABLE resort_family_metrics
ALTER COLUMN family_overall_score TYPE DECIMAL(3,1)
USING family_overall_score::DECIMAL(3,1);

ALTER TABLE resort_family_metrics
ALTER COLUMN nightlife_score TYPE DECIMAL(3,1)
USING nightlife_score::DECIMAL(3,1);

ALTER TABLE resort_family_metrics
ALTER COLUMN non_ski_activities TYPE DECIMAL(3,1)
USING non_ski_activities::DECIMAL(3,1);

ALTER TABLE resort_family_metrics
ALTER COLUMN snow_reliability TYPE DECIMAL(3,1)
USING snow_reliability::DECIMAL(3,1);

ALTER TABLE resort_family_metrics
ALTER COLUMN village_charm TYPE DECIMAL(3,1)
USING village_charm::DECIMAL(3,1);

-- ============================================
-- STEP 3: Add new CHECK constraints for decimal range
-- ============================================

ALTER TABLE resort_family_metrics
ADD CONSTRAINT resort_family_metrics_family_overall_score_check
CHECK (family_overall_score >= 1.0 AND family_overall_score <= 10.0);

ALTER TABLE resort_family_metrics
ADD CONSTRAINT resort_family_metrics_nightlife_score_check
CHECK (nightlife_score >= 1.0 AND nightlife_score <= 10.0);

ALTER TABLE resort_family_metrics
ADD CONSTRAINT resort_family_metrics_non_ski_activities_check
CHECK (non_ski_activities >= 1.0 AND non_ski_activities <= 10.0);

ALTER TABLE resort_family_metrics
ADD CONSTRAINT resort_family_metrics_snow_reliability_check
CHECK (snow_reliability >= 1.0 AND snow_reliability <= 10.0);

ALTER TABLE resort_family_metrics
ADD CONSTRAINT resort_family_metrics_village_charm_check
CHECK (village_charm >= 1.0 AND village_charm <= 10.0);

-- ============================================
-- STEP 4: Create index for efficient sorting at scale
-- ============================================

CREATE INDEX IF NOT EXISTS idx_family_metrics_score
ON resort_family_metrics(family_overall_score DESC);

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON COLUMN resort_family_metrics.family_overall_score IS
'Family friendliness score (1.0-10.0). Deterministically calculated from childcare, ski school, terrain, value, and convenience factors.';

COMMENT ON COLUMN resort_family_metrics.nightlife_score IS
'Nightlife/apres-ski score (1.0-10.0). Used for party-seeker profile matching.';

COMMENT ON COLUMN resort_family_metrics.non_ski_activities IS
'Non-skiing activities score (1.0-10.0). Includes village activities, spas, shopping, etc.';

COMMENT ON COLUMN resort_family_metrics.snow_reliability IS
'Snow reliability score (1.0-10.0). Based on elevation, snowfall, snowmaking.';

COMMENT ON COLUMN resort_family_metrics.village_charm IS
'Village charm/atmosphere score (1.0-10.0). Based on pedestrian areas, architecture, ambiance.';
