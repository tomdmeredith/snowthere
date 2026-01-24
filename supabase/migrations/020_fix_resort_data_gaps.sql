-- Fix Resort Data Gaps (Round 5.9)
-- Addresses issues identified in Round 5.8 audit:
-- - St. Anton missing family metrics
-- - All 3 resorts missing cost data
-- - St. Anton trail map shows wrong data

-- ============================================
-- FIX 1: St. Anton Family Metrics
-- ============================================
-- Content analysis shows St. Anton is expert-oriented, best for older kids (8-16)
-- Family score 7/10 (good but not ideal for young families)

INSERT INTO resort_family_metrics (
    resort_id,
    family_overall_score,
    best_age_min,
    best_age_max,
    ski_school_min_age,
    has_childcare,
    childcare_min_age,
    has_magic_carpet,
    has_terrain_park_kids,
    kid_friendly_terrain_pct
)
SELECT
    id,
    7,      -- Family score (expert-oriented, challenging terrain)
    8,      -- Best age min (older kids handle the terrain better)
    16,     -- Best age max
    3,      -- Ski school accepts kids from age 3
    true,   -- Has childcare (Kinderland facilities)
    3,      -- Childcare from 3 years
    true,   -- Has magic carpet
    true,   -- Has kids terrain park
    35      -- ~35% beginner terrain (relatively low for family resort)
FROM resorts
WHERE slug = 'st-anton'
ON CONFLICT (resort_id) DO UPDATE SET
    family_overall_score = EXCLUDED.family_overall_score,
    best_age_min = EXCLUDED.best_age_min,
    best_age_max = EXCLUDED.best_age_max,
    ski_school_min_age = EXCLUDED.ski_school_min_age,
    has_childcare = EXCLUDED.has_childcare,
    childcare_min_age = EXCLUDED.childcare_min_age,
    has_magic_carpet = EXCLUDED.has_magic_carpet,
    has_terrain_park_kids = EXCLUDED.has_terrain_park_kids,
    kid_friendly_terrain_pct = EXCLUDED.kid_friendly_terrain_pct;

-- ============================================
-- FIX 2: Cost Data for All 3 Resorts
-- ============================================

-- Park City, Utah (USD) - Expensive US resort
INSERT INTO resort_costs (
    resort_id,
    currency,
    lift_adult_daily,
    lift_child_daily,
    lift_family_daily,
    lodging_budget_nightly,
    lodging_mid_nightly,
    lodging_luxury_nightly,
    meal_family_avg
)
SELECT
    id,
    'USD',
    225,    -- Adult lift ticket ($179-269 range, midpoint ~225)
    160,    -- Child lift ticket (~30% less than adult)
    610,    -- Family of 4 (2 adults + 2 kids)
    150,    -- Budget lodging
    300,    -- Mid-range lodging
    600,    -- Luxury lodging
    120     -- Family meal average
FROM resorts
WHERE slug = 'park-city'
ON CONFLICT (resort_id) DO UPDATE SET
    currency = EXCLUDED.currency,
    lift_adult_daily = EXCLUDED.lift_adult_daily,
    lift_child_daily = EXCLUDED.lift_child_daily,
    lift_family_daily = EXCLUDED.lift_family_daily,
    lodging_budget_nightly = EXCLUDED.lodging_budget_nightly,
    lodging_mid_nightly = EXCLUDED.lodging_mid_nightly,
    lodging_luxury_nightly = EXCLUDED.lodging_luxury_nightly,
    meal_family_avg = EXCLUDED.meal_family_avg;

-- St. Anton, Austria (EUR) - Premium European resort
INSERT INTO resort_costs (
    resort_id,
    currency,
    lift_adult_daily,
    lift_child_daily,
    lift_family_daily,
    lodging_budget_nightly,
    lodging_mid_nightly,
    lodging_luxury_nightly,
    meal_family_avg
)
SELECT
    id,
    'EUR',
    75,     -- Adult lift ticket (€72-79 range)
    45,     -- Child lift ticket (€43-47 range)
    195,    -- Family of 4 (2 adults + 2 kids, some discounts apply)
    125,    -- Budget lodging (pension/gasthof)
    200,    -- Mid-range lodging (3-star hotel)
    400,    -- Luxury lodging (4-5 star)
    80      -- Family meal average
FROM resorts
WHERE slug = 'st-anton'
ON CONFLICT (resort_id) DO UPDATE SET
    currency = EXCLUDED.currency,
    lift_adult_daily = EXCLUDED.lift_adult_daily,
    lift_child_daily = EXCLUDED.lift_child_daily,
    lift_family_daily = EXCLUDED.lift_family_daily,
    lodging_budget_nightly = EXCLUDED.lodging_budget_nightly,
    lodging_mid_nightly = EXCLUDED.lodging_mid_nightly,
    lodging_luxury_nightly = EXCLUDED.lodging_luxury_nightly,
    meal_family_avg = EXCLUDED.meal_family_avg;

-- Zermatt, Switzerland (CHF) - Premium Swiss resort
INSERT INTO resort_costs (
    resort_id,
    currency,
    lift_adult_daily,
    lift_child_daily,
    lift_family_daily,
    lodging_budget_nightly,
    lodging_mid_nightly,
    lodging_luxury_nightly,
    meal_family_avg
)
SELECT
    id,
    'CHF',
    95,     -- Adult lift ticket (CHF 89-99 range)
    0,      -- Child under 9 FREE with Wolli Card
    190,    -- Family of 4 (2 adults, kids free under 9)
    200,    -- Budget lodging (Zermatt is expensive)
    350,    -- Mid-range lodging
    700,    -- Luxury lodging
    150     -- Family meal average (Switzerland prices)
FROM resorts
WHERE slug = 'zermatt'
ON CONFLICT (resort_id) DO UPDATE SET
    currency = EXCLUDED.currency,
    lift_adult_daily = EXCLUDED.lift_adult_daily,
    lift_child_daily = EXCLUDED.lift_child_daily,
    lift_family_daily = EXCLUDED.lift_family_daily,
    lodging_budget_nightly = EXCLUDED.lodging_budget_nightly,
    lodging_mid_nightly = EXCLUDED.lodging_mid_nightly,
    lodging_luxury_nightly = EXCLUDED.lodging_luxury_nightly,
    meal_family_avg = EXCLUDED.meal_family_avg;

-- ============================================
-- FIX 3: St. Anton Trail Map Data
-- ============================================
-- Current data shows only 13 runs (wrong)
-- Ski Arlberg (full area) has 305km of pistes, ~300 runs, 88 lifts

UPDATE resorts
SET trail_map_data = '{
    "runs_total": 300,
    "lifts_total": 88,
    "skiable_terrain_km": 305,
    "runs_by_difficulty": {
        "easy": 105,
        "intermediate": 120,
        "advanced": 75
    },
    "vertical_drop_m": 1507,
    "summit_elevation_m": 2811,
    "base_elevation_m": 1304,
    "quality": "manual",
    "source": "ski-arlberg.at",
    "notes": "Full Ski Arlberg area including St. Anton, St. Christoph, Stuben, Lech, Zürs, Warth-Schröcken"
}'::jsonb
WHERE slug = 'st-anton';

-- ============================================
-- VERIFICATION QUERIES (run manually to verify)
-- ============================================
-- SELECT r.name, rfm.family_overall_score, rfm.best_age_min, rfm.best_age_max
-- FROM resorts r
-- LEFT JOIN resort_family_metrics rfm ON r.id = rfm.resort_id
-- WHERE r.slug IN ('park-city', 'st-anton', 'zermatt');

-- SELECT r.name, rc.currency, rc.lift_adult_daily, rc.lodging_mid_nightly
-- FROM resorts r
-- LEFT JOIN resort_costs rc ON r.id = rc.resort_id
-- WHERE r.slug IN ('park-city', 'st-anton', 'zermatt');

-- SELECT name, trail_map_data->'runs_total' as runs, trail_map_data->'lifts_total' as lifts
-- FROM resorts
-- WHERE slug = 'st-anton';
