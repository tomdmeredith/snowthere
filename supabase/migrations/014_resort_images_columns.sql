-- Migration: Add attribution and metadata columns to resort_images
-- Created: 2026-01-22
-- Purpose: Support UGC photo attributions and additional metadata

-- Add attribution column for photo credits (Google Places attributions)
ALTER TABLE resort_images
ADD COLUMN IF NOT EXISTS attribution TEXT;

-- Add metadata column for additional data (category, relevance_score, place_id, etc.)
ALTER TABLE resort_images
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Comments
COMMENT ON COLUMN resort_images.attribution IS
'Photo attribution/credit text (e.g., from Google Places)';

COMMENT ON COLUMN resort_images.metadata IS
'Additional metadata JSON: category, relevance_score, place_id, etc.';
