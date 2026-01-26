# Snowthere Quick Start

**Round 7.1**: External Linking Infrastructure ✅ IN PROGRESS
**Type**: Strategic implementation
**Status**: Primitives and migrations ready, pending affiliate setup

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R6.6: **Email compliance fixes** - unsubscribe endpoint, template variables, sequence trigger, physical address
- R7.1: **Migration 027** - entity_link_cache table for Google Places caching
- R7.1: **Migration 028** - affiliate_config table for affiliate programs + link_click_log for analytics
- R7.1: **external_links.py** - Google Places resolution, affiliate URL lookup, link click tracking
- R7.1: **Entity extraction** - `extract_linkable_entities()` in intelligence.py finds hotels, restaurants, etc. in content

**Next**:
- R7.2: Apply to affiliate programs (Booking.com, Ski.com, Liftopia) - manual
- R7.2: Add GOOGLE_PLACES_API_KEY to Railway for external link resolution
- R7.3: Integrate entity link injection into pipeline Stage 4.9
- R7.4: Add outbound link click tracking via GA4 events

**Key Files**:
- Strategic plan: `/.claude/plans/snuggly-herding-liskov.md`
- External links: `agents/shared/primitives/external_links.py`
- Entity extraction: `agents/shared/primitives/intelligence.py` (extract_linkable_entities)
- Migrations: `supabase/migrations/027_entity_link_cache.sql`, `028_affiliate_config.sql`

**Full context**: CLAUDE.md | .compound-beads/context.md
