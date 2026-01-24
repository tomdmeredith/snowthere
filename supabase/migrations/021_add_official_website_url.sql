-- Add official_website_url to resorts table
-- Round 5.9.2: Enable website scraping for cost acquisition

ALTER TABLE resorts ADD COLUMN IF NOT EXISTS official_website_url TEXT;

-- Add index for resorts with known websites (useful for batch scraping)
CREATE INDEX IF NOT EXISTS idx_resorts_has_website ON resorts(id)
WHERE official_website_url IS NOT NULL;

-- Comment for documentation
COMMENT ON COLUMN resorts.official_website_url IS 'Official resort website URL for direct pricing scraping';
