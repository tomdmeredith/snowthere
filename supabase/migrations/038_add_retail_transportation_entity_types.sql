-- Add retail and transportation entity types to entity_link_cache
-- Cortina d'Ampezzo has luxury retail (Gucci, Dior), Shiga Kogen has transportation hubs (Tokyo Station)

ALTER TABLE entity_link_cache
DROP CONSTRAINT IF EXISTS valid_entity_type;

ALTER TABLE entity_link_cache
ADD CONSTRAINT valid_entity_type CHECK (
    entity_type IN (
        'hotel', 'restaurant', 'ski_school', 'rental', 'activity',
        'grocery', 'transport', 'official', 'airport', 'location',
        'childcare', 'bar', 'cafe', 'spa', 'attraction',
        'retail', 'transportation'
    )
);
