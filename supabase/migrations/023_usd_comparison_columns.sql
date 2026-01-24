-- Add USD comparison columns to resort_costs
-- Round 5.9.2: Enable cross-resort price comparison in normalized currency

ALTER TABLE resort_costs ADD COLUMN IF NOT EXISTS lift_adult_daily_usd DECIMAL(10,2);
ALTER TABLE resort_costs ADD COLUMN IF NOT EXISTS lodging_mid_nightly_usd DECIMAL(10,2);

-- Index for sorting by USD price (useful for "cheapest resorts" queries)
CREATE INDEX IF NOT EXISTS idx_resort_costs_lift_usd ON resort_costs(lift_adult_daily_usd)
WHERE lift_adult_daily_usd IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_resort_costs_lodging_usd ON resort_costs(lodging_mid_nightly_usd)
WHERE lodging_mid_nightly_usd IS NOT NULL;

COMMENT ON COLUMN resort_costs.lift_adult_daily_usd IS 'Adult lift ticket in USD for cross-resort comparison';
COMMENT ON COLUMN resort_costs.lodging_mid_nightly_usd IS 'Mid-range lodging in USD for cross-resort comparison';
