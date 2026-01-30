#!/usr/bin/env python3
"""
Fix cost outliers in the resort database.

Identifies and optionally corrects:
1. US resorts with implausibly low lift prices (< $50 USD)
2. European resorts with currency mismatches (EUR stored as USD)

Usage:
    python -m scripts.fix_cost_outliers            # Dry run (default)
    python -m scripts.fix_cost_outliers --apply     # Apply fixes
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.config import settings
from shared.supabase_client import get_supabase_client


# Price thresholds for flagging
US_MIN_ADULT_DAILY = 50  # No major US resort has $50/day adult lift tickets
EUR_COUNTRIES = {"Austria", "France", "Switzerland", "Italy", "Germany"}


def get_all_resort_costs():
    """Fetch all resorts with their cost data."""
    sb = get_supabase_client()
    result = (
        sb.table("resorts")
        .select("id, name, country, slug, resort_costs(*)")
        .eq("status", "published")
        .execute()
    )
    return result.data or []


def flag_us_low_prices(resorts: list) -> list:
    """Flag US resorts with suspiciously low adult lift prices."""
    flagged = []
    for r in resorts:
        if r["country"] != "United States":
            continue
        costs = r.get("resort_costs")
        if not costs:
            continue
        # Supabase returns single object for 1-to-1, list for 1-to-many
        if isinstance(costs, list):
            costs = costs[0] if costs else None
        if not costs:
            continue
        adult_daily = costs.get("lift_adult_daily")
        if adult_daily is not None and adult_daily < US_MIN_ADULT_DAILY:
            flagged.append({
                "resort": r["name"],
                "country": r["country"],
                "resort_id": r["id"],
                "current_adult_daily": adult_daily,
                "currency": costs.get("currency", "USD"),
                "issue": f"Adult daily ${adult_daily} is below ${US_MIN_ADULT_DAILY} threshold",
            })
    return flagged


def flag_currency_mismatches(resorts: list) -> list:
    """Flag European resorts storing EUR values as USD."""
    flagged = []
    for r in resorts:
        if r["country"] not in EUR_COUNTRIES:
            continue
        costs = r.get("resort_costs")
        if not costs:
            continue
        if isinstance(costs, list):
            costs = costs[0] if costs else None
        if not costs:
            continue
        currency = costs.get("currency", "USD")
        if currency == "USD":
            flagged.append({
                "resort": r["name"],
                "country": r["country"],
                "resort_id": r["id"],
                "current_currency": currency,
                "estimated_family_daily": costs.get("estimated_family_daily"),
                "issue": f"European resort storing costs as USD instead of EUR",
            })
    return flagged


def fix_currency_to_eur(resort_id: str, dry_run: bool) -> bool:
    """Update a European resort's currency from USD to EUR."""
    if dry_run:
        return True
    sb = get_supabase_client()
    result = (
        sb.table("resort_costs")
        .update({"currency": "EUR"})
        .eq("resort_id", resort_id)
        .execute()
    )
    return bool(result.data)


def main():
    parser = argparse.ArgumentParser(description="Fix cost data outliers")
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry run)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    dry_run = not args.apply

    print(f"\n{'DRY RUN' if dry_run else 'APPLYING FIXES'} - Cost Outlier Analysis")
    print("=" * 60)

    resorts = get_all_resort_costs()
    print(f"\nAnalyzing {len(resorts)} published resorts...\n")

    # Flag issues
    us_low = flag_us_low_prices(resorts)
    currency_mismatch = flag_currency_mismatches(resorts)

    all_issues = []

    # Report US low prices
    if us_low:
        print(f"US Resorts with Low Lift Prices ({len(us_low)}):")
        print("-" * 50)
        for item in us_low:
            print(f"  {item['resort']}: ${item['current_adult_daily']}/day - {item['issue']}")
            all_issues.append({**item, "type": "us_low_price"})
        print()
        print("  NOTE: These need manual research to get correct prices.")
        print("  The pipeline may have picked up child prices or promotional rates.")
        print()

    # Report and optionally fix currency mismatches
    if currency_mismatch:
        print(f"European Resorts with USD Currency ({len(currency_mismatch)}):")
        print("-" * 50)
        fixed_count = 0
        for item in currency_mismatch:
            action = ""
            if fix_currency_to_eur(item["resort_id"], dry_run):
                action = " -> FIXED to EUR" if not dry_run else " -> WOULD FIX to EUR"
                fixed_count += 1
            print(f"  {item['resort']} ({item['country']}): {item['current_currency']}{action}")
            all_issues.append({**item, "type": "currency_mismatch"})
        print()
        if not dry_run:
            print(f"  Fixed {fixed_count}/{len(currency_mismatch)} currency mismatches.")
        print()

    if not us_low and not currency_mismatch:
        print("No cost outliers found.")

    # Summary
    print("=" * 60)
    print(f"Total issues: {len(all_issues)}")
    print(f"  US low prices: {len(us_low)} (needs manual research)")
    print(f"  Currency mismatches: {len(currency_mismatch)} ({'auto-fixable' if not dry_run else 'fixable with --apply'})")

    if dry_run and (us_low or currency_mismatch):
        print(f"\nRun with --apply to fix currency mismatches.")
        print("US low prices require re-research via the pipeline or manual update.")

    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(all_issues, indent=2))


if __name__ == "__main__":
    main()
