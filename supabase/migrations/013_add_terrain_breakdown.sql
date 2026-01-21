-- Migration: Add Terrain Breakdown Fields
-- Created: 2026-01-21
-- Purpose: Store terrain difficulty percentages for the TerrainBreakdown visual component

-- Add terrain percentage columns to resort_family_metrics
ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS terrain_beginner_pct INTEGER CHECK (terrain_beginner_pct BETWEEN 0 AND 100),
ADD COLUMN IF NOT EXISTS terrain_intermediate_pct INTEGER CHECK (terrain_intermediate_pct BETWEEN 0 AND 100),
ADD COLUMN IF NOT EXISTS terrain_advanced_pct INTEGER CHECK (terrain_advanced_pct BETWEEN 0 AND 100);

-- Add constraint to ensure percentages sum to ~100 (with tolerance for rounding)
-- Note: Only enforced when all three values are set
ALTER TABLE resort_family_metrics
ADD CONSTRAINT terrain_pct_sum_check
CHECK (
    terrain_beginner_pct IS NULL OR
    terrain_intermediate_pct IS NULL OR
    terrain_advanced_pct IS NULL OR
    (terrain_beginner_pct + terrain_intermediate_pct + terrain_advanced_pct BETWEEN 95 AND 105)
);

COMMENT ON COLUMN resort_family_metrics.terrain_beginner_pct IS 'Percentage of terrain suitable for beginners (green runs)';
COMMENT ON COLUMN resort_family_metrics.terrain_intermediate_pct IS 'Percentage of terrain for intermediate skiers (blue runs)';
COMMENT ON COLUMN resort_family_metrics.terrain_advanced_pct IS 'Percentage of terrain for advanced/expert skiers (black runs)';
