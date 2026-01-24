-- Delete duplicate Kitzbühel resort
-- Round 5.9.3: Two entries exist with different slugs due to umlaut encoding
-- Keep ASCII version (kitzbuhel) for URL compatibility, delete Unicode version (kitzbühel)
-- Applied: 2026-01-24

-- Delete the Unicode slug version
-- This cascades to related tables via foreign key constraints
DELETE FROM resorts
WHERE slug = 'kitzbühel' AND country = 'Austria';

-- Add comment to slug column as reminder for future
COMMENT ON COLUMN resorts.slug IS 'URL-safe slug - should use ASCII transliteration (e.g., kitzbuhel not kitzbühel)';
