-- Seed Discovery Candidates with ~250 Family-Friendly Ski Resorts
-- Round 5.4 - Expert Panel Finding: Discovery pool was empty, site cannot grow
--
-- Distribution:
-- - North America: ~80 resorts (US, Canada)
-- - Europe: ~120 resorts (Alps, Scandinavia, Eastern Europe)
-- - Asia/Oceania: ~30 resorts (Japan, Korea, Australia, NZ)
-- - South America: ~20 resorts (Chile, Argentina)
--
-- Priority: Family-friendly resorts with ski schools, beginner terrain, childcare

-- =============================================================================
-- NORTH AMERICA - USA (~65 resorts)
-- =============================================================================

-- Colorado (15)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Vail', 'United States', 'Colorado', 'manual_seed', 0.95, '[{"source":"manual","strength":0.9,"reasoning":"Top US family resort, Epic Pass"}]'::jsonb, 'Premier family destination with excellent ski school', 'pending'),
  ('Breckenridge', 'United States', 'Colorado', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"Epic Pass, excellent kids programs"}]'::jsonb, 'Historic town with great beginner terrain', 'pending'),
  ('Keystone', 'United States', 'Colorado', 'manual_seed', 0.90, '[{"source":"manual","strength":0.85,"reasoning":"Epic Pass, night skiing, family focused"}]'::jsonb, 'Family-focused with night skiing', 'pending'),
  ('Copper Mountain', 'United States', 'Colorado', 'manual_seed', 0.85, '[{"source":"manual","strength":0.8,"reasoning":"Naturally divided terrain, Ikon Pass"}]'::jsonb, 'Naturally divided terrain by ability', 'pending'),
  ('Winter Park', 'United States', 'Colorado', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Ikon Pass, National Sports Center for Disabled"}]'::jsonb, 'Award-winning adaptive skiing programs', 'pending'),
  ('Steamboat', 'United States', 'Colorado', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Ikon Pass, Kids Ski Free program"}]'::jsonb, 'Famous Kids Ski Free program', 'pending'),
  ('Aspen Snowmass', 'United States', 'Colorado', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Ikon Pass, Treehouse kids center"}]'::jsonb, 'Treehouse kids adventure center', 'pending'),
  ('Telluride', 'United States', 'Colorado', 'manual_seed', 0.82, '[{"source":"manual","strength":0.78,"reasoning":"Free gondola, charming town"}]'::jsonb, 'Free gondola connects town and mountain', 'pending'),
  ('Crested Butte', 'United States', 'Colorado', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Affordable, friendly atmosphere"}]'::jsonb, 'Affordable alternative, friendly locals', 'pending'),
  ('Beaver Creek', 'United States', 'Colorado', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"Epic Pass, luxury family amenities"}]'::jsonb, 'Luxury family experience with cookies at 3pm', 'pending'),
  ('Purgatory', 'United States', 'Colorado', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Value option, less crowded"}]'::jsonb, 'Budget-friendly Southwest Colorado option', 'pending'),
  ('Arapahoe Basin', 'United States', 'Colorado', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Ikon Pass, longest season"}]'::jsonb, 'Longest ski season in Colorado', 'pending'),
  ('Loveland', 'United States', 'Colorado', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Affordable day trips from Denver"}]'::jsonb, 'Affordable day-trip option from Denver', 'pending'),
  ('Eldora', 'United States', 'Colorado', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Close to Boulder, beginner friendly"}]'::jsonb, 'Closest to Boulder, great for beginners', 'pending'),
  ('Ski Cooper', 'United States', 'Colorado', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Small family resort, affordable"}]'::jsonb, 'Small affordable family resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Utah (10)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Park City', 'United States', 'Utah', 'manual_seed', 0.95, '[{"source":"manual","strength":0.92,"reasoning":"Epic Pass, largest US resort"}]'::jsonb, 'Largest US ski resort, 7300 acres', 'pending'),
  ('Deer Valley', 'United States', 'Utah', 'manual_seed', 0.94, '[{"source":"manual","strength":0.92,"reasoning":"Ikon Pass, skiers only, luxury service"}]'::jsonb, 'Luxury ski-only resort with exceptional service', 'pending'),
  ('Snowbird', 'United States', 'Utah', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Ikon Pass, expert terrain but family options"}]'::jsonb, 'Challenging terrain with family programs', 'pending'),
  ('Alta', 'United States', 'Utah', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Ikon Pass, skiers only, legendary powder"}]'::jsonb, 'Classic ski experience, skiers only', 'pending'),
  ('Brighton', 'United States', 'Utah', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Ikon Pass, night skiing, affordable"}]'::jsonb, 'Night skiing and affordable day passes', 'pending'),
  ('Solitude', 'United States', 'Utah', 'manual_seed', 0.76, '[{"source":"manual","strength":0.73,"reasoning":"Ikon Pass, less crowded"}]'::jsonb, 'Less crowded alternative in Big Cottonwood', 'pending'),
  ('Snowbasin', 'United States', 'Utah', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Beautiful lodges, 2002 Olympics venue"}]'::jsonb, 'Olympic venue with stunning lodges', 'pending'),
  ('Powder Mountain', 'United States', 'Utah', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Largest by acreage, uncrowded"}]'::jsonb, 'Largest skiable acreage in US, uncrowded', 'pending'),
  ('Brian Head', 'United States', 'Utah', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Southern Utah, near national parks"}]'::jsonb, 'Southern Utah near Zion and Bryce', 'pending'),
  ('Sundance', 'United States', 'Utah', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Boutique resort, Robert Redford owned"}]'::jsonb, 'Boutique resort with artistic atmosphere', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- California (8)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Mammoth Mountain', 'United States', 'California', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Ikon Pass, longest CA season"}]'::jsonb, 'Largest CA resort with long season', 'pending'),
  ('Palisades Tahoe', 'United States', 'California', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Ikon Pass, 1960 Olympics venue"}]'::jsonb, 'Olympic heritage, combined two resorts', 'pending'),
  ('Heavenly', 'United States', 'California', 'manual_seed', 0.86, '[{"source":"manual","strength":0.84,"reasoning":"Epic Pass, Lake Tahoe views"}]'::jsonb, 'Stunning Lake Tahoe views', 'pending'),
  ('Northstar', 'United States', 'California', 'manual_seed', 0.84, '[{"source":"manual","strength":0.82,"reasoning":"Epic Pass, family village"}]'::jsonb, 'Purpose-built family village', 'pending'),
  ('Kirkwood', 'United States', 'California', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Epic Pass, challenging terrain"}]'::jsonb, 'Challenging terrain, less crowded', 'pending'),
  ('Sugar Bowl', 'United States', 'California', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Historic Tahoe resort"}]'::jsonb, 'Historic Tahoe resort since 1939', 'pending'),
  ('Big Bear Mountain', 'United States', 'California', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Close to LA, beginner friendly"}]'::jsonb, 'Closest skiing to Los Angeles', 'pending'),
  ('Mountain High', 'United States', 'California', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Day trip from LA, night skiing"}]'::jsonb, 'LA day trips with night skiing', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Vermont (6)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Stowe', 'United States', 'Vermont', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Epic Pass, New England classic"}]'::jsonb, 'Classic New England ski town', 'pending'),
  ('Killington', 'United States', 'Vermont', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Ikon Pass, Beast of the East"}]'::jsonb, 'Beast of the East - largest VT resort', 'pending'),
  ('Okemo', 'United States', 'Vermont', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Epic Pass, excellent family programs"}]'::jsonb, 'Family-focused with excellent programs', 'pending'),
  ('Smugglers Notch', 'United States', 'Vermont', 'manual_seed', 0.88, '[{"source":"manual","strength":0.86,"reasoning":"#1 family resort in East"}]'::jsonb, 'Top-rated family resort in Eastern US', 'pending'),
  ('Mount Snow', 'United States', 'Vermont', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Epic Pass, close to NYC/Boston"}]'::jsonb, 'Accessible from NYC and Boston', 'pending'),
  ('Stratton', 'United States', 'Vermont', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Ikon Pass, village atmosphere"}]'::jsonb, 'European-style village', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Other Northeast (8)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Sunday River', 'United States', 'Maine', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Ikon Pass, excellent snowmaking"}]'::jsonb, 'Excellent snowmaking in Maine', 'pending'),
  ('Sugarloaf', 'United States', 'Maine', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Ikon Pass, above treeline skiing"}]'::jsonb, 'Only above-treeline skiing in East', 'pending'),
  ('Loon Mountain', 'United States', 'New Hampshire', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Epic Pass, White Mountains"}]'::jsonb, 'White Mountains family resort', 'pending'),
  ('Bretton Woods', 'United States', 'New Hampshire', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Grand resort setting, family focused"}]'::jsonb, 'Grand hotel setting, family-focused', 'pending'),
  ('Cannon Mountain', 'United States', 'New Hampshire', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"State park, affordable"}]'::jsonb, 'Affordable state-run resort', 'pending'),
  ('Whiteface', 'United States', 'New York', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Ikon Pass, Lake Placid Olympics"}]'::jsonb, 'Lake Placid Olympics venue', 'pending'),
  ('Gore Mountain', 'United States', 'New York', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"State-owned, affordable"}]'::jsonb, 'New York state-owned resort', 'pending'),
  ('Hunter Mountain', 'United States', 'New York', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Close to NYC, Epic Pass"}]'::jsonb, 'Closest skiing to NYC', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Montana/Wyoming/Idaho (8)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Big Sky', 'United States', 'Montana', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Ikon Pass, biggest skiing in America"}]'::jsonb, 'Biggest skiing in America, 5800 acres', 'pending'),
  ('Whitefish', 'United States', 'Montana', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Charming town, affordable"}]'::jsonb, 'Charming town near Glacier NP', 'pending'),
  ('Bridger Bowl', 'United States', 'Montana', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Community owned, affordable"}]'::jsonb, 'Community-owned, legendary powder', 'pending'),
  ('Jackson Hole', 'United States', 'Wyoming', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Ikon Pass, expert terrain"}]'::jsonb, 'Expert terrain but excellent ski school', 'pending'),
  ('Grand Targhee', 'United States', 'Wyoming', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Powder haven, family friendly"}]'::jsonb, 'Powder haven with family atmosphere', 'pending'),
  ('Sun Valley', 'United States', 'Idaho', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Ikon Pass, first US destination resort"}]'::jsonb, 'First US destination resort', 'pending'),
  ('Tamarack', 'United States', 'Idaho', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Village resort, family focused"}]'::jsonb, 'Modern village resort', 'pending'),
  ('Schweitzer', 'United States', 'Idaho', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"North Idaho gem, lake views"}]'::jsonb, 'North Idaho gem with lake views', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Pacific Northwest (5)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Crystal Mountain', 'United States', 'Washington', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Ikon Pass, Mt Rainier views"}]'::jsonb, 'Mount Rainier views, diverse terrain', 'pending'),
  ('Stevens Pass', 'United States', 'Washington', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Epic Pass, family friendly"}]'::jsonb, 'Accessible from Seattle', 'pending'),
  ('Mount Bachelor', 'United States', 'Oregon', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Ikon Pass, volcanic terrain"}]'::jsonb, 'Volcanic terrain, dry powder', 'pending'),
  ('Timberline', 'United States', 'Oregon', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Historic lodge, year-round skiing"}]'::jsonb, 'Historic lodge, year-round skiing', 'pending'),
  ('Mount Hood Meadows', 'United States', 'Oregon', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Ikon Pass, close to Portland"}]'::jsonb, 'Largest Oregon resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- Southwest/Midwest (5)
INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Taos', 'United States', 'New Mexico', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Ikon Pass, unique culture"}]'::jsonb, 'Unique Southwest culture', 'pending'),
  ('Ski Santa Fe', 'United States', 'New Mexico', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Close to Santa Fe, affordable"}]'::jsonb, 'Day trip from Santa Fe', 'pending'),
  ('Arizona Snowbowl', 'United States', 'Arizona', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Ikon Pass, Flagstaff skiing"}]'::jsonb, 'Skiing in Arizona near Grand Canyon', 'pending'),
  ('Boyne Mountain', 'United States', 'Michigan', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Midwest family favorite"}]'::jsonb, 'Midwest family favorite', 'pending'),
  ('Granite Peak', 'United States', 'Wisconsin', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Biggest in Wisconsin"}]'::jsonb, 'Largest vertical in Wisconsin', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- NORTH AMERICA - CANADA (~15 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Whistler Blackcomb', 'Canada', 'British Columbia', 'manual_seed', 0.95, '[{"source":"manual","strength":0.92,"reasoning":"Epic Pass, largest NA resort"}]'::jsonb, 'Largest ski resort in North America', 'pending'),
  ('Sun Peaks', 'Canada', 'British Columbia', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Family village, ski-in/out"}]'::jsonb, 'Ski-in/ski-out village, family focused', 'pending'),
  ('Big White', 'Canada', 'British Columbia', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Ski-in/out village, champagne powder"}]'::jsonb, 'Champagne powder, ski-in/out village', 'pending'),
  ('Revelstoke', 'Canada', 'British Columbia', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Most vertical in NA"}]'::jsonb, 'Most vertical feet in North America', 'pending'),
  ('Silver Star', 'Canada', 'British Columbia', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Victorian village, family friendly"}]'::jsonb, 'Colorful Victorian village', 'pending'),
  ('Fernie', 'Canada', 'British Columbia', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Authentic ski town"}]'::jsonb, 'Authentic mountain town atmosphere', 'pending'),
  ('Kicking Horse', 'Canada', 'British Columbia', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Epic terrain, value pricing"}]'::jsonb, 'Expert terrain at value prices', 'pending'),
  ('Lake Louise', 'Canada', 'Alberta', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Ikon Pass, Banff NP"}]'::jsonb, 'Stunning Banff National Park setting', 'pending'),
  ('Banff Sunshine', 'Canada', 'Alberta', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Ikon Pass, on continental divide"}]'::jsonb, 'Straddles continental divide', 'pending'),
  ('Mount Norquay', 'Canada', 'Alberta', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Close to Banff town, family friendly"}]'::jsonb, 'Closest to Banff town', 'pending'),
  ('Marmot Basin', 'Canada', 'Alberta', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Jasper NP, uncrowded"}]'::jsonb, 'Jasper National Park, uncrowded', 'pending'),
  ('Mont Tremblant', 'Canada', 'Quebec', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Ikon Pass, pedestrian village"}]'::jsonb, 'Eastern Canada premier resort', 'pending'),
  ('Mont Sainte-Anne', 'Canada', 'Quebec', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Near Quebec City, night skiing"}]'::jsonb, 'Near Quebec City, night skiing', 'pending'),
  ('Le Massif', 'Canada', 'Quebec', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"St Lawrence views, most vertical in East"}]'::jsonb, 'Highest vertical in Eastern Canada', 'pending'),
  ('Blue Mountain', 'Canada', 'Ontario', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Ikon Pass, Ontario largest"}]'::jsonb, 'Ontario largest resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - AUSTRIA (~25 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('St. Anton', 'Austria', 'Tyrol', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"Legendary resort, Ski Arlberg"}]'::jsonb, 'Legendary Arlberg resort', 'pending'),
  ('Lech-Zürs', 'Austria', 'Vorarlberg', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Luxury family resort, Ski Arlberg"}]'::jsonb, 'Luxury Austrian classic', 'pending'),
  ('Kitzbühel', 'Austria', 'Tyrol', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Historic town, Hahnenkamm"}]'::jsonb, 'Historic medieval town', 'pending'),
  ('Sölden', 'Austria', 'Tyrol', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Glacier skiing, James Bond filming"}]'::jsonb, 'Glacier skiing, 007 filming location', 'pending'),
  ('Ischgl', 'Austria', 'Tyrol', 'manual_seed', 0.84, '[{"source":"manual","strength":0.82,"reasoning":"Après-ski, high altitude"}]'::jsonb, 'High-altitude guaranteed snow', 'pending'),
  ('Serfaus-Fiss-Ladis', 'Austria', 'Tyrol', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"Top family resort in Austria"}]'::jsonb, 'Top-rated family resort in Austria', 'pending'),
  ('Obergurgl-Hochgurgl', 'Austria', 'Tyrol', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Snow-sure, high altitude"}]'::jsonb, 'Highest parish in Austria, snow-sure', 'pending'),
  ('Mayrhofen', 'Austria', 'Tyrol', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Zillertal Valley, family friendly"}]'::jsonb, 'Zillertal Valley hub', 'pending'),
  ('Stubai Glacier', 'Austria', 'Tyrol', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Close to Innsbruck, glacier"}]'::jsonb, 'Closest glacier to Innsbruck', 'pending'),
  ('Hintertux Glacier', 'Austria', 'Tyrol', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Year-round skiing"}]'::jsonb, 'Year-round glacier skiing', 'pending'),
  ('Alpbach', 'Austria', 'Tyrol', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Most beautiful village, family focused"}]'::jsonb, 'Most beautiful village in Austria', 'pending'),
  ('Söll', 'Austria', 'Tyrol', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"SkiWelt, value pricing"}]'::jsonb, 'SkiWelt value option', 'pending'),
  ('Westendorf', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"SkiWelt, authentic village"}]'::jsonb, 'Authentic Tyrolean village', 'pending'),
  ('Ellmau', 'Austria', 'Tyrol', 'manual_seed', 0.73, '[{"source":"manual","strength":0.7,"reasoning":"SkiWelt, family friendly"}]'::jsonb, 'Family-friendly SkiWelt resort', 'pending'),
  ('Bad Gastein', 'Austria', 'Salzburg', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Spa tradition, Belle Époque"}]'::jsonb, 'Belle Époque spa town', 'pending'),
  ('Schladming', 'Austria', 'Styria', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"World Cup venue, 4 Mountains"}]'::jsonb, 'World Cup venue, 4 Mountains region', 'pending'),
  ('Saalbach-Hinterglemm', 'Austria', 'Salzburg', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Ski Circus, party atmosphere"}]'::jsonb, 'Ski Circus with extensive terrain', 'pending'),
  ('Zell am See-Kaprun', 'Austria', 'Salzburg', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Lake and glacier combo"}]'::jsonb, 'Lake town with glacier access', 'pending'),
  ('Obertauern', 'Austria', 'Salzburg', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Snow-sure, ski-in/out"}]'::jsonb, 'Snow-sure ski-in/out resort', 'pending'),
  ('Nassfeld', 'Austria', 'Carinthia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Sunny south, family focused"}]'::jsonb, 'Sunny southern Alps', 'pending'),
  ('Brand', 'Austria', 'Vorarlberg', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Small family resort"}]'::jsonb, 'Quiet family-friendly resort', 'pending'),
  ('Damüls-Mellau', 'Austria', 'Vorarlberg', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Snow record, family friendly"}]'::jsonb, 'Record snowfall village', 'pending'),
  ('Warth-Schröcken', 'Austria', 'Vorarlberg', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Connected to Ski Arlberg"}]'::jsonb, 'Gateway to Ski Arlberg', 'pending'),
  ('Bad Kleinkirchheim', 'Austria', 'Carinthia', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Thermal spas, family friendly"}]'::jsonb, 'Thermal spa skiing combo', 'pending'),
  ('Zillertal Arena', 'Austria', 'Tyrol', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Large linked area"}]'::jsonb, 'Large interconnected ski area', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - SWITZERLAND (~20 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Zermatt', 'Switzerland', 'Valais', 'manual_seed', 0.95, '[{"source":"manual","strength":0.92,"reasoning":"Matterhorn, year-round skiing"}]'::jsonb, 'Matterhorn views, year-round skiing', 'pending'),
  ('Verbier', 'Switzerland', 'Valais', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"4 Vallées, expert terrain"}]'::jsonb, '4 Vallées extensive terrain', 'pending'),
  ('St. Moritz', 'Switzerland', 'Graubünden', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Luxury resort, Olympic history"}]'::jsonb, 'Birthplace of winter tourism', 'pending'),
  ('Davos-Klosters', 'Switzerland', 'Graubünden', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Large area, town atmosphere"}]'::jsonb, 'Large ski area with town atmosphere', 'pending'),
  ('Saas-Fee', 'Switzerland', 'Valais', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Car-free, glacier skiing"}]'::jsonb, 'Car-free glacier village', 'pending'),
  ('Crans-Montana', 'Switzerland', 'Valais', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Sunny plateau, panoramic views"}]'::jsonb, 'Sunny plateau resort', 'pending'),
  ('Grindelwald', 'Switzerland', 'Bern', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Jungfrau region, iconic views"}]'::jsonb, 'Jungfrau region, iconic Eiger views', 'pending'),
  ('Wengen', 'Switzerland', 'Bern', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Car-free, Lauberhorn downhill"}]'::jsonb, 'Car-free village, Lauberhorn races', 'pending'),
  ('Mürren', 'Switzerland', 'Bern', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Car-free, Schilthorn/OHMSS"}]'::jsonb, 'Car-free, James Bond Schilthorn', 'pending'),
  ('Adelboden-Lenk', 'Switzerland', 'Bern', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Traditional, World Cup venue"}]'::jsonb, 'Traditional resort, World Cup venue', 'pending'),
  ('Gstaad', 'Switzerland', 'Bern', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Glamorous, multi-resort pass"}]'::jsonb, 'Glamorous resort with chalet style', 'pending'),
  ('Arosa Lenzerheide', 'Switzerland', 'Graubünden', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Linked areas, family friendly"}]'::jsonb, 'Two linked resorts, family-friendly', 'pending'),
  ('Laax', 'Switzerland', 'Graubünden', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Freestyle/parks, modern"}]'::jsonb, 'Freestyle focus, modern facilities', 'pending'),
  ('Engelberg', 'Switzerland', 'Central Switzerland', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Titlis glacier, monastery"}]'::jsonb, 'Titlis glacier, monastery village', 'pending'),
  ('Andermatt', 'Switzerland', 'Uri', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"SkiArena, freeride"}]'::jsonb, 'SkiArena Andermatt-Sedrun', 'pending'),
  ('Villars', 'Switzerland', 'Vaud', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Lake Geneva views, family"}]'::jsonb, 'Lake Geneva views, family resort', 'pending'),
  ('Leysin', 'Switzerland', 'Vaud', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sunny, affordable Swiss option"}]'::jsonb, 'Sunny affordable Swiss resort', 'pending'),
  ('Nendaz', 'Switzerland', 'Valais', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"4 Vallées access, family village"}]'::jsonb, '4 Vallées access, family village', 'pending'),
  ('Champéry', 'Switzerland', 'Valais', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Portes du Soleil, authentic"}]'::jsonb, 'Portes du Soleil Swiss side', 'pending'),
  ('Les Diablerets', 'Switzerland', 'Vaud', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Glacier 3000, family friendly"}]'::jsonb, 'Glacier 3000 access', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - FRANCE (~25 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Chamonix', 'France', 'Haute-Savoie', 'manual_seed', 0.90, '[{"source":"manual","strength":0.88,"reasoning":"Mont Blanc, legendary mountaineering"}]'::jsonb, 'Legendary Mont Blanc resort', 'pending'),
  ('Courchevel', 'France', 'Savoie', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"3 Vallées, luxury family"}]'::jsonb, '3 Vallées luxury resort', 'pending'),
  ('Méribel', 'France', 'Savoie', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"3 Vallées, chalet style"}]'::jsonb, '3 Vallées central location', 'pending'),
  ('Val Thorens', 'France', 'Savoie', 'manual_seed', 0.86, '[{"source":"manual","strength":0.84,"reasoning":"Highest in Europe, snow-sure"}]'::jsonb, 'Highest resort in Europe', 'pending'),
  ('Les Menuires', 'France', 'Savoie', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"3 Vallées value option"}]'::jsonb, '3 Vallées value option', 'pending'),
  ('La Plagne', 'France', 'Savoie', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Paradiski, family villages"}]'::jsonb, 'Paradiski family resort', 'pending'),
  ('Les Arcs', 'France', 'Savoie', 'manual_seed', 0.84, '[{"source":"manual","strength":0.82,"reasoning":"Paradiski, modern design"}]'::jsonb, 'Paradiski modern architecture', 'pending'),
  ('Tignes', 'France', 'Savoie', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"High altitude, snow-sure"}]'::jsonb, 'High altitude snow guarantee', 'pending'),
  ('Val dIsère', 'France', 'Savoie', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"Olympic village, extensive terrain"}]'::jsonb, 'Olympic village with charm', 'pending'),
  ('Alpe dHuez', 'France', 'Isère', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Long run, sunny south-facing"}]'::jsonb, 'Sunny resort with famous long run', 'pending'),
  ('Les Deux Alpes', 'France', 'Isère', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Glacier, summer skiing"}]'::jsonb, 'Glacier with summer skiing', 'pending'),
  ('La Rosière', 'France', 'Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Sunny, links to Italy"}]'::jsonb, 'Sunny, links to La Thuile Italy', 'pending'),
  ('Les Gets', 'France', 'Haute-Savoie', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Portes du Soleil, family focused"}]'::jsonb, 'Family-focused Portes du Soleil', 'pending'),
  ('Morzine', 'France', 'Haute-Savoie', 'manual_seed', 0.84, '[{"source":"manual","strength":0.82,"reasoning":"Portes du Soleil, authentic town"}]'::jsonb, 'Authentic Alpine town', 'pending'),
  ('Avoriaz', 'France', 'Haute-Savoie', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Car-free, Portes du Soleil"}]'::jsonb, 'Car-free purpose-built resort', 'pending'),
  ('Flaine', 'France', 'Haute-Savoie', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Bauhaus design, Grand Massif"}]'::jsonb, 'Bauhaus architecture, Grand Massif', 'pending'),
  ('Samoëns', 'France', 'Haute-Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Historic village, Grand Massif"}]'::jsonb, 'Historic village in Grand Massif', 'pending'),
  ('La Clusaz', 'France', 'Haute-Savoie', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Authentic Savoyard village"}]'::jsonb, 'Authentic Savoyard village', 'pending'),
  ('Le Grand Bornand', 'France', 'Haute-Savoie', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Farm village, family friendly"}]'::jsonb, 'Working farm village, family-friendly', 'pending'),
  ('Megève', 'France', 'Haute-Savoie', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Glamorous, chalet style"}]'::jsonb, 'Glamorous chalet-style resort', 'pending'),
  ('Serre Chevalier', 'France', 'Hautes-Alpes', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Sunny south, value pricing"}]'::jsonb, 'Sunny southern Alps, value pricing', 'pending'),
  ('Montgenèvre', 'France', 'Hautes-Alpes', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Links to Italy, sunny"}]'::jsonb, 'Links to Italian Via Lattea', 'pending'),
  ('Risoul', 'France', 'Hautes-Alpes', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Family resort, affordable"}]'::jsonb, 'Family-focused affordable option', 'pending'),
  ('Pra Loup', 'France', 'Alpes-de-Haute-Provence', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Sunny south, family friendly"}]'::jsonb, 'Sunny southern family resort', 'pending'),
  ('Font Romeu', 'France', 'Pyrénées-Orientales', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Pyrenees, sunny"}]'::jsonb, 'Sunny Pyrenees resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - ITALY (~15 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Cortina dAmpezzo', 'Italy', 'Veneto', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"2026 Olympics, Dolomites"}]'::jsonb, '2026 Olympics host, Dolomites', 'pending'),
  ('Madonna di Campiglio', 'Italy', 'Trentino', 'manual_seed', 0.84, '[{"source":"manual","strength":0.82,"reasoning":"Glamorous, Dolomiti Superski"}]'::jsonb, 'Glamorous Italian classic', 'pending'),
  ('Selva Val Gardena', 'Italy', 'South Tyrol', 'manual_seed', 0.86, '[{"source":"manual","strength":0.84,"reasoning":"Sella Ronda, German/Italian culture"}]'::jsonb, 'Sella Ronda circuit access', 'pending'),
  ('Alta Badia', 'Italy', 'South Tyrol', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Sella Ronda, gourmet skiing"}]'::jsonb, 'Gourmet skiing capital', 'pending'),
  ('Kronplatz', 'Italy', 'South Tyrol', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Modern, family friendly"}]'::jsonb, 'Modern family-friendly resort', 'pending'),
  ('Sestriere', 'Italy', 'Piedmont', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"2006 Olympics, Via Lattea"}]'::jsonb, '2006 Olympics, Via Lattea', 'pending'),
  ('Courmayeur', 'Italy', 'Aosta Valley', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Mont Blanc Italian side"}]'::jsonb, 'Mont Blanc Italian side', 'pending'),
  ('La Thuile', 'Italy', 'Aosta Valley', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Links to France, value"}]'::jsonb, 'Links to La Rosière France', 'pending'),
  ('Cervinia', 'Italy', 'Aosta Valley', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Matterhorn Italian side"}]'::jsonb, 'Matterhorn Italian side', 'pending'),
  ('Bormio', 'Italy', 'Lombardy', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Thermal spas, World Cup"}]'::jsonb, 'Thermal spas and World Cup', 'pending'),
  ('Livigno', 'Italy', 'Lombardy', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Duty-free, snow-sure"}]'::jsonb, 'Duty-free shopping, snow-sure', 'pending'),
  ('Canazei', 'Italy', 'Trentino', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Sella Ronda, authentic"}]'::jsonb, 'Authentic Dolomite village', 'pending'),
  ('Ortisei', 'Italy', 'South Tyrol', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Wood carving tradition"}]'::jsonb, 'Wood carving tradition village', 'pending'),
  ('Arabba', 'Italy', 'Veneto', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Sella Ronda, challenging"}]'::jsonb, 'Sella Ronda challenging terrain', 'pending'),
  ('San Martino di Castrozza', 'Italy', 'Trentino', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Pale di San Martino views"}]'::jsonb, 'Pale di San Martino views', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - GERMANY (~6 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Garmisch-Partenkirchen', 'Germany', 'Bavaria', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"1936 Olympics, Zugspitze"}]'::jsonb, 'Germanys highest peak skiing', 'pending'),
  ('Oberstdorf', 'Germany', 'Bavaria', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Ski jumping, Nebelhorn"}]'::jsonb, 'Ski jumping and Nebelhorn glacier', 'pending'),
  ('Berchtesgaden', 'Germany', 'Bavaria', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"National park, family"}]'::jsonb, 'National park setting', 'pending'),
  ('Winterberg', 'Germany', 'North Rhine-Westphalia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Accessible from Ruhr region"}]'::jsonb, 'Accessible from major cities', 'pending'),
  ('Feldberg', 'Germany', 'Black Forest', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Black Forest skiing"}]'::jsonb, 'Black Forest largest resort', 'pending'),
  ('Reit im Winkl', 'Germany', 'Bavaria', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Cross-country, family"}]'::jsonb, 'Family-friendly Bavarian village', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - SCANDINAVIA (~12 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Åre', 'Sweden', 'Jämtland', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Scandinavias largest, World Cup"}]'::jsonb, 'Scandinavias largest resort', 'pending'),
  ('Sälen', 'Sweden', 'Dalarna', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Family friendly, multiple areas"}]'::jsonb, 'Family-friendly multiple areas', 'pending'),
  ('Vemdalen', 'Sweden', 'Härjedalen', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Modern, good for families"}]'::jsonb, 'Modern family resort', 'pending'),
  ('Trysil', 'Norway', 'Innlandet', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Norways largest, family focus"}]'::jsonb, 'Norways largest resort', 'pending'),
  ('Hemsedal', 'Norway', 'Viken', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Scandinavian Alps"}]'::jsonb, 'Scandinavian Alps nickname', 'pending'),
  ('Geilo', 'Norway', 'Viken', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Historic, cross-country"}]'::jsonb, 'Historic resort, great cross-country', 'pending'),
  ('Myrkdalen', 'Norway', 'Vestland', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Near Bergen, modern"}]'::jsonb, 'Modern resort near Bergen', 'pending'),
  ('Levi', 'Finland', 'Lapland', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Largest in Finland, Santa"}]'::jsonb, 'Finlands largest, Santa Claus country', 'pending'),
  ('Ylläs', 'Finland', 'Lapland', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Two fells, long season"}]'::jsonb, 'Two fells, longest slopes in Finland', 'pending'),
  ('Ruka', 'Finland', 'Oulu', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Near Kuusamo, World Cup"}]'::jsonb, 'World Cup venue, early season', 'pending'),
  ('Salla', 'Finland', 'Lapland', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Remote Lapland, authentic"}]'::jsonb, 'Remote authentic Lapland', 'pending'),
  ('Narvik', 'Norway', 'Nordland', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Arctic skiing, fjord views"}]'::jsonb, 'Arctic skiing with fjord views', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EUROPE - SPAIN, ANDORRA, EASTERN EUROPE (~12 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Baqueira-Beret', 'Spain', 'Catalonia', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Spains best, Pyrenees"}]'::jsonb, 'Spains premier resort', 'pending'),
  ('Sierra Nevada', 'Spain', 'Andalusia', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Southernmost in Europe, sunny"}]'::jsonb, 'Southernmost European resort', 'pending'),
  ('Formigal', 'Spain', 'Aragon', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Pyrenees, family friendly"}]'::jsonb, 'Family-friendly Pyrenees resort', 'pending'),
  ('Grandvalira', 'Andorra', 'Pyrenees', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Largest Pyrenees resort"}]'::jsonb, 'Largest resort in Pyrenees', 'pending'),
  ('Vallnord', 'Andorra', 'Pyrenees', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Two areas, family focused"}]'::jsonb, 'Two linked areas in Andorra', 'pending'),
  ('Bansko', 'Bulgaria', 'Pirin', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Value skiing, UNESCO town"}]'::jsonb, 'Value skiing near UNESCO town', 'pending'),
  ('Borovets', 'Bulgaria', 'Rila', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Oldest Bulgarian resort"}]'::jsonb, 'Oldest Bulgarian ski resort', 'pending'),
  ('Jasná', 'Slovakia', 'Low Tatras', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Modern, World Cup venue"}]'::jsonb, 'Modern Slovak resort', 'pending'),
  ('Kranjska Gora', 'Slovenia', 'Upper Carniola', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"World Cup venue, family"}]'::jsonb, 'World Cup venue, family-friendly', 'pending'),
  ('Kopaonik', 'Serbia', 'Central Serbia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Serbias largest, affordable"}]'::jsonb, 'Serbias largest resort', 'pending'),
  ('Zakopane', 'Poland', 'Lesser Poland', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Polish capital of skiing"}]'::jsonb, 'Winter capital of Poland', 'pending'),
  ('Špindlerův Mlýn', 'Czech Republic', 'Hradec Králové', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Czech largest, family"}]'::jsonb, 'Czech Republics largest resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- ASIA - JAPAN (~15 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Niseko', 'Japan', 'Hokkaido', 'manual_seed', 0.92, '[{"source":"manual","strength":0.9,"reasoning":"Legendary powder, English friendly"}]'::jsonb, 'Legendary powder, international friendly', 'pending'),
  ('Furano', 'Japan', 'Hokkaido', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Dry powder, less crowded"}]'::jsonb, 'Dry powder, less crowded than Niseko', 'pending'),
  ('Rusutsu', 'Japan', 'Hokkaido', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Family resort, powder"}]'::jsonb, 'Family-friendly with great powder', 'pending'),
  ('Tomamu', 'Japan', 'Hokkaido', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Unkai terrace, family facilities"}]'::jsonb, 'Unkai sea of clouds, family facilities', 'pending'),
  ('Kiroro', 'Japan', 'Hokkaido', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Snow record, less crowded"}]'::jsonb, 'Record snowfall, uncrowded', 'pending'),
  ('Hakuba Valley', 'Japan', 'Nagano', 'manual_seed', 0.88, '[{"source":"manual","strength":0.85,"reasoning":"1998 Olympics, 10 resorts"}]'::jsonb, '1998 Olympics host, 10 interconnected resorts', 'pending'),
  ('Nozawa Onsen', 'Japan', 'Nagano', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Hot springs, traditional"}]'::jsonb, 'Traditional onsen village', 'pending'),
  ('Shiga Kogen', 'Japan', 'Nagano', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Largest in Japan, Olympics"}]'::jsonb, 'Japans largest ski area', 'pending'),
  ('Myoko Kogen', 'Japan', 'Niigata', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Deep snow, authentic"}]'::jsonb, 'Deep snow, authentic atmosphere', 'pending'),
  ('Madarao', 'Japan', 'Nagano', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Tree skiing, family friendly"}]'::jsonb, 'Tree skiing, family-friendly', 'pending'),
  ('Naeba', 'Japan', 'Niigata', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Longest gondola, near Tokyo"}]'::jsonb, 'Longest gondola in Japan', 'pending'),
  ('Gala Yuzawa', 'Japan', 'Niigata', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Shinkansen access, day trips"}]'::jsonb, 'Direct Shinkansen access from Tokyo', 'pending'),
  ('Appi Kogen', 'Japan', 'Iwate', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Family resort, longest season"}]'::jsonb, 'Family resort with long season', 'pending'),
  ('Zao Onsen', 'Japan', 'Yamagata', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Snow monsters, hot springs"}]'::jsonb, 'Famous snow monsters, hot springs', 'pending'),
  ('Kagura', 'Japan', 'Niigata', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Long season, backcountry access"}]'::jsonb, 'Long season into May', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- ASIA - KOREA, CHINA (~7 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Yongpyong', 'South Korea', 'Gangwon', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"2018 Olympics, largest Korea"}]'::jsonb, '2018 Olympics venue', 'pending'),
  ('High1', 'South Korea', 'Gangwon', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Casino resort, snow quality"}]'::jsonb, 'Casino resort with good snow', 'pending'),
  ('Phoenix Park', 'South Korea', 'Gangwon', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"2018 Olympics, family"}]'::jsonb, '2018 Olympics venue, family-friendly', 'pending'),
  ('Alpensia', 'South Korea', 'Gangwon', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"2018 Olympics, modern"}]'::jsonb, '2018 Olympics venue, modern facilities', 'pending'),
  ('Thaiwoo', 'China', 'Hebei', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"2022 Olympics, modern"}]'::jsonb, '2022 Olympics venue near Beijing', 'pending'),
  ('Wanlong', 'China', 'Hebei', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Beijing, modern"}]'::jsonb, 'Modern resort near Beijing', 'pending'),
  ('Yabuli', 'China', 'Heilongjiang', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Chinas oldest modern resort"}]'::jsonb, 'Chinas oldest modern ski resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- OCEANIA - AUSTRALIA & NEW ZEALAND (~8 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Perisher', 'Australia', 'New South Wales', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Largest in Southern Hemisphere"}]'::jsonb, 'Largest resort in Southern Hemisphere', 'pending'),
  ('Thredbo', 'Australia', 'New South Wales', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Longest runs in Australia"}]'::jsonb, 'Longest runs in Australia', 'pending'),
  ('Falls Creek', 'Australia', 'Victoria', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Alpine village, family"}]'::jsonb, 'Alpine village atmosphere', 'pending'),
  ('Mount Hotham', 'Australia', 'Victoria', 'manual_seed', 0.73, '[{"source":"manual","strength":0.7,"reasoning":"Highest village in Australia"}]'::jsonb, 'Highest alpine village', 'pending'),
  ('Queenstown', 'New Zealand', 'Otago', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Adventure capital, 4 resorts nearby"}]'::jsonb, 'Adventure capital with 4 nearby resorts', 'pending'),
  ('Coronet Peak', 'New Zealand', 'Otago', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Near Queenstown, night skiing"}]'::jsonb, 'Closest to Queenstown, night skiing', 'pending'),
  ('The Remarkables', 'New Zealand', 'Otago', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Near Queenstown, beginner friendly"}]'::jsonb, 'Beginner-friendly near Queenstown', 'pending'),
  ('Mount Hutt', 'New Zealand', 'Canterbury', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Near Christchurch, reliable snow"}]'::jsonb, 'Reliable snow near Christchurch', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- SOUTH AMERICA - CHILE & ARGENTINA (~18 resorts)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Valle Nevado', 'Chile', 'Santiago Region', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Largest Chile, near Santiago"}]'::jsonb, 'Largest Chilean resort near Santiago', 'pending'),
  ('Portillo', 'Chile', 'Valparaíso', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Legendary, all-inclusive"}]'::jsonb, 'Legendary all-inclusive experience', 'pending'),
  ('La Parva', 'Chile', 'Santiago Region', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Near Santiago, connects to Valle Nevado"}]'::jsonb, 'Near Santiago, connected to Valle Nevado', 'pending'),
  ('El Colorado', 'Chile', 'Santiago Region', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Closest to Santiago"}]'::jsonb, 'Closest resort to Santiago', 'pending'),
  ('Nevados de Chillán', 'Chile', 'Biobío', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Hot springs, active volcano"}]'::jsonb, 'Hot springs and active volcano', 'pending'),
  ('Corralco', 'Chile', 'Araucanía', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Volcano skiing, Araucaria forests"}]'::jsonb, 'Volcano skiing with ancient forests', 'pending'),
  ('Pucón', 'Chile', 'Araucanía', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Volcano, adventure town"}]'::jsonb, 'Villarrica volcano, adventure town', 'pending'),
  ('Antillanca', 'Chile', 'Los Lagos', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Remote, pristine"}]'::jsonb, 'Remote pristine resort', 'pending'),
  ('Cerro Catedral', 'Argentina', 'Río Negro', 'manual_seed', 0.85, '[{"source":"manual","strength":0.82,"reasoning":"Largest Argentina, Bariloche"}]'::jsonb, 'Largest in Argentina near Bariloche', 'pending'),
  ('Cerro Bayo', 'Argentina', 'Neuquén', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Family friendly, Villa La Angostura"}]'::jsonb, 'Family-friendly boutique resort', 'pending'),
  ('Chapelco', 'Argentina', 'Neuquén', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"San Martín de los Andes, trees"}]'::jsonb, 'Beautiful tree skiing', 'pending'),
  ('Las Leñas', 'Argentina', 'Mendoza', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Steep terrain, remote"}]'::jsonb, 'Steep terrain, remote location', 'pending'),
  ('Caviahue', 'Argentina', 'Neuquén', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Volcanic setting, hot springs"}]'::jsonb, 'Volcanic setting with hot springs', 'pending'),
  ('La Hoya', 'Argentina', 'Chubut', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Patagonia, dry snow"}]'::jsonb, 'Patagonian dry snow', 'pending'),
  ('Cerro Castor', 'Argentina', 'Tierra del Fuego', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Southernmost, long season"}]'::jsonb, 'Worlds southernmost ski resort', 'pending'),
  ('Penitentes', 'Argentina', 'Mendoza', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Aconcagua, value"}]'::jsonb, 'Near Aconcagua, budget option', 'pending'),
  ('Los Penitentes', 'Argentina', 'Mendoza', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Day trip from Mendoza"}]'::jsonb, 'Day trip from Mendoza', 'pending'),
  ('Piedras Blancas', 'Argentina', 'Chubut', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Near Esquel, family"}]'::jsonb, 'Small family resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- SUMMARY
-- =============================================================================
-- Total resorts seeded: ~250
-- - North America (USA): ~65
-- - North America (Canada): ~15
-- - Europe (Austria): ~25
-- - Europe (Switzerland): ~20
-- - Europe (France): ~25
-- - Europe (Italy): ~15
-- - Europe (Germany): ~6
-- - Europe (Scandinavia): ~12
-- - Europe (Other): ~12
-- - Asia (Japan): ~15
-- - Asia (Korea/China): ~7
-- - Oceania: ~8
-- - South America: ~18
