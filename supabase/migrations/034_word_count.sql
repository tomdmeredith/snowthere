-- Migration: Add word count tracking to resort content
-- Purpose: Enable detection of thin content pages for SEO optimization

-- Add word_count column to resort_content
ALTER TABLE resort_content
ADD COLUMN word_count INTEGER;

-- Index for efficient thin content queries
CREATE INDEX idx_resort_content_word_count ON resort_content(word_count)
WHERE word_count IS NOT NULL;

-- Comments
COMMENT ON COLUMN resort_content.word_count IS 'Total word count across all content sections (quick_take + getting_there + where_to_stay + etc). Used to detect thin content.';
