-- Fix non-ASCII characters in resort slugs for URL safety
-- Unicode characters in URL path segments cause encoding/normalization issues
-- across browsers, CDNs, and edge runtimes
--
-- Applied manually via Supabase SQL Editor on 2026-01-30
-- Two Kitzbühel records existed:
--   4ce9f3b3 (slug: kitzbuhel, status: archived, created 2026-01-21)
--   e32d3ec3 (slug: kitzbühel, status: published, created 2026-01-24)

BEGIN;

-- Delete all child records for the archived duplicate
DELETE FROM resort_family_metrics WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM resort_content WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM resort_costs WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM ski_quality_calendar WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM resort_passes WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM resort_images WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM resort_links WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM content_queue WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';
DELETE FROM agent_audit_log WHERE resort_id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';

-- Delete the archived resort record
DELETE FROM resorts WHERE id = '4ce9f3b3-85eb-4472-a58d-de12f5510839';

-- Update published resort slug from Unicode to ASCII
UPDATE resorts SET slug = 'kitzbuhel' WHERE id = 'e32d3ec3-f500-402b-9500-2e62f984678c';

COMMIT;
