-- Migration 043: Add hybrid scoring columns for three-layer score system
-- Part of Round 20: Content Quality & Linking Overhaul
--
-- New scoring model:
--   structural_score (30%) + content_score (50%) + review_score (20%)
-- If no reviews: structural (35%) + content (65%)

ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS structural_score DECIMAL(3,1),
ADD COLUMN IF NOT EXISTS content_score DECIMAL(3,1),
ADD COLUMN IF NOT EXISTS review_score DECIMAL(3,1),
ADD COLUMN IF NOT EXISTS score_confidence VARCHAR(10) DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS score_reasoning TEXT,
ADD COLUMN IF NOT EXISTS score_dimensions JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS scored_at TIMESTAMPTZ;
