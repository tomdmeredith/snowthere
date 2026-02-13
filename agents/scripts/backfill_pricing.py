#!/usr/bin/env python3
"""Backfill and fix pricing for resorts with wrong, suspicious, or missing data.

Audit (Feb 12) found 3 categories:
1. Clearly wrong (regex errors): Copper Mountain $29, Smugglers Notch $27, etc.
2. Currency confusion: Japan JPY stored as USD, Austria EUR as USD, etc.
3. Missing entirely: Davos-Klosters, Furano, Mont Tremblant, Northstar, Park City, Schladming

Uses the new Exa + Claude pricing pipeline from Round 24.

Usage:
    # Audit only (show suspicious prices, no changes)
    python scripts/backfill_pricing.py --audit

    # Dry run (show what would change)
    python scripts/backfill_pricing.py

    # Write fixes for clearly wrong prices only
    python scripts/backfill_pricing.py --write

    # Fix a single resort
    python scripts/backfill_pricing.py --resort "Copper Mountain" --write

    # Fix all missing prices
    python scripts/backfill_pricing.py --missing-only --write

    # Re-acquire pricing for ALL published resorts
    python scripts/backfill_pricing.py --all --write
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.costs import (
    acquire_resort_costs,
    validate_costs,
    validate_price,
    LIFT_TICKET_RANGES,
    COUNTRY_CURRENCIES,
)
from shared.primitives.system import get_daily_spend


def audit_pricing() -> dict[str, list[dict]]:
    """Audit all resort pricing and categorize issues."""
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select("id, name, country, slug, resort_costs(lift_adult_daily, lift_child_daily, currency)")
        .eq("status", "published")
        .order("name")
        .execute()
    )

    missing = []
    wrong = []
    suspicious = []
    ok = []

    for r in response.data or []:
        costs_data = r.get("resort_costs")
        if isinstance(costs_data, list):
            costs_data = costs_data[0] if costs_data else None

        name = r["name"]
        country = r["country"]
        adult = costs_data.get("lift_adult_daily") if costs_data else None
        child = costs_data.get("lift_child_daily") if costs_data else None
        currency = costs_data.get("currency", "USD") if costs_data else "USD"

        info = {
            "id": r["id"],
            "name": name,
            "country": country,
            "adult": adult,
            "child": child,
            "currency": currency,
        }

        if adult is None:
            missing.append(info)
            continue

        # Validate against country ranges
        validation = validate_price("lift_adult_daily", adult, country)
        if validation.severity == "hard_reject":
            wrong.append({**info, "reason": validation.message})
        elif validation.severity == "warning":
            suspicious.append({**info, "reason": validation.message})
        else:
            ok.append(info)

    return {"missing": missing, "wrong": wrong, "suspicious": suspicious, "ok": ok}


async def fix_resort_pricing(resort: dict, write: bool) -> dict:
    """Fix pricing for a single resort using the new Exa+Claude pipeline."""
    name = resort["name"]
    country = resort["country"]
    resort_id = resort["id"]
    old_adult = resort.get("adult")

    # Clear bad cache entry
    client = get_supabase_client()
    result = client.table("pricing_cache").delete().eq(
        "resort_name", name
    ).eq("country", country).execute()
    deleted = len(result.data) if result.data else 0
    if deleted:
        print(f"    Cleared {deleted} cache entries")

    # Re-acquire pricing with new system
    cost_result = await acquire_resort_costs(name, country)

    if cost_result and cost_result.success and cost_result.costs:
        costs = cost_result.costs
        validated, notes = validate_costs(costs, country)

        new_adult = validated.get("lift_adult_daily")
        new_child = validated.get("lift_child_daily")
        source = cost_result.source
        confidence = cost_result.confidence

        change = ""
        if old_adult and new_adult:
            change = f" (was ${old_adult})"

        print(f"    Adult: ${new_adult}{change}, Child: ${new_child}")
        print(f"    Source: {source}, Confidence: {confidence:.2f}")
        for note in notes:
            print(f"    Note: {note}")

        if write and new_adult is not None:
            update_data = {}
            if new_adult is not None:
                update_data["lift_adult_daily"] = new_adult
            if new_child is not None:
                update_data["lift_child_daily"] = new_child
            if validated.get("lodging_mid_nightly"):
                update_data["lodging_mid_nightly"] = validated["lodging_mid_nightly"]
            if update_data:
                update_data["currency"] = cost_result.currency or COUNTRY_CURRENCIES.get(country.lower(), "USD")
                client.table("resort_costs").update(
                    update_data
                ).eq("resort_id", resort_id).execute()
                print(f"    Written to DB")

        return {
            "name": name,
            "status": "fixed",
            "old_adult": old_adult,
            "new_adult": new_adult,
            "new_child": new_child,
            "source": source,
            "confidence": confidence,
        }
    else:
        error = cost_result.error if cost_result else "No result"
        print(f"    FAILED: {error}")
        return {"name": name, "status": "failed", "error": error}


async def main():
    parser = argparse.ArgumentParser(description="Backfill/fix resort pricing")
    parser.add_argument("--audit", action="store_true", help="Audit only, show categories")
    parser.add_argument("--write", action="store_true", help="Write fixes to DB")
    parser.add_argument("--resort", help="Fix a single resort by name")
    parser.add_argument("--missing-only", action="store_true", help="Only fix missing prices")
    parser.add_argument("--wrong-only", action="store_true", help="Only fix clearly wrong prices")
    parser.add_argument("--all", action="store_true", help="Re-acquire pricing for ALL published resorts")
    args = parser.parse_args()

    print("Pricing Backfill")
    print(f"  Write: {args.write}")
    print()

    # Always audit first
    categories = audit_pricing()
    missing = categories["missing"]
    wrong = categories["wrong"]
    suspicious = categories["suspicious"]
    ok = categories["ok"]

    print(f"Audit Results:")
    print(f"  OK: {len(ok)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Clearly wrong: {len(wrong)}")
    print(f"  Suspicious: {len(suspicious)}")
    print()

    if missing:
        print("Missing pricing:")
        for r in missing:
            print(f"  - {r['name']} ({r['country']})")
        print()

    if wrong:
        print("Clearly wrong pricing:")
        for r in wrong:
            print(f"  - {r['name']} ({r['country']}): ${r['adult']} — {r['reason']}")
        print()

    if suspicious:
        print("Suspicious pricing (may be currency issue):")
        for r in suspicious:
            print(f"  - {r['name']} ({r['country']}): ${r['adult']} [{r['currency']}] — {r['reason']}")
        print()

    if args.audit:
        return

    # Build target list
    targets = []
    if args.resort:
        client = get_supabase_client()
        response = (
            client.table("resorts")
            .select("id, name, country, slug, resort_costs(lift_adult_daily, lift_child_daily, currency)")
            .ilike("name", f"%{args.resort}%")
            .limit(5)
            .execute()
        )
        for r in response.data or []:
            costs_data = r.get("resort_costs")
            if isinstance(costs_data, list):
                costs_data = costs_data[0] if costs_data else None
            targets.append({
                "id": r["id"],
                "name": r["name"],
                "country": r["country"],
                "adult": costs_data.get("lift_adult_daily") if costs_data else None,
            })
    elif getattr(args, 'all'):
        # Re-acquire ALL published resorts (wrong + missing + suspicious + ok)
        targets = wrong + missing + suspicious + ok
    elif args.missing_only:
        targets = missing
    elif args.wrong_only:
        targets = wrong
    else:
        targets = wrong + missing  # Fix wrong and missing by default

    if not targets:
        print("No resorts to fix")
        return

    print(f"Fixing {len(targets)} resorts...")
    print()

    fixed = 0
    failed = 0
    for i, resort in enumerate(targets):
        print(f"  [{i+1}/{len(targets)}] {resort['name']} ({resort['country']})")
        result = await fix_resort_pricing(resort, args.write)
        if result["status"] == "fixed":
            fixed += 1
        else:
            failed += 1
        print()

    print(f"Results: {fixed} fixed, {failed} failed")
    print(f"Daily spend: ${get_daily_spend():.2f}")
    if not args.write and fixed > 0:
        print("  (Dry run — use --write to save to DB)")


if __name__ == "__main__":
    asyncio.run(main())
