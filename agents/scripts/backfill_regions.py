#!/usr/bin/env python3
"""
Backfill regions for all existing resorts.

This script uses Claude Haiku to extract the region/state/province for each
resort that doesn't have one, then updates the database.

Usage:
    python scripts/backfill_regions.py          # Dry run (preview changes)
    python scripts/backfill_regions.py --apply  # Actually update database

Cost: ~$0.002 per resort = ~$0.06 for 29 resorts
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import settings
from shared.supabase_client import get_supabase_client
from shared.primitives.intelligence import extract_region


async def get_resorts_without_regions() -> list[dict]:
    """Get all resorts that don't have a region set."""
    supabase = get_supabase_client()

    response = supabase.table("resorts").select(
        "id, name, country, region, status"
    ).or_("region.is.null,region.eq.").order("name").execute()

    return response.data


async def update_resort_region(resort_id: str, region: str) -> bool:
    """Update a resort's region in the database."""
    supabase = get_supabase_client()

    try:
        supabase.table("resorts").update(
            {"region": region}
        ).eq("id", resort_id).execute()
        return True
    except Exception as e:
        print(f"  Error updating: {e}")
        return False


async def main(apply: bool = False):
    """Main backfill function."""
    print("=" * 60)
    print("Region Backfill Script")
    print("=" * 60)

    if not apply:
        print("\n[DRY RUN] - Use --apply to actually update the database\n")
    else:
        print("\n[LIVE] - Will update the database\n")

    # Get resorts without regions
    resorts = await get_resorts_without_regions()
    print(f"Found {len(resorts)} resorts without regions:\n")

    if not resorts:
        print("All resorts already have regions!")
        return

    # Process each resort
    results = []
    for i, resort in enumerate(resorts, 1):
        name = resort["name"]
        country = resort["country"]
        status = resort["status"]

        print(f"[{i}/{len(resorts)}] {name} ({country})...")

        # Extract region using Claude Haiku
        region = await extract_region(name, country)

        if region:
            print(f"  -> {region}")
            results.append({
                "id": resort["id"],
                "name": name,
                "country": country,
                "region": region,
                "status": status,
            })

            if apply:
                success = await update_resort_region(resort["id"], region)
                if success:
                    print(f"  [UPDATED]")
                else:
                    print(f"  [FAILED]")
        else:
            print(f"  -> [Could not determine region]")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"\nProcessed: {len(resorts)} resorts")
    print(f"Regions found: {len(results)}")
    print(f"Could not determine: {len(resorts) - len(results)}")

    if results:
        print("\nRegions to update:")
        for r in results:
            print(f"  {r['name']}: {r['region']}, {r['country']}")

    if not apply and results:
        print(f"\n[DRY RUN] Run with --apply to update {len(results)} resorts")
    elif apply:
        print(f"\n[COMPLETE] Updated {len(results)} resorts")

    # Estimate cost
    cost = len(resorts) * 0.002
    print(f"\nEstimated API cost: ${cost:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill regions for resorts")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually update the database (default is dry run)",
    )
    args = parser.parse_args()

    asyncio.run(main(apply=args.apply))
