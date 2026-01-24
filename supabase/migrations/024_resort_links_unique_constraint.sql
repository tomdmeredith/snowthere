-- Add unique constraint to resort_links for upsert support
-- Round 5.9.2: Fix "no unique or exclusion constraint matching the ON CONFLICT specification"
-- The pipeline runner uses ON CONFLICT(resort_id, url) but the table lacks this constraint

-- Add unique constraint on resort_id + url for upsert operations
ALTER TABLE resort_links
ADD CONSTRAINT uq_resort_links_resort_url UNIQUE (resort_id, url);

COMMENT ON CONSTRAINT uq_resort_links_resort_url ON resort_links
IS 'Unique constraint for upsert operations - same URL cannot be stored twice for a resort';
