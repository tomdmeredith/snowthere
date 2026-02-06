-- Migration 042: Add flight search URL support for airport entities
-- Part of Round 20: Content Quality & Linking Overhaul

-- Add flight search URL to entity link cache
ALTER TABLE entity_link_cache ADD COLUMN IF NOT EXISTS flight_search_url TEXT;

-- Add flight search URL and IATA code to resort entities
ALTER TABLE resort_entities ADD COLUMN IF NOT EXISTS flight_search_url TEXT;
ALTER TABLE resort_entities ADD COLUMN IF NOT EXISTS iata_code TEXT;
