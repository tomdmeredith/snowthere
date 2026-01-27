#!/usr/bin/env python3
"""
Recalculate family scores for all existing resorts using the new deterministic formula.

This script recalculates the family_overall_score for all resorts using
the formula in scoring.py instead of LLM-extracted values, providing:
- More variance (7.3, 8.2, 6.8 instead of clustered 7, 8, 9)
- Reproducibility (same inputs = same output)
- Explainability (breakdown available for each score)

Usage:
    python scripts/recalculate_scores.py          # Dry run (preview changes)
    python scripts/recalculate_scores.py --apply  # Actually update database
    python scripts/recalculate_scores.py --verbose  # Show score breakdowns
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.scoring import (
    calculate_family_score,
    calculate_family_score_with_breakdown,
    format_score_explanation,
)


def get_all_family_metrics() -> list[dict]:
    """Get all resort family metrics from the database."""
    supabase = get_supabase_client()

    response = (
        supabase.table("resort_family_metrics")
        .select("*, resort:resorts(name, country)")
        .execute()
    )

    return response.data or []


def update_family_score(resort_id: str, new_score: float) -> bool:
    """Update a resort's family_overall_score in the database."""
    supabase = get_supabase_client()

    try:
        supabase.table("resort_family_metrics").update(
            {"family_overall_score": new_score}
        ).eq("resort_id", resort_id).execute()
        return True
    except Exception as e:
        print(f"  Error updating: {e}")
        return False


def main(apply: bool = False, verbose: bool = False):
    """Main recalculation function."""
    print("=" * 70)
    print("Family Score Recalculation Script (Round 9)")
    print("=" * 70)

    if not apply:
        print("\n[DRY RUN] - Use --apply to actually update the database\n")
    else:
        print("\n[LIVE] - Will update the database\n")

    # Get all family metrics
    metrics_list = get_all_family_metrics()
    print(f"Found {len(metrics_list)} resorts with family metrics\n")

    if not metrics_list:
        print("No resorts found!")
        return

    # Process each resort
    results = []
    unchanged = []
    score_distribution = {}  # Track distribution for summary

    for i, metrics in enumerate(metrics_list, 1):
        resort = metrics.get("resort", {}) or {}
        name = resort.get("name", "Unknown")
        country = resort.get("country", "")
        resort_id = metrics["resort_id"]

        old_score = metrics.get("family_overall_score")

        # Calculate new score
        if verbose:
            breakdown = calculate_family_score_with_breakdown(metrics)
            new_score = breakdown.total
        else:
            new_score = calculate_family_score(metrics)

        # Track distribution
        score_bucket = int(new_score)
        score_distribution[score_bucket] = score_distribution.get(score_bucket, 0) + 1

        # Check if score changed
        # Handle comparison with decimals (old might be int, new is float)
        old_float = float(old_score) if old_score is not None else None
        score_changed = old_float != new_score

        if score_changed:
            print(f"[{i}/{len(metrics_list)}] {name} ({country})")
            print(f"  {old_float} → {new_score}")

            if verbose:
                breakdown = calculate_family_score_with_breakdown(metrics)
                print(f"  Breakdown: childcare({breakdown.childcare}) + ski_school({breakdown.ski_school}) + terrain({breakdown.terrain}) + value({breakdown.value}) + convenience({breakdown.convenience})")

            results.append({
                "resort_id": resort_id,
                "name": name,
                "country": country,
                "old_score": old_float,
                "new_score": new_score,
            })

            if apply:
                success = update_family_score(resort_id, new_score)
                if success:
                    print(f"  [UPDATED]")
                else:
                    print(f"  [FAILED]")
        else:
            unchanged.append(name)

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    print(f"\nProcessed: {len(metrics_list)} resorts")
    print(f"Changed: {len(results)}")
    print(f"Unchanged: {len(unchanged)}")

    if results:
        print("\nScore changes:")
        for r in results:
            change = r["new_score"] - (r["old_score"] or 0)
            direction = "↑" if change > 0 else "↓" if change < 0 else "="
            print(f"  {r['name']}: {r['old_score']} → {r['new_score']} ({direction}{abs(change):.1f})")

    print("\nNew score distribution:")
    for score in sorted(score_distribution.keys()):
        count = score_distribution[score]
        bar = "█" * count
        print(f"  {score}.x: {bar} ({count})")

    # Variance check
    if len(set(r["new_score"] for r in results)) > 1:
        print("\n✓ Good variance - scores are differentiated")
    else:
        print("\n⚠ Low variance - scores may be too clustered")

    if not apply and results:
        print(f"\n[DRY RUN] Run with --apply to update {len(results)} resorts")
    elif apply:
        print(f"\n[COMPLETE] Updated {len(results)} resorts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recalculate family scores using deterministic formula"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually update the database (default is dry run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed score breakdowns",
    )
    args = parser.parse_args()

    main(apply=args.apply, verbose=args.verbose)
