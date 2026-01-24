#!/usr/bin/env python3
"""Fix resort data gaps identified in Round 5.8 audit.

This script fixes:
1. St. Anton missing family metrics
2. All 3 resorts missing cost data
3. St. Anton trail map data (wrong counts)

Usage:
    cd agents
    python scripts/fix_resort_data_gaps.py
    # Or with --dry-run to see what would happen:
    python scripts/fix_resort_data_gaps.py --dry-run
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client


def get_resort_id(slug: str) -> str | None:
    """Get resort ID by slug."""
    client = get_supabase_client()
    response = client.table("resorts").select("id").eq("slug", slug).single().execute()
    return response.data["id"] if response.data else None


def fix_st_anton_family_metrics(dry_run: bool = False) -> bool:
    """Fix St. Anton family metrics (currently missing)."""
    print("\n=== FIX 1: St. Anton Family Metrics ===")

    resort_id = get_resort_id("st-anton")
    if not resort_id:
        print("ERROR: St. Anton not found in database")
        return False

    metrics = {
        "family_overall_score": 7,  # Expert-oriented, challenging terrain
        "best_age_min": 8,  # Older kids handle terrain better
        "best_age_max": 16,
        "ski_school_min_age": 3,
        "has_childcare": True,
        "childcare_min_age": 3,
        "has_magic_carpet": True,
        "has_terrain_park_kids": True,
        "kid_friendly_terrain_pct": 35,  # ~35% beginner terrain
    }

    print(f"Resort ID: {resort_id}")
    print(f"Metrics to insert: {metrics}")

    if dry_run:
        print("[DRY RUN] Would upsert family metrics")
        return True

    client = get_supabase_client()
    data = {"resort_id": resort_id, **metrics}
    response = client.table("resort_family_metrics").upsert(data).execute()

    if response.data:
        print("SUCCESS: St. Anton family metrics updated")
        return True
    else:
        print("ERROR: Failed to update family metrics")
        return False


def fix_resort_costs(dry_run: bool = False) -> bool:
    """Fix cost data for all 3 resorts."""
    print("\n=== FIX 2: Resort Cost Data ===")

    costs_data = {
        "park-city": {
            "currency": "USD",
            "lift_adult_daily": 225,
            "lift_child_daily": 160,
            "lift_family_daily": 610,
            "lodging_budget_nightly": 150,
            "lodging_mid_nightly": 300,
            "lodging_luxury_nightly": 600,
            "meal_family_avg": 120,
        },
        "st-anton": {
            "currency": "EUR",
            "lift_adult_daily": 75,
            "lift_child_daily": 45,
            "lift_family_daily": 195,
            "lodging_budget_nightly": 125,
            "lodging_mid_nightly": 200,
            "lodging_luxury_nightly": 400,
            "meal_family_avg": 80,
        },
        "zermatt": {
            "currency": "CHF",
            "lift_adult_daily": 95,
            "lift_child_daily": 0,  # Free under 9 with Wolli Card
            "lift_family_daily": 190,
            "lodging_budget_nightly": 200,
            "lodging_mid_nightly": 350,
            "lodging_luxury_nightly": 700,
            "meal_family_avg": 150,
        },
    }

    all_success = True
    client = get_supabase_client()

    for slug, costs in costs_data.items():
        resort_id = get_resort_id(slug)
        if not resort_id:
            print(f"ERROR: {slug} not found in database")
            all_success = False
            continue

        print(f"\n{slug}:")
        print(f"  Resort ID: {resort_id}")
        print(f"  Currency: {costs['currency']}")
        print(f"  Adult lift: {costs['lift_adult_daily']}, Child lift: {costs['lift_child_daily']}")
        print(f"  Lodging mid: {costs['lodging_mid_nightly']}")

        if dry_run:
            print(f"  [DRY RUN] Would upsert costs")
            continue

        data = {"resort_id": resort_id, **costs}
        response = client.table("resort_costs").upsert(data).execute()

        if response.data:
            print(f"  SUCCESS: {slug} costs updated")
        else:
            print(f"  ERROR: Failed to update {slug} costs")
            all_success = False

    return all_success


def fix_st_anton_trail_map(dry_run: bool = False) -> bool:
    """Fix St. Anton trail map data (currently shows 13 runs, should be ~300)."""
    print("\n=== FIX 3: St. Anton Trail Map ===")

    resort_id = get_resort_id("st-anton")
    if not resort_id:
        print("ERROR: St. Anton not found in database")
        return False

    trail_map_data = {
        "runs_total": 300,
        "lifts_total": 88,
        "skiable_terrain_km": 305,
        "runs_by_difficulty": {
            "easy": 105,
            "intermediate": 120,
            "advanced": 75,
        },
        "vertical_drop_m": 1507,
        "summit_elevation_m": 2811,
        "base_elevation_m": 1304,
        "quality": "manual",
        "source": "ski-arlberg.at",
        "notes": "Full Ski Arlberg area including St. Anton, St. Christoph, Stuben, Lech, Zürs, Warth-Schröcken",
    }

    print(f"Resort ID: {resort_id}")
    print(f"Trail map data: {trail_map_data['runs_total']} runs, {trail_map_data['lifts_total']} lifts")

    if dry_run:
        print("[DRY RUN] Would update trail_map_data")
        return True

    client = get_supabase_client()
    response = (
        client.table("resorts")
        .update({"trail_map_data": trail_map_data})
        .eq("id", resort_id)
        .execute()
    )

    if response.data:
        print("SUCCESS: St. Anton trail map updated")
        return True
    else:
        print("ERROR: Failed to update trail map")
        return False


def verify_fixes() -> None:
    """Verify all fixes were applied correctly."""
    print("\n=== VERIFICATION ===")

    client = get_supabase_client()

    # Check family metrics
    print("\nFamily Metrics:")
    response = client.table("resorts").select(
        "name, family_metrics:resort_family_metrics(family_overall_score, best_age_min, best_age_max)"
    ).in_("slug", ["park-city", "st-anton", "zermatt"]).execute()

    for resort in response.data:
        metrics = resort.get("family_metrics")
        if metrics:
            print(f"  {resort['name']}: Score {metrics.get('family_overall_score')}, Ages {metrics.get('best_age_min')}-{metrics.get('best_age_max')}")
        else:
            print(f"  {resort['name']}: NO METRICS")

    # Check costs
    print("\nCost Data:")
    response = client.table("resorts").select(
        "name, costs:resort_costs(currency, lift_adult_daily, lodging_mid_nightly)"
    ).in_("slug", ["park-city", "st-anton", "zermatt"]).execute()

    for resort in response.data:
        costs = resort.get("costs")
        if costs:
            print(f"  {resort['name']}: {costs.get('currency')} - Lift ${costs.get('lift_adult_daily')}, Lodging ${costs.get('lodging_mid_nightly')}")
        else:
            print(f"  {resort['name']}: NO COSTS")

    # Check trail map
    print("\nTrail Map (St. Anton):")
    response = client.table("resorts").select("name, trail_map_data").eq("slug", "st-anton").single().execute()
    if response.data and response.data.get("trail_map_data"):
        tmd = response.data["trail_map_data"]
        print(f"  Runs: {tmd.get('runs_total')}, Lifts: {tmd.get('lifts_total')}, Quality: {tmd.get('quality')}")
    else:
        print("  NO TRAIL MAP DATA")


def main():
    """Run all fixes."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix resort data gaps from Round 5.8 audit")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    print("=" * 60)
    print("FIX RESORT DATA GAPS (Round 5.9)")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Run fixes
    results = []
    results.append(("St. Anton family metrics", fix_st_anton_family_metrics(args.dry_run)))
    results.append(("Cost data", fix_resort_costs(args.dry_run)))
    results.append(("St. Anton trail map", fix_st_anton_trail_map(args.dry_run)))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_success = True
    for name, success in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"  {name}: {status}")
        if not success:
            all_success = False

    if not args.dry_run:
        print("\n--- Verifying fixes ---")
        verify_fixes()

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
