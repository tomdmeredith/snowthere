"""External linking primitives for Google Places and affiliate URL resolution.

Part of Round 7: External Linking & Affiliate System.

Provides:
- Google Places API integration for entity resolution
- Entity link caching with appropriate TTLs
- Affiliate URL lookup and transformation
- Maps URL generation

Cache Strategy:
- place_id: Cache indefinitely (stable identifier)
- Website URLs: Cache 90 days (can change)
- Maps URLs: Derived from place_id (no expiration)
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx

from ..config import get_settings
from ..supabase_client import get_supabase_client


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ResolvedEntity:
    """Result of resolving an entity to external links."""

    name: str
    entity_type: str
    google_place_id: str | None = None
    resolved_name: str | None = None
    direct_url: str | None = None
    maps_url: str | None = None
    affiliate_url: str | None = None
    affiliate_program: str | None = None
    confidence: float = 0.0
    from_cache: bool = False


@dataclass
class AffiliateConfig:
    """Configuration for an affiliate program."""

    program_name: str
    display_name: str
    url_template: str | None
    affiliate_id: str | None
    tracking_param: str | None
    domains: list[str]
    is_active: bool = True


# ============================================================================
# CACHE OPERATIONS
# ============================================================================


def _normalize_entity_name(name: str) -> str:
    """Normalize entity name for cache lookup."""
    # Lowercase, strip whitespace, normalize whitespace
    normalized = name.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _get_cached_entity(
    name_normalized: str,
    entity_type: str,
    location_context: str,
) -> dict[str, Any] | None:
    """Look up entity in cache."""
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("entity_link_cache")
            .select("*")
            .eq("name_normalized", name_normalized)
            .eq("entity_type", entity_type)
            .eq("location_context", location_context)
            .limit(1)
            .execute()
        )

        if result.data:
            cached = result.data[0]
            # Check if expired (for non-place_id data)
            if cached.get("expires_at"):
                expires_at = datetime.fromisoformat(
                    cached["expires_at"].replace("Z", "+00:00")
                )
                if expires_at < datetime.now(expires_at.tzinfo):
                    return None  # Expired
            return cached
        return None
    except Exception as e:
        print(f"Cache lookup failed: {e}")
        return None


def _cache_entity(
    name_normalized: str,
    entity_type: str,
    location_context: str,
    google_place_id: str | None = None,
    resolved_name: str | None = None,
    direct_url: str | None = None,
    maps_url: str | None = None,
    affiliate_url: str | None = None,
    affiliate_program: str | None = None,
    resolution_source: str = "google_places",
    confidence: float = 0.0,
    expires_days: int = 90,
) -> bool:
    """Cache entity resolution result."""
    try:
        supabase = get_supabase_client()

        # Set expiration for volatile data (not place_id)
        expires_at = None
        if direct_url or affiliate_url:
            expires_at = (datetime.utcnow() + timedelta(days=expires_days)).isoformat()

        data = {
            "name_normalized": name_normalized,
            "entity_type": entity_type,
            "location_context": location_context,
            "google_place_id": google_place_id,
            "resolved_name": resolved_name,
            "direct_url": direct_url,
            "maps_url": maps_url,
            "affiliate_url": affiliate_url,
            "affiliate_program": affiliate_program,
            "resolution_source": resolution_source,
            "confidence": confidence,
            "expires_at": expires_at,
        }

        supabase.table("entity_link_cache").upsert(
            data, on_conflict="name_normalized,entity_type,location_context"
        ).execute()

        return True
    except Exception as e:
        print(f"Cache write failed: {e}")
        return False


# ============================================================================
# GOOGLE PLACES API
# ============================================================================


def _build_maps_url(place_id: str) -> str:
    """Build Google Maps URL from place_id."""
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


async def resolve_google_place(
    name: str,
    entity_type: str,
    location_context: str,
) -> ResolvedEntity | None:
    """Resolve an entity name to Google Places data.

    Uses Text Search (New) API for best results.

    Args:
        name: Entity name (e.g., "Hotel Schweizerhof")
        entity_type: Type hint ('hotel', 'restaurant', etc.)
        location_context: Location for disambiguation (e.g., "Zermatt, Switzerland")

    Returns:
        ResolvedEntity with place data, or None if not found
    """
    settings = get_settings()

    if not settings.google_places_api_key:
        print("Google Places API key not configured")
        return None

    name_normalized = _normalize_entity_name(name)

    # Check cache first
    cached = _get_cached_entity(name_normalized, entity_type, location_context)
    if cached:
        return ResolvedEntity(
            name=name,
            entity_type=entity_type,
            google_place_id=cached.get("google_place_id"),
            resolved_name=cached.get("resolved_name"),
            direct_url=cached.get("direct_url"),
            maps_url=cached.get("maps_url"),
            affiliate_url=cached.get("affiliate_url"),
            affiliate_program=cached.get("affiliate_program"),
            confidence=cached.get("confidence", 0.0),
            from_cache=True,
        )

    # Map entity types to Google Places types
    type_mapping = {
        "hotel": "lodging",
        "restaurant": "restaurant",
        "ski_school": "point_of_interest",
        "rental": "store",
        "activity": "point_of_interest",
        "grocery": "grocery_or_supermarket",
        "transport": "transit_station",
    }

    included_type = type_mapping.get(entity_type, "point_of_interest")

    # Build search query with location context
    search_query = f"{name} {location_context}"

    try:
        async with httpx.AsyncClient() as client:
            # Use Text Search (New) API
            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.google_places_api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri,places.formattedAddress",
            }
            body = {
                "textQuery": search_query,
                "includedType": included_type,
                "maxResultCount": 1,
            }

            response = await client.post(url, headers=headers, json=body, timeout=10)

            if response.status_code != 200:
                print(f"Google Places API error: {response.status_code}")
                return None

            data = response.json()
            places = data.get("places", [])

            if not places:
                # Cache negative result to avoid repeated lookups
                _cache_entity(
                    name_normalized,
                    entity_type,
                    location_context,
                    resolution_source="google_places",
                    confidence=0.0,
                    expires_days=7,  # Shorter TTL for negative results
                )
                return None

            place = places[0]
            place_id = place.get("id")
            resolved_name = place.get("displayName", {}).get("text")
            website_url = place.get("websiteUri")
            maps_url = _build_maps_url(place_id) if place_id else None

            # Calculate confidence based on name similarity
            confidence = _calculate_name_confidence(name, resolved_name)

            # Cache the result
            _cache_entity(
                name_normalized,
                entity_type,
                location_context,
                google_place_id=place_id,
                resolved_name=resolved_name,
                direct_url=website_url,
                maps_url=maps_url,
                resolution_source="google_places",
                confidence=confidence,
            )

            return ResolvedEntity(
                name=name,
                entity_type=entity_type,
                google_place_id=place_id,
                resolved_name=resolved_name,
                direct_url=website_url,
                maps_url=maps_url,
                confidence=confidence,
                from_cache=False,
            )

    except Exception as e:
        print(f"Google Places lookup failed: {e}")
        return None


def _calculate_name_confidence(query_name: str, resolved_name: str | None) -> float:
    """Calculate confidence score based on name similarity."""
    if not resolved_name:
        return 0.0

    query_normalized = _normalize_entity_name(query_name)
    resolved_normalized = _normalize_entity_name(resolved_name)

    # Exact match
    if query_normalized == resolved_normalized:
        return 1.0

    # Containment
    if query_normalized in resolved_normalized or resolved_normalized in query_normalized:
        return 0.8

    # Word overlap
    query_words = set(query_normalized.split())
    resolved_words = set(resolved_normalized.split())
    overlap = len(query_words & resolved_words)
    total = len(query_words | resolved_words)

    if total > 0:
        return 0.5 + (0.3 * overlap / total)

    return 0.3


# ============================================================================
# AFFILIATE URL OPERATIONS
# ============================================================================


def _get_affiliate_configs() -> dict[str, AffiliateConfig]:
    """Load affiliate configurations from database."""
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("affiliate_config").select("*").eq("is_active", True).execute()
        )

        configs = {}
        for row in result.data or []:
            configs[row["program_name"]] = AffiliateConfig(
                program_name=row["program_name"],
                display_name=row["display_name"],
                url_template=row.get("url_template"),
                affiliate_id=row.get("affiliate_id"),
                tracking_param=row.get("tracking_param"),
                domains=row.get("domains", []),
                is_active=row.get("is_active", True),
            )
        return configs
    except Exception as e:
        print(f"Failed to load affiliate configs: {e}")
        return {}


def lookup_affiliate_url(direct_url: str) -> tuple[str | None, str | None]:
    """Look up affiliate URL for a direct URL.

    Args:
        direct_url: The original URL

    Returns:
        Tuple of (affiliate_url, program_name) or (None, None) if no match
    """
    if not direct_url:
        return None, None

    parsed = urlparse(direct_url)
    domain = parsed.netloc.lower()

    # Remove www. prefix for matching
    if domain.startswith("www."):
        domain = domain[4:]

    configs = _get_affiliate_configs()

    for program_name, config in configs.items():
        # Check if domain matches any affiliate program domains
        matching_domains = [d.replace("www.", "") for d in config.domains]
        if domain in matching_domains:
            # Build affiliate URL if we have an ID
            if config.affiliate_id and config.url_template:
                affiliate_url = config.url_template.replace("{aid}", config.affiliate_id)
                affiliate_url = affiliate_url.replace("{url}", direct_url)
                affiliate_url = affiliate_url.replace("{path}", parsed.path.lstrip("/"))
                return affiliate_url, program_name
            elif config.affiliate_id and config.tracking_param:
                # Add tracking param to existing URL
                sep = "&" if "?" in direct_url else "?"
                return f"{direct_url}{sep}{config.tracking_param}={config.affiliate_id}", program_name

    return None, None


# ============================================================================
# MAIN RESOLUTION FUNCTION
# ============================================================================


async def resolve_entity_link(
    name: str,
    entity_type: str,
    location_context: str,
    include_affiliate: bool = True,
) -> ResolvedEntity | None:
    """Resolve an entity name to all available links.

    This is the main entry point for external link resolution.

    Args:
        name: Entity name (e.g., "Hotel Schweizerhof")
        entity_type: Type ('hotel', 'restaurant', 'ski_school', 'rental', 'activity', 'grocery')
        location_context: Location for disambiguation (e.g., "Zermatt, Switzerland")
        include_affiliate: Whether to look up affiliate URLs

    Returns:
        ResolvedEntity with all available links, or None if resolution failed
    """
    # Resolve via Google Places
    result = await resolve_google_place(name, entity_type, location_context)

    if not result:
        return None

    # Look up affiliate URL if direct URL exists
    if include_affiliate and result.direct_url:
        affiliate_url, program_name = lookup_affiliate_url(result.direct_url)
        if affiliate_url:
            result.affiliate_url = affiliate_url
            result.affiliate_program = program_name

            # Update cache with affiliate data
            name_normalized = _normalize_entity_name(name)
            _cache_entity(
                name_normalized,
                entity_type,
                location_context,
                google_place_id=result.google_place_id,
                resolved_name=result.resolved_name,
                direct_url=result.direct_url,
                maps_url=result.maps_url,
                affiliate_url=affiliate_url,
                affiliate_program=program_name,
                resolution_source="google_places",
                confidence=result.confidence,
            )

    return result


# ============================================================================
# LINK CLICK TRACKING
# ============================================================================


def log_link_click(
    resort_id: str | None,
    link_url: str,
    link_category: str | None = None,
    is_affiliate: bool = False,
    affiliate_program: str | None = None,
    session_id: str | None = None,
    referrer: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """Log a link click for analytics.

    Args:
        resort_id: Resort the click came from
        link_url: The URL that was clicked
        link_category: Category of link ('lodging', 'dining', etc.)
        is_affiliate: Whether this was an affiliate link
        affiliate_program: Which affiliate program if applicable
        session_id: Session ID for deduplication
        referrer: Referring URL
        user_agent: Browser user agent

    Returns:
        True if logged successfully
    """
    try:
        supabase = get_supabase_client()

        data = {
            "resort_id": resort_id,
            "link_url": link_url,
            "link_category": link_category,
            "is_affiliate": is_affiliate,
            "affiliate_program": affiliate_program,
            "session_id": session_id,
            "referrer": referrer,
            "user_agent": user_agent,
        }

        supabase.table("link_click_log").insert(data).execute()
        return True
    except Exception as e:
        print(f"Failed to log link click: {e}")
        return False


def get_click_stats(
    resort_id: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Get link click statistics.

    Args:
        resort_id: Filter by resort (optional)
        days: Number of days to look back

    Returns:
        Statistics dict with total clicks, affiliate clicks, by category, etc.
    """
    try:
        supabase = get_supabase_client()
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        query = (
            supabase.table("link_click_log")
            .select("*")
            .gte("clicked_at", cutoff)
        )

        if resort_id:
            query = query.eq("resort_id", resort_id)

        result = query.execute()
        clicks = result.data or []

        # Calculate stats
        total = len(clicks)
        affiliate = sum(1 for c in clicks if c.get("is_affiliate"))
        by_category: dict[str, int] = {}
        by_program: dict[str, int] = {}

        for click in clicks:
            cat = click.get("link_category") or "unknown"
            by_category[cat] = by_category.get(cat, 0) + 1

            if click.get("affiliate_program"):
                prog = click["affiliate_program"]
                by_program[prog] = by_program.get(prog, 0) + 1

        return {
            "total_clicks": total,
            "affiliate_clicks": affiliate,
            "by_category": by_category,
            "by_affiliate_program": by_program,
            "period_days": days,
        }
    except Exception as e:
        print(f"Failed to get click stats: {e}")
        return {"error": str(e)}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_rel_attribute(
    is_affiliate: bool = False,
    is_ugc: bool = False,
) -> str:
    """Get the appropriate rel attribute for a link.

    SEO best practices:
    - Affiliate links: rel="sponsored noopener"
    - UGC (Google Maps): rel="nofollow noopener"
    - Regular external: rel="nofollow noopener noreferrer"

    Args:
        is_affiliate: Whether this is an affiliate link
        is_ugc: Whether this is user-generated content (Maps, etc.)

    Returns:
        Appropriate rel attribute value
    """
    if is_affiliate:
        return "sponsored noopener"
    if is_ugc:
        return "nofollow noopener"
    return "nofollow noopener noreferrer"


def clear_expired_cache() -> int:
    """Clear expired entries from entity link cache.

    Returns:
        Number of entries cleared
    """
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("entity_link_cache")
            .delete()
            .lt("expires_at", datetime.utcnow().isoformat())
            .execute()
        )

        return len(result.data or [])
    except Exception as e:
        print(f"Failed to clear expired cache: {e}")
        return 0
