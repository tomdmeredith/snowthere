#!/usr/bin/env python3
"""Backfill missing cost data for published resorts.

For resorts where estimated_family_daily is NULL, uses Claude to estimate
costs from existing content sections and country/region averages.

Usage:
    python scripts/backfill_costs.py                    # Full backfill
    python scripts/backfill_costs.py --dry-run           # Preview only
    python scripts/backfill_costs.py --limit 5           # Process 5 resorts
    python scripts/backfill_costs.py --resort "Zermatt"  # Single resort
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.database import update_resort_costs
from shared.primitives.system import log_cost

import anthropic
from shared.config import settings


async def estimate_cost_from_content(
    resort_name: str,
    country: str,
    content: dict,
    country_avg: float | None,
) -> float | None:
    """Use Claude to estimate daily family cost from content sections."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    content_text = ""
    for section_name in ["lift_tickets", "where_to_stay", "off_mountain", "getting_there"]:
        section = content.get(section_name, "")
        if section:
            content_text += f"\n{section_name}:\n{section[:500]}\n"

    if not content_text.strip():
        return country_avg

    prompt = f"""Estimate the total daily cost for a family of 4 (2 adults, 2 kids ages 6 and 10)
skiing at {resort_name}, {country}. Include: lift tickets, mid-range lodging, meals, and equipment rental.

Content sections:
{content_text}

{f"Country average for other resorts: ${country_avg:.0f}/day" if country_avg else ""}

Return ONLY a JSON object: {{"estimated_family_daily": <number>, "currency": "USD"}}
No explanation, just the JSON."""

    try:
        message = client.messages.create(
            model=settings.default_model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1].split("```")[0]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
        return parsed.get("estimated_family_daily")
    except Exception as e:
        print(f"  Estimation failed: {e}")
        return country_avg


async def backfill_costs(
    dry_run: bool = False,
    limit: int | None = None,
    resort_filter: str | None = None,
):
    """Backfill missing cost data."""
    client = get_supabase_client()

    # Get resorts missing cost data
    query = (
        client.table("resorts")
        .select("id, name, country, slug")
        .eq("status", "published")
    )
    if resort_filter:
        query = query.ilike("name", f"%{resort_filter}%")

    resorts_resp = query.execute()
    resorts = resorts_resp.data or []

    # Batch-fetch all cost data in one query (avoids N+1)
    all_costs_resp = (
        client.table("resort_costs")
        .select("resort_id, estimated_family_daily")
        .execute()
    )
    cost_lookup = {
        c["resort_id"]: c.get("estimated_family_daily")
        for c in (all_costs_resp.data or [])
    }
    missing_cost_resorts = [
        r for r in resorts if cost_lookup.get(r["id"]) is None
    ]

    if limit:
        missing_cost_resorts = missing_cost_resorts[:limit]

    print(f"Found {len(missing_cost_resorts)} resorts missing cost data")

    if not missing_cost_resorts:
        return

    # Build country avg lookup using the already-fetched cost data
    resort_country = {r["id"]: r["country"] for r in resorts}
    country_costs: dict[str, list[float]] = {}
    for c in all_costs_resp.data or []:
        country = resort_country.get(c["resort_id"])
        if country and c.get("estimated_family_daily"):
            country_costs.setdefault(country, []).append(c["estimated_family_daily"])
    country_avgs = {c: sum(v) / len(v) for c, v in country_costs.items() if v}

    for resort in missing_cost_resorts:
        print(f"\nProcessing: {resort['name']} ({resort['country']})")

        # Get content for estimation
        content_resp = (
            client.table("resort_content")
            .select("*")
            .eq("resort_id", resort["id"])
            .execute()
        )
        content = content_resp.data[0] if content_resp.data else {}
        country_avg = country_avgs.get(resort["country"])

        estimated = await estimate_cost_from_content(
            resort["name"], resort["country"], content, country_avg
        )

        if estimated:
            print(f"  Estimated: ${estimated:.0f}/day")
            if not dry_run:
                update_resort_costs(resort["id"], {
                    "estimated_family_daily": estimated,
                    "currency": "USD",
                })
                print(f"  Saved to database")
            else:
                print(f"  [DRY RUN] Would save ${estimated:.0f}/day")
        else:
            print(f"  Could not estimate cost")


def main():
    parser = argparse.ArgumentParser(description="Backfill missing cost data")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--limit", type=int, help="Max resorts to process")
    parser.add_argument("--resort", type=str, help="Filter by resort name")
    args = parser.parse_args()

    asyncio.run(backfill_costs(
        dry_run=args.dry_run,
        limit=args.limit,
        resort_filter=args.resort,
    ))


if __name__ == "__main__":
    main()
