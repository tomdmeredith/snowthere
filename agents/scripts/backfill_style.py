#!/usr/bin/env python3
"""Backfill style editing across existing resorts.

Usage:
    # Dry run (preview changes, no DB writes)
    python scripts/backfill_style.py --resort "Alta" --layers det

    # Deterministic only (free, safe)
    python scripts/backfill_style.py --batch --layers det --write

    # Det + em-dash contextual fix (~$0.20 for all resorts)
    python scripts/backfill_style.py --batch --layers det,em_dash --write

    # Full style edit on one resort (~$0.50-1.00)
    python scripts/backfill_style.py --resort "Alta" --layers det,em_dash,style --write

    # Batch with offset/limit
    python scripts/backfill_style.py --batch --batch-limit 10 --batch-offset 20 --layers det --write

Cost estimates (for ~95 resorts):
    det only:           $0.00
    det + em_dash:      ~$0.20
    det + em_dash + style: ~$24 (Sonnet Batch API recommended)
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.style import (
    apply_deterministic_style,
    apply_em_dash_fix,
    apply_full_style_edit,
)
from shared.style_profiles import get_style_profile
from shared.primitives.system import get_daily_spend

# Content sections that contain prose text (eligible for style editing)
PROSE_SECTIONS = [
    "quick_take",
    "getting_there",
    "where_to_stay",
    "lift_tickets",
    "on_mountain",
    "off_mountain",
    "parent_reviews_summary",
]


def get_published_resorts(limit: int = 200, offset: int = 0) -> list[dict]:
    """Get published resorts with their content."""
    client = get_supabase_client()

    section_select = ", ".join(PROSE_SECTIONS)
    response = (
        client.table("resorts")
        .select(f"id, name, country, resort_content({section_select})")
        .eq("status", "published")
        .order("updated_at", desc=False)  # Oldest first
        .range(offset, offset + limit - 1)
        .execute()
    )

    results = []
    for r in response.data or []:
        content_data = r.get("resort_content")
        if isinstance(content_data, list):
            content_data = content_data[0] if content_data else None
        if not content_data:
            continue

        # Build sections dict from individual columns
        sections = {}
        for col in PROSE_SECTIONS:
            val = content_data.get(col)
            if val and isinstance(val, str) and val.strip():
                sections[col] = val

        if sections:
            results.append({
                "id": r["id"],
                "name": r["name"],
                "country": r["country"],
                "sections": sections,
            })

    return results


def count_em_dashes(content: dict) -> int:
    """Count em-dashes across all text sections."""
    count = 0
    for value in content.values():
        if isinstance(value, str):
            count += value.count("\u2014")
    return count


async def process_resort(
    resort: dict,
    layers: list[str],
    profile_name: str,
    write: bool,
) -> dict:
    """Process a single resort through style layers."""
    name = resort["name"]
    sections = resort["sections"]
    resort_id = resort["id"]

    if not isinstance(sections, dict):
        return {"name": name, "status": "skipped", "reason": "sections not a dict"}

    original_em_dashes = count_em_dashes(sections)
    result = {"name": name, "original_em_dashes": original_em_dashes}

    current = dict(sections)

    # Layer 1: Deterministic
    if "det" in layers:
        profile = get_style_profile(profile_name)
        current = apply_deterministic_style(current, profile)
        result["det_applied"] = True

    # Layer 2: Em-dash contextual
    if "em_dash" in layers:
        current = await apply_em_dash_fix(current)
        result["em_dash_applied"] = True

    # Layer 3: Full style edit
    if "style" in layers:
        profile = get_style_profile(profile_name)
        current = await apply_full_style_edit(current, profile)
        result["style_applied"] = True

    final_em_dashes = count_em_dashes(current)
    result["final_em_dashes"] = final_em_dashes
    result["em_dashes_removed"] = original_em_dashes - final_em_dashes

    # Write to DB — update individual columns, not a "sections" blob
    if write:
        client = get_supabase_client()
        update_data = {}
        for col in PROSE_SECTIONS:
            if col in current and current[col] != sections.get(col):
                update_data[col] = current[col]

        if update_data:
            client.table("resort_content").update(
                update_data
            ).eq("resort_id", resort_id).execute()
            result["columns_updated"] = list(update_data.keys())
        else:
            result["columns_updated"] = []
        result["written"] = True
    else:
        result["written"] = False

    return result


async def main():
    parser = argparse.ArgumentParser(description="Backfill style editing")
    parser.add_argument("--resort", help="Single resort name")
    parser.add_argument("--batch", action="store_true", help="Process all published resorts")
    parser.add_argument("--batch-limit", type=int, default=200)
    parser.add_argument("--batch-offset", type=int, default=0)
    parser.add_argument("--layers", default="det", help="Comma-separated: det,em_dash,style")
    parser.add_argument("--profile", default="spielplatz", help="Style profile name")
    parser.add_argument("--write", action="store_true", help="Write changes to DB")

    args = parser.parse_args()
    layers = [l.strip() for l in args.layers.split(",")]

    print(f"Style Backfill")
    print(f"  Layers: {layers}")
    print(f"  Profile: {args.profile}")
    print(f"  Write: {args.write}")
    print()

    if args.resort:
        # Single resort
        client = get_supabase_client()
        section_select = ", ".join(PROSE_SECTIONS)
        response = (
            client.table("resorts")
            .select(f"id, name, country, resort_content({section_select})")
            .ilike("name", f"%{args.resort}%")
            .limit(1)
            .execute()
        )

        if not response.data:
            print(f"Resort not found: {args.resort}")
            return

        r = response.data[0]
        content_data = r.get("resort_content")
        if isinstance(content_data, list):
            content_data = content_data[0] if content_data else None

        if not content_data:
            print(f"No content found for {r['name']}")
            return

        sections = {}
        for col in PROSE_SECTIONS:
            val = content_data.get(col)
            if val and isinstance(val, str) and val.strip():
                sections[col] = val

        if not sections:
            print(f"No text sections found for {r['name']}")
            return

        resort = {
            "id": r["id"],
            "name": r["name"],
            "country": r["country"],
            "sections": sections,
        }

        result = await process_resort(resort, layers, args.profile, args.write)
        print(f"  {result['name']}: {result.get('em_dashes_removed', 0)} em-dashes removed, written={result.get('written')}")
        if result.get("columns_updated"):
            print(f"  Updated columns: {result['columns_updated']}")

    elif args.batch:
        resorts = get_published_resorts(limit=args.batch_limit, offset=args.batch_offset)
        print(f"  Found {len(resorts)} published resorts")
        print()

        total_removed = 0
        for i, resort in enumerate(resorts):
            result = await process_resort(resort, layers, args.profile, args.write)
            removed = result.get("em_dashes_removed", 0)
            total_removed += removed

            status = "written" if result.get("written") else "dry-run"
            print(f"  [{i+1}/{len(resorts)}] {result['name']}: {result.get('original_em_dashes', 0)} → {result.get('final_em_dashes', 0)} em-dashes ({status})")

        print()
        print(f"  Total em-dashes removed: {total_removed}")
        print(f"  Daily spend: ${get_daily_spend():.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
