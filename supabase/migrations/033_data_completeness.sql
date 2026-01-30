-- Migration 033: Add data_completeness column to resort_family_metrics
-- Part of Data Quality & Scoring Overhaul
--
-- This column stores the fraction (0.0-1.0) of key family metric fields
-- that are populated for each resort. The frontend uses this to decide
-- whether to show the Family Metrics and Cost tables.

ALTER TABLE resort_family_metrics
ADD COLUMN IF NOT EXISTS data_completeness DECIMAL(3,2) DEFAULT 0.0;

-- Add a comment explaining the column
COMMENT ON COLUMN resort_family_metrics.data_completeness IS
  'Fraction of key family metrics fields populated (0.0-1.0). Used by frontend to conditionally show/hide tables. Calculated by scoring.calculate_data_completeness().';
