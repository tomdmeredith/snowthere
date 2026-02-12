#!/usr/bin/env python3
"""Backfill missing coordinates for all published resorts.

Audit (Feb 12): 90 of 95 published resorts have NULL coordinates.
The pipeline never called extract_coordinates() for the first 90 resorts.

Uses the improved extract_coordinates() with:
- Nominatim + countrycodes parameter for disambiguation
- Country bounding box validation
- Google Geocoding API fallback

Rate limiting: ~1.1s per Nominatim query, 4 queries per resort worst case.
Estimated time: ~6 minutes for 90 resorts (most resolve on first query).

Usage:
    # Dry run (no DB writes)
    python scripts/backfill_coordinates.py

    # Write fixes
    python scripts/backfill_coordinates.py --write

    # Single resort
    python scripts/backfill_coordinates.py --resort "Kitzbühel" --write

    # Batch with limit
    python scripts/backfill_coordinates.py --batch-limit 20 --write
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.research import extract_coordinates


async def get_resorts_missing_coords(limit: int = 200) -> list[dict]:
    """Get published resorts with NULL coordinates."""
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select("id, name, country, slug, latitude, longitude")
        .eq("status", "published")
        .is_("latitude", "null")
        .order("name")
        .limit(limit)
        .execute()
    )
    return response.data or []


async def main():
    parser = argparse.ArgumentParser(description="Backfill missing coordinates")
    parser.add_argument("--write", action="store_true", help="Write fixes to DB")
    parser.add_argument("--resort", help="Fix a single resort by name")
    parser.add_argument("--batch-limit", type=int, default=200)
    args = parser.parse_args()

    print("Coordinate Backfill")
    print(f"  Write: {args.write}")
    print()

    client = get_supabase_client()

    if args.resort:
        resorts = (
            client.table("resorts")
            .select("id, name, country, slug, latitude, longitude")
            .ilike("name", f"%{args.resort}%")
            .limit(5)
            .execute()
        ).data or []
    else:
        resorts = await get_resorts_missing_coords(limit=args.batch_limit)

    print(f"  Found {len(resorts)} resorts to process")
    print()

    success = 0
    failed = 0
    skipped = 0

    for i, resort in enumerate(resorts):
        name = resort["name"]
        country = resort["country"]

        # Skip if already has coordinates (for --resort mode)
        if resort["latitude"] is not None and resort["longitude"] is not None:
            print(f"  [{i+1}/{len(resorts)}] {name}: already has coords ({resort['latitude']:.4f}, {resort['longitude']:.4f})")
            skipped += 1
            continue

        print(f"  [{i+1}/{len(resorts)}] {name} ({country})...", end=" ", flush=True)

        coords = await extract_coordinates(name, country)

        if coords:
            lat, lon = coords
            print(f"({lat:.4f}, {lon:.4f})")

            if args.write:
                try:
                    client.table("resorts").update({
                        "latitude": lat,
                        "longitude": lon,
                    }).eq("id", resort["id"]).execute()
                    await asyncio.sleep(0.3)  # Rate limit writes
                except Exception as e:
                    print(f"    DB write failed: {e}")
                    # Retry once after 2s
                    await asyncio.sleep(2)
                    try:
                        client.table("resorts").update({
                            "latitude": lat,
                            "longitude": lon,
                        }).eq("id", resort["id"]).execute()
                    except Exception:
                        print(f"    Retry also failed, skipping")
                        failed += 1
                        continue

            success += 1
        else:
            print("FAILED")
            failed += 1

    print()
    print(f"Results: {success} found, {failed} failed, {skipped} skipped")
    if not args.write and success > 0:
        print("  (Dry run — use --write to save to DB)")


if __name__ == "__main__":
    asyncio.run(main())
