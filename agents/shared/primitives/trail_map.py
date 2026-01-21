"""Trail map primitives for ski resort piste data.

Uses OpenStreetMap data via Overpass API to retrieve ski trail information.
OSM has 100,000+ km of ski trails mapped globally under ODbL license.

Design Decision: OpenStreetMap over scraping official resort maps because:
1. Legal: ODbL license allows use with attribution
2. Structured: Data is queryable, not just images
3. Coverage: Global, consistent format
4. Free: No per-resort API costs

Fallback Strategy:
- Tier A: Full piste network (interactive OSM map)
- Tier B: Partial data >50% (OSM map + official link)
- Tier C: Minimal data (satellite + markers + official link)
- Tier D: No coordinates (link to official map only)

Resources:
- OpenSkiMap.org - Uses this same data
- OpenSnowMap.org - Additional snow/ski layers
"""

import asyncio
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from ..config import settings


# Overpass API endpoint (public, rate-limited)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Backup Overpass endpoints if primary is overloaded
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]


class TrailDifficulty(str, Enum):
    """Standard piste difficulty ratings."""

    NOVICE = "novice"  # Green (US) / Green (EU)
    EASY = "easy"  # Blue (US/EU)
    INTERMEDIATE = "intermediate"  # Red (EU) / Blue (US)
    ADVANCED = "advanced"  # Black (US) / Red (EU)
    EXPERT = "expert"  # Double Black / Black
    FREERIDE = "freeride"  # Off-piste


class TrailMapQuality(str, Enum):
    """Quality tier for trail map data."""

    FULL = "full"  # Tier A: Complete piste network
    PARTIAL = "partial"  # Tier B: >50% coverage
    MINIMAL = "minimal"  # Tier C: <50% coverage
    NONE = "none"  # Tier D: No OSM data


@dataclass
class PisteData:
    """Individual ski run/piste data."""

    osm_id: int
    name: str | None
    difficulty: TrailDifficulty | None
    piste_type: str  # 'downhill', 'nordic', 'skitour', etc.
    groomed: bool | None
    lit: bool | None  # Night skiing
    geometry: list[tuple[float, float]]  # List of (lat, lon) coordinates


@dataclass
class LiftData:
    """Ski lift data."""

    osm_id: int
    name: str | None
    lift_type: str  # 'chair_lift', 'gondola', 'drag_lift', etc.
    capacity: int | None  # persons per hour
    geometry: list[tuple[float, float]]


@dataclass
class TrailMapResult:
    """Result from trail map query."""

    resort_name: str
    country: str
    quality: TrailMapQuality
    pistes: list[PisteData] = field(default_factory=list)
    lifts: list[LiftData] = field(default_factory=list)
    center_coords: tuple[float, float] | None = None  # (lat, lon)
    bbox: tuple[float, float, float, float] | None = None  # (south, west, north, east)
    official_map_url: str | None = None
    osm_attribution: str = "© OpenStreetMap contributors, ODbL"
    confidence: float = 0.0  # 0-1 based on data completeness
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "resort_name": self.resort_name,
            "country": self.country,
            "quality": self.quality.value,
            "piste_count": len(self.pistes),
            "lift_count": len(self.lifts),
            "center_coords": self.center_coords,
            "bbox": self.bbox,
            "official_map_url": self.official_map_url,
            "osm_attribution": self.osm_attribution,
            "confidence": self.confidence,
            "pistes": [
                {
                    "osm_id": p.osm_id,
                    "name": p.name,
                    "difficulty": p.difficulty.value if p.difficulty else None,
                    "piste_type": p.piste_type,
                    "groomed": p.groomed,
                    "lit": p.lit,
                    "geometry": p.geometry,
                }
                for p in self.pistes
            ],
            "lifts": [
                {
                    "osm_id": l.osm_id,
                    "name": l.name,
                    "lift_type": l.lift_type,
                    "capacity": l.capacity,
                    "geometry": l.geometry,
                }
                for l in self.lifts
            ],
        }


def calculate_bbox(
    lat: float, lon: float, radius_km: float = 5.0
) -> tuple[float, float, float, float]:
    """
    Calculate bounding box around a point.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius_km: Radius in kilometers

    Returns:
        (south, west, north, east) bounding box
    """
    # Approximate degrees per km
    lat_per_km = 1 / 111.0  # ~111km per degree latitude
    lon_per_km = 1 / (111.0 * math.cos(math.radians(lat)))  # varies with latitude

    delta_lat = radius_km * lat_per_km
    delta_lon = radius_km * lon_per_km

    return (
        lat - delta_lat,  # south
        lon - delta_lon,  # west
        lat + delta_lat,  # north
        lon + delta_lon,  # east
    )


def parse_difficulty(tags: dict[str, str]) -> TrailDifficulty | None:
    """Parse piste difficulty from OSM tags."""
    difficulty = tags.get("piste:difficulty")

    mapping = {
        "novice": TrailDifficulty.NOVICE,
        "easy": TrailDifficulty.EASY,
        "intermediate": TrailDifficulty.INTERMEDIATE,
        "advanced": TrailDifficulty.ADVANCED,
        "expert": TrailDifficulty.EXPERT,
        "freeride": TrailDifficulty.FREERIDE,
    }

    return mapping.get(difficulty)


async def query_overpass(query: str, timeout: int = 60) -> dict[str, Any] | None:
    """
    Execute Overpass API query with fallback endpoints.

    Args:
        query: Overpass QL query string
        timeout: Request timeout in seconds

    Returns:
        JSON response or None on failure
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        for endpoint in OVERPASS_ENDPOINTS:
            try:
                response = await client.post(
                    endpoint,
                    data={"data": query},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Overpass query failed at {endpoint}: {e}")
                continue

    return None


async def get_trail_map(
    resort_name: str,
    country: str,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float = 8.0,
) -> TrailMapResult:
    """
    Fetch ski trail map data from OpenStreetMap.

    This is the main entry point for trail map data. It queries the Overpass API
    for ski pistes and lifts within a bounding box around the resort coordinates.

    Args:
        resort_name: Name of the ski resort
        country: Country name
        latitude: Resort center latitude (optional if using search)
        longitude: Resort center longitude (optional if using search)
        radius_km: Search radius in kilometers (default 8km for larger resorts)

    Returns:
        TrailMapResult with piste data, lift data, and quality assessment
    """
    result = TrailMapResult(
        resort_name=resort_name,
        country=country,
        quality=TrailMapQuality.NONE,
    )

    # If no coordinates provided, try to search by name
    if latitude is None or longitude is None:
        coords = await search_resort_location(resort_name, country)
        if coords:
            latitude, longitude = coords
        else:
            result.error = "No coordinates available and location search failed"
            return result

    result.center_coords = (latitude, longitude)
    bbox = calculate_bbox(latitude, longitude, radius_km)
    result.bbox = bbox

    # Build Overpass query for ski pistes and lifts
    # Query includes: pistes (downhill, nordic), lifts (all types), ski area boundaries
    query = f"""
    [out:json][timeout:45];
    (
      // Ski pistes
      way["piste:type"~"downhill|nordic|skitour"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      relation["piste:type"~"downhill|nordic|skitour"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});

      // Ski lifts
      way["aerialway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});

      // Ski area boundaries (for context)
      relation["landuse"="winter_sports"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body;
    >;
    out skel qt;
    """

    data = await query_overpass(query)

    if not data:
        result.error = "Overpass API query failed"
        return result

    elements = data.get("elements", [])

    # Build node lookup for resolving way geometries
    nodes: dict[int, tuple[float, float]] = {}
    for el in elements:
        if el.get("type") == "node":
            nodes[el["id"]] = (el["lat"], el["lon"])

    # Parse pistes
    for el in elements:
        if el.get("type") in ("way", "relation"):
            tags = el.get("tags", {})
            piste_type = tags.get("piste:type")

            if piste_type:
                # Get geometry from way nodes
                geometry = []
                for node_id in el.get("nodes", []):
                    if node_id in nodes:
                        geometry.append(nodes[node_id])

                if geometry:
                    piste = PisteData(
                        osm_id=el["id"],
                        name=tags.get("name"),
                        difficulty=parse_difficulty(tags),
                        piste_type=piste_type,
                        groomed=tags.get("piste:grooming") == "classic",
                        lit=tags.get("piste:lit") == "yes",
                        geometry=geometry,
                    )
                    result.pistes.append(piste)

    # Parse lifts
    for el in elements:
        if el.get("type") == "way":
            tags = el.get("tags", {})
            lift_type = tags.get("aerialway")

            if lift_type:
                geometry = []
                for node_id in el.get("nodes", []):
                    if node_id in nodes:
                        geometry.append(nodes[node_id])

                if geometry:
                    lift = LiftData(
                        osm_id=el["id"],
                        name=tags.get("name"),
                        lift_type=lift_type,
                        capacity=int(tags["aerialway:capacity"])
                        if tags.get("aerialway:capacity", "").isdigit()
                        else None,
                        geometry=geometry,
                    )
                    result.lifts.append(lift)

    # Assess quality based on data completeness
    piste_count = len(result.pistes)
    lift_count = len(result.lifts)

    if piste_count >= 20 and lift_count >= 5:
        result.quality = TrailMapQuality.FULL
        result.confidence = 0.9
    elif piste_count >= 10 or lift_count >= 3:
        result.quality = TrailMapQuality.PARTIAL
        result.confidence = 0.6
    elif piste_count > 0 or lift_count > 0:
        result.quality = TrailMapQuality.MINIMAL
        result.confidence = 0.3
    else:
        result.quality = TrailMapQuality.NONE
        result.confidence = 0.0

    return result


async def search_resort_location(
    resort_name: str, country: str
) -> tuple[float, float] | None:
    """
    Search for resort coordinates using Nominatim.

    This is a fallback when coordinates aren't in our database.
    Note: Nominatim has rate limits (1 request/second for free tier).
    """
    query = f"{resort_name} ski resort, {country}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                },
                headers={
                    "User-Agent": "Snowthere/1.0 (family-ski-directory)",
                },
            )
            response.raise_for_status()
            results = response.json()

            if results:
                return (float(results[0]["lat"]), float(results[0]["lon"]))
        except httpx.HTTPError as e:
            print(f"Nominatim search failed: {e}")

    return None


async def get_difficulty_breakdown(pistes: list[PisteData]) -> dict[str, int]:
    """
    Get count of pistes by difficulty level.

    Returns dict like: {"novice": 5, "easy": 12, "intermediate": 8, "advanced": 3}
    """
    breakdown: dict[str, int] = {}

    for piste in pistes:
        if piste.difficulty:
            key = piste.difficulty.value
            breakdown[key] = breakdown.get(key, 0) + 1
        else:
            breakdown["unknown"] = breakdown.get("unknown", 0) + 1

    return breakdown


async def search_official_trail_map(resort_name: str, country: str) -> str | None:
    """
    Search for official resort trail map URL.

    Uses Brave search to find the official trail map page.
    """
    from .research import brave_search

    query = f"{resort_name} {country} official trail map piste map"
    results = await brave_search(query, num_results=5)

    # Look for official resort domain in results
    resort_slug = resort_name.lower().replace(" ", "")

    for result in results:
        url_lower = result.url.lower()
        # Prioritize URLs that look like official resort sites
        if any(
            pattern in url_lower
            for pattern in [resort_slug, "trail-map", "piste-map", "pistemap"]
        ):
            return result.url

    # Fallback to first result if no perfect match
    if results:
        return results[0].url

    return None


async def get_trail_map_with_fallback(
    resort_name: str,
    country: str,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float = 8.0,
) -> TrailMapResult:
    """
    Fetch trail map data with fallback to official URL when OSM fails.

    This is the recommended entry point for trail map data. It:
    1. Tries OSM via get_trail_map()
    2. If quality is "none", searches for official trail map URL
    3. Updates quality to "minimal" if we have at least a link

    Args:
        resort_name: Name of the ski resort
        country: Country name
        latitude: Resort center latitude
        longitude: Resort center longitude
        radius_km: Search radius in kilometers

    Returns:
        TrailMapResult with best available data
    """
    result = await get_trail_map(resort_name, country, latitude, longitude, radius_km)

    # If OSM returned no data, try to find official trail map URL
    if result.quality == TrailMapQuality.NONE:
        try:
            official_url = await search_official_trail_map(resort_name, country)
            if official_url:
                result.official_map_url = official_url
                result.quality = TrailMapQuality.MINIMAL
                result.confidence = 0.2
                result.error = None  # Clear error since we have a fallback
        except Exception as e:
            # Don't let fallback failure affect the result
            print(f"Official trail map search failed: {e}")

    return result


# Convenience function for checking if trail map is available
async def has_trail_map_data(
    latitude: float, longitude: float, radius_km: float = 5.0
) -> bool:
    """Quick check if OSM has trail data for a location."""
    bbox = calculate_bbox(latitude, longitude, radius_km)

    query = f"""
    [out:json][timeout:10];
    way["piste:type"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    out count;
    """

    data = await query_overpass(query, timeout=15)

    if data:
        count = data.get("elements", [{}])[0].get("tags", {}).get("total", 0)
        return int(count) > 0

    return False
