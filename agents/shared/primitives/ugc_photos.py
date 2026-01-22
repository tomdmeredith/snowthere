"""
UGC Photos Primitives - User-Generated Content via Google Places API

Fetches real photos from Google Places to provide social proof
that families actually visit these resorts.

Pivoted from Instagram (API no longer viable) to Google Places.

Cost: ~$0.06 per resort (first lookup)
- Place Details: $0.017
- Photo fetches: $0.007 each (5 photos = $0.035)
- Optional vision filtering: ~$0.01

With place_id caching, subsequent lookups save $0.003 per resort.
"""

import asyncio
import base64
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import httpx

from shared.config import settings
from shared.supabase_client import get_supabase_client


# Country name variants for better Google Places matching
COUNTRY_VARIANTS = {
    "Switzerland": ["Switzerland", "Suisse", "Schweiz", "Svizzera"],
    "Austria": ["Austria", "Österreich"],
    "France": ["France", "Francia"],
    "Germany": ["Germany", "Deutschland"],
    "Italy": ["Italy", "Italia"],
    "Spain": ["Spain", "España"],
    "Norway": ["Norway", "Norge"],
    "Sweden": ["Sweden", "Sverige"],
    "Finland": ["Finland", "Suomi"],
    "Japan": ["Japan", "日本", "Nippon"],
    "South Korea": ["South Korea", "Korea", "한국"],
    "Czech Republic": ["Czech Republic", "Czechia", "Česko"],
    "Poland": ["Poland", "Polska"],
    "Slovakia": ["Slovakia", "Slovensko"],
    "Slovenia": ["Slovenia", "Slovenija"],
}


def _transliterate_name(name: str) -> str:
    """Convert non-Latin characters to ASCII equivalents.

    Helps with Google Places API matching for Russian, Arabic, CJK, etc.
    Falls back gracefully if unidecode is not installed.
    """
    try:
        from unidecode import unidecode
        return unidecode(name)
    except ImportError:
        # Graceful fallback - return original name
        return name


def _get_country_variants(country: str) -> list[str]:
    """Get all name variants for a country."""
    variants = COUNTRY_VARIANTS.get(country, [country])
    if country not in variants:
        variants = [country] + list(variants)
    return variants


async def get_cached_place_id(resort_name: str, country: str) -> Optional[str]:
    """Check if we have a cached place_id for this resort.

    Queries the resorts table for google_place_id column.
    Saves API calls on subsequent lookups.
    """
    try:
        supabase = get_supabase_client()

        # Case-insensitive search
        result = supabase.table("resorts")\
            .select("google_place_id")\
            .ilike("name", resort_name)\
            .ilike("country", country)\
            .not_.is_("google_place_id", "null")\
            .limit(1)\
            .execute()

        if result.data and result.data[0].get("google_place_id"):
            return result.data[0]["google_place_id"]

        return None

    except Exception as e:
        print(f"Error checking cached place_id: {e}")
        return None


async def cache_place_id(resort_name: str, country: str, place_id: str) -> bool:
    """Cache a place_id in the resorts table.

    Updates the google_place_id column for the matching resort.
    """
    try:
        supabase = get_supabase_client()

        # Find the resort and update its place_id
        result = supabase.table("resorts")\
            .update({"google_place_id": place_id})\
            .ilike("name", resort_name)\
            .ilike("country", country)\
            .execute()

        return len(result.data) > 0 if result.data else False

    except Exception as e:
        print(f"Error caching place_id: {e}")
        return False


class PhotoCategory(str, Enum):
    """Categories for UGC photos."""
    FAMILY = "family"
    SKIING = "skiing"
    LODGE = "lodge"
    SCENERY = "scenery"
    FOOD = "food"
    ACTIVITIES = "activities"
    UNKNOWN = "unknown"


@dataclass
class UGCPhoto:
    """A user-generated photo from Google Places."""
    url: str
    source: str = "google_places"
    photo_reference: str = ""
    width: int = 0
    height: int = 0
    attributions: list[str] = field(default_factory=list)
    category: PhotoCategory = PhotoCategory.UNKNOWN
    relevance_score: float = 0.0  # 0-1, higher = more family-relevant


@dataclass
class UGCPhotoResult:
    """Result of fetching UGC photos for a resort."""
    success: bool
    photos: list[UGCPhoto] = field(default_factory=list)
    place_id: Optional[str] = None
    place_name: Optional[str] = None
    total_found: int = 0
    filtered_count: int = 0
    cost: float = 0.0
    error: Optional[str] = None


async def find_place_id(
    resort_name: str,
    country: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    use_cache: bool = True,
) -> Optional[str]:
    """
    Find the Google Places ID for a ski resort using multiple strategies.

    Uses a probabilistic approach - tries multiple query formats and strategies
    to maximize chances of finding the correct place.

    Strategies:
    0. Check cache first (saves API calls)
    1. Nearby search with coordinates (most accurate if coords available)
    2. Text search with multiple query formats
    3. Transliterated name search (for non-Latin names)
    4. Country variant search (Schweiz vs Switzerland)

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        latitude: Optional latitude for more accurate results
        longitude: Optional longitude for more accurate results
        use_cache: Whether to check/use cached place_id (default True)

    Returns:
        Google Place ID or None if not found
    """
    # Strategy 0: Check cache first
    if use_cache:
        cached = await get_cached_place_id(resort_name, country)
        if cached:
            return cached

    # Use dedicated Places API key, fall back to generic Google key
    api_key = settings.google_places_api_key or settings.google_api_key
    if not api_key:
        print("⚠️  GOOGLE_PLACES_API_KEY not configured - skipping UGC photo lookup")
        return None

    # Generate name variants (original + transliterated)
    name_variants = [resort_name]
    transliterated = _transliterate_name(resort_name)
    if transliterated != resort_name:
        name_variants.append(transliterated)

    # Get country variants
    country_variants = _get_country_variants(country)

    place_id = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Strategy 1: Nearby search with coordinates (most accurate)
        if latitude and longitude:
            for name in name_variants:
                for keyword in [name, f"{name} ski", f"{name} mountain"]:
                    try:
                        response = await client.get(
                            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                            params={
                                "location": f"{latitude},{longitude}",
                                "radius": 10000,  # 10km radius
                                "keyword": keyword,
                                "key": api_key,
                            },
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status") == "OK" and data.get("results"):
                                place_id = data["results"][0].get("place_id")
                                break
                    except httpx.HTTPError:
                        continue
                if place_id:
                    break
            if place_id:
                # Cache the result before returning
                if use_cache:
                    await cache_place_id(resort_name, country, place_id)
                return place_id

        # Strategy 2: Text search with multiple query formats and variants
        for name in name_variants:
            for country_var in country_variants:
                queries = [
                    f"{name} ski resort {country_var}",
                    f"{name} ski area {country_var}",
                    f"{name} skiing {country_var}",
                    f"{name} {country_var}",  # Simple: "La Plagne France"
                    f"{name} mountain {country_var}",
                ]

                for query in queries:
                    try:
                        params = {
                            "input": query,
                            "inputtype": "textquery",
                            "fields": "place_id,name,formatted_address,geometry",
                            "key": api_key,
                        }

                        # Add location bias if coordinates provided
                        if latitude and longitude:
                            params["locationbias"] = f"circle:10000@{latitude},{longitude}"

                        response = await client.get(
                            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                            params=params,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status") == "OK" and data.get("candidates"):
                                place_id = data["candidates"][0].get("place_id")
                                # Cache the result before returning
                                if use_cache:
                                    await cache_place_id(resort_name, country, place_id)
                                return place_id

                    except httpx.HTTPError:
                        continue

        # Strategy 3: Fallback - just the name without country
        for name in name_variants:
            for query in [f"{name} ski", name]:
                try:
                    params = {
                        "input": query,
                        "inputtype": "textquery",
                        "fields": "place_id,name,formatted_address,geometry",
                        "key": api_key,
                    }

                    if latitude and longitude:
                        params["locationbias"] = f"circle:10000@{latitude},{longitude}"

                    response = await client.get(
                        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                        params=params,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "OK" and data.get("candidates"):
                            place_id = data["candidates"][0].get("place_id")
                            if use_cache:
                                await cache_place_id(resort_name, country, place_id)
                            return place_id

                except httpx.HTTPError:
                    continue

        return None  # All strategies failed


async def get_place_details(place_id: str) -> Optional[dict]:
    """
    Get details for a place including photo references.

    Args:
        place_id: Google Place ID

    Returns:
        Place details dict or None
    """
    # Use dedicated Places API key, fall back to generic Google key
    api_key = settings.google_places_api_key or settings.google_api_key
    if not api_key:
        return None

    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {
            "place_id": place_id,
            "fields": "name,photos,rating,user_ratings_total,editorial_summary",
            "key": api_key,
        }

        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params=params,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("status") == "OK":
            return data.get("result")

        return None


async def fetch_place_photo(
    photo_reference: str,
    max_width: int = 800,
    max_height: int = 600,
) -> Optional[bytes]:
    """
    Fetch a photo from Google Places.

    Args:
        photo_reference: Photo reference from Place Details
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels

    Returns:
        Photo bytes or None
    """
    # Use dedicated Places API key, fall back to generic Google key
    api_key = settings.google_places_api_key or settings.google_api_key
    if not api_key:
        return None

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        params = {
            "photo_reference": photo_reference,
            "maxwidth": max_width,
            "maxheight": max_height,
            "key": api_key,
        }

        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/photo",
            params=params,
        )

        if response.status_code == 200:
            return response.content

        return None


async def upload_ugc_photo_to_storage(
    photo_data: bytes,
    resort_id: str,
    photo_index: int,
) -> Optional[str]:
    """
    Upload a UGC photo to Supabase Storage.

    Args:
        photo_data: Photo bytes
        resort_id: Resort UUID
        photo_index: Index for naming

    Returns:
        Public URL or None
    """
    try:
        supabase = get_supabase_client()

        # Generate unique filename based on content hash
        content_hash = hashlib.md5(photo_data).hexdigest()[:8]
        filename = f"ugc/{resort_id}/ugc_{photo_index}_{content_hash}.jpg"

        # Upload to storage
        result = supabase.storage.from_("resort-images").upload(
            path=filename,
            file=photo_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )

        # Get public URL
        public_url = supabase.storage.from_("resort-images").get_public_url(filename)
        return public_url

    except Exception as e:
        print(f"Failed to upload UGC photo: {e}")
        return None


async def classify_photo_with_vision(
    photo_data: bytes,
) -> tuple[PhotoCategory, float]:
    """
    Use Gemini vision to classify if a photo is family-relevant.

    Args:
        photo_data: Photo bytes

    Returns:
        Tuple of (category, relevance_score)
    """
    if not settings.google_api_key:
        return PhotoCategory.UNKNOWN, 0.5

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.google_api_key)

        # Encode image to base64
        image_b64 = base64.b64encode(photo_data).decode("utf-8")

        prompt = """Analyze this ski resort photo and classify it.

Return a JSON object with:
{
    "category": "family" | "skiing" | "lodge" | "scenery" | "food" | "activities" | "unknown",
    "family_relevance": 0.0-1.0,
    "has_children": true/false,
    "has_ski_school": true/false,
    "shows_beginner_terrain": true/false,
    "reasoning": "brief explanation"
}

Higher family_relevance for:
- Photos showing families or children
- Beginner slopes and learning areas
- Cozy lodge interiors
- Family-friendly activities
- Ski school scenes

Lower family_relevance for:
- Expert terrain, cliff drops
- Nightlife, bars
- Close-up food only
- Empty landscapes
- Parking lots
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=photo_data,
                            )
                        ),
                    ]
                )
            ],
        )

        # Parse response
        import json
        response_text = response.text.strip()

        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text)

        category_map = {
            "family": PhotoCategory.FAMILY,
            "skiing": PhotoCategory.SKIING,
            "lodge": PhotoCategory.LODGE,
            "scenery": PhotoCategory.SCENERY,
            "food": PhotoCategory.FOOD,
            "activities": PhotoCategory.ACTIVITIES,
        }

        category = category_map.get(result.get("category", "unknown"), PhotoCategory.UNKNOWN)
        relevance = float(result.get("family_relevance", 0.5))

        return category, relevance

    except Exception as e:
        print(f"Vision classification failed: {e}")
        return PhotoCategory.UNKNOWN, 0.5


async def fetch_ugc_photos(
    resort_name: str,
    country: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    max_photos: int = 10,
    filter_with_vision: bool = True,
    min_relevance: float = 0.4,
) -> UGCPhotoResult:
    """
    Fetch user-generated photos for a ski resort from Google Places.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        latitude: Optional latitude for accuracy
        longitude: Optional longitude for accuracy
        max_photos: Maximum photos to return
        filter_with_vision: Use Gemini to filter for family-relevant photos
        min_relevance: Minimum relevance score to keep (0-1)

    Returns:
        UGCPhotoResult with photos and metadata
    """
    cost = 0.0

    # Step 1: Find Place ID
    place_id = await find_place_id(resort_name, country, latitude, longitude)
    cost += 0.003  # Find Place API cost

    if not place_id:
        return UGCPhotoResult(
            success=False,
            error=f"Could not find Google Place for {resort_name}, {country}",
            cost=cost,
        )

    # Step 2: Get Place Details with photo references
    details = await get_place_details(place_id)
    cost += 0.017  # Place Details API cost

    if not details:
        return UGCPhotoResult(
            success=False,
            place_id=place_id,
            error="Could not fetch place details",
            cost=cost,
        )

    photo_refs = details.get("photos", [])
    total_found = len(photo_refs)

    if not photo_refs:
        return UGCPhotoResult(
            success=True,
            place_id=place_id,
            place_name=details.get("name"),
            photos=[],
            total_found=0,
            cost=cost,
        )

    # Step 3: Fetch photos (limit to save costs)
    photos_to_fetch = photo_refs[:max_photos]
    photos: list[UGCPhoto] = []

    for ref_data in photos_to_fetch:
        photo_ref = ref_data.get("photo_reference")
        if not photo_ref:
            continue

        photo_bytes = await fetch_place_photo(photo_ref)
        cost += 0.007  # Photo API cost

        if not photo_bytes:
            continue

        # Classify with vision if enabled
        category = PhotoCategory.UNKNOWN
        relevance = 0.5

        if filter_with_vision:
            category, relevance = await classify_photo_with_vision(photo_bytes)
            cost += 0.002  # Vision API cost (Gemini Flash is cheap)

            # Skip low-relevance photos
            if relevance < min_relevance:
                continue

        # Create photo object (URL will be set after storage upload)
        photo = UGCPhoto(
            url="",  # Will be set after upload
            photo_reference=photo_ref,
            width=ref_data.get("width", 0),
            height=ref_data.get("height", 0),
            attributions=ref_data.get("html_attributions", []),
            category=category,
            relevance_score=relevance,
        )

        # Store photo bytes temporarily for upload
        photo._bytes = photo_bytes  # type: ignore
        photos.append(photo)

    # Sort by relevance
    photos.sort(key=lambda p: p.relevance_score, reverse=True)

    return UGCPhotoResult(
        success=True,
        photos=photos,
        place_id=place_id,
        place_name=details.get("name"),
        total_found=total_found,
        filtered_count=len(photos),
        cost=cost,
    )


async def fetch_and_store_ugc_photos(
    resort_id: str,
    resort_name: str,
    country: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    max_photos: int = 8,
    filter_with_vision: bool = True,
) -> UGCPhotoResult:
    """
    Fetch UGC photos and store them in Supabase.

    This is the main entry point for the pipeline.

    Args:
        resort_id: Resort UUID for storage path
        resort_name: Name of the ski resort
        country: Country where resort is located
        latitude: Optional latitude
        longitude: Optional longitude
        max_photos: Maximum photos to store
        filter_with_vision: Use vision to filter family-relevant photos

    Returns:
        UGCPhotoResult with stored photos
    """
    # Fetch photos
    result = await fetch_ugc_photos(
        resort_name=resort_name,
        country=country,
        latitude=latitude,
        longitude=longitude,
        max_photos=max_photos,
        filter_with_vision=filter_with_vision,
    )

    if not result.success or not result.photos:
        return result

    # Upload to storage and update URLs
    stored_photos: list[UGCPhoto] = []

    for i, photo in enumerate(result.photos):
        if not hasattr(photo, "_bytes") or not photo._bytes:  # type: ignore
            continue

        url = await upload_ugc_photo_to_storage(
            photo_data=photo._bytes,  # type: ignore
            resort_id=resort_id,
            photo_index=i,
        )

        if url:
            photo.url = url
            stored_photos.append(photo)

    # Store references in database
    if stored_photos:
        try:
            supabase = get_supabase_client()

            for photo in stored_photos:
                supabase.table("resort_images").upsert({
                    "resort_id": resort_id,
                    "image_type": "ugc",
                    "image_url": photo.url,  # Fixed: was "url", schema has "image_url"
                    "source": "google_places",
                    "alt_text": f"User photo of {resort_name} - {photo.category.value}",
                    "attribution": "; ".join(photo.attributions) if photo.attributions else None,
                    "metadata": {
                        "category": photo.category.value,
                        "relevance_score": photo.relevance_score,
                        "place_id": result.place_id,
                    },
                }).execute()
        except Exception as e:
            print(f"Failed to store UGC photo references: {e}")

    result.photos = stored_photos
    return result


# Convenience function for pipeline integration
async def get_ugc_photos_for_resort(
    resort_id: str,
    resort_name: str,
    country: str,
    **kwargs,
) -> list[dict]:
    """
    Simple wrapper returning list of photo dicts for pipeline.

    Returns:
        List of photo dictionaries with url, category, relevance_score
    """
    result = await fetch_and_store_ugc_photos(
        resort_id=resort_id,
        resort_name=resort_name,
        country=country,
        **kwargs,
    )

    if not result.success:
        return []

    return [
        {
            "url": photo.url,
            "category": photo.category.value,
            "relevance_score": photo.relevance_score,
            "attributions": photo.attributions,
        }
        for photo in result.photos
        if photo.url
    ]
