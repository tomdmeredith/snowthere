-- Migration: Resort Images Table
-- Created: 2026-01-17
-- Purpose: Store AI-generated and official resort images with metadata
--
-- Image types:
--   - hero: Main resort hero image (landscape, 16:9)
--   - atmosphere: Lodge/cozy lifestyle shots (square, 1:1)
--   - activity: Ski school, family activities
--   - landscape: Mountain vistas
--
-- Sources (3-tier fallback):
--   - gemini: Google Gemini (Tier 1, ~$0.002)
--   - glif: Nano Banana Pro (Tier 2, ~$0.01)
--   - replicate: Flux Schnell (Tier 3, ~$0.003)
--   - official: Scraped from resort website

-- =============================================================================
-- RESORT IMAGES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS resort_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resort_id UUID NOT NULL REFERENCES resorts(id) ON DELETE CASCADE,

    -- Image classification
    image_type VARCHAR(50) NOT NULL,  -- 'hero', 'atmosphere', 'activity', 'landscape'

    -- Image storage
    image_url TEXT NOT NULL,  -- Supabase Storage URL or external URL

    -- Source tracking
    source VARCHAR(50) NOT NULL,  -- 'gemini', 'glif', 'replicate', 'official'

    -- Generation metadata
    prompt TEXT,  -- The prompt used for AI generation (for reference/iteration)
    alt_text TEXT,  -- Accessibility alt text

    -- Additional metadata
    width INTEGER,
    height INTEGER,
    file_size INTEGER,  -- bytes
    mime_type VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_image_type CHECK (
        image_type IN ('hero', 'atmosphere', 'activity', 'landscape', 'trail_map', 'ugc')
    ),
    CONSTRAINT valid_source CHECK (
        source IN ('gemini', 'glif', 'replicate', 'official', 'google_places', 'osm')
    )
);

-- Index for efficient resort lookups
CREATE INDEX IF NOT EXISTS idx_resort_images_resort_id
ON resort_images(resort_id);

-- Index for type filtering
CREATE INDEX IF NOT EXISTS idx_resort_images_type
ON resort_images(resort_id, image_type);

-- Index for finding latest images
CREATE INDEX IF NOT EXISTS idx_resort_images_created
ON resort_images(resort_id, created_at DESC);

-- =============================================================================
-- STORAGE BUCKET (RUN MANUALLY OR VIA SUPABASE DASHBOARD)
-- =============================================================================
--
-- Create a public bucket for resort images:
--
-- 1. Go to Supabase Dashboard → Storage
-- 2. Click "New bucket"
-- 3. Name: resort-images
-- 4. Public: Yes (images need to be publicly accessible)
-- 5. File size limit: 5MB
-- 6. Allowed MIME types: image/png, image/jpeg, image/webp
--
-- Or via SQL (requires appropriate permissions):
--
-- INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
-- VALUES (
--     'resort-images',
--     'resort-images',
--     true,
--     5242880,  -- 5MB
--     ARRAY['image/png', 'image/jpeg', 'image/webp']
-- );
--
-- Storage policies (allow public read, authenticated write):
--
-- CREATE POLICY "Public read access" ON storage.objects
-- FOR SELECT USING (bucket_id = 'resort-images');
--
-- CREATE POLICY "Service role write access" ON storage.objects
-- FOR INSERT WITH CHECK (bucket_id = 'resort-images');

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to get the hero image URL for a resort (or NULL if none)
CREATE OR REPLACE FUNCTION get_resort_hero_image_url(p_resort_id UUID)
RETURNS TEXT AS $$
    SELECT image_url
    FROM resort_images
    WHERE resort_id = p_resort_id
      AND image_type = 'hero'
    ORDER BY created_at DESC
    LIMIT 1;
$$ LANGUAGE SQL STABLE;

-- Function to check if a resort has any images
CREATE OR REPLACE FUNCTION resort_has_images(p_resort_id UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS(
        SELECT 1 FROM resort_images WHERE resort_id = p_resort_id
    );
$$ LANGUAGE SQL STABLE;

-- Function to count images by type for a resort
CREATE OR REPLACE FUNCTION count_resort_images(p_resort_id UUID)
RETURNS TABLE(image_type VARCHAR(50), count BIGINT) AS $$
    SELECT image_type, COUNT(*)
    FROM resort_images
    WHERE resort_id = p_resort_id
    GROUP BY image_type;
$$ LANGUAGE SQL STABLE;

-- =============================================================================
-- VIEW: Resort Image Summary
-- =============================================================================

CREATE OR REPLACE VIEW resort_image_summary AS
SELECT
    r.id AS resort_id,
    r.name AS resort_name,
    r.country,
    COUNT(ri.id) AS total_images,
    COUNT(CASE WHEN ri.image_type = 'hero' THEN 1 END) AS hero_count,
    COUNT(CASE WHEN ri.image_type = 'atmosphere' THEN 1 END) AS atmosphere_count,
    MAX(ri.created_at) AS latest_image_at,
    (SELECT image_url FROM resort_images WHERE resort_id = r.id AND image_type = 'hero' ORDER BY created_at DESC LIMIT 1) AS hero_url
FROM resorts r
LEFT JOIN resort_images ri ON r.id = ri.resort_id
GROUP BY r.id, r.name, r.country;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE resort_images IS
'AI-generated and official images for ski resorts. Uses 3-tier fallback: Gemini → Glif → Replicate';

COMMENT ON COLUMN resort_images.image_type IS
'Type of image: hero (main banner), atmosphere (lifestyle), activity (families), landscape (vistas)';

COMMENT ON COLUMN resort_images.source IS
'Generation source: gemini (Tier 1), glif (Tier 2), replicate (Tier 3), official (scraped)';

COMMENT ON COLUMN resort_images.prompt IS
'The AI prompt used to generate this image (for future iteration/improvement)';
