#!/usr/bin/env python3
"""Backfill taglines using the new Agent-Native tagline system.

This script runs the new tagline generation system (Round 12) against all
published resorts, replacing the old generic taglines with specific,
structurally diverse ones.

Usage:
    python scripts/backfill_taglines.py           # Full backfill
    python scripts/backfill_taglines.py --dry-run # Preview only (no saves)
    python scripts/backfill_taglines.py --limit 5 # Process only 5 resorts
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.intelligence import (
    extract_tagline_atoms,
    generate_diverse_tagline,
    evaluate_tagline_quality,
)
from shared.primitives.database import get_recent_portfolio_taglines


async def backfill_taglines(dry_run: bool = False, limit: int | None = None):
    """Run the new tagline system against all published resorts."""

    client = get_supabase_client()

    # Get all published resorts with their content
    query = (
        client.table("resorts")
        .select("id, name, country, slug")
        .eq("status", "published")
        .order("name")
    )

    if limit:
        query = query.limit(limit)

    resorts_response = query.execute()
    resorts = resorts_response.data or []

    print(f"\n{'='*60}")
    print(f"TAGLINE BACKFILL - Agent-Native System (Round 12)")
    print(f"{'='*60}")
    print(f"Mode: {'DRY RUN (no saves)' if dry_run else 'LIVE (will save changes)'}")
    print(f"Resorts to process: {len(resorts)}")
    print(f"{'='*60}\n")

    updated = 0
    skipped = 0
    failed = 0

    for i, resort in enumerate(resorts, 1):
        resort_id = resort["id"]
        name = resort["name"]
        country = resort["country"]

        print(f"\n[{i}/{len(resorts)}] {name}, {country}")
        print("-" * 40)

        try:
            # Get existing content
            content_response = (
                client.table("resort_content")
                .select("tagline, quick_take")
                .eq("resort_id", resort_id)
                .single()
                .execute()
            )
            content = content_response.data or {}
            old_tagline = content.get("tagline", "")
            quick_take = content.get("quick_take", "")

            # Get family metrics
            metrics_response = (
                client.table("resort_family_metrics")
                .select("*")
                .eq("resort_id", resort_id)
                .single()
                .execute()
            )
            family_metrics = metrics_response.data or {}

            # Get costs
            costs_response = (
                client.table("resort_costs")
                .select("*")
                .eq("resort_id", resort_id)
                .single()
                .execute()
            )
            costs = costs_response.data or {}

            # Prepare research data from existing database content
            research_data = {
                "family_metrics": family_metrics,
                "costs": costs,
                "quick_take": quick_take,
            }

            # Extract quick take context if available
            quick_take_context = None
            if quick_take:
                # We'll extract atoms from the quick_take text
                quick_take_context = {
                    "unique_angle": None,  # Would need to re-extract
                    "signature_experience": None,
                    "memorable_detail": None,
                }

            print(f"  Old tagline: \"{old_tagline}\"")

            # Step 1: Extract tagline atoms
            atoms = await extract_tagline_atoms(
                resort_name=name,
                country=country,
                research_data=research_data,
                quick_take_context=quick_take_context,
            )

            if atoms.numbers:
                print(f"  Atoms found: {len(atoms.numbers)} numbers, landmark={atoms.landmark_or_icon is not None}")

            # Step 2: Get recent portfolio taglines for diversity
            recent_taglines = get_recent_portfolio_taglines(limit=10, exclude_country=country)

            # Step 3: Quality loop (max 3 attempts)
            best_tagline = None
            best_quality = None

            for attempt in range(3):
                temperature = 0.7 + (attempt * 0.15)

                candidate = await generate_diverse_tagline(
                    resort_name=name,
                    country=country,
                    atoms=atoms,
                    recent_taglines=recent_taglines,
                    temperature=temperature,
                )

                quality = await evaluate_tagline_quality(
                    tagline=candidate,
                    atoms=atoms,
                    resort_name=name,
                    recent_taglines=recent_taglines,
                )

                if best_quality is None or quality.overall_score > best_quality.overall_score:
                    best_tagline = candidate
                    best_quality = quality

                if quality.passes_threshold and quality.structure_novelty >= 0.6:
                    print(f"  Accepted on attempt {attempt + 1}")
                    break

            new_tagline = best_tagline or f"Your family adventure starts in {name}"

            print(f"  New tagline: \"{new_tagline}\"")
            print(f"  Quality: score={best_quality.overall_score:.2f}, novelty={best_quality.structure_novelty:.2f}")

            # Step 4: Save if not dry run
            if not dry_run:
                client.table("resort_content").update({
                    "tagline": new_tagline
                }).eq("resort_id", resort_id).execute()
                print(f"  ✅ Saved")
                updated += 1
            else:
                print(f"  [DRY RUN - not saved]")
                updated += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"BACKFILL COMPLETE")
    print(f"{'='*60}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Backfill taglines with Agent-Native system")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't save")
    parser.add_argument("--limit", type=int, help="Limit number of resorts to process")
    args = parser.parse_args()

    asyncio.run(backfill_taglines(dry_run=args.dry_run, limit=args.limit))


if __name__ == "__main__":
    main()
