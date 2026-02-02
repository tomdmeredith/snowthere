-- Expand entity_link_cache valid types to include village
-- Needed for entity link coverage overhaul (13 entity types in extraction)

ALTER TABLE entity_link_cache
DROP CONSTRAINT IF EXISTS valid_entity_type;

ALTER TABLE entity_link_cache
ADD CONSTRAINT valid_entity_type CHECK (
    entity_type IN (
        'hotel', 'restaurant', 'ski_school', 'rental', 'activity',
        'grocery', 'transport', 'official', 'airport', 'location',
        'childcare', 'bar', 'cafe', 'spa', 'attraction',
        'retail', 'transportation', 'village'
    )
);
