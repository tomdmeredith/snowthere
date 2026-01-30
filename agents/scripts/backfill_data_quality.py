#!/usr/bin/env python3
"""
Backfill data quality for all published resorts.

For each published resort:
1. Re-run search_resort_info() (targeted queries for missing fields)
2. Re-extract via improved extract_resort_data() with calibration
3. Recalculate score via improved calculate_family_score()
4. Compute and store data_completeness
5. Update database
6. Log reasoning via log_reasoning() for every score change

Usage:
    python scripts/backfill_data_quality.py                     # Dry run (preview)
    python scripts/backfill_data_quality.py --apply             # Actually update
    python scripts/backfill_data_quality.py --verbose           # Show detail
    python scripts/backfill_data_quality.py --resort zermatt    # Single resort
    python scripts/backfill_data_quality.py --skip-research     # Re-extract only (no API calls)

Estimated cost: ~$0.20/resort (research + extraction), ~$6 total for 30 resorts.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.scoring import (
    KEY_COMPLETENESS_FIELDS,
    calculate_data_completeness,
    calculate_family_score,
    calculate_family_score_with_breakdown,
)
from shared.primitives.intelligence import extract_resort_data
from shared.primitives.research import search_resort_info
from shared.primitives.system import log_reasoning


def get_published_resorts(slug_filter: str | None = None) -> list[dict]:
    """Get published resorts, optionally filtered by slug."""
    supabase = get_supabase_client()

    query = (
        supabase.table("resorts")
        .select("id, name, slug, country, status")
        .eq("status", "published")
    )

    if slug_filter:
        query = query.eq("slug", slug_filter)

    response = query.execute()
    return response.data or []


def get_current_metrics(resort_id: str) -> dict | None:
    """Get current family metrics for comparison."""
    supabase = get_supabase_client()
    response = (
        supabase.table("resort_family_metrics")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_current_costs(resort_id: str) -> dict | None:
    """Get current cost data for comparison."""
    supabase = get_supabase_client()
    response = (
        supabase.table("resort_costs")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )
    return response.data[0] if response.data else None


def update_metrics(resort_id: str, updates: dict) -> bool:
    """Update family metrics in database."""
    supabase = get_supabase_client()
    try:
        supabase.table("resort_family_metrics").update(
            updates
        ).eq("resort_id", resort_id).execute()
        return True
    except Exception as e:
        print(f"  Error updating metrics: {e}")
        return False


def update_costs(resort_id: str, updates: dict) -> bool:
    """Update cost data in database."""
    supabase = get_supabase_client()
    try:
        supabase.table("resort_costs").update(
            updates
        ).eq("resort_id", resort_id).execute()
        return True
    except Exception as e:
        print(f"  Error updating costs: {e}")
        return False


async def backfill_resort(
    resort: dict,
    apply: bool = False,
    verbose: bool = False,
    skip_research: bool = False,
) -> dict:
    """Backfill data quality for a single resort."""
    resort_id = resort["id"]
    name = resort["name"]
    country = resort["country"]

    result = {
        "name": name,
        "country": country,
        "resort_id": resort_id,
        "status": "skipped",
        "old_score": None,
        "new_score": None,
        "old_completeness": None,
        "new_completeness": None,
        "fields_improved": [],
    }

    # Get current state
    old_metrics = get_current_metrics(resort_id)
    old_costs = get_current_costs(resort_id)

    if not old_metrics:
        print(f"  [SKIP] No family metrics row for {name}")
        return result

    old_score = old_metrics.get("family_overall_score")
    old_completeness = calculate_data_completeness(old_metrics)
    result["old_score"] = old_score
    result["old_completeness"] = round(old_completeness, 2)

    if verbose:
        print(f"  Before: score={old_score}, completeness={old_completeness:.0%}")
        null_fields = [f for f in KEY_COMPLETENESS_FIELDS if old_metrics.get(f) is None]
        if null_fields:
            print(f"  NULL key fields: {', '.join(null_fields)}")

    # Step 1: Re-research (unless skipping)
    raw_research = None
    if not skip_research:
        print(f"  Researching {name}, {country}...")
        try:
            raw_research = await search_resort_info(name, country)
        except Exception as e:
            print(f"  [WARN] Research failed: {e}")
            raw_research = None

    # Step 2: Re-extract with improved prompt
    extracted = None
    if raw_research:
        print(f"  Extracting structured data...")
        try:
            extracted = await extract_resort_data(raw_research, name, country)
        except Exception as e:
            print(f"  [WARN] Extraction failed: {e}")
            extracted = None

    # Step 3: Merge extracted data with existing (fill gaps, don't overwrite with None)
    new_metrics = dict(old_metrics)  # Start with existing
    new_costs = dict(old_costs) if old_costs else {}

    fields_improved = []

    if extracted and extracted.confidence >= 0.4:
        # Merge family metrics — only fill in NULL fields or update if we have better data
        for key, value in extracted.family_metrics.items():
            if value is not None:
                old_value = old_metrics.get(key)
                if old_value is None:
                    new_metrics[key] = value
                    fields_improved.append(f"{key}: None → {value}")

        # Merge costs
        for key, value in extracted.costs.items():
            if value is not None:
                old_value = new_costs.get(key)
                if old_value is None:
                    new_costs[key] = value
                    fields_improved.append(f"cost.{key}: None → {value}")

        if verbose and extracted.reasoning:
            print(f"  Extraction reasoning: {extracted.reasoning}")
            print(f"  Confidence: {extracted.confidence:.2f}")
    elif extracted:
        print(f"  [SKIP] Low confidence extraction ({extracted.confidence:.2f})")

    # Step 4: Recalculate score and completeness
    new_score = calculate_family_score(new_metrics)
    new_completeness = calculate_data_completeness(new_metrics)

    result["new_score"] = new_score
    result["new_completeness"] = round(new_completeness, 2)
    result["fields_improved"] = fields_improved
    result["status"] = "updated" if fields_improved or new_score != old_score else "unchanged"

    if verbose:
        print(f"  After: score={new_score}, completeness={new_completeness:.0%}")
        if fields_improved:
            print(f"  Fields improved: {len(fields_improved)}")
            for f in fields_improved:
                print(f"    {f}")

    # Step 5: Apply updates
    if apply and (fields_improved or new_score != old_score):
        # Build update payload for metrics
        metrics_update = {
            "family_overall_score": new_score,
            "data_completeness": round(new_completeness, 2),
        }
        # Add any newly filled fields
        for key in KEY_COMPLETENESS_FIELDS:
            if new_metrics.get(key) is not None and old_metrics.get(key) is None:
                metrics_update[key] = new_metrics[key]

        # Also include non-key fields that were filled
        for key in ["best_age_min", "best_age_max", "has_ski_school", "has_ski_in_out", "english_friendly"]:
            if new_metrics.get(key) is not None and old_metrics.get(key) is None:
                metrics_update[key] = new_metrics[key]

        success = update_metrics(resort_id, metrics_update)
        if success:
            print(f"  [UPDATED] Metrics")
        else:
            result["status"] = "error"

        # Update costs if improved
        if old_costs and any(k.startswith("cost.") for f in fields_improved for k in [f.split(":")[0]]):
            cost_update = {}
            for key, value in extracted.costs.items():
                if value is not None and new_costs.get(key) != (old_costs or {}).get(key):
                    cost_update[key] = value
            if cost_update:
                cost_success = update_costs(resort_id, cost_update)
                if cost_success:
                    print(f"  [UPDATED] Costs")

        # Step 6: Log reasoning
        score_delta = round(new_score - (old_score or 0), 1)
        log_reasoning(
            task_id=None,
            agent_name="backfill_data_quality",
            action="score_recalculation",
            reasoning=(
                f"Backfill for {name}: score {old_score} → {new_score} "
                f"(delta: {score_delta:+.1f}), "
                f"completeness {old_completeness:.0%} → {new_completeness:.0%}, "
                f"fields improved: {len(fields_improved)}"
            ),
            metadata={
                "resort_id": resort_id,
                "old_score": old_score,
                "new_score": new_score,
                "old_completeness": round(old_completeness, 2),
                "new_completeness": round(new_completeness, 2),
                "fields_improved": fields_improved,
            },
        )

    elif apply and new_score == old_score and not fields_improved:
        # Still store completeness even if nothing else changed
        update_metrics(resort_id, {
            "data_completeness": round(new_completeness, 2),
        })

    return result


async def main(
    apply: bool = False,
    verbose: bool = False,
    resort_slug: str | None = None,
    skip_research: bool = False,
):
    """Run the backfill."""
    print("=" * 70)
    print("DATA QUALITY BACKFILL")
    print("=" * 70)

    if not apply:
        print("\n[DRY RUN] - Use --apply to update the database\n")
    else:
        print("\n[LIVE] - Will update the database\n")

    resorts = get_published_resorts(slug_filter=resort_slug)
    print(f"Found {len(resorts)} resort(s) to process\n")

    if not resorts:
        print("No resorts found!")
        return

    results = []
    for i, resort in enumerate(resorts, 1):
        print(f"[{i}/{len(resorts)}] {resort['name']} ({resort['country']})")
        result = await backfill_resort(
            resort,
            apply=apply,
            verbose=verbose,
            skip_research=skip_research,
        )
        results.append(result)
        print()

    # Summary
    print("=" * 70)
    print("BACKFILL SUMMARY")
    print("=" * 70)

    updated = [r for r in results if r["status"] == "updated"]
    unchanged = [r for r in results if r["status"] == "unchanged"]
    skipped = [r for r in results if r["status"] == "skipped"]
    errors = [r for r in results if r["status"] == "error"]

    print(f"\nProcessed: {len(results)}")
    print(f"Updated:   {len(updated)}")
    print(f"Unchanged: {len(unchanged)}")
    print(f"Skipped:   {len(skipped)}")
    print(f"Errors:    {len(errors)}")

    if updated:
        print(f"\nScore Changes:")
        for r in updated:
            old_s = r["old_score"] or 0
            new_s = r["new_score"] or 0
            delta = new_s - old_s
            direction = "+" if delta > 0 else "" if delta < 0 else "="
            print(
                f"  {r['name']:30s} {r['old_score']:>5} → {r['new_score']:>5} "
                f"({direction}{delta:.1f})  "
                f"completeness: {r['old_completeness']:.0%} → {r['new_completeness']:.0%}  "
                f"fields: +{len(r['fields_improved'])}"
            )

    # Completeness distribution after backfill
    completeness_values = [r["new_completeness"] for r in results if r["new_completeness"] is not None]
    if completeness_values:
        print(f"\nCompleteness After Backfill:")
        avg = sum(completeness_values) / len(completeness_values)
        show_full = sum(1 for c in completeness_values if c >= 0.6)
        show_partial = sum(1 for c in completeness_values if 0.3 <= c < 0.6)
        hidden = sum(1 for c in completeness_values if c < 0.3)
        print(f"  Average: {avg:.0%}")
        print(f"  Show full table: {show_full} resorts")
        print(f"  Show partial:    {show_partial} resorts")
        print(f"  Keep hidden:     {hidden} resorts")

    if not apply and updated:
        print(f"\n[DRY RUN] Run with --apply to update {len(updated)} resorts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill data quality for published resorts"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually update the database (default is dry run)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output per resort",
    )
    parser.add_argument(
        "--resort",
        type=str,
        default=None,
        help="Single resort slug to process",
    )
    parser.add_argument(
        "--skip-research",
        action="store_true",
        help="Skip re-research, only re-extract and re-score with existing data",
    )
    args = parser.parse_args()

    asyncio.run(main(
        apply=args.apply,
        verbose=args.verbose,
        resort_slug=args.resort,
        skip_research=args.skip_research,
    ))
