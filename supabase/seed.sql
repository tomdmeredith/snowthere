-- Seed data for Family Ski Directory
-- Initial ski passes and sample resorts for testing

-- ============================================
-- SKI PASSES
-- ============================================

INSERT INTO ski_passes (name, type, website_url, purchase_url) VALUES
-- Mega Passes (US-based, global reach)
('Epic Pass', 'mega', 'https://www.epicpass.com/', 'https://www.epicpass.com/passes'),
('Epic Local Pass', 'mega', 'https://www.epicpass.com/', 'https://www.epicpass.com/passes/epic-local-pass'),
('Ikon Pass', 'mega', 'https://www.ikonpass.com/', 'https://www.ikonpass.com/en/shop-passes'),
('Ikon Base Pass', 'mega', 'https://www.ikonpass.com/', 'https://www.ikonpass.com/en/shop-passes'),
('Mountain Collective', 'mega', 'https://mountaincollective.com/', 'https://mountaincollective.com/'),
('Indy Pass', 'regional', 'https://www.indyskipass.com/', 'https://www.indyskipass.com/'),

-- European Superpasses
('SkiWelt Wilder Kaiser-Brixental', 'regional', 'https://www.skiwelt.at/', 'https://www.skiwelt.at/en/prices-packages'),
('Ski Arlberg', 'regional', 'https://www.skiarlberg.at/', 'https://www.skiarlberg.at/en/ski-passes'),
('Dolomiti Superski', 'regional', 'https://www.dolomitisuperski.com/', 'https://www.dolomitisuperski.com/en/ski-pass'),
('Portes du Soleil', 'regional', 'https://www.portesdusoleil.com/', 'https://www.portesdusoleil.com/skipass'),
('Les 3 Vallees', 'regional', 'https://www.les3vallees.com/', 'https://www.les3vallees.com/en/ski-pass'),
('Paradiski', 'regional', 'https://www.paradiski.com/', 'https://www.paradiski.com/en/skipass'),
('4 Vallees', 'regional', 'https://www.4vallees.ch/', 'https://www.4vallees.ch/en/skipass'),
('Zermatt-Cervinia', 'regional', 'https://www.zermatt.ch/', 'https://www.zermatt.ch/en/tickets-prices'),

-- US Regional Passes
('Ski Utah Interconnect', 'regional', 'https://www.skiutah.com/', 'https://www.skiutah.com/'),
('Colorado Gems Card', 'regional', NULL, NULL),
('New England Pass', 'regional', 'https://www.newenglandpass.com/', 'https://www.newenglandpass.com/'),

-- Canada
('Ski Big 3', 'regional', 'https://www.skibig3.com/', 'https://www.skibig3.com/lift-tickets/'),

-- Japan
('Japan Ski Pass', 'regional', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- SAMPLE RESORTS (for testing)
-- ============================================

-- Park City, Utah (US)
INSERT INTO resorts (slug, name, country, region, latitude, longitude, status)
VALUES ('park-city', 'Park City Mountain', 'United States', 'Utah', 40.6461, -111.4980, 'published');

-- St. Anton, Austria (Europe)
INSERT INTO resorts (slug, name, country, region, latitude, longitude, status)
VALUES ('st-anton', 'St. Anton am Arlberg', 'Austria', 'Tyrol', 47.1297, 10.2685, 'published');

-- Zermatt, Switzerland (Europe)
INSERT INTO resorts (slug, name, country, region, latitude, longitude, status)
VALUES ('zermatt', 'Zermatt', 'Switzerland', 'Valais', 46.0207, 7.7491, 'published');

-- Get resort IDs for the sample data
DO $$
DECLARE
    park_city_id UUID;
    st_anton_id UUID;
    zermatt_id UUID;
    epic_pass_id UUID;
    ikon_pass_id UUID;
    ski_arlberg_id UUID;
    zermatt_pass_id UUID;
BEGIN
    SELECT id INTO park_city_id FROM resorts WHERE slug = 'park-city';
    SELECT id INTO st_anton_id FROM resorts WHERE slug = 'st-anton';
    SELECT id INTO zermatt_id FROM resorts WHERE slug = 'zermatt';
    SELECT id INTO epic_pass_id FROM ski_passes WHERE name = 'Epic Pass';
    SELECT id INTO ikon_pass_id FROM ski_passes WHERE name = 'Ikon Pass';
    SELECT id INTO ski_arlberg_id FROM ski_passes WHERE name = 'Ski Arlberg';
    SELECT id INTO zermatt_pass_id FROM ski_passes WHERE name = 'Zermatt-Cervinia';

    -- Park City Family Metrics
    INSERT INTO resort_family_metrics (
        resort_id, family_overall_score, best_age_min, best_age_max,
        kid_friendly_terrain_pct, has_childcare, childcare_min_age,
        ski_school_min_age, kids_ski_free_age, has_magic_carpet,
        has_terrain_park_kids, perfect_if, skip_if
    ) VALUES (
        park_city_id, 8, 4, 14, 35, true, 18, 3, 5, true, true,
        ARRAY['You want variety - 7,300 acres of terrain', 'Kids need ski school options', 'You want easy access from Salt Lake City airport'],
        ARRAY['You''re on a tight budget - it''s pricey', 'You want a quaint village vibe - it''s a proper town']
    );

    -- St. Anton Family Metrics
    INSERT INTO resort_family_metrics (
        resort_id, family_overall_score, best_age_min, best_age_max,
        kid_friendly_terrain_pct, has_childcare, childcare_min_age,
        ski_school_min_age, kids_ski_free_age, has_magic_carpet,
        has_terrain_park_kids, perfect_if, skip_if
    ) VALUES (
        st_anton_id, 7, 6, 16, 25, true, 24, 4, 6, true, false,
        ARRAY['Your kids are confident skiers already', 'You want legendary Austrian apres-ski', 'You appreciate challenging terrain'],
        ARRAY['You have complete beginners - it''s steep', 'You want budget-friendly - it''s premium pricing', 'You need lots of green runs']
    );

    -- Zermatt Family Metrics
    INSERT INTO resort_family_metrics (
        resort_id, family_overall_score, best_age_min, best_age_max,
        kid_friendly_terrain_pct, has_childcare, childcare_min_age,
        ski_school_min_age, kids_ski_free_age, has_magic_carpet,
        has_terrain_park_kids, perfect_if, skip_if
    ) VALUES (
        zermatt_id, 8, 5, 16, 30, true, 30, 3, 6, true, true,
        ARRAY['You want iconic Matterhorn views', 'You value a car-free village', 'You want to ski into Italy for lunch'],
        ARRAY['You''re budget-conscious - it''s expensive', 'You hate long lift rides - the vertical is huge', 'You want quick access from airport']
    );

    -- Park City Costs
    INSERT INTO resort_costs (
        resort_id, currency, lift_adult_daily, lift_child_daily,
        lodging_budget_nightly, lodging_mid_nightly, lodging_luxury_nightly,
        meal_family_avg, estimated_family_daily
    ) VALUES (
        park_city_id, 'USD', 239, 149, 150, 350, 800, 120, 950
    );

    -- St. Anton Costs
    INSERT INTO resort_costs (
        resort_id, currency, lift_adult_daily, lift_child_daily,
        lodging_budget_nightly, lodging_mid_nightly, lodging_luxury_nightly,
        meal_family_avg, estimated_family_daily
    ) VALUES (
        st_anton_id, 'EUR', 72, 36, 100, 250, 600, 80, 450
    );

    -- Zermatt Costs
    INSERT INTO resort_costs (
        resort_id, currency, lift_adult_daily, lift_child_daily,
        lodging_budget_nightly, lodging_mid_nightly, lodging_luxury_nightly,
        meal_family_avg, estimated_family_daily
    ) VALUES (
        zermatt_id, 'CHF', 92, 46, 150, 400, 1200, 100, 700
    );

    -- Link passes to resorts
    INSERT INTO resort_passes (resort_id, pass_id, access_type) VALUES
        (park_city_id, epic_pass_id, 'full'),
        (st_anton_id, ski_arlberg_id, 'full'),
        (st_anton_id, ikon_pass_id, 'limited'),
        (zermatt_id, zermatt_pass_id, 'full');

    -- Park City Calendar
    INSERT INTO ski_quality_calendar (resort_id, month, snow_quality_score, crowd_level, family_recommendation, notes) VALUES
        (park_city_id, 12, 3, 'high', 6, 'Holiday crowds, early season snow'),
        (park_city_id, 1, 5, 'medium', 9, 'Best powder month, post-holiday lull'),
        (park_city_id, 2, 4, 'high', 7, 'Presidents Week busy, great snow'),
        (park_city_id, 3, 4, 'medium', 9, 'Spring skiing begins, fewer crowds'),
        (park_city_id, 4, 3, 'low', 8, 'Warm weather, deal season');

    -- St. Anton Calendar
    INSERT INTO ski_quality_calendar (resort_id, month, snow_quality_score, crowd_level, family_recommendation, notes) VALUES
        (st_anton_id, 12, 3, 'high', 5, 'Christmas rush, variable early snow'),
        (st_anton_id, 1, 5, 'medium', 8, 'Peak powder, quieter after New Year'),
        (st_anton_id, 2, 4, 'high', 6, 'UK half-term crowds'),
        (st_anton_id, 3, 4, 'medium', 8, 'Great spring conditions'),
        (st_anton_id, 4, 3, 'low', 7, 'Late season deals');

    -- Zermatt Calendar
    INSERT INTO ski_quality_calendar (resort_id, month, snow_quality_score, crowd_level, family_recommendation, notes) VALUES
        (zermatt_id, 12, 4, 'high', 6, 'Glacier skiing reliable, holiday premium'),
        (zermatt_id, 1, 5, 'medium', 9, 'Best conditions, post-holiday value'),
        (zermatt_id, 2, 5, 'medium', 8, 'Excellent snow, Swiss school holidays'),
        (zermatt_id, 3, 4, 'low', 9, 'Spring sun, empty slopes'),
        (zermatt_id, 4, 4, 'low', 8, 'Late season, still great glacier skiing');

END $$;
