-- Seed Discovery Candidates Batch 2 - Additional 300 Family-Friendly Ski Resorts
-- Round 5.4 - Expanding discovery pool to ~550 total resorts
--
-- This batch adds:
-- - More Japan resorts (family-friendly powder destinations)
-- - More Austrian villages (SkiWelt, Zillertal, smaller gems)
-- - More French resorts (Portes du Soleil, smaller Savoie)
-- - More Swiss family villages
-- - More Italian Dolomites
-- - US regional resorts (Midwest, Southeast, smaller mountains)
-- - More Canadian resorts
-- - More Scandinavian resorts
-- - Eastern European gems

-- =============================================================================
-- JAPAN - Additional Resorts (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Tomamu', 'Japan', 'Hokkaido', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Unkai terrace, great family facilities"}]'::jsonb, 'Sea of clouds terrace, excellent family amenities', 'pending'),
  ('Kiroro', 'Japan', 'Hokkaido', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Record snowfall, uncrowded"}]'::jsonb, 'Record snowfall, less crowded than Niseko', 'pending'),
  ('Sahoro', 'Japan', 'Hokkaido', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Club Med, family focused"}]'::jsonb, 'Club Med resort, family-focused all-inclusive', 'pending'),
  ('Asahidake', 'Japan', 'Hokkaido', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Highest in Hokkaido, powder"}]'::jsonb, 'Highest peak in Hokkaido, deep powder', 'pending'),
  ('Kamui Ski Links', 'Japan', 'Hokkaido', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Budget option, good powder"}]'::jsonb, 'Budget-friendly Hokkaido powder', 'pending'),
  ('Naeba', 'Japan', 'Niigata', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Longest gondola, easy Tokyo access"}]'::jsonb, 'Longest gondola in Japan, Shinkansen access', 'pending'),
  ('Gala Yuzawa', 'Japan', 'Niigata', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Direct Shinkansen, day trips"}]'::jsonb, 'Direct Shinkansen from Tokyo station', 'pending'),
  ('Kagura', 'Japan', 'Niigata', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Long season, backcountry"}]'::jsonb, 'Long season into May, backcountry access', 'pending'),
  ('Joetsu Kokusai', 'Japan', 'Niigata', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Naeba, good value"}]'::jsonb, 'Near Naeba, good value option', 'pending'),
  ('Tangram Ski Circus', 'Japan', 'Nagano', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Multiple resorts, family"}]'::jsonb, 'Multiple linked resorts, family-friendly', 'pending'),
  ('志賀高原 Shiga Kogen', 'Japan', 'Nagano', 'manual_seed', 0.82, '[{"source":"manual","strength":0.8,"reasoning":"Largest Japan, Olympics"}]'::jsonb, 'Largest ski area in Japan', 'pending'),
  ('Ryuoo', 'Japan', 'Nagano', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"SORA terrace, family"}]'::jsonb, 'SORA terrace views, family atmosphere', 'pending'),
  ('Togari Onsen', 'Japan', 'Nagano', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Hot springs, affordable"}]'::jsonb, 'Traditional onsen village, affordable', 'pending'),
  ('Ikenotaira', 'Japan', 'Nagano', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Beginner friendly"}]'::jsonb, 'Beginner-friendly, good for kids', 'pending'),
  ('Lotte Arai', 'Japan', 'Niigata', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Luxury resort, deep powder"}]'::jsonb, 'Luxury resort with deep powder', 'pending'),
  ('Tazawako', 'Japan', 'Akita', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Lake views, Tohoku powder"}]'::jsonb, 'Lake Tazawa views, Tohoku powder', 'pending'),
  ('Ani', 'Japan', 'Akita', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Deep snow, uncrowded"}]'::jsonb, 'Deep snow, very uncrowded', 'pending'),
  ('Grandeco', 'Japan', 'Fukushima', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Family resort, good facilities"}]'::jsonb, 'Family-focused with good facilities', 'pending'),
  ('Alts Bandai', 'Japan', 'Fukushima', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Large Tohoku resort"}]'::jsonb, 'Largest in Fukushima, family-friendly', 'pending'),
  ('Geto Kogen', 'Japan', 'Iwate', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Massive snowfall, uncrowded"}]'::jsonb, 'Massive snowfall, uncrowded gem', 'pending'),
  ('Hachimantai', 'Japan', 'Iwate', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Onsen, tree skiing"}]'::jsonb, 'Onsen resort with tree skiing', 'pending'),
  ('Sapporo Kokusai', 'Japan', 'Hokkaido', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Sapporo, day trip"}]'::jsonb, 'Easy day trip from Sapporo', 'pending'),
  ('Sapporo Teine', 'Japan', 'Hokkaido', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"1972 Olympics, city views"}]'::jsonb, '1972 Olympics venue, city views', 'pending'),
  ('Moiwa', 'Japan', 'Hokkaido', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Cat skiing, powder"}]'::jsonb, 'Cat skiing operation, deep powder', 'pending'),
  ('Kurodake', 'Japan', 'Hokkaido', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Backcountry, advanced"}]'::jsonb, 'Backcountry access, advanced terrain', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- AUSTRIA - Additional Resorts (~35 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- SkiWelt villages
  ('Brixen im Thale', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"SkiWelt, family friendly"}]'::jsonb, 'SkiWelt family village', 'pending'),
  ('Hopfgarten', 'Austria', 'Tyrol', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"SkiWelt, traditional"}]'::jsonb, 'Traditional SkiWelt village', 'pending'),
  ('Itter', 'Austria', 'Tyrol', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"SkiWelt, quiet"}]'::jsonb, 'Quiet SkiWelt option', 'pending'),
  ('Scheffau', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"SkiWelt, family"}]'::jsonb, 'Family-friendly SkiWelt village', 'pending'),
  ('Going', 'Austria', 'Tyrol', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"SkiWelt, romantic"}]'::jsonb, 'Romantic SkiWelt village', 'pending'),
  -- Zillertal valley
  ('Fügen-Spieljoch', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Zillertal, family gondola"}]'::jsonb, 'Zillertal family resort', 'pending'),
  ('Kaltenbach-Hochzillertal', 'Austria', 'Tyrol', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Zillertal, extensive terrain"}]'::jsonb, 'Extensive Zillertal terrain', 'pending'),
  ('Zell am Ziller', 'Austria', 'Tyrol', 'manual_seed', 0.73, '[{"source":"manual","strength":0.7,"reasoning":"Zillertal Arena access"}]'::jsonb, 'Zillertal Arena hub', 'pending'),
  ('Gerlos', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Zillertal Arena, snow sure"}]'::jsonb, 'Snow-sure Zillertal Arena', 'pending'),
  ('Tux-Finkenberg', 'Austria', 'Tyrol', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Hintertux access"}]'::jsonb, 'Hintertux glacier access', 'pending'),
  -- Ötztal
  ('Oetz', 'Austria', 'Tyrol', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Ötztal, family"}]'::jsonb, 'Family-friendly Ötztal', 'pending'),
  ('Hochoetz-Kühtai', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"High altitude, snow sure"}]'::jsonb, 'High altitude, snow reliable', 'pending'),
  -- Stubaital
  ('Schlick 2000', 'Austria', 'Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Stubaital, family"}]'::jsonb, 'Stubaital family resort', 'pending'),
  ('Serles', 'Austria', 'Tyrol', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Small, family"}]'::jsonb, 'Small family-friendly area', 'pending'),
  -- Salzburg region
  ('Zauchensee-Flachau', 'Austria', 'Salzburg', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Ski Amadé, snow sure"}]'::jsonb, 'Snow-sure Ski Amadé resort', 'pending'),
  ('Wagrain-Kleinarl', 'Austria', 'Salzburg', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Ski Amadé, family"}]'::jsonb, 'Family-friendly Ski Amadé', 'pending'),
  ('Filzmoos', 'Austria', 'Salzburg', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Beginner friendly, traditional"}]'::jsonb, 'Traditional beginner-friendly village', 'pending'),
  ('Radstadt-Altenmarkt', 'Austria', 'Salzburg', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Ski Amadé, value"}]'::jsonb, 'Good value Ski Amadé option', 'pending'),
  ('Großarl-Dorfgastein', 'Austria', 'Salzburg', 'manual_seed', 0.73, '[{"source":"manual","strength":0.7,"reasoning":"Ski Amadé, authentic"}]'::jsonb, 'Authentic Ski Amadé valley', 'pending'),
  ('Sportgastein', 'Austria', 'Salzburg', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"High altitude, snow"}]'::jsonb, 'High altitude snow guarantee', 'pending'),
  -- Carinthia
  ('Gerlitzen', 'Austria', 'Carinthia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Lake Ossiach views"}]'::jsonb, 'Lake Ossiach panorama', 'pending'),
  ('Katschberg', 'Austria', 'Carinthia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family village, snow"}]'::jsonb, 'Family village, reliable snow', 'pending'),
  ('Turracher Höhe', 'Austria', 'Carinthia', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"High plateau, snow"}]'::jsonb, 'High plateau, snow-sure', 'pending'),
  ('Goldeck', 'Austria', 'Carinthia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Lake views, sunny"}]'::jsonb, 'Lake Millstatt views, sunny', 'pending'),
  -- Vorarlberg
  ('Montafon', 'Austria', 'Vorarlberg', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Extensive area, authentic"}]'::jsonb, 'Extensive authentic valley', 'pending'),
  ('Silvretta Montafon', 'Austria', 'Vorarlberg', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Modern, extensive"}]'::jsonb, 'Modern extensive terrain', 'pending'),
  ('Gargellen', 'Austria', 'Vorarlberg', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Traditional, family"}]'::jsonb, 'Traditional family village', 'pending'),
  ('Kleinwalsertal', 'Austria', 'Vorarlberg', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"German enclave, family"}]'::jsonb, 'German-accessible family area', 'pending'),
  ('Sonnenkopf', 'Austria', 'Vorarlberg', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Klostertal, family"}]'::jsonb, 'Klostertal family resort', 'pending'),
  -- Styria
  ('Planai-Hochwurzen', 'Austria', 'Styria', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"World Cup, night skiing"}]'::jsonb, 'World Cup venue, night skiing', 'pending'),
  ('Reiteralm', 'Austria', 'Styria', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"4 Mountains, family"}]'::jsonb, '4 Mountains family option', 'pending'),
  ('Hauser Kaibling', 'Austria', 'Styria', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"4 Mountains, modern"}]'::jsonb, 'Modern 4 Mountains resort', 'pending'),
  ('Tauplitz', 'Austria', 'Styria', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"High plateau, traditional"}]'::jsonb, 'Traditional high plateau resort', 'pending'),
  ('Lachtal', 'Austria', 'Styria', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, affordable"}]'::jsonb, 'Affordable family option', 'pending'),
  ('Kreischberg', 'Austria', 'Styria', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Snowboard park, family"}]'::jsonb, 'Snowboard focus, family-friendly', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- FRANCE - Additional Resorts (~35 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- Portes du Soleil French side
  ('Châtel', 'France', 'Haute-Savoie', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Portes du Soleil, authentic"}]'::jsonb, 'Authentic Portes du Soleil village', 'pending'),
  ('Abondance', 'France', 'Haute-Savoie', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Portes du Soleil, quiet"}]'::jsonb, 'Quiet Portes du Soleil option', 'pending'),
  ('La Chapelle dAbondance', 'France', 'Haute-Savoie', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Traditional, family"}]'::jsonb, 'Traditional family village', 'pending'),
  ('Saint Jean dAulps', 'France', 'Haute-Savoie', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Portes du Soleil, value"}]'::jsonb, 'Value Portes du Soleil option', 'pending'),
  ('Montriond', 'France', 'Haute-Savoie', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Morzine, quiet"}]'::jsonb, 'Quiet alternative to Morzine', 'pending'),
  -- Grand Massif
  ('Morillon', 'France', 'Haute-Savoie', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Grand Massif, family"}]'::jsonb, 'Family-friendly Grand Massif', 'pending'),
  ('Les Carroz', 'France', 'Haute-Savoie', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Grand Massif, authentic"}]'::jsonb, 'Authentic Grand Massif village', 'pending'),
  ('Sixt-Fer-à-Cheval', 'France', 'Haute-Savoie', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Small, beautiful"}]'::jsonb, 'Beautiful small village', 'pending'),
  -- Évasion Mont-Blanc
  ('Combloux', 'France', 'Haute-Savoie', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Mont Blanc views, family"}]'::jsonb, 'Mont Blanc views, family village', 'pending'),
  ('Saint-Gervais', 'France', 'Haute-Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Spa town, Évasion MB"}]'::jsonb, 'Spa town with Évasion access', 'pending'),
  ('Les Contamines-Montjoie', 'France', 'Haute-Savoie', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Authentic, national park"}]'::jsonb, 'Authentic village near national park', 'pending'),
  -- Aravis
  ('Manigod', 'France', 'Haute-Savoie', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Traditional, family"}]'::jsonb, 'Traditional family village', 'pending'),
  ('Saint-Jean-de-Sixt', 'France', 'Haute-Savoie', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near La Clusaz, quiet"}]'::jsonb, 'Quiet La Clusaz alternative', 'pending'),
  -- Savoie
  ('Peisey-Vallandry', 'France', 'Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Paradiski, authentic"}]'::jsonb, 'Authentic Paradiski village', 'pending'),
  ('Champagny-en-Vanoise', 'France', 'Savoie', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Paradiski, peaceful"}]'::jsonb, 'Peaceful Paradiski option', 'pending'),
  ('Montchavin-Les Coches', 'France', 'Savoie', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Paradiski, family"}]'::jsonb, 'Family-oriented Paradiski', 'pending'),
  ('Brides-les-Bains', 'France', 'Savoie', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"3 Vallées, spa town"}]'::jsonb, '3 Vallées access, spa town', 'pending'),
  ('Saint-Martin-de-Belleville', 'France', 'Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"3 Vallées, authentic"}]'::jsonb, 'Authentic 3 Vallées village', 'pending'),
  ('Pralognan-la-Vanoise', 'France', 'Savoie', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Vanoise NP, traditional"}]'::jsonb, 'Traditional Vanoise gateway', 'pending'),
  ('Aussois', 'France', 'Savoie', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Sunny, family"}]'::jsonb, 'Sunny family resort', 'pending'),
  ('Bonneval-sur-Arc', 'France', 'Savoie', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Most beautiful village"}]'::jsonb, 'One of Frances most beautiful villages', 'pending'),
  ('Valmorel', 'France', 'Savoie', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Purpose-built, family"}]'::jsonb, 'Family-focused purpose-built', 'pending'),
  ('Doucy-Combelouvière', 'France', 'Savoie', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Valmorel access, quiet"}]'::jsonb, 'Quiet Valmorel access', 'pending'),
  -- Isère
  ('Villard-de-Lans', 'France', 'Isère', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Vercors, family"}]'::jsonb, 'Vercors family destination', 'pending'),
  ('Autrans-Méaudre', 'France', 'Isère', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Nordic focus, family"}]'::jsonb, 'Nordic skiing focus, family', 'pending'),
  ('Chamrousse', 'France', 'Isère', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"1968 Olympics, near Grenoble"}]'::jsonb, '1968 Olympics venue', 'pending'),
  ('Les 7 Laux', 'France', 'Isère', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Grenoble, value"}]'::jsonb, 'Value option near Grenoble', 'pending'),
  ('Vaujany', 'France', 'Isère', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Alpe dHuez access, quiet"}]'::jsonb, 'Quiet Alpe dHuez access', 'pending'),
  ('Oz-en-Oisans', 'France', 'Isère', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Alpe dHuez, family"}]'::jsonb, 'Family-friendly Alpe dHuez access', 'pending'),
  -- Southern Alps
  ('Vars', 'France', 'Hautes-Alpes', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Forêt Blanche, sunny"}]'::jsonb, 'Sunny Forêt Blanche resort', 'pending'),
  ('Les Orres', 'France', 'Hautes-Alpes', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Family, sunny"}]'::jsonb, 'Family-friendly sunny resort', 'pending'),
  ('Orcières-Merlette', 'France', 'Hautes-Alpes', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Sunny, family"}]'::jsonb, 'Sunny family destination', 'pending'),
  ('SuperDévoluy', 'France', 'Hautes-Alpes', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Family, value"}]'::jsonb, 'Value family resort', 'pending'),
  ('Isola 2000', 'France', 'Alpes-Maritimes', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Nice, sunny"}]'::jsonb, 'Near Nice, Mediterranean sun', 'pending'),
  ('Auron', 'France', 'Alpes-Maritimes', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Nice, traditional"}]'::jsonb, 'Traditional resort near Nice', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- SWITZERLAND - Additional Resorts (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Zinal', 'Switzerland', 'Valais', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Val dAnniviers, authentic"}]'::jsonb, 'Authentic Val dAnniviers village', 'pending'),
  ('Grimentz', 'Switzerland', 'Valais', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Val dAnniviers, charming"}]'::jsonb, 'Charming traditional village', 'pending'),
  ('St-Luc', 'Switzerland', 'Valais', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Val dAnniviers, sunny"}]'::jsonb, 'Sunny Val dAnniviers', 'pending'),
  ('Evolène', 'Switzerland', 'Valais', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Traditional, quiet"}]'::jsonb, 'Traditional quiet village', 'pending'),
  ('Ovronnaz', 'Switzerland', 'Valais', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Thermal baths, family"}]'::jsonb, 'Thermal baths, family resort', 'pending'),
  ('Anzère', 'Switzerland', 'Valais', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sunny, family"}]'::jsonb, 'Sunny family resort', 'pending'),
  ('Thyon-4 Vallées', 'Switzerland', 'Valais', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"4 Vallées, value"}]'::jsonb, 'Value 4 Vallées option', 'pending'),
  ('Veysonnaz', 'Switzerland', 'Valais', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"4 Vallées, family"}]'::jsonb, 'Family 4 Vallées access', 'pending'),
  ('Morgins', 'Switzerland', 'Valais', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Portes du Soleil, quiet"}]'::jsonb, 'Quiet Portes du Soleil Swiss', 'pending'),
  ('Torgon', 'Switzerland', 'Valais', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Portes du Soleil, small"}]'::jsonb, 'Small Portes du Soleil village', 'pending'),
  ('Savognin', 'Switzerland', 'Graubünden', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family, sunny"}]'::jsonb, 'Sunny family resort', 'pending'),
  ('Splügen', 'Switzerland', 'Graubünden', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Traditional, affordable"}]'::jsonb, 'Traditional affordable option', 'pending'),
  ('Vals', 'Switzerland', 'Graubünden', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Thermal baths, design"}]'::jsonb, 'Famous thermal baths', 'pending'),
  ('Scuol', 'Switzerland', 'Graubünden', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Engadin, spa, family"}]'::jsonb, 'Engadin spa resort', 'pending'),
  ('Samnaun', 'Switzerland', 'Graubünden', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Duty-free, links Ischgl"}]'::jsonb, 'Duty-free, Ischgl connection', 'pending'),
  ('Disentis', 'Switzerland', 'Graubünden', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Glacier skiing, family"}]'::jsonb, 'Glacier skiing, family village', 'pending'),
  ('Sedrun', 'Switzerland', 'Graubünden', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"SkiArena, snow sure"}]'::jsonb, 'SkiArena Andermatt-Sedrun', 'pending'),
  ('Brigels-Waltensburg-Andiast', 'Switzerland', 'Graubünden', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, quiet"}]'::jsonb, 'Quiet family area', 'pending'),
  ('Meiringen-Hasliberg', 'Switzerland', 'Bern', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family, authentic"}]'::jsonb, 'Authentic family resort', 'pending'),
  ('Lenk', 'Switzerland', 'Bern', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Adelboden link, family"}]'::jsonb, 'Linked to Adelboden, family', 'pending'),
  ('Château-dOex', 'Switzerland', 'Vaud', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Hot air balloons, family"}]'::jsonb, 'Hot air balloon festival town', 'pending'),
  ('Les Paccots', 'Switzerland', 'Fribourg', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Near Fribourg, small"}]'::jsonb, 'Small resort near Fribourg', 'pending'),
  ('Schwarzsee', 'Switzerland', 'Fribourg', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Lake views, family"}]'::jsonb, 'Lake views, family atmosphere', 'pending'),
  ('Hoch-Ybrig', 'Switzerland', 'Schwyz', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Zurich, family"}]'::jsonb, 'Near Zurich, family resort', 'pending'),
  ('Stoos', 'Switzerland', 'Schwyz', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Steepest funicular, car-free"}]'::jsonb, 'Worlds steepest funicular, car-free', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- ITALY - Additional Resorts (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- More Dolomites
  ('Moena-Alpe Lusia', 'Italy', 'Trentino', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Dolomiti Superski, family"}]'::jsonb, 'Family-friendly Dolomiti Superski', 'pending'),
  ('Pozza di Fassa', 'Italy', 'Trentino', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Val di Fassa, family"}]'::jsonb, 'Val di Fassa family village', 'pending'),
  ('Vigo di Fassa', 'Italy', 'Trentino', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Catinaccio views"}]'::jsonb, 'Catinaccio Rosengarten views', 'pending'),
  ('Campitello di Fassa', 'Italy', 'Trentino', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Sella Ronda access"}]'::jsonb, 'Sella Ronda starting point', 'pending'),
  ('Alpe di Siusi', 'Italy', 'South Tyrol', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Europes largest alpine meadow"}]'::jsonb, 'Europes largest high-altitude meadow', 'pending'),
  ('Santa Cristina', 'Italy', 'South Tyrol', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Val Gardena, charming"}]'::jsonb, 'Charming Val Gardena village', 'pending'),
  ('Corvara', 'Italy', 'South Tyrol', 'manual_seed', 0.76, '[{"source":"manual","strength":0.74,"reasoning":"Alta Badia, Sella Ronda"}]'::jsonb, 'Alta Badia hub, Sella Ronda', 'pending'),
  ('Colfosco', 'Italy', 'South Tyrol', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Alta Badia, quiet"}]'::jsonb, 'Quiet Alta Badia option', 'pending'),
  ('La Villa', 'Italy', 'South Tyrol', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Alta Badia, World Cup"}]'::jsonb, 'World Cup venue in Alta Badia', 'pending'),
  ('San Cassiano', 'Italy', 'South Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Alta Badia, gourmet"}]'::jsonb, 'Gourmet destination Alta Badia', 'pending'),
  ('Plan de Corones', 'Italy', 'South Tyrol', 'manual_seed', 0.80, '[{"source":"manual","strength":0.78,"reasoning":"Modern, 360 views"}]'::jsonb, 'Modern resort, 360-degree views', 'pending'),
  ('Brunico', 'Italy', 'South Tyrol', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Town base, Kronplatz"}]'::jsonb, 'Town base for Kronplatz', 'pending'),
  ('San Vigilio di Marebbe', 'Italy', 'South Tyrol', 'manual_seed', 0.74, '[{"source":"manual","strength":0.72,"reasoning":"Kronplatz, authentic"}]'::jsonb, 'Authentic Kronplatz village', 'pending'),
  -- Lombardy/Piedmont
  ('Santa Caterina Valfurva', 'Italy', 'Lombardy', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Bormio, quiet"}]'::jsonb, 'Quiet alternative to Bormio', 'pending'),
  ('Madesimo', 'Italy', 'Lombardy', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family, snow sure"}]'::jsonb, 'Family-friendly, reliable snow', 'pending'),
  ('Chiesa in Valmalenco', 'Italy', 'Lombardy', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Sondrio, family"}]'::jsonb, 'Family resort near Sondrio', 'pending'),
  ('Foppolo', 'Italy', 'Lombardy', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Bergamo, value"}]'::jsonb, 'Value option near Bergamo', 'pending'),
  ('Bardonecchia', 'Italy', 'Piedmont', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"2006 Olympics, affordable"}]'::jsonb, '2006 Olympics venue, affordable', 'pending'),
  ('Sauze dOulx', 'Italy', 'Piedmont', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Via Lattea, nightlife"}]'::jsonb, 'Via Lattea with lively nightlife', 'pending'),
  ('Pragelato', 'Italy', 'Piedmont', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Via Lattea, quiet"}]'::jsonb, 'Quiet Via Lattea village', 'pending'),
  ('Claviere', 'Italy', 'Piedmont', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Via Lattea, French border"}]'::jsonb, 'Via Lattea at French border', 'pending'),
  -- Aosta Valley
  ('Champoluc', 'Italy', 'Aosta Valley', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Monterosa Ski, authentic"}]'::jsonb, 'Authentic Monterosa village', 'pending'),
  ('Gressoney', 'Italy', 'Aosta Valley', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Monterosa Ski, Walser"}]'::jsonb, 'Walser culture, Monterosa Ski', 'pending'),
  ('Alagna Valsesia', 'Italy', 'Piedmont', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Monterosa, freeride"}]'::jsonb, 'Freeride paradise, Monterosa', 'pending'),
  ('Pila', 'Italy', 'Aosta Valley', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Near Aosta, family"}]'::jsonb, 'Family resort above Aosta', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- USA - Additional Resorts (~65 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- More Colorado
  ('Monarch Mountain', 'United States', 'Colorado', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Uncrowded, family"}]'::jsonb, 'Uncrowded family favorite', 'pending'),
  ('Wolf Creek', 'United States', 'Colorado', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Most snow in Colorado"}]'::jsonb, 'Most snow in Colorado', 'pending'),
  ('Sunlight Mountain', 'United States', 'Colorado', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Glenwood, family"}]'::jsonb, 'Family resort near Glenwood Springs', 'pending'),
  ('Powderhorn', 'United States', 'Colorado', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Grand Mesa, value"}]'::jsonb, 'Grand Mesa value resort', 'pending'),
  ('Echo Mountain', 'United States', 'Colorado', 'manual_seed', 0.58, '[{"source":"manual","strength":0.55,"reasoning":"Near Denver, night skiing"}]'::jsonb, 'Night skiing near Denver', 'pending'),
  -- More California
  ('Dodge Ridge', 'United States', 'California', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, affordable"}]'::jsonb, 'Affordable family option', 'pending'),
  ('Bear Valley', 'United States', 'California', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Uncrowded, family"}]'::jsonb, 'Uncrowded family resort', 'pending'),
  ('China Peak', 'United States', 'California', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Central CA, family"}]'::jsonb, 'Central California family resort', 'pending'),
  ('Tahoe Donner', 'United States', 'California', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Beginner focused"}]'::jsonb, 'Beginner-focused Tahoe', 'pending'),
  ('Boreal', 'United States', 'California', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"I-80 access, night skiing"}]'::jsonb, 'Easy I-80 access, night skiing', 'pending'),
  ('Soda Springs', 'United States', 'California', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Tubing, kids"}]'::jsonb, 'Tubing focus, great for little kids', 'pending'),
  ('Homewood', 'United States', 'California', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Lake Tahoe views, family"}]'::jsonb, 'Lake Tahoe views, family vibe', 'pending'),
  ('Diamond Peak', 'United States', 'Nevada', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Family, lake views"}]'::jsonb, 'Family resort with lake views', 'pending'),
  ('Mt Rose', 'United States', 'Nevada', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Reno, high elevation"}]'::jsonb, 'Highest base elevation at Tahoe', 'pending'),
  -- Pacific Northwest
  ('White Pass', 'United States', 'Washington', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Family, affordable"}]'::jsonb, 'Affordable family resort', 'pending'),
  ('Mission Ridge', 'United States', 'Washington', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sunny, dry snow"}]'::jsonb, 'Sunny with dry snow', 'pending'),
  ('Snoqualmie Pass', 'United States', 'Washington', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Seattle day trip, night skiing"}]'::jsonb, 'Seattle day trip, night skiing', 'pending'),
  ('Mt Baker', 'United States', 'Washington', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"World record snowfall"}]'::jsonb, 'World record snowfall', 'pending'),
  ('49 Degrees North', 'United States', 'Washington', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, affordable"}]'::jsonb, 'Family-friendly affordable', 'pending'),
  ('Mt Ashland', 'United States', 'Oregon', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Southern Oregon, value"}]'::jsonb, 'Southern Oregon value', 'pending'),
  ('Willamette Pass', 'United States', 'Oregon', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, affordable"}]'::jsonb, 'Affordable family option', 'pending'),
  ('Anthony Lakes', 'United States', 'Oregon', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Remote, powder"}]'::jsonb, 'Remote powder destination', 'pending'),
  -- Midwest
  ('Lutsen Mountains', 'United States', 'Minnesota', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Midwest largest, Lake Superior"}]'::jsonb, 'Midwest largest, Lake Superior views', 'pending'),
  ('Spirit Mountain', 'United States', 'Minnesota', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Duluth, family"}]'::jsonb, 'Duluth family resort', 'pending'),
  ('Giants Ridge', 'United States', 'Minnesota', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Iron Range, family"}]'::jsonb, 'Iron Range family destination', 'pending'),
  ('Cascade Mountain', 'United States', 'Wisconsin', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Wisconsin Dells, family"}]'::jsonb, 'Near Wisconsin Dells', 'pending'),
  ('Devils Head', 'United States', 'Wisconsin', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Family, terrain park"}]'::jsonb, 'Family with terrain park', 'pending'),
  ('Crystal Mountain', 'United States', 'Michigan', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Michigan largest, spa"}]'::jsonb, 'Michigan largest with spa', 'pending'),
  ('Nubs Nob', 'United States', 'Michigan', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Family favorite, natural snow"}]'::jsonb, 'Family favorite, good natural snow', 'pending'),
  ('Shanty Creek', 'United States', 'Michigan', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Multiple peaks, family"}]'::jsonb, 'Multiple peaks, family resort', 'pending'),
  ('Caberfae Peaks', 'United States', 'Michigan', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Family, value"}]'::jsonb, 'Family value resort', 'pending'),
  ('Mad River Mountain', 'United States', 'Ohio', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Ohio largest"}]'::jsonb, 'Ohio largest ski area', 'pending'),
  ('Perfect North Slopes', 'United States', 'Indiana', 'manual_seed', 0.58, '[{"source":"manual","strength":0.55,"reasoning":"Near Cincinnati, family"}]'::jsonb, 'Family resort near Cincinnati', 'pending'),
  ('Paoli Peaks', 'United States', 'Indiana', 'manual_seed', 0.55, '[{"source":"manual","strength":0.52,"reasoning":"Southern Indiana, family"}]'::jsonb, 'Southern Indiana family option', 'pending'),
  -- Southeast
  ('Snowshoe Mountain', 'United States', 'West Virginia', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Southeast largest, village"}]'::jsonb, 'Southeast largest, ski village', 'pending'),
  ('Winterplace', 'United States', 'West Virginia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, accessible"}]'::jsonb, 'Family-friendly, accessible', 'pending'),
  ('Canaan Valley', 'United States', 'West Virginia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"State park, family"}]'::jsonb, 'State park resort, family', 'pending'),
  ('Timberline Mountain', 'United States', 'West Virginia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Tucker County, family"}]'::jsonb, 'Tucker County family resort', 'pending'),
  ('Wisp', 'United States', 'Maryland', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Deep Creek Lake, family"}]'::jsonb, 'Deep Creek Lake, family resort', 'pending'),
  ('Wintergreen', 'United States', 'Virginia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Blue Ridge, family"}]'::jsonb, 'Blue Ridge family resort', 'pending'),
  ('Massanutten', 'United States', 'Virginia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Indoor waterpark, family"}]'::jsonb, 'Indoor waterpark combo', 'pending'),
  ('Bryce Resort', 'United States', 'Virginia', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Family, affordable"}]'::jsonb, 'Affordable family option', 'pending'),
  ('Beech Mountain', 'United States', 'North Carolina', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Highest SE elevation"}]'::jsonb, 'Highest elevation in Southeast', 'pending'),
  ('Sugar Mountain', 'United States', 'North Carolina', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"SE largest, family"}]'::jsonb, 'Largest in NC, family-friendly', 'pending'),
  ('Appalachian Ski Mountain', 'United States', 'North Carolina', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Family, accessible"}]'::jsonb, 'Family-friendly, accessible', 'pending'),
  ('Cataloochee', 'United States', 'North Carolina', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Asheville, family"}]'::jsonb, 'Near Asheville, family resort', 'pending'),
  ('Ober Gatlinburg', 'United States', 'Tennessee', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Smoky Mtns, tramway"}]'::jsonb, 'Smoky Mountains, aerial tramway', 'pending'),
  -- More Northeast
  ('Wildcat Mountain', 'United States', 'New Hampshire', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Mt Washington views"}]'::jsonb, 'Mt Washington views, challenging', 'pending'),
  ('Attitash', 'United States', 'New Hampshire', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Two peaks, family"}]'::jsonb, 'Two peaks, family resort', 'pending'),
  ('Cranmore', 'United States', 'New Hampshire', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"North Conway, family"}]'::jsonb, 'North Conway, family mountain', 'pending'),
  ('Gunstock', 'United States', 'New Hampshire', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Lake views, family"}]'::jsonb, 'Lake Winnipesaukee views', 'pending'),
  ('Ragged Mountain', 'United States', 'New Hampshire', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Family, value"}]'::jsonb, 'Family value resort', 'pending'),
  ('Pats Peak', 'United States', 'New Hampshire', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Near Boston, family"}]'::jsonb, 'Near Boston, family resort', 'pending'),
  ('Black Mountain', 'United States', 'New Hampshire', 'manual_seed', 0.58, '[{"source":"manual","strength":0.55,"reasoning":"Jackson, family"}]'::jsonb, 'Jackson village, family focus', 'pending'),
  ('Mad River Glen', 'United States', 'Vermont', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Cooperative, natural snow"}]'::jsonb, 'Cooperative owned, natural snow', 'pending'),
  ('Jay Peak', 'United States', 'Vermont', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Most snow in East, waterpark"}]'::jsonb, 'Most snow in East, indoor waterpark', 'pending'),
  ('Burke Mountain', 'United States', 'Vermont', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Academy, uncrowded"}]'::jsonb, 'Ski academy, uncrowded', 'pending'),
  ('Bromley', 'United States', 'Vermont', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"South-facing, family"}]'::jsonb, 'South-facing, sunny family resort', 'pending'),
  ('Bolton Valley', 'United States', 'Vermont', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Burlington, family"}]'::jsonb, 'Near Burlington, family focused', 'pending'),
  ('Pico Mountain', 'United States', 'Vermont', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Near Killington, family"}]'::jsonb, 'Killingtons quieter neighbor', 'pending'),
  ('Magic Mountain', 'United States', 'Vermont', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Classic Vermont"}]'::jsonb, 'Classic Vermont experience', 'pending'),
  ('Windham Mountain', 'United States', 'New York', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Catskills, family"}]'::jsonb, 'Catskills family resort', 'pending'),
  ('Belleayre', 'United States', 'New York', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"State-run, value"}]'::jsonb, 'State-run Catskills resort', 'pending'),
  ('Bristol Mountain', 'United States', 'New York', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Finger Lakes, family"}]'::jsonb, 'Finger Lakes family resort', 'pending'),
  ('Greek Peak', 'United States', 'New York', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Central NY, waterpark"}]'::jsonb, 'Central NY with waterpark', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- CANADA - Additional Resorts (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  ('Red Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.78, '[{"source":"manual","strength":0.75,"reasoning":"Powder, authentic"}]'::jsonb, 'Legendary powder, authentic town', 'pending'),
  ('Apex Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Family, Okanagan"}]'::jsonb, 'Family resort in Okanagan', 'pending'),
  ('Panorama', 'Canada', 'British Columbia', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Village, heli-skiing"}]'::jsonb, 'Village resort with heli-skiing', 'pending'),
  ('Kimberley', 'Canada', 'British Columbia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family, Bavarian theme"}]'::jsonb, 'Bavarian themed family resort', 'pending'),
  ('Fairmont', 'Canada', 'British Columbia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Hot springs, family"}]'::jsonb, 'Hot springs resort combo', 'pending'),
  ('Whitewater', 'Canada', 'British Columbia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Powder, Nelson"}]'::jsonb, 'Nelson powder resort', 'pending'),
  ('Sasquatch Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Vancouver, family"}]'::jsonb, 'Near Vancouver, family', 'pending'),
  ('Mount Washington', 'Canada', 'British Columbia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Vancouver Island, family"}]'::jsonb, 'Vancouver Island largest', 'pending'),
  ('Cypress Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"2010 Olympics, Vancouver"}]'::jsonb, '2010 Olympics freestyle venue', 'pending'),
  ('Grouse Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Vancouver city views"}]'::jsonb, 'Vancouver skyline views', 'pending'),
  ('Seymour Mountain', 'Canada', 'British Columbia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Vancouver, night skiing"}]'::jsonb, 'Vancouver night skiing', 'pending'),
  ('Nakiska', 'Canada', 'Alberta', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"1988 Olympics, Calgary"}]'::jsonb, '1988 Olympics, near Calgary', 'pending'),
  ('Castle Mountain', 'Canada', 'Alberta', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Powder, uncrowded"}]'::jsonb, 'Powder paradise, uncrowded', 'pending'),
  ('Canyon Ski Resort', 'Canada', 'Alberta', 'manual_seed', 0.60, '[{"source":"manual","strength":0.58,"reasoning":"Near Edmonton, family"}]'::jsonb, 'Edmonton area family resort', 'pending'),
  ('Rabbit Hill', 'Canada', 'Alberta', 'manual_seed', 0.55, '[{"source":"manual","strength":0.52,"reasoning":"Edmonton, learning"}]'::jsonb, 'Edmonton learning hill', 'pending'),
  ('Stoneham', 'Canada', 'Quebec', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Quebec City, night skiing"}]'::jsonb, 'Quebec City, excellent night skiing', 'pending'),
  ('Mont Orford', 'Canada', 'Quebec', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Eastern Townships, family"}]'::jsonb, 'Eastern Townships family resort', 'pending'),
  ('Bromont', 'Canada', 'Quebec', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Night skiing, waterpark"}]'::jsonb, 'Night skiing and waterpark', 'pending'),
  ('Mont Sutton', 'Canada', 'Quebec', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Glades, natural snow"}]'::jsonb, 'Famous glades, natural snow', 'pending'),
  ('Owl Head', 'Canada', 'Quebec', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Lake views, family"}]'::jsonb, 'Lake Memphremagog views', 'pending'),
  ('Mont Blanc', 'Canada', 'Quebec', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Laurentians, family"}]'::jsonb, 'Laurentians family resort', 'pending'),
  ('Tremblant Nord', 'Canada', 'Quebec', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Tremblant area, value"}]'::jsonb, 'Tremblant area value option', 'pending'),
  ('Searchmont', 'Canada', 'Ontario', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Near Sault, Lake Superior"}]'::jsonb, 'Lake Superior snow belt', 'pending'),
  ('Calabogie Peaks', 'Canada', 'Ontario', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Ottawa area, family"}]'::jsonb, 'Ottawa area family resort', 'pending'),
  ('Mount St Louis Moonstone', 'Canada', 'Ontario', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Toronto, family"}]'::jsonb, 'Toronto area family favorite', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- SCANDINAVIA - Additional Resorts (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- Sweden
  ('Kläppen', 'Sweden', 'Dalarna', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sälen area, family"}]'::jsonb, 'Sälen area family resort', 'pending'),
  ('Tandådalen', 'Sweden', 'Dalarna', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sälen, beginner"}]'::jsonb, 'Sälen beginner-friendly', 'pending'),
  ('Hundfjället', 'Sweden', 'Dalarna', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Sälen, family"}]'::jsonb, 'Sälen family mountain', 'pending'),
  ('Idre Fjäll', 'Sweden', 'Dalarna', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Family, 41 slopes"}]'::jsonb, 'Family-focused with 41 slopes', 'pending'),
  ('Romme Alpin', 'Sweden', 'Dalarna', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Stockholm, family"}]'::jsonb, 'Accessible from Stockholm', 'pending'),
  ('Branäs', 'Sweden', 'Värmland', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Family resort, pools"}]'::jsonb, 'Family resort with pools', 'pending'),
  ('Riksgränsen', 'Sweden', 'Norrbotten', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Midnight sun skiing"}]'::jsonb, 'Midnight sun skiing', 'pending'),
  ('Björkliden', 'Sweden', 'Norrbotten', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Arctic, Northern Lights"}]'::jsonb, 'Arctic skiing, Northern Lights', 'pending'),
  -- Norway
  ('Kvitfjell', 'Norway', 'Innlandet', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"1994 Olympics, family"}]'::jsonb, '1994 Olympics downhill venue', 'pending'),
  ('Hafjell', 'Norway', 'Innlandet', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"1994 Olympics, family park"}]'::jsonb, '1994 Olympics, family terrain park', 'pending'),
  ('Beitostølen', 'Norway', 'Innlandet', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Royal family, family"}]'::jsonb, 'Royal family favorite', 'pending'),
  ('Oppdal', 'Norway', 'Trøndelag', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Four mountains, family"}]'::jsonb, 'Four mountains in one pass', 'pending'),
  ('Voss', 'Norway', 'Vestland', 'manual_seed', 0.75, '[{"source":"manual","strength":0.72,"reasoning":"Adventure capital"}]'::jsonb, 'Norway adventure capital', 'pending'),
  ('Hovden', 'Norway', 'Agder', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Southern Norway, family"}]'::jsonb, 'Southern Norway largest', 'pending'),
  ('Norefjell', 'Norway', 'Viken', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Oslo, family"}]'::jsonb, 'Near Oslo, family resort', 'pending'),
  ('Kongsberg', 'Norway', 'Viken', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Oslo day trip, family"}]'::jsonb, 'Oslo day trip, family', 'pending'),
  -- Finland
  ('Pyhä', 'Finland', 'Lapland', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"National park, family"}]'::jsonb, 'National park setting, family', 'pending'),
  ('Luosto', 'Finland', 'Lapland', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Aurora, family"}]'::jsonb, 'Aurora viewing, family resort', 'pending'),
  ('Pallas', 'Finland', 'Lapland', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"National park, quiet"}]'::jsonb, 'National park, quiet', 'pending'),
  ('Iso-Syöte', 'Finland', 'Oulu', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Southernmost fell, family"}]'::jsonb, 'Southernmost fell in Finland', 'pending'),
  ('Tahko', 'Finland', 'Savonia', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Lakeland, family"}]'::jsonb, 'Finnish Lakeland largest', 'pending'),
  ('Himos', 'Finland', 'Central Finland', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Central, family"}]'::jsonb, 'Central Finland family resort', 'pending'),
  ('Messilä', 'Finland', 'Päijät-Häme', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Near Helsinki, family"}]'::jsonb, 'Closest major resort to Helsinki', 'pending'),
  ('Sappee', 'Finland', 'Pirkanmaa', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Family, Tampere"}]'::jsonb, 'Near Tampere, family', 'pending'),
  ('Vuokatti', 'Finland', 'Kainuu', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Sport center, family"}]'::jsonb, 'Sports center, family resort', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- EASTERN EUROPE & OTHER (~25 more)
-- =============================================================================

INSERT INTO discovery_candidates (resort_name, country, region, discovery_source, opportunity_score, signals, reasoning, status)
VALUES
  -- Romania
  ('Poiana Brașov', 'Romania', 'Transylvania', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Romania largest, Dracula country"}]'::jsonb, 'Romania largest, Transylvania', 'pending'),
  ('Sinaia', 'Romania', 'Prahova Valley', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Pearl of Carpathians"}]'::jsonb, 'Pearl of Carpathians', 'pending'),
  ('Straja', 'Romania', 'Hunedoara', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Value, developing"}]'::jsonb, 'Value developing resort', 'pending'),
  -- More Bulgaria
  ('Pamporovo', 'Bulgaria', 'Rhodope', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Sunny, beginner"}]'::jsonb, 'Sunny beginner-friendly', 'pending'),
  ('Vitosha', 'Bulgaria', 'Sofia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Sofia day trip"}]'::jsonb, 'Sofia city skiing', 'pending'),
  -- More Czech
  ('Pec pod Sněžkou', 'Czech Republic', 'Hradec Králové', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Highest Czech peak"}]'::jsonb, 'Below highest Czech peak', 'pending'),
  ('Harrachov', 'Czech Republic', 'Liberec', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Ski jumping, family"}]'::jsonb, 'Ski jumping tradition, family', 'pending'),
  ('Rokytnice nad Jizerou', 'Czech Republic', 'Liberec', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Giant Mtns, family"}]'::jsonb, 'Giant Mountains family resort', 'pending'),
  -- More Poland
  ('Białka Tatrzańska', 'Poland', 'Lesser Poland', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Tatra views, modern"}]'::jsonb, 'Modern with Tatra views', 'pending'),
  ('Szczyrk', 'Poland', 'Silesia', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Beskids, family"}]'::jsonb, 'Beskids family resort', 'pending'),
  ('Karpacz', 'Poland', 'Lower Silesia', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Giant Mtns, family"}]'::jsonb, 'Giant Mountains Polish side', 'pending'),
  -- More Slovenia
  ('Vogel', 'Slovenia', 'Upper Carniola', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Lake Bohinj views"}]'::jsonb, 'Lake Bohinj views, Triglav NP', 'pending'),
  ('Krvavec', 'Slovenia', 'Upper Carniola', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Near Ljubljana, family"}]'::jsonb, 'Near Ljubljana, family', 'pending'),
  ('Cerkno', 'Slovenia', 'Goriška', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Family, value"}]'::jsonb, 'Family value resort', 'pending'),
  -- Georgia
  ('Bakuriani', 'Georgia', 'Samtskhe-Javakheti', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Soviet-era resort, developing"}]'::jsonb, 'Developing Georgian resort', 'pending'),
  -- China additions
  ('Beidahu', 'China', 'Jilin', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Northeast China, powder"}]'::jsonb, 'Northeast China powder', 'pending'),
  ('Yabuli Sun Mountain', 'China', 'Heilongjiang', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Club Med, family"}]'::jsonb, 'Club Med resort', 'pending'),
  ('Songhua Lake', 'China', 'Jilin', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Modern, family"}]'::jsonb, 'Modern family resort', 'pending'),
  ('Changbaishan', 'China', 'Jilin', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"Volcanic, developing"}]'::jsonb, 'Volcanic setting, developing', 'pending'),
  -- South America additions
  ('El Colorado-Farellones', 'Chile', 'Santiago Region', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Santiago day trip, linked"}]'::jsonb, 'Santiago day trip, linked areas', 'pending'),
  ('Ski Arpa', 'Chile', 'Valparaíso', 'manual_seed', 0.65, '[{"source":"manual","strength":0.62,"reasoning":"Cat skiing, adventure"}]'::jsonb, 'Cat skiing adventure', 'pending'),
  ('Termas de Chillán', 'Chile', 'Biobío', 'manual_seed', 0.72, '[{"source":"manual","strength":0.7,"reasoning":"Hot springs, volcano"}]'::jsonb, 'Hot springs and volcano skiing', 'pending'),
  ('La Hoya', 'Argentina', 'Chubut', 'manual_seed', 0.68, '[{"source":"manual","strength":0.65,"reasoning":"Esquel, dry snow"}]'::jsonb, 'Esquel dry snow', 'pending'),
  ('Perito Moreno', 'Argentina', 'Río Negro', 'manual_seed', 0.62, '[{"source":"manual","strength":0.6,"reasoning":"Patagonia, remote"}]'::jsonb, 'Remote Patagonia', 'pending'),
  ('Ushuaia', 'Argentina', 'Tierra del Fuego', 'manual_seed', 0.70, '[{"source":"manual","strength":0.68,"reasoning":"End of world, glacier"}]'::jsonb, 'End of the world skiing', 'pending')
ON CONFLICT (resort_name, country) DO NOTHING;

-- =============================================================================
-- SUMMARY BATCH 2
-- =============================================================================
-- Additional resorts seeded: ~300
-- - Japan: +25
-- - Austria: +35
-- - France: +35
-- - Switzerland: +25
-- - Italy: +25
-- - USA: +65
-- - Canada: +25
-- - Scandinavia: +25
-- - Eastern Europe & Other: +25
--
-- Total with Batch 1: ~550 resorts
