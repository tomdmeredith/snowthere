#!/usr/bin/env python3
"""Fetch hero images for resorts missing them.

Uses Google Places API to find and store hero images for resorts
that currently have placeholder images.

Usage:
    cd agents
    python scripts/fetch_hero_images.py
    # Or for specific resorts:
    python scripts/fetch_hero_images.py --slugs park-city st-anton
    # Dry run:
    python scripts/fetch_hero_images.py --dry-run
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.ugc_photos import (
    find_place_id,
    get_place_details,
    fetch_place_photo,
    upload_ugc_photo_to_storage,
    classify_photo_with_vision,
    PhotoCategory,
)


def get_resorts_missing_hero() -> list[dict]:
    """Get all published resorts missing hero images."""
    client = get_supabase_client()

    # Get all published resorts
    resorts = client.table("resorts").select(
        "id, slug, name, country, latitude, longitude"
    ).eq("status", "published").execute()

    # Get resorts with hero images
    images = client.table("resort_images").select(
        "resort_id"
    ).eq("image_type", "hero").execute()

    resorts_with_hero = {img["resort_id"] for img in images.data} if images.data else set()

    # Return resorts without hero images
    missing = [r for r in resorts.data if r["id"] not in resorts_with_hero]
    return missing


async def fetch_best_hero_photo(
    resort_name: str,
    country: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> tuple[bytes | None, dict | None]:
    """Fetch the best photo for use as hero image.

    Prioritizes wide landscape shots with scenic views.
    Uses vision to filter out unsuitable photos.

    Returns:
        Tuple of (photo_bytes, photo_metadata) or (None, None)
    """
    # Find the place
    place_id = await find_place_id(resort_name, country, latitude, longitude)
    if not place_id:
        print(f"  Could not find Google Place for {resort_name}")
        return None, None

    # Get place details with photos
    details = await get_place_details(place_id)
    if not details:
        print(f"  Could not get place details")
        return None, None

    photo_refs = details.get("photos", [])
    if not photo_refs:
        print(f"  No photos found in Google Places")
        return None, None

    print(f"  Found {len(photo_refs)} photos, evaluating...")

    # Score each photo for hero suitability
    best_photo = None
    best_score = 0.0
    best_metadata = None

    for i, ref_data in enumerate(photo_refs[:8]):  # Check up to 8 photos
        photo_ref = ref_data.get("photo_reference")
        if not photo_ref:
            continue

        # Fetch the photo
        photo_bytes = await fetch_place_photo(photo_ref, max_width=1200, max_height=800)
        if not photo_bytes:
            continue

        # Get dimensions - prefer landscape orientation
        width = ref_data.get("width", 0)
        height = ref_data.get("height", 0)

        # Skip portrait photos
        if height > 0 and width > 0 and height > width:
            print(f"    Photo {i+1}: Skipping portrait orientation")
            continue

        # Use vision to classify
        category, relevance = await classify_photo_with_vision(photo_bytes)

        # Calculate hero score
        # Higher score for: scenery, skiing, family content
        # Lower score for: food, lodge interior, unknown
        category_scores = {
            PhotoCategory.SCENERY: 0.9,
            PhotoCategory.SKIING: 0.85,
            PhotoCategory.FAMILY: 0.8,
            PhotoCategory.ACTIVITIES: 0.7,
            PhotoCategory.LODGE: 0.5,
            PhotoCategory.FOOD: 0.3,
            PhotoCategory.UNKNOWN: 0.4,
        }

        base_score = category_scores.get(category, 0.4)
        # Boost by relevance
        score = base_score * 0.6 + relevance * 0.4

        print(f"    Photo {i+1}: {category.value}, relevance={relevance:.2f}, score={score:.2f}")

        if score > best_score:
            best_score = score
            best_photo = photo_bytes
            best_metadata = {
                "width": width,
                "height": height,
                "category": category.value,
                "relevance_score": relevance,
                "place_id": place_id,
                "photo_index": i,
                "attributions": ref_data.get("html_attributions", []),
            }

    if best_photo and best_score >= 0.5:
        print(f"  Selected photo with score {best_score:.2f}")
        return best_photo, best_metadata
    else:
        print(f"  No suitable hero photo found (best score: {best_score:.2f})")
        return None, None


async def store_hero_image(
    resort_id: str,
    resort_name: str,
    photo_bytes: bytes,
    metadata: dict,
) -> str | None:
    """Store a hero image in Supabase storage and database."""
    client = get_supabase_client()

    # Upload to storage
    url = await upload_ugc_photo_to_storage(
        photo_data=photo_bytes,
        resort_id=resort_id,
        photo_index=0,  # Hero is always index 0
    )

    if not url:
        print(f"  Failed to upload to storage")
        return None

    # Store in resort_images table as hero type
    try:
        # Delete any existing hero image for this resort
        client.table("resort_images").delete().eq(
            "resort_id", resort_id
        ).eq("image_type", "hero").execute()

        # Insert new hero image
        client.table("resort_images").insert({
            "resort_id": resort_id,
            "image_type": "hero",
            "image_url": url,
            "source": "google_places",
            "alt_text": f"{resort_name} ski resort - family skiing destination",
            "metadata": metadata,
        }).execute()

        return url

    except Exception as e:
        print(f"  Failed to store in database: {e}")
        return None


async def fetch_hero_images(slugs: list[str] | None = None, dry_run: bool = False) -> dict:
    """Fetch hero images for resorts.

    Args:
        slugs: Specific resort slugs to process, or None for all missing
        dry_run: If True, don't actually store images

    Returns:
        Dict with results summary
    """
    results = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "details": [],
    }

    # Get resorts to process
    if slugs:
        client = get_supabase_client()
        response = client.table("resorts").select(
            "id, slug, name, country, latitude, longitude"
        ).in_("slug", slugs).execute()
        resorts = response.data or []
    else:
        resorts = get_resorts_missing_hero()

    if not resorts:
        print("No resorts to process")
        return results

    print(f"\nProcessing {len(resorts)} resorts:\n")

    for resort in resorts:
        results["processed"] += 1
        print(f"[{results['processed']}/{len(resorts)}] {resort['name']} ({resort['country']})")

        # Fetch best hero photo
        photo_bytes, metadata = await fetch_best_hero_photo(
            resort_name=resort["name"],
            country=resort["country"],
            latitude=resort.get("latitude"),
            longitude=resort.get("longitude"),
        )

        if not photo_bytes:
            results["failed"] += 1
            results["details"].append({
                "slug": resort["slug"],
                "name": resort["name"],
                "status": "failed",
                "reason": "No suitable photo found",
            })
            continue

        if dry_run:
            print(f"  [DRY RUN] Would store hero image")
            results["success"] += 1
            results["details"].append({
                "slug": resort["slug"],
                "name": resort["name"],
                "status": "dry_run",
                "metadata": metadata,
            })
            continue

        # Store the hero image
        url = await store_hero_image(
            resort_id=resort["id"],
            resort_name=resort["name"],
            photo_bytes=photo_bytes,
            metadata=metadata,
        )

        if url:
            print(f"  SUCCESS: {url}")
            results["success"] += 1
            results["details"].append({
                "slug": resort["slug"],
                "name": resort["name"],
                "status": "success",
                "url": url,
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "slug": resort["slug"],
                "name": resort["name"],
                "status": "failed",
                "reason": "Storage failed",
            })

    return results


def main():
    """Run the hero image fetcher."""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch hero images for resorts")
    parser.add_argument(
        "--slugs",
        nargs="+",
        help="Specific resort slugs to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("FETCH HERO IMAGES")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE ***\n")

    results = asyncio.run(fetch_hero_images(
        slugs=args.slugs,
        dry_run=args.dry_run,
    ))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Processed: {results['processed']}")
    print(f"  Success:   {results['success']}")
    print(f"  Failed:    {results['failed']}")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
