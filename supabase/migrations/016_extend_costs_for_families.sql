-- =============================================================================
-- MIGRATION 016: Extend costs for family-critical data
-- =============================================================================
--
-- Purpose: Add columns that families actually need to budget ski trips
-- - Ski school costs (often the LARGEST line item for families)
-- - Rental costs (most families rent gear)
-- - Under-6 lift pricing (often free - huge decision driver)
--
-- Context: The extraction layer correctly identified these as essential for
-- the "Instagram mom" target audience. The database schema was incomplete.
-- See audit from 2026-01-23.
--
-- Rollback: ALTER TABLE resort_costs DROP COLUMN IF EXISTS ...
-- =============================================================================

-- Add lesson costs (ski school - most families book these)
ALTER TABLE resort_costs
ADD COLUMN IF NOT EXISTS lesson_group_child DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS lesson_private_hour DECIMAL(10,2);

COMMENT ON COLUMN resort_costs.lesson_group_child IS 'Child group ski lesson price (per day)';
COMMENT ON COLUMN resort_costs.lesson_private_hour IS 'Private ski lesson price (per hour)';

-- Add rental costs (most families rent gear)
ALTER TABLE resort_costs
ADD COLUMN IF NOT EXISTS rental_adult_daily DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS rental_child_daily DECIMAL(10,2);

COMMENT ON COLUMN resort_costs.rental_adult_daily IS 'Adult ski/boot rental (per day)';
COMMENT ON COLUMN resort_costs.rental_child_daily IS 'Child ski/boot rental (per day)';

-- Add under-6 lift pricing (often free - huge decision factor)
ALTER TABLE resort_costs
ADD COLUMN IF NOT EXISTS lift_under6 DECIMAL(10,2) DEFAULT 0;

COMMENT ON COLUMN resort_costs.lift_under6 IS 'Lift ticket for under 6 (0 means free)';

-- =============================================================================
-- VERIFY: Check column additions
-- =============================================================================
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'resort_costs'
-- ORDER BY ordinal_position;
