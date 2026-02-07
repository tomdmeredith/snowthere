"""External linking primitives for Google Places and affiliate URL resolution.

Part of Round 7: External Linking & Affiliate System.
Updated: Entity Link Coverage Overhaul — brand registry, type validation,
Maps search fallback, per-entity-type confidence thresholds.

Provides:
- Well-known brand registry (resolves before Google Places)
- Google Places API integration with type cross-validation
- Maps search URL fallback for low-confidence entities
- Entity link caching with appropriate TTLs
- Affiliate URL lookup and transformation
- Per-entity-type confidence thresholds
- Variable per-section link caps

Cache Strategy:
- place_id: Cache indefinitely (stable identifier)
- Website URLs: Cache 90 days (can change)
- Maps URLs: Derived from place_id (no expiration)

Resolution Tiers:
1. Brand registry → canonical URL (confidence 1.0)
2. Google Places (verified) → place-specific link (confidence 0.6-1.0)
3. Maps search fallback → search URL (always safe, rel=nofollow)
"""

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, NamedTuple
from urllib.parse import quote_plus, urlparse

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
    flight_search_url: str | None = None
    confidence: float = 0.0
    from_cache: bool = False
    is_maps_search_fallback: bool = False


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
# WELL-KNOWN BRAND REGISTRY
# ============================================================================
# Checked BEFORE Google Places. Brands resolve with confidence 1.0.
# No API call needed. Prevents mismatches like "Ikon" → random Maps place.

WELL_KNOWN_BRANDS: dict[str, dict[str, str]] = {
    # Ski passes
    "ikon": {"url": "https://www.ikonpass.com/", "type": "ski_pass"},
    "ikon pass": {"url": "https://www.ikonpass.com/", "type": "ski_pass"},
    "epic": {"url": "https://www.epicpass.com/", "type": "ski_pass"},
    "epic pass": {"url": "https://www.epicpass.com/", "type": "ski_pass"},
    "mountain collective": {"url": "https://mountaincollective.com/", "type": "ski_pass"},
    "indy pass": {"url": "https://www.indyskipass.com/", "type": "ski_pass"},
    "magic pass": {"url": "https://www.magicpass.ch/", "type": "ski_pass"},
    "ski amade": {"url": "https://www.skiamade.com/", "type": "ski_pass"},
    "dolomiti superski": {"url": "https://www.dolomitisuperski.com/", "type": "ski_pass"},
    "trois vallees": {"url": "https://www.les3vallees.com/", "type": "ski_pass"},
    "les 3 vallees": {"url": "https://www.les3vallees.com/", "type": "ski_pass"},
    "paradiski": {"url": "https://www.paradiski.com/", "type": "ski_pass"},
    "portes du soleil": {"url": "https://www.portesdusoleil.com/", "type": "ski_pass"},
    "tarentaise": {"url": "https://www.skipass-tarentaise.com/", "type": "ski_pass"},
    "ski arlberg": {"url": "https://www.skiarlberg.at/", "type": "ski_pass"},
    "zillertal superskipass": {"url": "https://www.zillertal.at/", "type": "ski_pass"},
    "wilder kaiser": {"url": "https://www.wilderkaiser.info/", "type": "ski_pass"},
    # European grocery chains
    "coop": {"url": "https://www.coop.ch/", "type": "grocery"},
    "spar": {"url": "https://www.spar.at/", "type": "grocery"},
    "billa": {"url": "https://www.billa.at/", "type": "grocery"},
    "migros": {"url": "https://www.migros.ch/", "type": "grocery"},
    "aldi": {"url": "https://www.aldi.com/", "type": "grocery"},
    "lidl": {"url": "https://www.lidl.com/", "type": "grocery"},
    "mpreis": {"url": "https://www.mpreis.at/", "type": "grocery"},
    "denner": {"url": "https://www.denner.ch/", "type": "grocery"},
    "interspar": {"url": "https://www.interspar.at/", "type": "grocery"},
    "volg": {"url": "https://www.volg.ch/", "type": "grocery"},
    # Japanese convenience stores
    "lawson": {"url": "https://www.lawson.co.jp/", "type": "grocery"},
    "seicomart": {"url": "https://www.seicomart.co.jp/", "type": "grocery"},
    "7-eleven": {"url": "https://www.7andi.com/", "type": "grocery"},
    "familymart": {"url": "https://www.family.co.jp/", "type": "grocery"},
    # Airlines (getting there sections)
    "easyjet": {"url": "https://www.easyjet.com/", "type": "transport"},
    "ryanair": {"url": "https://www.ryanair.com/", "type": "transport"},
    "swiss": {"url": "https://www.swiss.com/", "type": "transport"},
    "austrian airlines": {"url": "https://www.austrian.com/", "type": "transport"},
    "lufthansa": {"url": "https://www.lufthansa.com/", "type": "transport"},
    "air france": {"url": "https://www.airfrance.com/", "type": "transport"},
    # Rental/equipment chains
    "intersport": {"url": "https://www.intersport.com/", "type": "rental"},
    "sport 2000": {"url": "https://www.sport2000rent.com/", "type": "rental"},
    # Booking platforms (not entity links but prevent mismatches)
    "booking.com": {"url": "https://www.booking.com/", "type": "hotel"},
    "airbnb": {"url": "https://www.airbnb.com/", "type": "hotel"},
}


def _resolve_brand(name: str) -> ResolvedEntity | None:
    """Check if entity name is a well-known brand.

    Returns ResolvedEntity with confidence 1.0 if found, None otherwise.
    """
    normalized = name.lower().strip()
    brand = WELL_KNOWN_BRANDS.get(normalized)
    if brand:
        return ResolvedEntity(
            name=name,
            entity_type=brand["type"],
            direct_url=brand["url"],
            confidence=1.0,
            from_cache=False,
            is_maps_search_fallback=False,
        )
    return None


# ============================================================================
# FLIGHT SEARCH URL BUILDER
# ============================================================================

# Regex to extract IATA code from airport names like "Zurich Airport (ZRH)"
_IATA_PATTERN = re.compile(r"\(([A-Z]{3})\)")


def _extract_iata_code(name: str) -> str | None:
    """Extract 3-letter IATA code from an airport entity name.

    Looks for pattern like (ZRH), (INN), (GVA) in the name string.
    """
    match = _IATA_PATTERN.search(name)
    return match.group(1) if match else None


def build_flight_search_url(iata_code: str) -> str:
    """Build a Skyscanner flight search URL for a destination airport.

    Args:
        iata_code: 3-letter IATA airport code (e.g., "ZRH", "INN")

    Returns:
        Skyscanner search URL pre-filled with destination
    """
    return f"https://www.skyscanner.net/transport/flights-to/{iata_code.lower()}/"


# ============================================================================
# NAME CONFIDENCE VALIDATION
# ============================================================================

# Words to filter from Jaccard calculation (function words, prepositions)
_FUNCTION_WORDS = frozenset({
    "de", "del", "di", "da", "the", "la", "le", "les", "el", "los", "las",
    "der", "die", "das", "den", "dem", "des", "van", "von", "zu", "zum",
    "san", "saint", "st", "santa", "santo", "sainte",
    "and", "und", "et", "e", "y", "i", "og",
    "in", "im", "am", "an", "au", "en", "a", "of",
})

# Type-mismatch negative keywords — instant rejection
TYPE_NEGATIVE_KEYWORDS: dict[str, frozenset[str]] = {
    "airport": frozenset({
        "church", "iglesia", "cathedral", "catedral", "basilica", "chapel",
        "kapelle", "kirche", "mosque", "temple", "cemetery", "cementerio",
        "museum", "restaurant", "hotel", "school", "escuela", "schule",
    }),
    "hotel": frozenset({
        "airport", "aeropuerto", "flughafen", "church", "iglesia", "hospital",
    }),
    "restaurant": frozenset({
        "airport", "aeropuerto", "flughafen", "hospital", "church",
    }),
    "ski_school": frozenset({
        "airport", "church", "hospital", "restaurant",
    }),
    "childcare": frozenset({
        "airport", "church", "bar", "nightclub", "pub",
    }),
}

# Type-positive keywords — expected in resolved name
TYPE_POSITIVE_KEYWORDS: dict[str, frozenset[str]] = {
    "airport": frozenset({
        "airport", "aeropuerto", "aeroport", "flughafen", "aeroporto",
        "lufthavn", "lentokentta", "kuukou", "international",
    }),
    "hotel": frozenset({
        "hotel", "lodge", "inn", "chalet", "residence", "pension",
        "gasthof", "haus", "hof", "albergo", "auberge", "hostel",
    }),
    "grocery": frozenset({
        "market", "grocery", "supermarket", "supermercado", "markt",
        "coop", "spar", "billa", "migros", "convenience", "konbini",
    }),
}

# Per-entity-type confidence thresholds for verified links
ENTITY_TYPE_THRESHOLDS: dict[str, float] = {
    # Low risk — common businesses, easy to verify
    "hotel": 0.6,
    "restaurant": 0.6,
    "grocery": 0.6,
    "bar": 0.6,
    "cafe": 0.6,
    # Medium risk — specialized services
    "rental": 0.7,
    "spa": 0.7,
    "ski_school": 0.7,
    # High risk — wrong link could mislead families
    "airport": 0.75,
    "transport": 0.75,
    "activity": 0.75,
    "childcare": 0.75,
    # Bypass — brand/known URL resolution
    "ski_pass": 0.0,  # Handled by brand registry
    "official": 0.0,  # Handled by brand registry
    # Maps-only types (always use Maps search)
    "village": float("inf"),  # Never passes threshold → always Maps search
    "location": float("inf"),
}


def _calculate_name_confidence(
    query_name: str,
    resolved_name: str | None,
    entity_type: str = "",
) -> float:
    """Calculate confidence score based on name similarity + type validation.

    Three layers:
    A) Type-mismatch rejection: negative keywords → 0.0
    B) Critical keyword check: positive keywords → penalty if absent
    C) Structural similarity: filtered Jaccard on significant words
    """
    if not resolved_name:
        return 0.0

    query_normalized = _normalize_entity_name(query_name)
    resolved_normalized = _normalize_entity_name(resolved_name)

    # === Layer A: Type-mismatch rejection ===
    negative_keywords = TYPE_NEGATIVE_KEYWORDS.get(entity_type, frozenset())
    if negative_keywords:
        resolved_lower = resolved_normalized
        for neg_word in negative_keywords:
            if neg_word in resolved_lower:
                return 0.0

    # === Layer B: Positive keyword check ===
    positive_penalty = 0.0
    positive_keywords = TYPE_POSITIVE_KEYWORDS.get(entity_type, frozenset())
    if positive_keywords:
        resolved_lower = resolved_normalized
        has_positive = any(kw in resolved_lower for kw in positive_keywords)
        if not has_positive:
            positive_penalty = 0.15

    # === Layer C: Structural similarity ===

    # Exact match
    if query_normalized == resolved_normalized:
        return 1.0 - positive_penalty

    # Containment
    if query_normalized in resolved_normalized or resolved_normalized in query_normalized:
        return max(0.0, 0.8 - positive_penalty)

    # Filtered Jaccard on significant words
    query_words = set(query_normalized.split()) - _FUNCTION_WORDS
    resolved_words = set(resolved_normalized.split()) - _FUNCTION_WORDS

    # If no significant words remain, fall back to full sets
    if not query_words:
        query_words = set(query_normalized.split())
    if not resolved_words:
        resolved_words = set(resolved_normalized.split())

    overlap = len(query_words & resolved_words)
    total = len(query_words | resolved_words)

    if total == 0:
        return 0.0

    jaccard = overlap / total

    # Zero word overlap → 0.0 (not 0.3 floor like before)
    if overlap == 0:
        return 0.0

    # Require >= 30% Jaccard on significant words
    if jaccard < 0.3:
        return 0.0

    confidence = 0.5 + (0.4 * jaccard)
    return max(0.0, confidence - positive_penalty)


# ============================================================================
# GOOGLE PLACES TYPE CROSS-VALIDATION
# ============================================================================

# Maps entity_type → expected Google Places types
_EXPECTED_PLACES_TYPES: dict[str, set[str]] = {
    "airport": {"airport"},
    "hotel": {"lodging", "hotel"},
    "restaurant": {"restaurant", "food", "meal_delivery", "meal_takeaway", "cafe"},
    "grocery": {"grocery_or_supermarket", "supermarket", "convenience_store"},
    "bar": {"bar", "night_club"},
    "cafe": {"cafe", "bakery", "coffee_shop"},
}


def _validate_places_types(entity_type: str, places_types: list[str]) -> float:
    """Cross-validate Google Places returned types against expected types.

    Returns confidence penalty (0.0 = no penalty, 0.3 = type mismatch).
    """
    expected = _EXPECTED_PLACES_TYPES.get(entity_type)
    if not expected or not places_types:
        return 0.0  # No validation possible, no penalty

    # Check if ANY expected type is present
    if expected & set(places_types):
        return 0.0  # Match found, no penalty

    return 0.3  # Type mismatch penalty


# ============================================================================
# MAPS SEARCH URL FALLBACK
# ============================================================================


def _build_maps_search_url(name: str, location_context: str) -> str:
    """Build a Google Maps search URL (not a place-specific link).

    This is qualitatively different from a place_id link:
    - It's a search, never asserts a specific wrong place
    - Always safe to use as fallback
    - SEO: must use rel="nofollow noopener"
    """
    query = f"{name} {location_context}"
    return f"https://www.google.com/maps/search/{quote_plus(query)}"


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
            expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat()

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
    Includes type cross-validation via places.types FieldMask.

    Args:
        name: Entity name (e.g., "Hotel Schweizerhof")
        entity_type: Type hint ('hotel', 'restaurant', etc.)
        location_context: Location for disambiguation (e.g., "Zermatt, Switzerland")

    Returns:
        ResolvedEntity with place data, or None if not found
    """
    settings = get_settings()

    api_key = settings.google_places_api_key or settings.google_api_key
    if not api_key:
        print("Google Places API key not configured (checked google_places_api_key and google_api_key)")
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

    # Map entity types to Google Places API (New) Table A types
    # Only use types that are valid for Text Search includedType
    type_mapping = {
        "hotel": "lodging",
        "restaurant": "restaurant",
        "ski_school": None,  # No good match — text query handles it
        "rental": "sporting_goods_store",
        "activity": "tourist_attraction",
        "grocery": "grocery_store",
        "transport": "transit_station",
        "transportation": "transit_station",
        "retail": "store",
        "airport": "airport",
        "bar": "bar",
        "cafe": "cafe",
        "childcare": None,  # No good match
        "village": None,  # No good match
    }

    included_type = type_mapping.get(entity_type)

    # Build search query with location context
    search_query = f"{name} {location_context}"

    try:
        async with httpx.AsyncClient() as client:
            # Use Text Search (New) API
            # Include places.types in FieldMask for type cross-validation (zero extra API cost)
            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri,places.formattedAddress,places.types",
            }
            body = {
                "textQuery": search_query,
                "maxResultCount": 1,
            }
            if included_type:
                body["includedType"] = included_type

            response = await client.post(url, headers=headers, json=body, timeout=10)

            if response.status_code != 200:
                print(f"Google Places API error: {response.status_code} - {response.text[:500]}")
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
            # Validate URL scheme — only accept http/https
            if website_url:
                parsed_url = urlparse(website_url)
                if parsed_url.scheme not in ("http", "https"):
                    website_url = None
            places_types = place.get("types", [])
            maps_url = _build_maps_url(place_id) if place_id else None

            # Calculate confidence: name similarity + type cross-validation
            name_confidence = _calculate_name_confidence(name, resolved_name, entity_type)
            type_penalty = _validate_places_types(entity_type, places_types)
            confidence = max(0.0, name_confidence - type_penalty)

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

    Three-tier resolution:
    1. Brand registry → canonical URL (confidence 1.0)
    2. Google Places, high confidence → verified place link
    3. Low confidence or no result → Maps search URL (always safe)

    Args:
        name: Entity name (e.g., "Hotel Schweizerhof")
        entity_type: Type ('hotel', 'restaurant', 'ski_school', etc.)
        location_context: Location for disambiguation (e.g., "Zermatt, Switzerland")
        include_affiliate: Whether to look up affiliate URLs

    Returns:
        ResolvedEntity with all available links, or None only if entity_type
        should be skipped entirely
    """
    # === Tier 1: Brand registry ===
    brand_result = _resolve_brand(name)
    if brand_result:
        return brand_result

    # === Tier 2: Google Places resolution ===
    result = await resolve_google_place(name, entity_type, location_context)

    # Get the confidence threshold for this entity type
    threshold = ENTITY_TYPE_THRESHOLDS.get(entity_type, 0.65)

    if result and result.confidence >= threshold:
        # High confidence — use verified place link
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

        # For airports, extract IATA code and build flight search URL
        if entity_type == "airport":
            iata = _extract_iata_code(name)
            if iata:
                result.flight_search_url = build_flight_search_url(iata)

        return result

    # === Tier 3: Maps search fallback ===
    maps_search_url = _build_maps_search_url(name, location_context)
    flight_url = None
    if entity_type == "airport":
        iata = _extract_iata_code(name)
        if iata:
            flight_url = build_flight_search_url(iata)
    return ResolvedEntity(
        name=name,
        entity_type=entity_type,
        maps_url=maps_search_url,
        flight_search_url=flight_url,
        confidence=0.5,  # Neutral — safe but unverified
        from_cache=False,
        is_maps_search_fallback=True,
    )


# ============================================================================
# ENTITY ATOM STORAGE
# ============================================================================


def upsert_resort_entity(
    resort_id: str,
    name: str,
    entity_type: str,
    source: str = "extraction",
    source_url: str | None = None,
    sections: list[str] | None = None,
    editorial_role: str = "mentioned",
    resolution_status: str = "pending",
    resolved_url: str | None = None,
    google_place_id: str | None = None,
    maps_url: str | None = None,
    confidence: float = 0.0,
) -> bool:
    """Store or update an entity atom in resort_entities table.

    Args:
        resort_id: UUID of the resort
        name: Entity name as it appears in content
        entity_type: Type classification
        source: How discovered (extraction, research, generation, manual)
        source_url: Pre-resolved URL from research/generation
        sections: Which content sections reference this entity
        editorial_role: mentioned, recommended, warned_about
        resolution_status: pending, resolved, failed, brand
        resolved_url: Final chosen URL
        google_place_id: Google Places ID
        maps_url: Google Maps URL
        confidence: Resolution confidence score

    Returns:
        True if stored successfully
    """
    entity_type = _TYPE_ALIASES.get(entity_type, entity_type)

    try:
        supabase = get_supabase_client()
        name_normalized = _normalize_entity_name(name)

        data = {
            "resort_id": resort_id,
            "name": name,
            "name_normalized": name_normalized,
            "entity_type": entity_type,
            "source": source,
            "source_url": source_url,
            "sections": sections or [],
            "editorial_role": editorial_role,
            "resolution_status": resolution_status,
            "resolved_url": resolved_url,
            "google_place_id": google_place_id,
            "maps_url": maps_url,
            "confidence": confidence,
        }

        supabase.table("resort_entities").upsert(
            data, on_conflict="resort_id,name_normalized,entity_type"
        ).execute()

        return True
    except Exception as e:
        print(f"Entity atom storage failed for '{name}': {e}")
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_rel_attribute(
    is_affiliate: bool = False,
    is_maps_place_link: bool = False,
    is_official: bool = False,
    is_maps_search_fallback: bool = False,
) -> str:
    """Get the appropriate rel attribute for a link.

    SEO + referral tracking best practices:
    - Official resort links: rel="noopener" (dofollow — authoritative sources)
    - Affiliate links: rel="sponsored noopener" (Google-compliant for paid links)
    - Maps place links: rel="nofollow noopener" (no equity to Maps, still sends referrer)
    - Maps search fallback: rel="nofollow noopener" (navigational aid, NOT editorial endorsement)
    - Entity links (hotels, restaurants, etc.): rel="noopener" (dofollow, sends referrer)

    Args:
        is_affiliate: Whether this is an affiliate link
        is_maps_place_link: Whether this is a Google Maps place-specific link
        is_official: Whether this is an official resort website link
        is_maps_search_fallback: Whether this is a Maps search URL (not a verified place)

    Returns:
        Appropriate rel attribute value
    """
    if is_official:
        return "noopener"
    if is_affiliate:
        return "sponsored noopener"
    if is_maps_place_link or is_maps_search_fallback:
        return "nofollow noopener"
    return "noopener"


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
            .lt("expires_at", datetime.now(timezone.utc).isoformat())
            .execute()
        )

        return len(result.data or [])
    except Exception as e:
        print(f"Failed to clear expired cache: {e}")
        return 0


def clear_low_confidence_cache(min_confidence: float = 0.65) -> int:
    """Clear cache entries below confidence threshold.

    Used before re-backfill to force re-resolution of low-quality matches.

    Returns:
        Number of entries cleared
    """
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("entity_link_cache")
            .delete()
            .lt("confidence", min_confidence)
            .execute()
        )

        count = len(result.data or [])
        print(f"Cleared {count} cache entries with confidence < {min_confidence}")
        return count
    except Exception as e:
        print(f"Failed to clear low confidence cache: {e}")
        return 0


# ============================================================================
# LINK INJECTION
# ============================================================================

# Variable per-section link caps (SEO expert recommendation)
SECTION_LINK_CAPS: dict[str, int] = {
    "where_to_stay": 5,
    "on_mountain": 5,
    "off_mountain": 5,
    "getting_there": 3,
    "lift_tickets": 3,
    "parent_reviews_summary": 3,
    "quick_take": 2,
}


class LinkChoice(NamedTuple):
    """Result of choosing the best link URL for an entity."""

    url: str | None
    is_affiliate: bool
    is_maps_place_link: bool
    is_maps_search_fallback: bool


# Context-aware link priority table: ordered list of (url_attr, is_affiliate, is_maps_place_link)
# - Booking types (hotel, rental): affiliate > direct > maps
# - Location types (restaurant, grocery): maps > direct
# - Info/registration types (ski_school, activity, transport): direct > maps
_ENTITY_LINK_PRIORITY: dict[str, list[tuple[str, bool, bool]]] = {
    "hotel":          [("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True)],
    "rental":         [("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True)],
    "restaurant":     [("maps_url", False, True), ("direct_url", False, False)],
    "grocery":        [("maps_url", False, True), ("direct_url", False, False)],
    "bar":            [("maps_url", False, True), ("direct_url", False, False)],
    "cafe":           [("maps_url", False, True), ("direct_url", False, False)],
    "ski_school":     [("direct_url", False, False), ("maps_url", False, True)],
    "activity":       [("direct_url", False, False), ("maps_url", False, True)],
    "transport":      [("direct_url", False, False), ("maps_url", False, True)],
    "transportation": [("direct_url", False, False), ("maps_url", False, True)],
    "retail":         [("direct_url", False, False), ("maps_url", False, True)],
    "childcare":      [("direct_url", False, False), ("maps_url", False, True)],
    "airport":        [("flight_search_url", False, False), ("direct_url", False, False), ("maps_url", False, True)],
    "village":        [("maps_url", False, True)],
}
_ENTITY_LINK_PRIORITY_DEFAULT: list[tuple[str, bool, bool]] = [
    ("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True),
]

# Normalize entity type aliases to match DB constraints
_TYPE_ALIASES: dict[str, str] = {"transportation": "transport"}


def _choose_link_url(resolved: ResolvedEntity) -> LinkChoice:
    """Choose the best link URL based on entity type.

    Uses the module-level _ENTITY_LINK_PRIORITY table for context-aware
    destination logic.

    Args:
        resolved: The resolved entity with available URLs

    Returns:
        LinkChoice with url, is_affiliate, is_maps_place_link, is_maps_search_fallback
    """
    # Maps search fallback entities only have maps_url
    if resolved.is_maps_search_fallback:
        return LinkChoice(resolved.maps_url, False, False, True)

    for attr, is_affiliate, is_maps_place_link in _ENTITY_LINK_PRIORITY.get(
        resolved.entity_type, _ENTITY_LINK_PRIORITY_DEFAULT
    ):
        url = getattr(resolved, attr, None)
        if url:
            return LinkChoice(url, is_affiliate, is_maps_place_link, False)

    return LinkChoice(None, False, False, False)


@dataclass
class InjectedLink:
    """Record of a link injection."""

    entity_name: str
    entity_type: str
    original_text: str
    url: str
    is_affiliate: bool
    affiliate_program: str | None = None
    rel_attribute: str = ""
    is_maps_search_fallback: bool = False


@dataclass
class LinkInjectionResult:
    """Result of link injection operation."""

    modified_content: str
    links_injected: list[InjectedLink]
    injection_count: int
    entities_not_resolved: list[str]
    success: bool = True
    error: str | None = None


async def inject_external_links(
    html_content: str,
    resort_name: str,
    country: str,
    section_name: str | None = None,
    already_linked: set[str] | None = None,
    max_links_per_section: int | None = None,
    resort_slug: str | None = None,
) -> LinkInjectionResult:
    """Inject external links into HTML content.

    Extracts linkable entities, resolves them via brand registry / Google
    Places / Maps search fallback, and injects links into the first mention.

    Args:
        html_content: HTML content to inject links into
        resort_name: Name of the resort for context
        country: Country for context/disambiguation
        section_name: Optional section name for logging and per-section caps
        already_linked: Set of entity names already linked (to avoid duplicates)
        max_links_per_section: Override for section link cap
        resort_slug: Resort slug for UTM tracking (optional)

    Returns:
        LinkInjectionResult with modified content and injection details
    """
    from .intelligence import extract_linkable_entities
    from .links import add_utm_params

    if already_linked is None:
        already_linked = set()

    # Use per-section caps if no override provided
    if max_links_per_section is None:
        max_links_per_section = SECTION_LINK_CAPS.get(section_name or "", 5)

    injected_links: list[InjectedLink] = []
    not_resolved: list[str] = []
    modified_content = html_content
    location_context = f"{resort_name}, {country}"

    try:
        # Extract entities from content
        extraction_result = await extract_linkable_entities(
            content=html_content,
            resort_name=resort_name,
            country=country,
            section_name=section_name,
        )

        if not extraction_result.entities:
            return LinkInjectionResult(
                modified_content=html_content,
                links_injected=[],
                injection_count=0,
                entities_not_resolved=[],
                success=True,
            )

        # Process entities in order of first mention
        entities_sorted = sorted(
            extraction_result.entities,
            key=lambda e: e.first_mention_offset,
        )

        links_added = 0

        for entity in entities_sorted:
            # Skip if already linked or max reached
            if entity.name.lower() in {name.lower() for name in already_linked}:
                continue
            if links_added >= max_links_per_section:
                break

            # Skip low confidence extractions (lowered threshold for wider net)
            if entity.confidence < 0.5:
                continue

            # Resolve entity to links (3-tier: brand → Places → Maps search)
            resolved = await resolve_entity_link(
                name=entity.name,
                entity_type=entity.entity_type,
                location_context=location_context,
                include_affiliate=True,
            )

            if not resolved:
                not_resolved.append(entity.name)
                continue

            # Context-aware destination logic
            choice = _choose_link_url(resolved)

            if not choice.url:
                not_resolved.append(entity.name)
                continue

            link_url = choice.url

            # Add UTM params to non-affiliate, non-Maps-search links
            if not choice.is_affiliate and not choice.is_maps_search_fallback and resort_slug:
                link_url = add_utm_params(
                    url=link_url,
                    resort_slug=resort_slug,
                    category=entity.entity_type,
                    campaign="in_content",
                )

            # Build the link HTML
            rel_attr = get_rel_attribute(
                is_affiliate=choice.is_affiliate,
                is_maps_place_link=choice.is_maps_place_link,
                is_maps_search_fallback=choice.is_maps_search_fallback,
            )

            # Inject link at first mention (case-insensitive)
            # Two-pass strategy: most entities are inside <strong> tags (Round 20+),
            # but some appear as plain text.
            safe_url = html.escape(link_url, quote=True)
            escaped_name = re.escape(entity.name)
            injected = False

            # Pass 1: Match entity wrapped in <strong> tags
            strong_pattern = rf'<strong>({escaped_name})</strong>(?![^<]*</a>)'
            match = re.search(strong_pattern, modified_content, re.IGNORECASE)

            if match:
                original_text = match.group(1)
                link_html_with_original = f'<a href="{safe_url}" rel="{rel_attr}" target="_blank"><strong>{original_text}</strong></a>'
                # Replace the full <strong>...</strong> span
                modified_content = (
                    modified_content[:match.start()]
                    + link_html_with_original
                    + modified_content[match.end():]
                )
                injected = True

            # Pass 2: Fall back to plain text match (not inside tags or attributes)
            if not injected:
                plain_pattern = rf'(?<!["\'/])(?<!<)\b({escaped_name})\b(?![^<]*</a>)'
                match = re.search(plain_pattern, modified_content, re.IGNORECASE)

                if match:
                    original_text = match.group(1)
                    link_html_with_original = f'<a href="{safe_url}" rel="{rel_attr}" target="_blank">{original_text}</a>'
                    modified_content = (
                        modified_content[:match.start(1)]
                        + link_html_with_original
                        + modified_content[match.end(1):]
                    )
                    injected = True

            if injected:
                injected_links.append(
                    InjectedLink(
                        entity_name=entity.name,
                        entity_type=entity.entity_type,
                        original_text=original_text,
                        url=link_url,
                        is_affiliate=choice.is_affiliate,
                        affiliate_program=resolved.affiliate_program,
                        rel_attribute=rel_attr,
                        is_maps_search_fallback=choice.is_maps_search_fallback,
                    )
                )

                already_linked.add(entity.name)
                links_added += 1

        return LinkInjectionResult(
            modified_content=modified_content,
            links_injected=injected_links,
            injection_count=len(injected_links),
            entities_not_resolved=not_resolved,
            success=True,
        )

    except Exception as e:
        return LinkInjectionResult(
            modified_content=html_content,
            links_injected=[],
            injection_count=0,
            entities_not_resolved=[],
            success=False,
            error=str(e),
        )


async def inject_links_in_content_sections(
    content: dict[str, str],
    resort_name: str,
    country: str,
    resort_slug: str | None = None,
) -> tuple[dict[str, str], list[InjectedLink]]:
    """Inject external links across multiple content sections.

    Processes sections in order, tracking already-linked entities to avoid
    redundant links across sections. Uses context-aware destination logic,
    variable per-section caps, and adds UTM params to non-affiliate links.

    Args:
        content: Dict of section_name -> HTML content
        resort_name: Resort name for context
        country: Country for context
        resort_slug: Resort slug for UTM tracking (optional)

    Returns:
        Tuple of (modified_content_dict, all_injected_links)
    """
    # Define which sections to process and in what order
    # (earlier sections get priority for first-mention links)
    section_order = [
        "quick_take",
        "where_to_stay",
        "on_mountain",
        "off_mountain",
        "getting_there",
        "lift_tickets",
        "parent_reviews_summary",
    ]

    already_linked: set[str] = set()
    all_injected_links: list[InjectedLink] = []
    modified_content = dict(content)

    for section_name in section_order:
        if section_name not in content:
            continue

        html_content = content[section_name]
        if not html_content or not isinstance(html_content, str):
            continue

        result = await inject_external_links(
            html_content=html_content,
            resort_name=resort_name,
            country=country,
            section_name=section_name,
            already_linked=already_linked,
            resort_slug=resort_slug,
        )

        if result.success:
            modified_content[section_name] = result.modified_content
            all_injected_links.extend(result.links_injected)

    return modified_content, all_injected_links


# =============================================================================
# EXTERNAL LINK VALIDATION
# =============================================================================


@dataclass
class LinkValidationResult:
    """Result of validating external links."""

    success: bool
    total_checked: int
    valid_count: int
    invalid_count: int
    skipped_count: int
    broken_links: list[dict]  # List of {url, name, entity_type, error}
    error: str | None = None


async def validate_external_links(
    max_links: int = 100,
    timeout_seconds: float = 10.0,
) -> LinkValidationResult:
    """
    Validate external links in entity_link_cache.

    Checks if direct_url links return 200 OK.
    Run weekly to detect broken links that hurt SEO trust signals.

    Args:
        max_links: Maximum number of links to check per run
        timeout_seconds: Timeout for each HTTP request

    Returns:
        LinkValidationResult with counts and broken links list
    """
    client = get_supabase_client()

    # Get links to validate (direct_url not null)
    response = (
        client.table("entity_link_cache")
        .select("id, name_normalized, entity_type, location_context, direct_url")
        .not_.is_("direct_url", "null")
        .limit(max_links)
        .execute()
    )

    links = response.data or []

    if not links:
        return LinkValidationResult(
            success=True,
            total_checked=0,
            valid_count=0,
            invalid_count=0,
            skipped_count=0,
            broken_links=[],
        )

    valid = 0
    invalid = 0
    skipped = 0
    broken: list[dict] = []

    async with httpx.AsyncClient(
        timeout=timeout_seconds,
        follow_redirects=True,
        headers={"User-Agent": "Snowthere-LinkChecker/1.0"},
    ) as http_client:
        for link in links:
            url = link.get("direct_url")
            if not url:
                skipped += 1
                continue

            try:
                # HEAD request is faster and sufficient for validation
                resp = await http_client.head(url)

                if resp.status_code == 405:
                    # Some servers don't allow HEAD, try GET
                    resp = await http_client.get(url)

                if resp.status_code < 400:
                    valid += 1
                else:
                    invalid += 1
                    broken.append({
                        "url": url,
                        "name": link.get("name_normalized"),
                        "entity_type": link.get("entity_type"),
                        "location": link.get("location_context"),
                        "status_code": resp.status_code,
                        "error": f"HTTP {resp.status_code}",
                    })

            except httpx.TimeoutException:
                invalid += 1
                broken.append({
                    "url": url,
                    "name": link.get("name_normalized"),
                    "entity_type": link.get("entity_type"),
                    "location": link.get("location_context"),
                    "error": "Timeout",
                })
            except httpx.ConnectError:
                invalid += 1
                broken.append({
                    "url": url,
                    "name": link.get("name_normalized"),
                    "entity_type": link.get("entity_type"),
                    "location": link.get("location_context"),
                    "error": "Connection failed",
                })
            except Exception:
                skipped += 1  # Count as skipped for unexpected errors

    return LinkValidationResult(
        success=True,
        total_checked=len(links),
        valid_count=valid,
        invalid_count=invalid,
        skipped_count=skipped,
        broken_links=broken,
    )
