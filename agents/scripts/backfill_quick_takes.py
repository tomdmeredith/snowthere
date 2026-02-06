#!/usr/bin/env python3
"""Backfill Quick Takes for all published resorts with the new constraint-based format.

Regenerates Quick Takes using the 40-65 word single paragraph format
(Round 20) replacing the old 80-120 word Editorial Verdict Model.

Usage:
    python scripts/backfill_quick_takes.py                    # Full backfill
    python scripts/backfill_quick_takes.py --dry-run           # Preview only
    python scripts/backfill_quick_takes.py --limit 3           # Process 3 resorts
    python scripts/backfill_quick_takes.py --resort "Zermatt"  # Single resort
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.database import update_resort_content, update_resort_family_metrics
from shared.primitives.quick_take import (
    QuickTakeContext,
    generate_quick_take,
)


async def backfill_quick_takes(
    dry_run: bool = False,
    limit: int | None = None,
    resort_filter: str | None = None,
):
    """Regenerate all Quick Takes with the new constraint-based format."""
    client = get_supabase_client()

    # Get published resorts
    query = (
        client.table("resorts")
        .select("id, name, country, region, slug")
        .eq("status", "published")
    )
    if resort_filter:
        query = query.ilike("name", f"%{resort_filter}%")

    resorts_resp = query.execute()
    resorts = resorts_resp.data or []

    if limit:
        resorts = resorts[:limit]

    print(f"Processing {len(resorts)} resorts")

    success_count = 0
    fail_count = 0

    for resort in resorts:
        print(f"\n{'='*60}")
        print(f"Resort: {resort['name']} ({resort['country']})")

        # Get family metrics
        metrics_resp = (
            client.table("resort_family_metrics")
            .select("*")
            .eq("resort_id", resort["id"])
            .execute()
        )
        metrics = metrics_resp.data[0] if metrics_resp.data else {}

        # Build context
        context = QuickTakeContext(
            resort_name=resort["name"],
            country=resort["country"],
            region=resort.get("region"),
            family_score=metrics.get("family_overall_score"),
            best_age_min=metrics.get("best_age_min"),
            best_age_max=metrics.get("best_age_max"),
            has_ski_school=metrics.get("has_ski_school", True),
            ski_school_min_age=metrics.get("ski_school_min_age"),
            has_childcare=bool(metrics.get("has_childcare")),
            kids_ski_free_age=metrics.get("kids_ski_free_age"),
            terrain_pct_beginner=metrics.get("kid_friendly_terrain_pct"),
        )

        try:
            result = await generate_quick_take(context)

            if result.is_valid:
                print(f"  Valid: {result.word_count} words, specificity {result.specificity_score:.2f}")
                print(f"  Preview: {result.quick_take_html[:120]}...")

                if not dry_run:
                    # Save quick_take HTML to resort_content
                    update_resort_content(resort["id"], {
                        "quick_take": result.quick_take_html,
                    })
                    # Route perfect_if/skip_if to family_metrics (not resort_content)
                    metrics_update = {}
                    if result.perfect_if:
                        metrics_update["perfect_if"] = result.perfect_if
                    if result.skip_if:
                        metrics_update["skip_if"] = result.skip_if
                    if metrics_update:
                        update_resort_family_metrics(resort["id"], metrics_update)
                    print(f"  Saved to database")
                else:
                    print(f"  [DRY RUN] Would save")

                success_count += 1
            else:
                print(f"  INVALID: {result.validation_errors}")
                fail_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"Results: {success_count} succeeded, {fail_count} failed")


def main():
    parser = argparse.ArgumentParser(description="Backfill Quick Takes")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--limit", type=int, help="Max resorts to process")
    parser.add_argument("--resort", type=str, help="Filter by resort name")
    args = parser.parse_args()

    asyncio.run(backfill_quick_takes(
        dry_run=args.dry_run,
        limit=args.limit,
        resort_filter=args.resort,
    ))


if __name__ == "__main__":
    main()
