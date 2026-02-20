#!/usr/bin/env python3
"""Backfill missing ski quality calendar data for published resorts.

Queries published resorts that have no rows in ski_quality_calendar,
then generates calendar data using generate_and_store_calendar().

Cost: ~$0.003 per resort (Haiku).

Usage:
    python scripts/backfill_calendars.py                    # Full backfill
    python scripts/backfill_calendars.py --dry-run           # Preview only
    python scripts/backfill_calendars.py --limit 5           # Process 5 resorts
    python scripts/backfill_calendars.py --resort "Zermatt"  # Single resort
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.calendar import generate_and_store_calendar
from shared.primitives.system import get_daily_spend


async def backfill_calendars(
    dry_run: bool = False,
    limit: int | None = None,
    resort_filter: str | None = None,
):
    """Backfill missing calendar data for published resorts."""
    client = get_supabase_client()

    # Get all published resorts
    query = (
        client.table("resorts")
        .select("id, name, country, slug")
        .eq("status", "published")
        .order("name")
    )
    if resort_filter:
        query = query.ilike("name", f"%{resort_filter}%")

    resorts_resp = query.execute()
    resorts = resorts_resp.data or []

    # Find which resorts already have calendar data
    calendar_resp = (
        client.table("ski_quality_calendar")
        .select("resort_id")
        .execute()
    )
    resorts_with_calendar = {row["resort_id"] for row in (calendar_resp.data or [])}

    missing = [r for r in resorts if r["id"] not in resorts_with_calendar]

    if limit:
        missing = missing[:limit]

    print(f"Published resorts: {len(resorts)}")
    print(f"With calendar data: {len(resorts_with_calendar)}")
    print(f"Missing calendar: {len(missing)}")
    print()

    if not missing:
        print("All resorts have calendar data.")
        return

    if dry_run:
        print("Would generate calendars for:")
        for r in missing:
            print(f"  - {r['name']} ({r['country']})")
        print(f"\nEstimated cost: ~${len(missing) * 0.003:.3f}")
        return

    success = 0
    failed = 0

    for i, resort in enumerate(missing):
        print(f"[{i + 1}/{len(missing)}] {resort['name']} ({resort['country']})")

        try:
            result = await generate_and_store_calendar(
                resort_id=resort["id"],
                resort_name=resort["name"],
                country=resort["country"],
                research_data=None,
            )

            if result.success:
                print(f"  Generated {len(result.months)} months")
                success += 1
            else:
                print(f"  FAILED: {result.error}")
                failed += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

        # Small delay to avoid rate limits
        await asyncio.sleep(1)

    print(f"\nResults: {success} generated, {failed} failed")
    print(f"Daily spend: ${get_daily_spend():.2f}")


def main():
    parser = argparse.ArgumentParser(description="Backfill missing calendar data")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--limit", type=int, help="Max resorts to process")
    parser.add_argument("--resort", type=str, help="Filter by resort name")
    args = parser.parse_args()

    asyncio.run(backfill_calendars(
        dry_run=args.dry_run,
        limit=args.limit,
        resort_filter=args.resort,
    ))


if __name__ == "__main__":
    main()
