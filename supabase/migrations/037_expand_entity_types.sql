-- Expand valid entity types for entity_link_cache
-- Claude extracts additional types like airport, location, childcare, etc.
-- These need to be cacheable to avoid repeated API lookups.

ALTER TABLE entity_link_cache
DROP CONSTRAINT IF EXISTS valid_entity_type;

ALTER TABLE entity_link_cache
ADD CONSTRAINT valid_entity_type CHECK (
    entity_type IN (
        'hotel', 'restaurant', 'ski_school', 'rental', 'activity',
        'grocery', 'transport', 'official', 'airport', 'location',
        'childcare', 'bar', 'cafe', 'spa', 'attraction'
    )
);
