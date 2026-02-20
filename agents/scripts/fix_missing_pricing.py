#!/usr/bin/env python3
"""Fix pricing for resorts where Tavily is rate-limited.

Two-pass approach:
  Pass 1: Exa URL discovery → scrape → Claude interpret (high confidence)
  Pass 2: Exa search_and_contents → Claude extraction (fallback)

Bypasses Tavily entirely.

Usage:
    python scripts/fix_missing_pricing.py              # Dry run
    python scripts/fix_missing_pricing.py --write      # Write to DB
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import settings
from shared.supabase_client import get_supabase_client
from shared.primitives.costs import (
    validate_costs,
    update_usd_columns,
    get_currency_for_country,
    scrape_and_interpret_pricing,
    COUNTRY_CURRENCIES,
)
from shared.primitives.system import log_cost, get_daily_spend

# The 6 resorts still missing pricing (Saint-Gervais + Serre Chevalier already fixed)
TARGETS = [
    ("Appi Kogen", "Japan"),
    ("Falls Creek", "Australia"),
    ("Mount Hutt", "New Zealand"),
    ("Solitude", "United States"),
    ("Stevens Pass", "United States"),
    ("The Remarkables", "New Zealand"),
]


async def exa_find_and_scrape(resort_name: str, country: str) -> dict | None:
    """Pass 1: Exa URL discovery → scrape → Claude interpret. Higher confidence."""
    from exa_py import Exa

    exa = Exa(api_key=settings.exa_api_key)

    # Try multiple query variations to improve URL discovery
    queries = [
        f"{resort_name} lift ticket prices 2025 2026 season",
        f"{resort_name} {country} ski pass daily rate",
    ]

    for query in queries:
        results = exa.search(query, num_results=5)
        log_cost("exa", 0.006, None, {"stage": "pricing_url_discovery", "resort": resort_name})

        for r in results.results:
            url = r.url.lower()
            # Skip aggregators
            aggregators = ["tripadvisor", "expedia", "booking.com", "liftopia",
                           "onthesnow", "skiresort.info", "wikipedia", "j2ski"]
            if any(a in url for a in aggregators):
                continue

            print(f"    Trying URL: {r.url}")
            result = await scrape_and_interpret_pricing(r.url, resort_name, country)
            if result.success:
                return {
                    "costs": result.costs,
                    "currency": result.currency,
                    "confidence": result.confidence,
                    "source": "exa_scrape",
                    "url": r.url,
                }

        await asyncio.sleep(0.5)

    return None


async def exa_search_with_content(resort_name: str, country: str) -> list[str]:
    """Pass 2: Exa search_and_contents for text snippets."""
    from exa_py import Exa

    exa = Exa(api_key=settings.exa_api_key)

    results = exa.search_and_contents(
        f"{resort_name} {country} ski lift ticket price 2025 2026",
        text=True,
        num_results=5,
    )

    log_cost("exa", 0.01, None, {"stage": "pricing_content_search", "resort": resort_name})

    snippets = []
    for r in results.results:
        text = getattr(r, "text", "") or ""
        if text:
            snippets.append(f"Source: {r.url}\n{text[:800]}")

    return snippets


async def extract_pricing(resort_name: str, country: str, snippets: list[str]) -> dict | None:
    """Use Claude Haiku to extract pricing from search snippets."""
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    combined = "\n\n---\n\n".join(snippets)
    currency = get_currency_for_country(country)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": f"""Extract ski lift ticket pricing for {resort_name}, {country} from these search results.

Search results:
{combined}

Return ONLY a JSON object:
{{
    "lift_adult_daily": <number in {currency} or null>,
    "lift_child_daily": <number in {currency} or null>,
    "currency": "{currency}",
    "confidence": <0.0-1.0>
}}

Extract the STANDARD ADULT 1-DAY WINDOW PRICE for the current/recent season.
Not multi-day, not promo, not online-only discounts.
If the results mention prices in a different currency, convert to {currency}.
Be conservative — only extract prices you're confident about."""}],
    )

    log_cost("anthropic", 0.003, None, {"stage": "pricing_extraction", "resort": resort_name})

    text = response.content[0].text
    json_match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if not json_match:
        return None

    data = json.loads(json_match.group())

    costs = {}
    if data.get("lift_adult_daily"):
        costs["lift_adult_daily"] = float(data["lift_adult_daily"])
    if data.get("lift_child_daily"):
        costs["lift_child_daily"] = float(data["lift_child_daily"])

    if not costs:
        return None

    validated, notes = validate_costs(costs, country)
    if not validated:
        print(f"    Validation failed: {'; '.join(notes)}")
        return None

    for note in notes:
        print(f"    Note: {note}")

    return {
        "costs": validated,
        "currency": data.get("currency", currency),
        "confidence": float(data.get("confidence", 0.6)),
        "source": "exa_content",
    }


async def main():
    parser = argparse.ArgumentParser(description="Fix missing pricing (Tavily-free)")
    parser.add_argument("--write", action="store_true", help="Write to DB")
    args = parser.parse_args()

    client = get_supabase_client()

    # Check which targets actually still need pricing
    actual_targets = []
    for name, country in TARGETS:
        resp = (
            client.table("resorts")
            .select("id, resort_costs(lift_adult_daily)")
            .eq("name", name)
            .eq("country", country)
            .limit(1)
            .execute()
        )
        if not resp.data:
            print(f"  SKIP: {name} not found in DB")
            continue
        costs_data = resp.data[0].get("resort_costs")
        if isinstance(costs_data, list):
            costs_data = costs_data[0] if costs_data else None
        if costs_data and costs_data.get("lift_adult_daily"):
            print(f"  SKIP: {name} already has pricing (${costs_data['lift_adult_daily']})")
            continue
        actual_targets.append((name, country, resp.data[0]["id"]))

    if not actual_targets:
        print("All resorts already have pricing!")
        return

    print(f"\nFixing pricing for {len(actual_targets)} resorts (Exa + Claude, no Tavily)")
    print(f"  Write: {args.write}")
    print()

    fixed = 0
    failed = 0

    for i, (name, country, resort_id) in enumerate(actual_targets):
        print(f"  [{i+1}/{len(actual_targets)}] {name} ({country})")

        # Pass 1: Exa URL discovery → scrape → Claude interpret
        result = None
        try:
            result = await exa_find_and_scrape(name, country)
            if result:
                print(f"    Pass 1 (scrape): SUCCESS from {result.get('url', 'unknown')}")
        except Exception as e:
            print(f"    Pass 1 (scrape): failed — {e}")

        # Pass 2: Exa content search → Claude extraction
        if not result:
            print(f"    Pass 1 (scrape): no pricing found, trying Pass 2...")
            try:
                snippets = await exa_search_with_content(name, country)
                if snippets:
                    print(f"    Found {len(snippets)} snippets")
                    result = await extract_pricing(name, country, snippets)
                    if result:
                        print(f"    Pass 2 (content): SUCCESS")
                else:
                    print(f"    Pass 2: No search results")
            except Exception as e:
                print(f"    Pass 2 (content): failed — {e}")

        if not result:
            print(f"    FAILED: Both passes could not find pricing")
            failed += 1
            print()
            continue

        costs = result["costs"]
        currency = result["currency"]
        confidence = result["confidence"]
        source = result.get("source", "unknown")

        adult = costs.get("lift_adult_daily")
        child = costs.get("lift_child_daily")
        print(f"    {currency} {adult} adult, {currency} {child} child (confidence: {confidence:.2f}, source: {source})")

        if args.write and adult is not None:
            update_data = {**costs, "currency": currency, "resort_id": resort_id}
            client.table("resort_costs").upsert(
                update_data, on_conflict="resort_id"
            ).execute()
            update_usd_columns(resort_id, costs, currency)
            print(f"    Written to DB (+ USD columns)")

        fixed += 1
        await asyncio.sleep(1)
        print()

    print(f"Results: {fixed} fixed, {failed} failed")
    print(f"Daily spend: ${get_daily_spend():.2f}")
    if not args.write and fixed > 0:
        print("  (Dry run — use --write to save to DB)")


if __name__ == "__main__":
    asyncio.run(main())
