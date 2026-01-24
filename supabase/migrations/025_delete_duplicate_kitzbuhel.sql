-- Delete duplicate Kitzbühel resort
-- Round 5.9.3: Two entries exist with different slugs due to umlaut encoding
-- Keep ASCII version (kitzbuhel) for URL compatibility, delete Unicode version (kitzbühel)

-- First, identify and log the duplicates
DO $$
DECLARE
    ascii_id UUID;
    unicode_id UUID;
    ascii_score INTEGER;
    unicode_score INTEGER;
BEGIN
    -- Find the ASCII slug version
    SELECT r.id, fm.family_overall_score INTO ascii_id, ascii_score
    FROM resorts r
    LEFT JOIN resort_family_metrics fm ON fm.resort_id = r.id
    WHERE r.slug = 'kitzbuhel' AND r.country = 'Austria';

    -- Find the Unicode slug version
    SELECT r.id, fm.family_overall_score INTO unicode_id, unicode_score
    FROM resorts r
    LEFT JOIN resort_family_metrics fm ON fm.resort_id = r.id
    WHERE r.slug = 'kitzbühel' AND r.country = 'Austria';

    IF ascii_id IS NOT NULL AND unicode_id IS NOT NULL THEN
        RAISE NOTICE 'Found duplicate Kitzbühel resorts:';
        RAISE NOTICE '  ASCII slug (kitzbuhel): id=%, score=%', ascii_id, ascii_score;
        RAISE NOTICE '  Unicode slug (kitzbühel): id=%, score=%', unicode_id, unicode_score;
    ELSIF unicode_id IS NOT NULL THEN
        RAISE NOTICE 'Only Unicode version found, will delete it';
    ELSE
        RAISE NOTICE 'No duplicate Kitzbühel found';
    END IF;
END $$;

-- Delete the Unicode slug version if it exists
-- This cascades to related tables via foreign key constraints
DELETE FROM resorts
WHERE slug = 'kitzbühel' AND country = 'Austria';

-- Also clean up any discovery candidate duplicates
DELETE FROM discovery_candidates
WHERE LOWER(name) LIKE '%kitzbühel%'
  AND country = 'Austria';

-- Add a check constraint or trigger to prevent future umlaut slugs
-- (For now, just add a comment as a reminder)
COMMENT ON COLUMN resorts.slug IS 'URL-safe slug - should use ASCII transliteration (e.g., kitzbuhel not kitzbühel)';
