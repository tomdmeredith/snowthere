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

import html
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
    }

    included_type = type_mapping.get(entity_type)

    # Build search query with location context
    search_query = f"{name} {location_context}"

    try:
        async with httpx.AsyncClient() as client:
            # Use Text Search (New) API
            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri,places.formattedAddress",
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
# UTILITY FUNCTIONS
# ============================================================================


def get_rel_attribute(
    is_affiliate: bool = False,
    is_ugc: bool = False,
    is_official: bool = False,
) -> str:
    """Get the appropriate rel attribute for a link.

    SEO + referral tracking best practices:
    - Official resort links: rel="noopener" (dofollow — authoritative sources)
    - Affiliate links: rel="sponsored noopener" (Google-compliant for paid links)
    - Maps links: rel="nofollow noopener" (no equity to Maps, still sends referrer)
    - Entity links (hotels, restaurants, etc.): rel="noopener" (dofollow, sends referrer)

    Rationale: Entity links are genuine editorial recommendations. Dofollow
    passes SEO equity (good for both parties). Sending the referrer lets
    businesses see snowthere.com traffic in their analytics — enabling
    future partnership conversations.

    Args:
        is_affiliate: Whether this is an affiliate link
        is_ugc: Whether this is user-generated content (Maps, etc.)
        is_official: Whether this is an official resort website link

    Returns:
        Appropriate rel attribute value
    """
    if is_official:
        return "noopener"
    if is_affiliate:
        return "sponsored noopener"
    if is_ugc:
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
            .lt("expires_at", datetime.utcnow().isoformat())
            .execute()
        )

        return len(result.data or [])
    except Exception as e:
        print(f"Failed to clear expired cache: {e}")
        return 0


# ============================================================================
# LINK INJECTION
# ============================================================================


def _choose_link_url(resolved: ResolvedEntity) -> tuple[str | None, bool, bool]:
    """Choose the best link URL based on entity type.

    Context-aware destination logic using priority table:
    - Booking types (hotel, rental): affiliate > direct > maps
    - Location types (restaurant, grocery): maps > direct
    - Info/registration types (ski_school, activity, transport): direct > maps
    - Default: affiliate > direct > maps

    Args:
        resolved: The resolved entity with available URLs

    Returns:
        Tuple of (url, is_affiliate, is_ugc)
    """
    # Priority table: ordered list of (url_attr, is_affiliate, is_ugc)
    PRIORITY = {
        "hotel":          [("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True)],
        "rental":         [("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True)],
        "restaurant":     [("maps_url", False, True), ("direct_url", False, False)],
        "grocery":        [("maps_url", False, True), ("direct_url", False, False)],
        "ski_school":     [("direct_url", False, False), ("maps_url", False, True)],
        "activity":       [("direct_url", False, False), ("maps_url", False, True)],
        "transport":      [("direct_url", False, False), ("maps_url", False, True)],
        "transportation": [("direct_url", False, False), ("maps_url", False, True)],
        "retail":         [("direct_url", False, False), ("maps_url", False, True)],
    }
    DEFAULT = [("affiliate_url", True, False), ("direct_url", False, False), ("maps_url", False, True)]

    for attr, is_affiliate, is_ugc in PRIORITY.get(resolved.entity_type, DEFAULT):
        url = getattr(resolved, attr, None)
        if url:
            return url, is_affiliate, is_ugc

    return None, False, False


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
    max_links_per_section: int = 5,
    resort_slug: str | None = None,
) -> LinkInjectionResult:
    """Inject external links into HTML content.

    Extracts linkable entities, resolves them via Google Places / affiliates,
    and injects links into the first mention of each entity.

    Uses context-aware destination logic: hotels → booking sites,
    restaurants → Google Maps, grocery → Google Maps, etc.

    Args:
        html_content: HTML content to inject links into
        resort_name: Name of the resort for context
        country: Country for context/disambiguation
        section_name: Optional section name for logging
        already_linked: Set of entity names already linked (to avoid duplicates)
        max_links_per_section: Maximum links to inject per section
        resort_slug: Resort slug for UTM tracking (optional)

    Returns:
        LinkInjectionResult with modified content and injection details

    Link Rules:
    - First mention only (no redundant links)
    - Affiliate links use rel="sponsored noopener"
    - Google Maps links use rel="nofollow noopener"
    - Entity links (hotels, restaurants, etc.) use rel="noopener" (dofollow, sends referrer)
    """
    from .intelligence import extract_linkable_entities
    from .links import add_utm_params

    if already_linked is None:
        already_linked = set()

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

            # Skip low confidence extractions
            if entity.confidence < 0.6:
                continue

            # Resolve entity to links
            resolved = await resolve_entity_link(
                name=entity.name,
                entity_type=entity.entity_type,
                location_context=location_context,
                include_affiliate=True,
            )

            if not resolved or resolved.confidence < 0.5:
                not_resolved.append(entity.name)
                continue

            # Context-aware destination logic
            link_url, is_affiliate, is_ugc = _choose_link_url(resolved)

            if not link_url:
                not_resolved.append(entity.name)
                continue

            # Add UTM params to non-affiliate links
            if not is_affiliate and resort_slug:
                link_url = add_utm_params(
                    url=link_url,
                    resort_slug=resort_slug,
                    category=entity.entity_type,
                    campaign="in_content",
                )

            # Build the link HTML
            rel_attr = get_rel_attribute(is_affiliate=is_affiliate, is_ugc=is_ugc)

            # Inject link at first mention (case-insensitive, word boundary)
            # Use regex to find first mention not already in a link
            pattern = rf'(?<!["\'>])(?<!/)\b({re.escape(entity.name)})\b(?![^<]*</a>)'
            match = re.search(pattern, modified_content, re.IGNORECASE)

            if match:
                # Replace first occurrence only
                original_text = match.group(1)
                safe_url = html.escape(link_url, quote=True)
                link_html_with_original = f'<a href="{safe_url}" rel="{rel_attr}" target="_blank">{original_text}</a>'

                modified_content = (
                    modified_content[:match.start(1)]
                    + link_html_with_original
                    + modified_content[match.end(1):]
                )

                injected_links.append(
                    InjectedLink(
                        entity_name=entity.name,
                        entity_type=entity.entity_type,
                        original_text=original_text,
                        url=link_url,
                        is_affiliate=is_affiliate,
                        affiliate_program=resolved.affiliate_program,
                        rel_attribute=rel_attr,
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
    redundant links across sections. Uses context-aware destination logic
    and adds UTM params to non-affiliate links.

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
            max_links_per_section=3,  # Limit per section to avoid over-linking
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
            except Exception as e:
                skipped += 1  # Count as skipped for unexpected errors

    return LinkValidationResult(
        success=True,
        total_checked=len(links),
        valid_count=valid,
        invalid_count=invalid,
        skipped_count=skipped,
        broken_links=broken,
    )


