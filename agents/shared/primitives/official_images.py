"""Official Resort Images - Fetch real photos from resort websites.

This primitive fetches authentic images from official resort websites,
prioritizing real photography over AI-generated content.

Philosophy: Families deserve to see REAL images of resorts they're planning
to visit - not AI-generated approximations.

Image Sources (in priority order):
1. Official resort website (most authentic)
2. Google Places UGC (real visitor photos)
3. NO AI-generated images for hero/main photos

Cost: Free (scraping) + ~$0.06 for UGC fallback
"""

import asyncio
import hashlib
import re
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..config import settings
from ..supabase_client import get_supabase_client
from .system import log_reasoning


@dataclass
class OfficialImageResult:
    """Result from official image fetch."""

    success: bool
    url: str | None = None
    source_url: str | None = None  # Original URL on resort website
    stored_url: str | None = None  # Our Supabase storage URL
    source: str = "official"  # 'official', 'google_places'
    alt_text: str | None = None
    attribution: str | None = None
    error: str | None = None


# Common image patterns on ski resort websites
IMAGE_PATTERNS = [
    # Hero/banner images
    r'hero[-_]?image',
    r'banner[-_]?image',
    r'main[-_]?image',
    r'header[-_]?image',
    r'featured[-_]?image',
    # Background images
    r'bg[-_]?image',
    r'background',
    # Gallery images
    r'gallery',
    r'carousel',
    r'slider',
    r'slideshow',
]

# Domains we trust for resort images
TRUSTED_IMAGE_DOMAINS = [
    'cloudinary.com',
    'imgix.net',
    'contentful.com',
    'sanity.io',
    'prismic.io',
    'amazonaws.com',
    'googleusercontent.com',
]

# Minimum image dimensions (pixels) - skip tiny images
MIN_WIDTH = 800
MIN_HEIGHT = 400


async def find_resort_website(
    resort_name: str,
    country: str,
) -> str | None:
    """Find the official website URL for a ski resort.

    Uses Brave Search to find the official resort website.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located

    Returns:
        Official website URL or None
    """
    if not settings.brave_api_key:
        return None

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.brave_api_key,
    }

    # Search for official resort website
    queries = [
        f"{resort_name} ski resort official website",
        f"{resort_name} {country} skiing official",
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        for query in queries:
            try:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params={"q": query, "count": 5},
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("web", {}).get("results", [])
                for result in results:
                    url = result.get("url", "")
                    title = result.get("title", "").lower()

                    # Look for official resort domains
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()

                    # Skip aggregator sites
                    skip_domains = [
                        'tripadvisor', 'yelp', 'booking.com', 'expedia',
                        'skiresort.info', 'onthesnow.com', 'snow-forecast',
                        'wikipedia', 'facebook', 'instagram', 'twitter',
                    ]
                    if any(skip in domain for skip in skip_domains):
                        continue

                    # Prefer domains containing the resort name
                    resort_slug = resort_name.lower().replace(' ', '')
                    if resort_slug in domain.replace('-', '').replace('.', ''):
                        return url

                    # Or if title clearly indicates official site
                    if 'official' in title and resort_name.lower() in title:
                        return url

            except httpx.HTTPError:
                continue

    return None


async def extract_images_from_page(
    url: str,
    resort_name: str,
) -> list[dict[str, Any]]:
    """Extract image URLs from a webpage.

    Finds high-quality images suitable for hero/banner use.

    Args:
        url: URL to scrape
        resort_name: Resort name for filtering relevant images

    Returns:
        List of image info dicts with url, alt, width, height
    """
    images = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; Snowthere/1.0; +https://snowthere.com)",
                },
            )
            response.raise_for_status()
            html = response.text
        except httpx.HTTPError as e:
            print(f"Failed to fetch {url}: {e}")
            return []

    soup = BeautifulSoup(html, "html.parser")
    base_url = url

    # Strategy 1: Look for og:image meta tag (usually hero image)
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        img_url = og_image.get("content")
        if img_url:
            images.append({
                "url": img_url if img_url.startswith("http") else urljoin(base_url, img_url),
                "alt": f"{resort_name} - official image",
                "source": "og_image",
                "priority": 10,  # Highest priority
            })

    # Strategy 2: Look for twitter:image meta tag
    twitter_image = soup.find("meta", {"name": "twitter:image"})
    if twitter_image and twitter_image.get("content"):
        img_url = twitter_image.get("content")
        if img_url:
            images.append({
                "url": img_url if img_url.startswith("http") else urljoin(base_url, img_url),
                "alt": f"{resort_name} - official image",
                "source": "twitter_image",
                "priority": 9,
            })

    # Strategy 3: Find hero/banner images by class/id patterns
    for pattern in IMAGE_PATTERNS:
        # Check img tags
        for img in soup.find_all("img"):
            classes = " ".join(img.get("class", []))
            img_id = img.get("id", "")

            if re.search(pattern, classes, re.I) or re.search(pattern, img_id, re.I):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if src:
                    images.append({
                        "url": src if src.startswith("http") else urljoin(base_url, src),
                        "alt": img.get("alt", f"{resort_name}"),
                        "source": f"pattern:{pattern}",
                        "priority": 7,
                    })

        # Check background images in divs
        for div in soup.find_all(["div", "section", "header"]):
            classes = " ".join(div.get("class", []))
            div_id = div.get("id", "")

            if re.search(pattern, classes, re.I) or re.search(pattern, div_id, re.I):
                style = div.get("style", "")
                # Extract url() from background-image
                bg_match = re.search(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
                if bg_match:
                    bg_url = bg_match.group(1)
                    images.append({
                        "url": bg_url if bg_url.startswith("http") else urljoin(base_url, bg_url),
                        "alt": f"{resort_name}",
                        "source": f"bg:{pattern}",
                        "priority": 6,
                    })

    # Strategy 4: Find large images in the page
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        # Skip tiny images, icons, logos
        width = img.get("width")
        height = img.get("height")

        # Skip if explicitly small
        if width and int(width) < MIN_WIDTH:
            continue
        if height and int(height) < MIN_HEIGHT:
            continue

        # Skip common non-content images
        src_lower = src.lower()
        skip_patterns = [
            'logo', 'icon', 'badge', 'button', 'avatar',
            'social', 'facebook', 'twitter', 'instagram',
            'placeholder', 'loading', 'spinner', 'pixel',
            '.svg', '.gif', '1x1', 'spacer',
        ]
        if any(skip in src_lower for skip in skip_patterns):
            continue

        # Prefer landscape images (likely scenic/resort shots)
        if width and height and int(width) > int(height):
            priority = 5
        else:
            priority = 3

        images.append({
            "url": src if src.startswith("http") else urljoin(base_url, src),
            "alt": img.get("alt", f"{resort_name}"),
            "source": "large_img",
            "priority": priority,
        })

    # Deduplicate by URL
    seen_urls = set()
    unique_images = []
    for img in images:
        if img["url"] not in seen_urls:
            seen_urls.add(img["url"])
            unique_images.append(img)

    # Sort by priority
    unique_images.sort(key=lambda x: x.get("priority", 0), reverse=True)

    return unique_images[:10]  # Return top 10


async def download_and_store_image(
    image_url: str,
    resort_id: str,
    image_type: str = "hero",
) -> str | None:
    """Download an image and store it in Supabase Storage.

    Args:
        image_url: URL of the image to download
        resort_id: Resort UUID for storage path
        image_type: Type of image (hero, atmosphere, etc.)

    Returns:
        Public URL of stored image or None
    """
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        try:
            response = await client.get(
                image_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; Snowthere/1.0)",
                },
            )
            response.raise_for_status()
            image_data = response.content

            # Verify it's actually an image
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                return None

            # Determine file extension
            # Note: IANA standard is "image/jpeg" not "image/jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"
            else:
                ext = "jpeg"  # Use IANA standard (image/jpeg, not image/jpg)

        except httpx.HTTPError as e:
            print(f"Failed to download image: {e}")
            return None

    try:
        supabase = get_supabase_client()

        # Generate unique filename
        content_hash = hashlib.md5(image_data).hexdigest()[:8]
        filename = f"official/{resort_id}/{image_type}_{content_hash}.{ext}"

        # Upload to storage
        supabase.storage.from_("resort-images").upload(
            path=filename,
            file=image_data,
            file_options={"content-type": f"image/{ext}", "upsert": "true"},
        )

        # Get public URL
        public_url = supabase.storage.from_("resort-images").get_public_url(filename)
        return public_url

    except Exception as e:
        print(f"Failed to store image: {e}")
        return None


async def fetch_official_resort_image(
    resort_id: str,
    resort_name: str,
    country: str,
    official_website: str | None = None,
    task_id: str | None = None,
) -> OfficialImageResult:
    """Fetch a real image from the official resort website.

    This is the primary method for getting resort hero images.
    Falls back to Google Places UGC if official site scraping fails.

    Args:
        resort_id: Resort UUID
        resort_name: Name of the ski resort
        country: Country where resort is located
        official_website: Known official website URL (optional)
        task_id: Optional task ID for audit logging

    Returns:
        OfficialImageResult with image details
    """
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="official_images",
            action="start_fetch",
            reasoning=f"Fetching official image for {resort_name}",
        )

    # Step 1: Find official website if not provided
    if not official_website:
        official_website = await find_resort_website(resort_name, country)

    if not official_website:
        if task_id:
            log_reasoning(
                task_id=task_id,
                agent_name="official_images",
                action="no_website_found",
                reasoning=f"Could not find official website for {resort_name}",
            )
        return OfficialImageResult(
            success=False,
            error=f"Could not find official website for {resort_name}",
        )

    # Step 2: Extract images from the website
    images = await extract_images_from_page(official_website, resort_name)

    if not images:
        if task_id:
            log_reasoning(
                task_id=task_id,
                agent_name="official_images",
                action="no_images_found",
                reasoning=f"No suitable images found on {official_website}",
            )
        return OfficialImageResult(
            success=False,
            source_url=official_website,
            error="No suitable images found on official website",
        )

    # Step 3: Try to download and store the best image
    for img_info in images:
        img_url = img_info["url"]

        stored_url = await download_and_store_image(
            image_url=img_url,
            resort_id=resort_id,
            image_type="hero",
        )

        if stored_url:
            # Success! Save to database
            try:
                supabase = get_supabase_client()
                supabase.table("resort_images").insert({
                    "resort_id": resort_id,
                    "image_type": "hero",
                    "image_url": stored_url,
                    "source": "official",
                    "alt_text": img_info.get("alt", f"{resort_name} ski resort"),
                    "attribution": f"Image from {official_website}",
                    "metadata": {
                        "original_url": img_url,
                        "source_type": img_info.get("source"),
                        "official_website": official_website,
                    },
                }).execute()
            except Exception as e:
                print(f"Failed to save image record: {e}")

            if task_id:
                log_reasoning(
                    task_id=task_id,
                    agent_name="official_images",
                    action="image_stored",
                    reasoning=f"Successfully fetched and stored official image for {resort_name}",
                    metadata={
                        "source_url": img_url,
                        "stored_url": stored_url,
                        "website": official_website,
                    },
                )

            return OfficialImageResult(
                success=True,
                url=stored_url,
                source_url=img_url,
                stored_url=stored_url,
                source="official",
                alt_text=img_info.get("alt"),
                attribution=f"Image from {official_website}",
            )

    # All image downloads failed
    return OfficialImageResult(
        success=False,
        source_url=official_website,
        error="Failed to download any images from official website",
    )


async def fetch_resort_images_with_fallback(
    resort_id: str,
    resort_name: str,
    country: str,
    official_website: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    task_id: str | None = None,
) -> OfficialImageResult:
    """Fetch resort images with fallback to Google Places UGC.

    Priority:
    1. Official website images (real photos)
    2. Google Places UGC (real visitor photos)
    3. Returns failure (NO AI-generated images)

    Args:
        resort_id: Resort UUID
        resort_name: Name of the ski resort
        country: Country where resort is located
        official_website: Known official website URL (optional)
        latitude: Resort latitude for UGC lookup
        longitude: Resort longitude for UGC lookup
        task_id: Optional task ID for audit logging

    Returns:
        OfficialImageResult with image details
    """
    # Try official website first
    result = await fetch_official_resort_image(
        resort_id=resort_id,
        resort_name=resort_name,
        country=country,
        official_website=official_website,
        task_id=task_id,
    )

    if result.success:
        return result

    # Fallback to Google Places UGC
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="official_images",
            action="fallback_to_ugc",
            reasoning=f"Official website images failed, trying Google Places UGC for {resort_name}",
        )

    try:
        from .ugc_photos import fetch_and_store_ugc_photos

        ugc_result = await fetch_and_store_ugc_photos(
            resort_id=resort_id,
            resort_name=resort_name,
            country=country,
            latitude=latitude,
            longitude=longitude,
            max_photos=5,
            filter_with_vision=True,
        )

        if ugc_result.success and ugc_result.photos:
            # Find the best photo (highest relevance) for hero
            best_photo = max(ugc_result.photos, key=lambda p: p.relevance_score)

            # Update this photo to be the hero image type
            try:
                supabase = get_supabase_client()
                supabase.table("resort_images").update({
                    "image_type": "hero",
                }).eq("resort_id", resort_id).eq("image_url", best_photo.url).execute()
            except Exception:
                pass

            if task_id:
                log_reasoning(
                    task_id=task_id,
                    agent_name="official_images",
                    action="ugc_success",
                    reasoning=f"Using Google Places UGC photo as hero for {resort_name}",
                    metadata={
                        "photo_url": best_photo.url,
                        "relevance_score": best_photo.relevance_score,
                        "category": best_photo.category.value,
                    },
                )

            return OfficialImageResult(
                success=True,
                url=best_photo.url,
                stored_url=best_photo.url,
                source="google_places",
                alt_text=f"Visitor photo of {resort_name}",
                attribution="; ".join(best_photo.attributions) if best_photo.attributions else None,
            )

    except ImportError:
        pass  # UGC module not available
    except Exception as e:
        if task_id:
            log_reasoning(
                task_id=task_id,
                agent_name="official_images",
                action="ugc_failed",
                reasoning=f"Google Places UGC also failed: {e}",
            )

    # Both methods failed - return failure (DO NOT fall back to AI)
    return OfficialImageResult(
        success=False,
        error="Could not fetch real images from official website or Google Places",
    )


def delete_ai_generated_images(resort_id: str | None = None) -> int:
    """Delete AI-generated images from the database.

    Use this to clean up existing AI-generated images that should
    be replaced with real photos.

    Args:
        resort_id: Optional specific resort. If None, deletes all AI images.

    Returns:
        Number of images deleted
    """
    try:
        supabase = get_supabase_client()

        query = supabase.table("resort_images").delete().in_(
            "source", ["gemini", "glif", "replicate"]
        )

        if resort_id:
            query = query.eq("resort_id", resort_id)

        result = query.execute()
        return len(result.data) if result.data else 0

    except Exception as e:
        print(f"Failed to delete AI images: {e}")
        return 0


def count_ai_generated_images() -> dict[str, int]:
    """Count AI-generated images by source.

    Returns:
        Dict mapping source to count
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("resort_images").select("source").in_(
            "source", ["gemini", "glif", "replicate"]
        ).execute()

        counts = {"gemini": 0, "glif": 0, "replicate": 0, "total": 0}
        for row in result.data or []:
            source = row.get("source")
            if source in counts:
                counts[source] += 1
                counts["total"] += 1

        return counts

    except Exception:
        return {"gemini": 0, "glif": 0, "replicate": 0, "total": 0}
