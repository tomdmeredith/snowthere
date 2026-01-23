#!/usr/bin/env python3
"""Cleanup script to remove AI-generated images from the database.

This script removes images with source = 'gemini', 'glif', or 'replicate'
from the resort_images table, as we now use only real images (official
website or Google Places UGC).

Philosophy: Families deserve to see REAL images of resorts they're planning
to visit - not AI-generated approximations.

Usage:
    python scripts/cleanup_ai_images.py           # Dry run (shows what would be deleted)
    python scripts/cleanup_ai_images.py --delete  # Actually delete the images
    python scripts/cleanup_ai_images.py --resort "Zermatt"  # Clean specific resort
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from shared
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client


def count_ai_images() -> dict:
    """Count AI-generated images by source and resort."""
    supabase = get_supabase_client()

    # Get all AI-generated images
    result = supabase.table("resort_images").select(
        "id, resort_id, image_type, source, image_url"
    ).in_("source", ["gemini", "glif", "replicate"]).execute()

    images = result.data or []

    # Count by source
    by_source = {"gemini": 0, "glif": 0, "replicate": 0}
    for img in images:
        source = img.get("source")
        if source in by_source:
            by_source[source] += 1

    # Get resort names for the images
    resort_ids = list(set(img.get("resort_id") for img in images))
    resorts = {}
    if resort_ids:
        resort_result = supabase.table("resorts").select(
            "id, name, country"
        ).in_("id", resort_ids).execute()
        for r in resort_result.data or []:
            resorts[r["id"]] = f"{r['name']}, {r['country']}"

    # Group images by resort
    by_resort = {}
    for img in images:
        resort_id = img.get("resort_id")
        resort_name = resorts.get(resort_id, "Unknown")
        if resort_name not in by_resort:
            by_resort[resort_name] = []
        by_resort[resort_name].append(img)

    return {
        "total": len(images),
        "by_source": by_source,
        "by_resort": by_resort,
        "images": images,
    }


def delete_ai_images(resort_name: str | None = None, dry_run: bool = True) -> int:
    """Delete AI-generated images.

    Args:
        resort_name: If provided, only delete images for this resort
        dry_run: If True, only show what would be deleted

    Returns:
        Number of images deleted (or would be deleted in dry run)
    """
    supabase = get_supabase_client()

    # Build query
    query = supabase.table("resort_images").select(
        "id, resort_id, image_type, source, image_url"
    ).in_("source", ["gemini", "glif", "replicate"])

    # Filter by resort if specified
    if resort_name:
        # Find resort ID
        resort_result = supabase.table("resorts").select(
            "id"
        ).ilike("name", resort_name).execute()

        if not resort_result.data:
            print(f"Resort not found: {resort_name}")
            return 0

        resort_id = resort_result.data[0]["id"]
        query = query.eq("resort_id", resort_id)

    result = query.execute()
    images = result.data or []

    if not images:
        print("No AI-generated images found to delete.")
        return 0

    if dry_run:
        print(f"\n🔍 DRY RUN: Would delete {len(images)} AI-generated images:\n")
        for img in images:
            print(f"  - {img['image_type']} from {img['source']}: {img['image_url'][:80]}...")
        print(f"\nRun with --delete to actually remove these images.")
        return len(images)

    # Actually delete
    delete_ids = [img["id"] for img in images]
    supabase.table("resort_images").delete().in_("id", delete_ids).execute()

    print(f"\n✓ Deleted {len(images)} AI-generated images")
    return len(images)


def main():
    parser = argparse.ArgumentParser(
        description="Remove AI-generated images from the database"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete images (default is dry run)",
    )
    parser.add_argument(
        "--resort",
        type=str,
        help="Only clean images for a specific resort",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Just count AI images without deleting",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("AI Image Cleanup Script")
    print("=" * 60)

    # Count current AI images
    counts = count_ai_images()

    print(f"\n📊 Current AI-generated images: {counts['total']}")
    print(f"   By source:")
    for source, count in counts["by_source"].items():
        if count > 0:
            print(f"     - {source}: {count}")

    if counts["by_resort"]:
        print(f"\n   By resort:")
        for resort, images in counts["by_resort"].items():
            print(f"     - {resort}: {len(images)} images")

    if args.count:
        return

    if counts["total"] == 0:
        print("\n✓ No AI-generated images to clean up!")
        return

    # Delete images
    dry_run = not args.delete
    deleted = delete_ai_images(resort_name=args.resort, dry_run=dry_run)

    if not dry_run and deleted > 0:
        print("\n🎉 Cleanup complete! Resort pages will now use real images only.")


if __name__ == "__main__":
    main()
