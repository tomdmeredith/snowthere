#!/usr/bin/env python3
"""
Post-backfill cross-resort validation.

Checks:
- Cost plausibility within same country (flag >2x or <0.5x country average)
- Score distribution (flag if >60% cluster in a 1-point range)
- Boolean consistency (flag if 90%+ of a country's resorts have a feature but one doesn't)
- Data quality report card

Usage:
    python scripts/validate_cross_resort.py           # Full validation report
    python scripts/validate_cross_resort.py --json    # Machine-readable output
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.scoring import (
    KEY_COMPLETENESS_FIELDS,
    calculate_data_completeness,
)


# Expected cost ranges by country (adult daily lift ticket)
EXPECTED_LIFT_RANGES = {
    "Austria": (30, 85),
    "Switzerland": (50, 100),
    "France": (30, 75),
    "Italy": (30, 70),
    "United States": (80, 300),
    "Canada": (70, 200),
    "Norway": (40, 80),
    "Sweden": (30, 60),
    "Japan": (30, 70),
    "Andorra": (30, 55),
}

BOOLEAN_FIELDS = [
    "has_childcare",
    "has_ski_school",
    "has_magic_carpet",
    "has_terrain_park_kids",
    "has_ski_in_out",
    "english_friendly",
]


def get_all_data() -> list[dict]:
    """Get all published resorts with metrics and costs."""
    supabase = get_supabase_client()

    # Get resorts
    resorts = (
        supabase.table("resorts")
        .select("id, name, slug, country, status")
        .eq("status", "published")
        .execute()
    ).data or []

    results = []
    for resort in resorts:
        rid = resort["id"]

        # Get metrics
        metrics = (
            supabase.table("resort_family_metrics")
            .select("*")
            .eq("resort_id", rid)
            .execute()
        ).data
        metrics = metrics[0] if metrics else {}

        # Get costs
        costs = (
            supabase.table("resort_costs")
            .select("*")
            .eq("resort_id", rid)
            .execute()
        ).data
        costs = costs[0] if costs else {}

        results.append({
            "resort": resort,
            "metrics": metrics,
            "costs": costs,
        })

    return results


def check_cost_plausibility(data: list[dict]) -> list[dict]:
    """Check costs against expected ranges and country averages."""
    flags = []

    # Group by country
    by_country = defaultdict(list)
    for d in data:
        country = d["resort"]["country"]
        lift_price = d["costs"].get("lift_adult_daily")
        if lift_price is not None:
            by_country[country].append({
                "name": d["resort"]["name"],
                "price": float(lift_price),
            })

    for country, resorts in by_country.items():
        if len(resorts) < 2:
            continue

        prices = [r["price"] for r in resorts]
        avg_price = sum(prices) / len(prices)

        # Check against expected range
        expected = EXPECTED_LIFT_RANGES.get(country)
        if expected:
            low, high = expected
            for r in resorts:
                if r["price"] < low * 0.8 or r["price"] > high * 1.2:
                    flags.append({
                        "type": "cost_range",
                        "severity": "warning",
                        "resort": r["name"],
                        "country": country,
                        "message": (
                            f"Lift price {r['price']} outside expected range "
                            f"{low}-{high} for {country}"
                        ),
                    })

        # Check within-country outliers (>2x or <0.5x average)
        for r in resorts:
            if r["price"] > avg_price * 2:
                flags.append({
                    "type": "cost_outlier",
                    "severity": "warning",
                    "resort": r["name"],
                    "country": country,
                    "message": (
                        f"Lift price {r['price']} is >2x country avg "
                        f"({avg_price:.0f}) for {country}"
                    ),
                })
            elif r["price"] < avg_price * 0.5:
                flags.append({
                    "type": "cost_outlier",
                    "severity": "warning",
                    "resort": r["name"],
                    "country": country,
                    "message": (
                        f"Lift price {r['price']} is <0.5x country avg "
                        f"({avg_price:.0f}) for {country}"
                    ),
                })

    return flags


def check_score_distribution(data: list[dict]) -> list[dict]:
    """Check for clustering in score distribution."""
    flags = []

    scores = []
    for d in data:
        score = d["metrics"].get("family_overall_score")
        if score is not None:
            scores.append(float(score))

    if len(scores) < 5:
        return flags

    # Check for clustering: >60% in a 1-point range
    for base in range(1, 10):
        in_range = sum(1 for s in scores if base <= s < base + 1)
        pct = in_range / len(scores)
        if pct > 0.6:
            flags.append({
                "type": "score_clustering",
                "severity": "warning",
                "message": (
                    f"{pct:.0%} of scores cluster in {base}.0-{base+1}.0 range "
                    f"({in_range}/{len(scores)}). Consider formula adjustment."
                ),
            })

    # Check range spread
    if scores:
        score_range = max(scores) - min(scores)
        if score_range < 2.0:
            flags.append({
                "type": "score_range",
                "severity": "warning",
                "message": (
                    f"Score range is only {score_range:.1f} "
                    f"({min(scores):.1f} - {max(scores):.1f}). "
                    f"Expected at least 3.0 spread."
                ),
            })

    return flags


def check_boolean_consistency(data: list[dict]) -> list[dict]:
    """Check if boolean values are consistent within countries."""
    flags = []

    # Group by country
    by_country = defaultdict(list)
    for d in data:
        if d["metrics"]:
            by_country[d["resort"]["country"]].append(d)

    for country, resorts in by_country.items():
        if len(resorts) < 3:
            continue

        for field in BOOLEAN_FIELDS:
            values = []
            for r in resorts:
                val = r["metrics"].get(field)
                values.append({
                    "name": r["resort"]["name"],
                    "value": val,
                })

            true_count = sum(1 for v in values if v["value"] is True)
            false_count = sum(1 for v in values if v["value"] is False)
            null_count = sum(1 for v in values if v["value"] is None)

            # Flag: 90%+ have it but one doesn't (might be data error)
            total_known = true_count + false_count
            if total_known >= 3 and true_count / total_known >= 0.9:
                outliers = [v["name"] for v in values if v["value"] is False]
                if outliers:
                    flags.append({
                        "type": "boolean_outlier",
                        "severity": "info",
                        "country": country,
                        "field": field,
                        "message": (
                            f"{field}: {true_count}/{total_known} resorts in {country} "
                            f"have this, but {', '.join(outliers)} don't. Verify."
                        ),
                    })

            # Flag: high NULL rate for a field
            if null_count > len(resorts) * 0.5:
                flags.append({
                    "type": "high_null_rate",
                    "severity": "info",
                    "country": country,
                    "field": field,
                    "message": (
                        f"{field}: {null_count}/{len(resorts)} resorts in {country} "
                        f"have NULL value. Priority for re-research."
                    ),
                })

    return flags


def generate_report_card(data: list[dict]) -> dict:
    """Generate overall data quality report card."""
    total = len(data)
    has_metrics = sum(1 for d in data if d["metrics"])
    has_costs = sum(1 for d in data if d["costs"])

    completeness_values = []
    for d in data:
        if d["metrics"]:
            c = calculate_data_completeness(d["metrics"])
            completeness_values.append(c)

    scores = [float(d["metrics"]["family_overall_score"])
              for d in data if d["metrics"].get("family_overall_score")]

    return {
        "total_resorts": total,
        "with_metrics": has_metrics,
        "with_costs": has_costs,
        "avg_completeness": (
            round(sum(completeness_values) / len(completeness_values), 2)
            if completeness_values else 0
        ),
        "completeness_above_60": sum(1 for c in completeness_values if c >= 0.6),
        "completeness_30_60": sum(1 for c in completeness_values if 0.3 <= c < 0.6),
        "completeness_below_30": sum(1 for c in completeness_values if c < 0.3),
        "score_range": (
            f"{min(scores):.1f} - {max(scores):.1f}" if scores else "N/A"
        ),
        "score_avg": round(sum(scores) / len(scores), 1) if scores else 0,
        "score_count": len(scores),
    }


def main(as_json: bool = False):
    """Run cross-resort validation."""
    data = get_all_data()

    if not data:
        print("No published resorts found!")
        return

    # Run all checks
    cost_flags = check_cost_plausibility(data)
    score_flags = check_score_distribution(data)
    boolean_flags = check_boolean_consistency(data)
    report_card = generate_report_card(data)

    all_flags = cost_flags + score_flags + boolean_flags

    if as_json:
        print(json.dumps({
            "report_card": report_card,
            "flags": all_flags,
        }, indent=2, default=str))
        return

    # Print report
    print("=" * 70)
    print("CROSS-RESORT VALIDATION REPORT")
    print("=" * 70)

    print(f"\n--- Report Card ---")
    print(f"  Total resorts:    {report_card['total_resorts']}")
    print(f"  With metrics:     {report_card['with_metrics']}")
    print(f"  With costs:       {report_card['with_costs']}")
    print(f"  Avg completeness: {report_card['avg_completeness']:.0%}")
    print(f"  Score range:      {report_card['score_range']}")
    print(f"  Score average:    {report_card['score_avg']}")

    print(f"\n  Frontend readiness:")
    print(f"    Full tables:    {report_card['completeness_above_60']} resorts")
    print(f"    Partial tables: {report_card['completeness_30_60']} resorts")
    print(f"    Hidden:         {report_card['completeness_below_30']} resorts")

    # Flags
    warnings = [f for f in all_flags if f["severity"] == "warning"]
    infos = [f for f in all_flags if f["severity"] == "info"]

    if warnings:
        print(f"\n--- Warnings ({len(warnings)}) ---")
        for f in warnings:
            resort = f.get("resort", "")
            prefix = f"  [{f['type']}]"
            if resort:
                prefix += f" {resort}:"
            print(f"{prefix} {f['message']}")

    if infos:
        print(f"\n--- Info ({len(infos)}) ---")
        for f in infos:
            print(f"  [{f['type']}] {f['message']}")

    if not all_flags:
        print(f"\n  No flags raised. Data quality looks consistent.")

    # Grade
    print(f"\n--- Overall Grade ---")
    completeness = report_card["avg_completeness"]
    warning_count = len(warnings)

    if completeness >= 0.7 and warning_count == 0:
        grade = "A"
    elif completeness >= 0.6 and warning_count <= 2:
        grade = "B"
    elif completeness >= 0.4 and warning_count <= 5:
        grade = "C"
    else:
        grade = "D"

    print(f"  Grade: {grade}")
    print(f"  Completeness: {completeness:.0%}, Warnings: {warning_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cross-resort validation and consistency checks"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    args = parser.parse_args()

    main(as_json=args.json)
