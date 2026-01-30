-- Migration: Comprehensive Affiliate Program Database
-- Created: 2026-01-27
-- Purpose: Add all researched affiliate programs from Round 7.2
-- Reference: PLAN.md - Comprehensive Affiliate Program Research

-- Add new columns for better organization
ALTER TABLE affiliate_config ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE affiliate_config ADD COLUMN IF NOT EXISTS network TEXT;
ALTER TABLE affiliate_config ADD COLUMN IF NOT EXISTS cookie_duration TEXT;
ALTER TABLE affiliate_config ADD COLUMN IF NOT EXISTS priority_tier INTEGER DEFAULT 3;
ALTER TABLE affiliate_config ADD COLUMN IF NOT EXISTS signup_url TEXT;

-- Add comments for new columns
COMMENT ON COLUMN affiliate_config.category IS 'Program category: accommodation, tour_operator, lift_tickets, rentals, flights, car_rental, gear, insurance, activities, baby_gear, camera';
COMMENT ON COLUMN affiliate_config.network IS 'Affiliate network: travelpayouts, awin, impact, avantlink, cj, direct, flexoffers, admitad, tradetracker, shareasale';
COMMENT ON COLUMN affiliate_config.cookie_duration IS 'Cookie duration: 7d, 30d, 90d, 365d, session';
COMMENT ON COLUMN affiliate_config.priority_tier IS 'Priority: 1=Must Have, 2=High Value, 3=Supplementary';
COMMENT ON COLUMN affiliate_config.signup_url IS 'URL to apply for this affiliate program';

-- Update existing programs with new fields
-- Note: Booking.com uses tracking_param approach (adds ?aid=XXX to any booking.com URL)
UPDATE affiliate_config SET
    category = 'accommodation',
    network = 'travelpayouts',
    cookie_duration = 'session',
    priority_tier = 1,
    signup_url = 'https://www.travelpayouts.com/en/programs/booking',
    url_template = NULL,  -- Use tracking_param approach instead
    tracking_param = 'aid'
WHERE program_name = 'booking.com';

UPDATE affiliate_config SET
    category = 'tour_operator',
    network = 'direct',
    cookie_duration = '30d',
    priority_tier = 2,
    signup_url = 'https://www.ski.com/affiliate'
WHERE program_name = 'ski.com';

UPDATE affiliate_config SET
    category = 'lift_tickets',
    network = 'direct',
    cookie_duration = '30d',
    priority_tier = 2,
    signup_url = 'https://www.liftopia.com/affiliate'
WHERE program_name = 'liftopia';

-- =====================================================
-- TIER 1: MUST HAVE (Priority 1)
-- =====================================================

-- Discover Cars - Exceptional 23-54% commission, 365-day cookie!
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'discover_cars', 'Discover Cars',
    'https://www.discovercars.com/{path}?a_aid={aid}',
    ARRAY['discovercars.com', 'www.discovercars.com'],
    '23-54%',
    'car_rental', 'travelpayouts', '365d', 1,
    'https://www.travelpayouts.com/en/programs/discover-cars',
    'BEST car rental program - exceptional commission and cookie. Via Travelpayouts.'
) ON CONFLICT (program_name) DO NOTHING;

-- Alps2Alps - Perfect for ski resort transfers
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'alps2alps', 'Alps2Alps',
    'https://www.alps2alps.com/{path}?ref={aid}',
    ARRAY['alps2alps.com', 'www.alps2alps.com'],
    '€24 flat',
    'transport', 'admitad', '30d', 1,
    'https://www.admitad.com/en/webmaster/offers/alps2alps/',
    'Low-cost Alps transfers, 400+ destinations. Perfect for ski trips!'
) ON CONFLICT (program_name) DO NOTHING;

-- Sunweb - World Best Ski Tour Operator (9x winner)
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'sunweb', 'Sunweb',
    'https://www.sunweb.co.uk/{path}?partnerid={aid}',
    ARRAY['sunweb.co.uk', 'www.sunweb.co.uk', 'sunweb.com', 'www.sunweb.com'],
    '€40 flat OR 2-7.2%',
    'tour_operator', 'flexoffers', '30d', 1,
    'https://www.flexoffers.com/advertisers/sunweb',
    'World Best Ski Tour Operator 9x winner. Excellent family packages with lift pass included.'
) ON CONFLICT (program_name) DO NOTHING;

-- Skiweekends - UK market short breaks
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'skiweekends', 'Skiweekends',
    'https://www.skiweekends.com/{path}?ref={aid}',
    ARRAY['skiweekends.com', 'www.skiweekends.com'],
    '3%',
    'tour_operator', 'direct', '30d', 1,
    'https://www.skiweekends.com/affiliate',
    'UK market focus. Avg booking £1500+ = £45+ per sale. Short break specialists.'
) ON CONFLICT (program_name) DO NOTHING;

-- World Nomads - Essential travel insurance
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'world_nomads', 'World Nomads',
    'https://www.worldnomads.com/travel-insurance/?affiliate={aid}',
    ARRAY['worldnomads.com', 'www.worldnomads.com'],
    'Referral fee',
    'insurance', 'direct', '30d', 1,
    'https://www.worldnomads.com/affiliate-program',
    '#1 rated travel insurance. Covers 150+ activities including skiing. Essential for families.'
) ON CONFLICT (program_name) DO NOTHING;

-- Viator - Non-ski family activities
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'viator', 'Viator',
    'https://www.viator.com/{path}?pid={aid}',
    ARRAY['viator.com', 'www.viator.com'],
    '8%',
    'activities', 'travelpayouts', '30d', 1,
    'https://www.travelpayouts.com/en/programs/viator',
    '300,000+ experiences. Great for rest days and non-ski family activities.'
) ON CONFLICT (program_name) DO NOTHING;

-- =====================================================
-- TIER 2: HIGH VALUE (Priority 2)
-- =====================================================

-- Skiset - #1 ski rental network
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'skiset', 'Skiset',
    'https://www.skiset.com/{path}?affiliate={aid}',
    ARRAY['skiset.com', 'www.skiset.com'],
    '5-10%',
    'rentals', 'direct', '30d', 2,
    'https://www.skiset.com/en/affiliate',
    '#1 ski rental network. 50% off walk-in prices. Massive network.'
) ON CONFLICT (program_name) DO NOTHING;

-- Snow Rental - Europe focus
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'snow_rental', 'Snow Rental',
    'https://www.snow-rental.com/{path}?partner={aid}',
    ARRAY['snow-rental.com', 'www.snow-rental.com'],
    'Commission-based',
    'rentals', 'awin', '30d', 2,
    'https://www.awin.com/gb/advertisers/snow-rental',
    '1,000 shops, 400+ resorts (Europe). Part of Ski Company group.'
) ON CONFLICT (program_name) DO NOTHING;

-- Crystal Ski Holidays - UK largest operator
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'crystal_ski', 'Crystal Ski Holidays',
    'https://www.crystalski.co.uk/{path}?affiliate={aid}',
    ARRAY['crystalski.co.uk', 'www.crystalski.co.uk'],
    '1.6-2% + up to 40% bonus',
    'tour_operator', 'impact', '30d', 2,
    'https://impact.com/advertisers/crystal-ski',
    'UK largest ski operator. 120+ resorts. Strong family focus.'
) ON CONFLICT (program_name) DO NOTHING;

-- Backcountry - Premium ski gear
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'backcountry', 'Backcountry',
    'https://www.backcountry.com/{path}?CMP_ID={aid}',
    ARRAY['backcountry.com', 'www.backcountry.com'],
    '4-12% tiered',
    'gear', 'impact', '30d', 2,
    'https://impact.com/advertisers/backcountry',
    'Premium ski gear, top brands. Excellent gear guide opportunities.'
) ON CONFLICT (program_name) DO NOTHING;

-- REI - Trusted outdoor co-op
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'rei', 'REI',
    'https://www.rei.com/{path}?cm_mmc={aid}',
    ARRAY['rei.com', 'www.rei.com'],
    '5%',
    'gear', 'avantlink', '30d', 2,
    'https://www.avantlink.com/merchants/rei/',
    'Premium outdoor. Family ski gear. Trusted co-op with loyal customers.'
) ON CONFLICT (program_name) DO NOTHING;

-- BabyQuip - Perfect for traveling families
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'babyquip', 'BabyQuip',
    'https://www.babyquip.com/{path}?ref={aid}',
    ARRAY['babyquip.com', 'www.babyquip.com'],
    '10%',
    'baby_gear', 'direct', '30d', 2,
    'https://www.babyquip.com/partners',
    '#1 baby gear rental - cribs, car seats, etc. Perfect for traveling families!'
) ON CONFLICT (program_name) DO NOTHING;

-- GetSkiTickets - Long 90-day cookie
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'getskitickets', 'GetSkiTickets',
    'https://www.getskitickets.com/{path}?affiliate={aid}',
    ARRAY['getskitickets.com', 'www.getskitickets.com'],
    '3%',
    'lift_tickets', 'direct', '90d', 2,
    'https://www.getskitickets.com/affiliate',
    'Lift tickets + rentals + lessons. Long 90-day cookie!'
) ON CONFLICT (program_name) DO NOTHING;

-- Interhome - European chalets
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'interhome', 'Interhome',
    'https://www.interhome.com/{path}?affiliate={aid}',
    ARRAY['interhome.com', 'www.interhome.com'],
    'Up to 8%',
    'accommodation', 'awin', '30d', 2,
    'https://www.awin.com/gb/advertisers/interhome',
    '40,000 holiday homes. Alps focus. Excellent for European chalets.'
) ON CONFLICT (program_name) DO NOTHING;

-- VRBO - Family-sized vacation rentals
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'vrbo', 'VRBO',
    'https://www.vrbo.com/{path}?affid={aid}',
    ARRAY['vrbo.com', 'www.vrbo.com'],
    '1.8%',
    'accommodation', 'cj', '7d', 2,
    'https://www.cj.com/advertiser/vrbo',
    '2M+ vacation homes. Better for families than hotels. Short cookie though.'
) ON CONFLICT (program_name) DO NOTHING;

-- Expedia - Package deals
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'expedia', 'Expedia',
    'https://www.expedia.com/{path}?afflid={aid}',
    ARRAY['expedia.com', 'www.expedia.com'],
    '2-6%',
    'accommodation', 'cj', '7d', 2,
    'https://www.cj.com/advertiser/expedia',
    'Bundles (flight+hotel) work well for ski trips. Short cookie limiting.'
) ON CONFLICT (program_name) DO NOTHING;

-- TripAdvisor - Research phase monetization
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'tripadvisor', 'TripAdvisor',
    'https://www.tripadvisor.com/{path}?m={aid}',
    ARRAY['tripadvisor.com', 'www.tripadvisor.com'],
    '50% of click-out',
    'accommodation', 'direct', '14d', 2,
    'https://www.tripadvisor.com/affiliates',
    'Pays on click, not booking. Good for research phase monetization.'
) ON CONFLICT (program_name) DO NOTHING;

-- Skyscanner - Flight comparison
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'skyscanner', 'Skyscanner',
    'https://www.skyscanner.com/{path}?associate={aid}',
    ARRAY['skyscanner.com', 'www.skyscanner.com', 'skyscanner.net'],
    '50% revenue + $1/app',
    'flights', 'cj', '30d', 2,
    'https://www.partners.skyscanner.net/',
    '100M monthly users. Leading flight comparison. ~20% effective commission.'
) ON CONFLICT (program_name) DO NOTHING;

-- evo - Ski/snowboard specialist
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'evo', 'evo',
    'https://www.evo.com/{path}?avad={aid}',
    ARRAY['evo.com', 'www.evo.com'],
    '8%',
    'gear', 'avantlink', '30d', 2,
    'https://www.avantlink.com/merchants/evo/',
    'Ski/snowboard specialist since 2001. Excellent selection.'
) ON CONFLICT (program_name) DO NOTHING;

-- Auto Europe - Car rental with winter options
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'auto_europe', 'Auto Europe',
    'https://www.autoeurope.com/{path}?aff={aid}',
    ARRAY['autoeurope.com', 'www.autoeurope.com'],
    '4.4-8%',
    'car_rental', 'cj', '30d', 2,
    'https://www.cj.com/advertiser/auto-europe',
    '60+ years, winter tires available. 180 countries.'
) ON CONFLICT (program_name) DO NOTHING;

-- =====================================================
-- TIER 3: SUPPLEMENTARY (Priority 3)
-- =====================================================

-- Burton - Top snowboard brand
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'burton', 'Burton',
    'https://www.burton.com/{path}?aid={aid}',
    ARRAY['burton.com', 'www.burton.com'],
    'Up to 6%',
    'gear', 'awin', '30d', 3,
    'https://www.awin.com/gb/advertisers/burton',
    '#1 snowboard brand. Strong kids gear line.'
) ON CONFLICT (program_name) DO NOTHING;

-- GoPro - Capture ski memories
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'gopro', 'GoPro',
    'https://gopro.com/{path}?ref={aid}',
    ARRAY['gopro.com', 'www.gopro.com'],
    '3%',
    'camera', 'cj', '30d', 3,
    'https://www.cj.com/advertiser/gopro',
    'Official camera of Freeride World Tour. Perfect for ski memories.'
) ON CONFLICT (program_name) DO NOTHING;

-- Epic Pass (epicpass.io) - Multi-resort passes
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'epic_pass', 'Epic Pass',
    'https://www.epicpass.com/{path}?ref={aid}',
    ARRAY['epicpass.com', 'www.epicpass.com'],
    '10% sales + 25% new signups',
    'lift_tickets', 'direct', '30d', 3,
    'https://www.epicpass.io/',
    'Multi-resort pass affiliate program. Via epicpass.io (not official Vail).'
) ON CONFLICT (program_name) DO NOTHING;

-- Esprit Ski - Family specialists with childcare
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'esprit_ski', 'Esprit Ski',
    'https://www.espritski.com/{path}?ref={aid}',
    ARRAY['espritski.com', 'www.espritski.com'],
    'Inquire',
    'tour_operator', 'direct', '30d', 3,
    'https://www.espritski.com/contact',
    'Family ski specialists. Childcare included. Perfect for families with young kids.'
) ON CONFLICT (program_name) DO NOTHING;

-- Ski Famille - Family-only ski holidays
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'ski_famille', 'Ski Famille',
    'https://www.skifamille.co.uk/{path}?ref={aid}',
    ARRAY['skifamille.co.uk', 'www.skifamille.co.uk'],
    'Inquire',
    'tour_operator', 'direct', '30d', 3,
    'https://www.skifamille.co.uk/contact',
    'Family-ONLY ski holidays. Kids clubs and nannies included.'
) ON CONFLICT (program_name) DO NOTHING;

-- Skiworld - UK independent specialist
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'skiworld', 'Skiworld',
    'https://www.skiworld.co.uk/{path}?aff={aid}',
    ARRAY['skiworld.co.uk', 'www.skiworld.co.uk'],
    'Commission-based',
    'tour_operator', 'direct', '30d', 3,
    'https://www.skiworld.co.uk/affiliate',
    'UK largest independent ski specialist. Chalet holidays, 40+ years experience.'
) ON CONFLICT (program_name) DO NOTHING;

-- Allianz Travel Insurance
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'allianz_travel', 'Allianz Travel',
    'https://www.allianztravelinsurance.com/{path}?aff={aid}',
    ARRAY['allianztravelinsurance.com', 'www.allianztravelinsurance.com'],
    'Via networks',
    'insurance', 'cj', '30d', 3,
    'https://www.cj.com/advertiser/allianz-travel',
    'Major insurer with winter sports add-on. Trusted brand.'
) ON CONFLICT (program_name) DO NOTHING;

-- Alps Resorts - Austrian holiday homes
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'alps_resorts', 'Alps Resorts',
    'https://www.alps-resorts.com/{path}?partner={aid}',
    ARRAY['alps-resorts.com', 'www.alps-resorts.com'],
    '4%',
    'accommodation', 'flexoffers', '30d', 3,
    'https://www.flexoffers.com/advertisers/alps-resorts',
    'Austria leading holiday homes. Ski-in/ski-out properties.'
) ON CONFLICT (program_name) DO NOTHING;

-- Europe-Mountains - Alps-focused since 2005
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'europe_mountains', 'Europe-Mountains',
    'https://www.europe-mountains.com/{path}?ref={aid}',
    ARRAY['europe-mountains.com', 'www.europe-mountains.com'],
    'Up to 8%',
    'accommodation', 'direct', '30d', 3,
    'https://www.europe-mountains.com/affiliate',
    'Alps-focused since 2005. Highly ski-specific accommodations.'
) ON CONFLICT (program_name) DO NOTHING;

-- GetYourGuide - Tours and activities
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'getyourguide', 'GetYourGuide',
    'https://www.getyourguide.com/{path}?partner_id={aid}',
    ARRAY['getyourguide.com', 'www.getyourguide.com'],
    'Commission-based',
    'activities', 'direct', '30d', 3,
    'https://partner.getyourguide.com/',
    'Tours and activities. Good for rest days and off-mountain family fun.'
) ON CONFLICT (program_name) DO NOTHING;

-- Peter Glenn - Long 150-day cookie!
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'peter_glenn', 'Peter Glenn',
    'https://www.peterglenn.com/{path}?ref={aid}',
    ARRAY['peterglenn.com', 'www.peterglenn.com'],
    '9-12% tiered',
    'gear', 'cj', '150d', 3,
    'https://www.cj.com/advertiser/peter-glenn',
    'Ski equipment specialists. Impressive 150-day cookie!'
) ON CONFLICT (program_name) DO NOTHING;

-- Helly Hansen - Professional ski wear
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'helly_hansen', 'Helly Hansen',
    'https://www.hellyhansen.com/{path}?affiliate={aid}',
    ARRAY['hellyhansen.com', 'www.hellyhansen.com'],
    'Via networks',
    'gear', 'avantlink', '30d', 3,
    'https://www.avantlink.com/merchants/helly-hansen/',
    'Professional ski wear, excellent base layers. Top kids base layer brand.'
) ON CONFLICT (program_name) DO NOTHING;

-- The North Face - Iconic outdoor brand
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'north_face', 'The North Face',
    'https://www.thenorthface.com/{path}?cm_mmc={aid}',
    ARRAY['thenorthface.com', 'www.thenorthface.com'],
    '2.4-4%',
    'gear', 'flexoffers', '30d', 3,
    'https://www.flexoffers.com/advertisers/the-north-face',
    'Iconic outdoor brand with excellent kids ski apparel line.'
) ON CONFLICT (program_name) DO NOTHING;

-- Columbia - Budget-friendly family ski wear
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'columbia', 'Columbia',
    'https://www.columbia.com/{path}?mid={aid}',
    ARRAY['columbia.com', 'www.columbia.com'],
    'Via networks',
    'gear', 'cj', '30d', 3,
    'https://www.cj.com/advertiser/columbia',
    'Affordable family ski wear. Budget-friendly option for families.'
) ON CONFLICT (program_name) DO NOTHING;

-- Patagonia - Premium ethical brand
INSERT INTO affiliate_config (
    program_name, display_name, url_template, domains, commission_rate,
    category, network, cookie_duration, priority_tier, signup_url, notes
) VALUES (
    'patagonia', 'Patagonia',
    'https://www.patagonia.com/{path}?utm_source={aid}',
    ARRAY['patagonia.com', 'www.patagonia.com'],
    'Commission-based',
    'gear', 'avantlink', '30d', 3,
    'https://www.avantlink.com/merchants/patagonia/',
    'Premium ethical brand. Appeals to eco-conscious families.'
) ON CONFLICT (program_name) DO NOTHING;

-- =====================================================
-- Create index for category-based queries
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_affiliate_config_category
ON affiliate_config(category) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_affiliate_config_priority
ON affiliate_config(priority_tier) WHERE is_active = TRUE;

-- =====================================================
-- Summary view for affiliate programs by category
-- =====================================================
CREATE OR REPLACE VIEW affiliate_programs_summary AS
SELECT
    category,
    COUNT(*) as program_count,
    COUNT(*) FILTER (WHERE priority_tier = 1) as tier1_count,
    COUNT(*) FILTER (WHERE priority_tier = 2) as tier2_count,
    COUNT(*) FILTER (WHERE priority_tier = 3) as tier3_count,
    ARRAY_AGG(display_name ORDER BY priority_tier, display_name) as programs
FROM affiliate_config
WHERE is_active = TRUE
GROUP BY category
ORDER BY category;

COMMENT ON VIEW affiliate_programs_summary IS 'Summary of affiliate programs by category with tier breakdown';
