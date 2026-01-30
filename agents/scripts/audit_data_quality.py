#!/usr/bin/env python3
"""
Audit current data quality across all published resorts.

Reports for each resort:
- Count of NULL fields in resort_family_metrics
- Count of NULL fields in resort_costs
- Current family_overall_score and contributing factors
- Boolean fields that are NULL (not TRUE or FALSE)
- Data completeness ratio
- Whether cost data exists at all

Usage:
    python scripts/audit_data_quality.py           # Summary report
    python scripts/audit_data_quality.py --verbose  # Per-resort detail
    python scripts/audit_data_quality.py --json     # Machine-readable output
"""

import argparse
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
    format_score_explanation,
)


# All boolean fields in resort_family_metrics
BOOLEAN_FIELDS = [
    "has_childcare",
    "has_ski_school",
    "has_magic_carpet",
    "has_terrain_park_kids",
    "has_ski_in_out",
    "english_friendly",
]

# Key numeric fields in resort_family_metrics
NUMERIC_FIELDS = [
    "childcare_min_age",
    "ski_school_min_age",
    "kid_friendly_terrain_pct",
    "kids_ski_free_age",
    "best_age_min",
    "best_age_max",
    "family_overall_score",
]

# Key cost fields in resort_costs
COST_FIELDS = [
    "lift_adult_daily",
    "lift_child_daily",
    "lift_family_daily",
    "lodging_budget_nightly",
    "lodging_mid_nightly",
    "lodging_luxury_nightly",
    "meal_budget_daily",
    "meal_mid_daily",
]


def get_published_resorts() -> list[dict]:
    """Get all published resorts with their family metrics."""
    supabase = get_supabase_client()

    response = (
        supabase.table("resorts")
        .select("id, name, slug, country, status")
        .eq("status", "published")
        .execute()
    )

    return response.data or []


def get_family_metrics(resort_id: str) -> dict | None:
    """Get family metrics for a resort."""
    supabase = get_supabase_client()

    response = (
        supabase.table("resort_family_metrics")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )

    return response.data[0] if response.data else None


def get_costs(resort_id: str) -> dict | None:
    """Get cost data for a resort."""
    supabase = get_supabase_client()

    response = (
        supabase.table("resort_costs")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )

    return response.data[0] if response.data else None


def audit_resort(resort: dict) -> dict:
    """Audit a single resort's data quality."""
    resort_id = resort["id"]
    metrics = get_family_metrics(resort_id)
    costs = get_costs(resort_id)

    result = {
        "resort_id": resort_id,
        "name": resort["name"],
        "country": resort["country"],
        "slug": resort["slug"],
        "has_metrics": metrics is not None,
        "has_costs": costs is not None,
    }

    # Audit family metrics
    if metrics:
        null_booleans = [f for f in BOOLEAN_FIELDS if metrics.get(f) is None]
        null_numerics = [f for f in NUMERIC_FIELDS if metrics.get(f) is None]
        completeness = calculate_data_completeness(metrics)
        current_score = metrics.get("family_overall_score")
        recalculated_score = calculate_family_score(metrics)

        result.update({
            "null_boolean_count": len(null_booleans),
            "null_boolean_fields": null_booleans,
            "null_numeric_count": len(null_numerics),
            "null_numeric_fields": null_numerics,
            "total_null_metrics": len(null_booleans) + len(null_numerics),
            "data_completeness": round(completeness, 2),
            "current_score": current_score,
            "recalculated_score": recalculated_score,
            "score_delta": round(recalculated_score - (current_score or 0), 1),
        })
    else:
        result.update({
            "null_boolean_count": len(BOOLEAN_FIELDS),
            "null_boolean_fields": BOOLEAN_FIELDS,
            "null_numeric_count": len(NUMERIC_FIELDS),
            "null_numeric_fields": NUMERIC_FIELDS,
            "total_null_metrics": len(BOOLEAN_FIELDS) + len(NUMERIC_FIELDS),
            "data_completeness": 0.0,
            "current_score": None,
            "recalculated_score": None,
            "score_delta": None,
        })

    # Audit costs
    if costs:
        null_costs = [f for f in COST_FIELDS if costs.get(f) is None]
        result.update({
            "null_cost_count": len(null_costs),
            "null_cost_fields": null_costs,
            "has_lift_prices": costs.get("lift_adult_daily") is not None,
            "has_lodging_prices": costs.get("lodging_mid_nightly") is not None,
        })
    else:
        result.update({
            "null_cost_count": len(COST_FIELDS),
            "null_cost_fields": COST_FIELDS,
            "has_lift_prices": False,
            "has_lodging_prices": False,
        })

    return result


def print_resort_detail(audit: dict):
    """Print detailed audit for one resort."""
    print(f"\n{'─' * 60}")
    print(f"  {audit['name']} ({audit['country']})")
    print(f"{'─' * 60}")

    # Metrics
    if audit["has_metrics"]:
        print(f"  Family Metrics:  {audit['data_completeness']:.0%} complete")
        print(f"  Current Score:   {audit['current_score']}")
        print(f"  Recalculated:    {audit['recalculated_score']}", end="")
        if audit["score_delta"] and audit["score_delta"] != 0:
            direction = "↑" if audit["score_delta"] > 0 else "↓"
            print(f" ({direction}{abs(audit['score_delta']):.1f})")
        else:
            print(" (unchanged)")

        if audit["null_boolean_fields"]:
            print(f"  NULL booleans:   {', '.join(audit['null_boolean_fields'])}")
        if audit["null_numeric_fields"]:
            print(f"  NULL numerics:   {', '.join(audit['null_numeric_fields'])}")
    else:
        print("  Family Metrics:  NO DATA")

    # Costs
    if audit["has_costs"]:
        filled = len(COST_FIELDS) - audit["null_cost_count"]
        print(f"  Cost Data:       {filled}/{len(COST_FIELDS)} fields populated")
        if audit["null_cost_fields"]:
            print(f"  NULL costs:      {', '.join(audit['null_cost_fields'])}")
    else:
        print("  Cost Data:       NO DATA")


def print_summary(audits: list[dict]):
    """Print aggregate summary."""
    total = len(audits)

    print("\n" + "=" * 70)
    print("DATA QUALITY AUDIT REPORT")
    print("=" * 70)

    print(f"\nPublished resorts: {total}")

    # Metrics coverage
    has_metrics = sum(1 for a in audits if a["has_metrics"])
    has_costs = sum(1 for a in audits if a["has_costs"])
    print(f"With family metrics: {has_metrics}/{total}")
    print(f"With cost data: {has_costs}/{total}")

    # Completeness distribution
    completeness_values = [a["data_completeness"] for a in audits if a["has_metrics"]]
    if completeness_values:
        print(f"\nData Completeness Distribution:")
        buckets = {"0-30%": 0, "30-60%": 0, "60-80%": 0, "80-100%": 0}
        for c in completeness_values:
            if c < 0.3:
                buckets["0-30%"] += 1
            elif c < 0.6:
                buckets["30-60%"] += 1
            elif c < 0.8:
                buckets["60-80%"] += 1
            else:
                buckets["80-100%"] += 1

        for label, count in buckets.items():
            bar = "█" * count
            print(f"  {label:>8}: {bar} ({count})")

        avg_completeness = sum(completeness_values) / len(completeness_values)
        print(f"  Average: {avg_completeness:.0%}")

    # Score distribution (recalculated)
    scores = [a["recalculated_score"] for a in audits if a["recalculated_score"] is not None]
    if scores:
        print(f"\nRecalculated Score Distribution:")
        score_buckets = {}
        for s in scores:
            bucket = int(s)
            score_buckets[bucket] = score_buckets.get(bucket, 0) + 1

        for bucket in sorted(score_buckets.keys()):
            count = score_buckets[bucket]
            bar = "█" * count
            print(f"  {bucket}.x: {bar} ({count})")

        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        print(f"  Range: {min_score:.1f} - {max_score:.1f} (avg {avg_score:.1f})")

    # Score deltas
    deltas = [a for a in audits if a["score_delta"] and a["score_delta"] != 0]
    if deltas:
        print(f"\nScore Changes (old formula → new formula):")
        for a in sorted(deltas, key=lambda x: x["score_delta"]):
            direction = "↑" if a["score_delta"] > 0 else "↓"
            print(f"  {a['name']:30s} {a['current_score']:>5} → {a['recalculated_score']:>5} ({direction}{abs(a['score_delta']):.1f})")

    # Most common NULL fields
    print(f"\nMost Common NULL Fields (family metrics):")
    field_nulls = {}
    for a in audits:
        if a["has_metrics"]:
            for f in a["null_boolean_fields"] + a["null_numeric_fields"]:
                field_nulls[f] = field_nulls.get(f, 0) + 1

    for field, count in sorted(field_nulls.items(), key=lambda x: -x[1]):
        pct = count / has_metrics * 100 if has_metrics else 0
        print(f"  {field:30s} NULL in {count}/{has_metrics} ({pct:.0f}%)")

    # Frontend readiness
    print(f"\nFrontend Table Readiness:")
    show_full = sum(1 for a in audits if a["data_completeness"] >= 0.6)
    show_partial = sum(1 for a in audits if 0.3 <= a["data_completeness"] < 0.6)
    hidden = sum(1 for a in audits if a["data_completeness"] < 0.3)
    print(f"  Show fully:     {show_full} resorts (completeness >= 60%)")
    print(f"  Show partially: {show_partial} resorts (completeness 30-60%)")
    print(f"  Keep hidden:    {hidden} resorts (completeness < 30%)")

    has_both_tables = sum(
        1 for a in audits
        if a["data_completeness"] >= 0.6 and a["has_lift_prices"] and a["has_lodging_prices"]
    )
    print(f"  Both tables OK: {has_both_tables} resorts (metrics + costs)")


def main(verbose: bool = False, as_json: bool = False):
    """Run the data quality audit."""
    resorts = get_published_resorts()

    if not resorts:
        print("No published resorts found!")
        return

    print(f"Auditing {len(resorts)} published resorts...")

    audits = []
    for resort in resorts:
        audit = audit_resort(resort)
        audits.append(audit)
        if verbose and not as_json:
            print_resort_detail(audit)

    if as_json:
        # Strip non-serializable fields and output JSON
        print(json.dumps(audits, indent=2, default=str))
    else:
        print_summary(audits)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Audit data quality across all published resorts"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show per-resort detail",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    args = parser.parse_args()

    main(verbose=args.verbose, as_json=args.json)
