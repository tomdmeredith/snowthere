#!/usr/bin/env python3
"""Fix the 5 US resorts from Feb 12 pipeline run.

Issues:
- Sunday River: $29 lift ticket (should be ~$129)
- Mount Bachelor: $23 lift ticket (should be ~$149)
- Crested Butte: No lift ticket data
- All 5: latitude=None, longitude=None
- All 5: data_completeness=0.0

Usage:
    # Dry run (no DB writes)
    python scripts/fix_feb12_resorts.py

    # Write fixes
    python scripts/fix_feb12_resorts.py --write

    # Single resort
    python scripts/fix_feb12_resorts.py --resort "Mount Bachelor" --write
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.costs import acquire_resort_costs, validate_costs
from shared.primitives.research import extract_coordinates
from shared.primitives.scoring import calculate_data_completeness
from shared.primitives.system import get_daily_spend

TARGET_RESORTS = [
    "Alta",
    "Mount Snow",
    "Sunday River",
    "Mount Bachelor",
    "Crested Butte",
]

# Resorts with known bad pricing that need cache cleared
BAD_PRICING_RESORTS = ["Sunday River", "Mount Bachelor", "Crested Butte"]


async def fix_coordinates(resort: dict, write: bool) -> dict:
    """Fix missing coordinates for a resort."""
    name = resort["name"]
    country = resort["country"]

    print(f"  [coords] Looking up {name}, {country}...")
    coords = await extract_coordinates(name, country)

    if coords:
        lat, lon = coords
        print(f"  [coords] Found: {lat:.4f}, {lon:.4f}")

        if write:
            client = get_supabase_client()
            client.table("resorts").update({
                "latitude": lat,
                "longitude": lon,
            }).eq("id", resort["id"]).execute()
            print(f"  [coords] Written to DB")

        return {"latitude": lat, "longitude": lon}
    else:
        print(f"  [coords] FAILED to find coordinates")
        return {"error": "not found"}


async def fix_pricing(resort: dict, write: bool) -> dict:
    """Fix pricing using new Exa discovery + Claude interpretation."""
    name = resort["name"]
    country = resort["country"]

    # Clear bad cache entry first
    if name in BAD_PRICING_RESORTS:
        client = get_supabase_client()
        result = client.table("pricing_cache").delete().eq(
            "resort_name", name
        ).eq("country", country).execute()
        deleted = len(result.data) if result.data else 0
        print(f"  [pricing] Cleared {deleted} cache entries for {name}")

    print(f"  [pricing] Acquiring pricing for {name}...")
    cost_result = await acquire_resort_costs(name, country)

    if cost_result and cost_result.costs:
        costs = cost_result.costs
        validated, notes = validate_costs(costs, country)

        adult = validated.get("lift_adult_daily")
        child = validated.get("lift_child_daily")
        source = cost_result.source
        confidence = cost_result.confidence

        print(f"  [pricing] Adult: ${adult}, Child: ${child}")
        print(f"  [pricing] Source: {source}, Confidence: {confidence:.2f}")
        if notes:
            for note in notes:
                print(f"  [pricing] Note: {note}")

        if write:
            client = get_supabase_client()
            update_data = {}
            if adult is not None:
                update_data["lift_adult_daily"] = adult
            if child is not None:
                update_data["lift_child_daily"] = child
            if validated.get("lodging_mid_nightly"):
                update_data["lodging_mid_nightly"] = validated["lodging_mid_nightly"]
            if update_data:
                update_data["currency"] = cost_result.currency or "USD"
                client.table("resort_costs").update(
                    update_data
                ).eq("resort_id", resort["id"]).execute()
                print(f"  [pricing] Written to DB")

        return {
            "adult": adult,
            "child": child,
            "source": source,
            "confidence": confidence,
            "notes": notes,
        }
    else:
        print(f"  [pricing] FAILED to acquire pricing")
        return {"error": "acquisition failed"}


async def fix_data_completeness(resort: dict, write: bool) -> dict:
    """Recalculate and store data_completeness."""
    client = get_supabase_client()

    metrics = client.table("resort_family_metrics").select("*").eq(
        "resort_id", resort["id"]
    ).execute()

    if not metrics.data:
        print(f"  [completeness] No family metrics found")
        return {"error": "no metrics"}

    m = metrics.data[0]
    completeness = calculate_data_completeness(m)
    print(f"  [completeness] Score: {completeness:.2f}")

    if write:
        client.table("resort_family_metrics").update({
            "data_completeness": completeness,
        }).eq("resort_id", resort["id"]).execute()
        print(f"  [completeness] Written to DB")

    return {"completeness": completeness}


async def main():
    parser = argparse.ArgumentParser(description="Fix Feb 12 resort data")
    parser.add_argument("--write", action="store_true", help="Write fixes to DB")
    parser.add_argument("--resort", help="Fix a single resort by name")
    parser.add_argument("--skip-pricing", action="store_true", help="Skip pricing fixes")
    parser.add_argument("--skip-coords", action="store_true", help="Skip coordinate fixes")
    parser.add_argument("--skip-completeness", action="store_true", help="Skip data completeness")
    args = parser.parse_args()

    targets = [args.resort] if args.resort else TARGET_RESORTS

    print(f"Fix Feb 12 Resorts")
    print(f"  Targets: {targets}")
    print(f"  Write: {args.write}")
    print()

    client = get_supabase_client()
    resorts = client.table("resorts").select(
        "id, name, country, slug, latitude, longitude"
    ).in_("name", targets).execute()

    if not resorts.data:
        print("No matching resorts found")
        return

    print(f"Found {len(resorts.data)} resorts")
    print()

    for resort in resorts.data:
        name = resort["name"]
        print(f"--- {name} ({resort['country']}) ---")

        # Fix coordinates
        if not args.skip_coords and resort["latitude"] is None:
            await fix_coordinates(resort, args.write)

        # Fix pricing
        if not args.skip_pricing and name in BAD_PRICING_RESORTS:
            await fix_pricing(resort, args.write)

        # Fix data completeness
        if not args.skip_completeness:
            await fix_data_completeness(resort, args.write)

        print()

    print(f"Daily spend: ${get_daily_spend():.2f}")


if __name__ == "__main__":
    asyncio.run(main())
